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


def test_t_cure_never_reaches_maturity():
    params = DGPParams(pc=0.5, prd=0.3, mean_cure_month=65.0)
    exposures = simulate_portfolio(params, n=20_000, rng=np.random.default_rng(0))
    t_cure = exposures.loc[exposures["cured"], "t_cure"]
    assert (t_cure < params.t_maturity).all()


def test_t_rd_never_negative_at_high_mean_cure_month():
    params = DGPParams(pc=0.5, prd=0.3, mean_cure_month=65.0)
    exposures = simulate_portfolio(params, n=20_000, rng=np.random.default_rng(0))
    t_rd = exposures.loc[exposures["redefaulted"], "t_rd"]
    assert (t_rd >= 0).all()


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
    assert set(inputs) == {"pc", "prd", "rr", "rr_brd", "rr_homogeneous", "rr_ard", "lgc"}
    assert all(math.isfinite(v) for v in inputs.values())


def test_estimate_formula_inputs_handles_no_redefaults():
    params = DGPParams(pc=0.2, prd=0.0)
    exposures = simulate_portfolio(params, n=2000, rng=np.random.default_rng(0))
    inputs = estimate_formula_inputs(exposures)
    assert inputs["prd"] == 0.0
    assert inputs["rr_brd"] == 0.0
    assert inputs["rr_ard"] == 0.0


def test_rr_ard_tracks_shifted_recovery_independently_of_rr_homogeneous():
    params = DGPParams(pc=0.2, prd=0.3, rr_after_redefault_alpha=0.15, rr_after_redefault_beta=0.4)
    exposures = simulate_portfolio(params, n=20_000, rng=np.random.default_rng(0))
    inputs = estimate_formula_inputs(exposures)

    true_rr_ard_mean = 0.15 / (0.15 + 0.4)
    true_rr_mean = 0.3 / (0.3 + 0.3)
    assert inputs["rr_ard"] == pytest.approx(true_rr_ard_mean, abs=0.02)
    assert inputs["rr_homogeneous"] == pytest.approx(true_rr_mean, abs=0.02)


def test_rr_homogeneous_absorbs_merged_exposures_under_compliance():
    params = DGPParams(pc=0.2, prd=0.3, mean_cure_month=20)
    exposures = simulate_portfolio(params, n=20_000, rng=np.random.default_rng(0))
    merged = exposures["redefaulted"] & (exposures["t_rd"] < 9.0)
    assert merged.sum() > 0

    inputs = estimate_formula_inputs(exposures, merge_threshold_months=9.0)
    merged_rr = 1 - (1 - exposures.loc[merged, "rr_before_redefault"]) * (
        1 - exposures.loc[merged, "rr_after_redefault"]
    )
    expected = pd.concat([exposures.loc[~exposures["cured"], "rr"], merged_rr]).mean()
    assert inputs["rr_homogeneous"] == pytest.approx(expected)

    never_cured_only = exposures.loc[~exposures["cured"], "rr"].mean()
    assert inputs["rr_homogeneous"] != pytest.approx(never_cured_only)


def test_estimate_formula_inputs_handles_no_cures():
    params = DGPParams(pc=0.0, prd=0.1)
    exposures = simulate_portfolio(params, n=2000, rng=np.random.default_rng(0))
    inputs = estimate_formula_inputs(exposures)
    assert inputs["pc"] == 0.0
    assert inputs["prd"] == 0.0
    assert inputs["lgc"] == 0.0


def test_merge_threshold_none_matches_default_behavior():
    params = DGPParams(pc=0.2, prd=0.3, mean_cure_month=20)
    exposures = simulate_portfolio(params, n=5000, rng=np.random.default_rng(0))
    assert estimate_formula_inputs(exposures) == estimate_formula_inputs(
        exposures, merge_threshold_months=None
    )


def test_merge_threshold_excludes_early_redefaults_from_independent_count():
    params = DGPParams(pc=0.2, prd=0.3, mean_cure_month=20)
    exposures = simulate_portfolio(params, n=20_000, rng=np.random.default_rng(0))
    n_merged = int((exposures["redefaulted"] & (exposures["t_rd"] < 9)).sum())
    assert n_merged > 0

    naive = estimate_formula_inputs(exposures)
    compliant = estimate_formula_inputs(exposures, merge_threshold_months=9.0)
    assert compliant["prd"] < naive["prd"]
    assert compliant["pc"] < naive["pc"]


def test_merge_threshold_zero_matches_default_behavior():
    params = DGPParams(pc=0.2, prd=0.3, mean_cure_month=20)
    exposures = simulate_portfolio(params, n=5000, rng=np.random.default_rng(0))
    naive = estimate_formula_inputs(exposures)
    compliant = estimate_formula_inputs(exposures, merge_threshold_months=0.0)
    assert compliant["pc"] == pytest.approx(naive["pc"])
    assert compliant["prd"] == pytest.approx(naive["prd"])


def test_merge_threshold_handles_no_redefaults():
    params = DGPParams(pc=0.2, prd=0.0)
    exposures = simulate_portfolio(params, n=2000, rng=np.random.default_rng(0))
    inputs = estimate_formula_inputs(exposures, merge_threshold_months=9.0)
    assert inputs["prd"] == 0.0
    assert inputs["rr_brd"] == 0.0
