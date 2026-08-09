import math

import numpy as np
import pandas as pd
import pytest

from lgd_sim.dgp import DGPParams, estimate_formula_inputs, simulate_portfolio, true_lgd

BASELINE = DGPParams(pc=0.2, prd=0.1)


def test_reproducible_given_same_seed():
    a = simulate_portfolio(BASELINE, n=1000, rng=np.random.default_rng(42))
    b = simulate_portfolio(BASELINE, n=1000, rng=np.random.default_rng(42))
    pd.testing.assert_frame_equal(a, b)


def test_different_seeds_give_different_output():
    a = simulate_portfolio(BASELINE, n=1000, rng=np.random.default_rng(1))
    b = simulate_portfolio(BASELINE, n=1000, rng=np.random.default_rng(2))
    assert not a["loss"].equals(b["loss"])


def test_cure_and_redefault_fractions_match_parameters():
    exposures = simulate_portfolio(BASELINE, n=50_000, rng=np.random.default_rng(0))
    assert exposures["cured"].mean() == pytest.approx(BASELINE.pc, abs=0.01)
    redefault_rate = exposures.loc[exposures["cured"], "redefaulted"].mean()
    assert redefault_rate == pytest.approx(BASELINE.prd, abs=0.02)


def test_non_cured_exposures_have_no_redefault_fields():
    exposures = simulate_portfolio(BASELINE, n=2000, rng=np.random.default_rng(0))
    non_cured = exposures.loc[~exposures["cured"]]
    assert non_cured["t_cure"].isna().all()
    assert non_cured["rr_after_redefault"].isna().all()


def test_cured_and_never_redefaulted_exposures_have_zero_loss():
    exposures = simulate_portfolio(BASELINE, n=2000, rng=np.random.default_rng(0))
    cured_forever = exposures.loc[exposures["cured"] & ~exposures["redefaulted"]]
    assert (cured_forever["loss"] == 0).all()


def test_swappable_recovery_distribution_shifts_mean():
    lower_mean_params = DGPParams(
        pc=0.2, prd=0.5, rr_after_redefault_alpha=0.15, rr_after_redefault_beta=0.4
    )
    baseline = simulate_portfolio(
        DGPParams(pc=0.2, prd=0.5), n=20_000, rng=np.random.default_rng(0)
    )
    misspecified = simulate_portfolio(lower_mean_params, n=20_000, rng=np.random.default_rng(0))

    baseline_mean = baseline["rr_after_redefault"].dropna().mean()
    misspecified_mean = misspecified["rr_after_redefault"].dropna().mean()
    assert misspecified_mean < baseline_mean


def test_true_lgd_is_a_valid_fraction():
    exposures = simulate_portfolio(BASELINE, n=5000, rng=np.random.default_rng(0))
    lgd = true_lgd(exposures)
    assert 0.0 <= lgd <= 1.0


def test_estimate_formula_inputs_returns_expected_keys():
    exposures = simulate_portfolio(BASELINE, n=5000, rng=np.random.default_rng(0))
    inputs = estimate_formula_inputs(exposures)
    assert set(inputs) == {"pc", "prd", "rr", "rr_brd", "lgc"}
    assert all(math.isfinite(v) for v in inputs.values())


def test_estimate_formula_inputs_handles_no_redefaults():
    params = DGPParams(pc=0.2, prd=0.0)
    exposures = simulate_portfolio(params, n=2000, rng=np.random.default_rng(0))
    inputs = estimate_formula_inputs(exposures)
    assert inputs["prd"] == 0.0
    assert inputs["rr_brd"] == 0.0


def test_estimate_formula_inputs_handles_no_cures():
    params = DGPParams(pc=0.0, prd=0.1)
    exposures = simulate_portfolio(params, n=2000, rng=np.random.default_rng(0))
    inputs = estimate_formula_inputs(exposures)
    assert inputs["pc"] == 0.0
    assert inputs["prd"] == 0.0
    assert inputs["lgc"] == 0.0
