import math

import numpy as np
import pandas as pd
import pytest

from lgd_sim.dgp import DGPParams
from lgd_sim.experiment import run_baseline, run_complexity_sweep, run_merge_compliance

BASELINE = DGPParams(pc=0.2, prd=0.1)
ERROR_COLUMNS = {"lgd_basic_error", "lgd_lgc_error", "lgd_prd_error", "lgd_new_error"}
VALUE_COLUMNS = {"lgd_true", "lgd_basic", "lgd_lgc", "lgd_prd", "lgd_new"}


def test_run_baseline_returns_expected_columns():
    result = run_baseline(
        sweep_param="prd",
        sweep_values=[0.0, 0.2],
        base_params=BASELINE,
        n_exposures=500,
        n_replications=3,
        rng=np.random.default_rng(0),
    )
    assert set(result.columns) == ERROR_COLUMNS | VALUE_COLUMNS | {"prd"}


def test_run_baseline_row_count_matches_sweep_times_replications():
    result = run_baseline(
        sweep_param="pc",
        sweep_values=[0.1, 0.2, 0.3],
        base_params=BASELINE,
        n_exposures=500,
        n_replications=4,
        rng=np.random.default_rng(0),
    )
    assert len(result) == 3 * 4


def test_run_baseline_reproducible_given_same_seed():
    kwargs = {
        "sweep_param": "mean_cure_month",
        "sweep_values": [3.0, 5.0],
        "base_params": BASELINE,
        "n_exposures": 500,
        "n_replications": 3,
    }
    a = run_baseline(rng=np.random.default_rng(42), **kwargs)
    b = run_baseline(rng=np.random.default_rng(42), **kwargs)
    pd.testing.assert_frame_equal(a, b)


def test_run_baseline_sweeps_the_requested_parameter():
    result = run_baseline(
        sweep_param="prd",
        sweep_values=[0.0, 0.3],
        base_params=BASELINE,
        n_exposures=500,
        n_replications=2,
        rng=np.random.default_rng(0),
    )
    assert set(result["prd"]) == {0.0, 0.3}


def test_run_baseline_holds_other_params_fixed():
    result = run_baseline(
        sweep_param="prd",
        sweep_values=[0.4],
        base_params=BASELINE,
        n_exposures=2000,
        n_replications=1,
        rng=np.random.default_rng(0),
    )
    assert all(math.isfinite(v) for v in result.iloc[0][list(ERROR_COLUMNS)])


def test_run_baseline_error_columns_match_raw_values():
    result = run_baseline(
        sweep_param="prd",
        sweep_values=[0.3],
        base_params=BASELINE,
        n_exposures=500,
        n_replications=5,
        rng=np.random.default_rng(0),
    )
    expected_error = result["lgd_new"] / result["lgd_true"] - 1
    pd.testing.assert_series_equal(result["lgd_new_error"], expected_error, check_names=False)


def test_run_baseline_rejects_unknown_sweep_param():
    with pytest.raises(TypeError):
        run_baseline(
            sweep_param="not_a_field",
            sweep_values=[0.1],
            base_params=BASELINE,
            n_exposures=500,
            n_replications=1,
            rng=np.random.default_rng(0),
        )


def test_run_complexity_sweep_returns_expected_columns():
    result = run_complexity_sweep(
        n_exposures_values=[200, 1000],
        base_params=BASELINE,
        n_replications=3,
        rng=np.random.default_rng(0),
    )
    expected = ERROR_COLUMNS | VALUE_COLUMNS | {"n_exposures", "n_redefault"}
    assert set(result.columns) == expected


def test_run_complexity_sweep_row_count_matches_sweep_times_replications():
    result = run_complexity_sweep(
        n_exposures_values=[200, 500, 1000],
        base_params=BASELINE,
        n_replications=4,
        rng=np.random.default_rng(0),
    )
    assert len(result) == 3 * 4


def test_run_complexity_sweep_reproducible_given_same_seed():
    kwargs = {
        "n_exposures_values": [200, 1000],
        "base_params": BASELINE,
        "n_replications": 3,
    }
    a = run_complexity_sweep(rng=np.random.default_rng(42), **kwargs)
    b = run_complexity_sweep(rng=np.random.default_rng(42), **kwargs)
    pd.testing.assert_frame_equal(a, b)


def test_run_complexity_sweep_sweeps_n_exposures():
    result = run_complexity_sweep(
        n_exposures_values=[200, 1000],
        base_params=BASELINE,
        n_replications=2,
        rng=np.random.default_rng(0),
    )
    assert set(result["n_exposures"]) == {200, 1000}


def test_run_complexity_sweep_redefault_count_grows_with_n_exposures():
    result = run_complexity_sweep(
        n_exposures_values=[200, 20_000],
        base_params=BASELINE,
        n_replications=5,
        rng=np.random.default_rng(0),
    )
    mean_by_n = result.groupby("n_exposures")["n_redefault"].mean()
    assert mean_by_n[20_000] > mean_by_n[200]


def test_run_merge_compliance_returns_expected_columns():
    result = run_merge_compliance(
        sweep_param="mean_cure_month",
        sweep_values=[5.0, 20.0],
        base_params=DGPParams(pc=0.2, prd=0.3),
        n_exposures=500,
        n_replications=3,
        rng=np.random.default_rng(0),
    )
    expected = (
        ERROR_COLUMNS | VALUE_COLUMNS | {"mean_cure_month", "regime", "n_redefault", "n_merged"}
    )
    assert set(result.columns) == expected


def test_run_merge_compliance_row_count_matches_sweep_times_replications_times_regimes():
    result = run_merge_compliance(
        sweep_param="mean_cure_month",
        sweep_values=[5.0, 20.0, 40.0],
        base_params=DGPParams(pc=0.2, prd=0.3),
        n_exposures=500,
        n_replications=4,
        rng=np.random.default_rng(0),
    )
    assert len(result) == 3 * 4 * 2


def test_run_merge_compliance_reproducible_given_same_seed():
    kwargs = {
        "sweep_param": "mean_cure_month",
        "sweep_values": [5.0, 20.0],
        "base_params": DGPParams(pc=0.2, prd=0.3),
        "n_exposures": 500,
        "n_replications": 3,
    }
    a = run_merge_compliance(rng=np.random.default_rng(42), **kwargs)
    b = run_merge_compliance(rng=np.random.default_rng(42), **kwargs)
    pd.testing.assert_frame_equal(a, b)


def test_run_merge_compliance_has_both_regimes():
    result = run_merge_compliance(
        sweep_param="mean_cure_month",
        sweep_values=[20.0],
        base_params=DGPParams(pc=0.2, prd=0.3),
        n_exposures=500,
        n_replications=2,
        rng=np.random.default_rng(0),
    )
    assert set(result["regime"]) == {"naive", "compliant"}


def test_run_merge_compliance_naive_and_compliant_share_the_same_simulated_portfolio():
    result = run_merge_compliance(
        sweep_param="mean_cure_month",
        sweep_values=[20.0],
        base_params=DGPParams(pc=0.2, prd=0.3),
        n_exposures=500,
        n_replications=2,
        rng=np.random.default_rng(0),
    )
    naive = result[result["regime"] == "naive"].reset_index(drop=True)
    compliant = result[result["regime"] == "compliant"].reset_index(drop=True)
    pd.testing.assert_series_equal(naive["lgd_true"], compliant["lgd_true"], check_names=False)


def test_run_merge_compliance_regimes_diverge_when_redefaults_are_fast():
    result = run_merge_compliance(
        sweep_param="mean_cure_month",
        sweep_values=[55.0],
        base_params=DGPParams(pc=0.2, prd=0.3),
        n_exposures=5000,
        n_replications=1,
        rng=np.random.default_rng(0),
    )
    naive = result[result["regime"] == "naive"].iloc[0]
    compliant = result[result["regime"] == "compliant"].iloc[0]
    assert naive["lgd_basic_error"] != compliant["lgd_basic_error"]


def test_run_merge_compliance_merged_share_grows_with_mean_cure_month():
    result = run_merge_compliance(
        sweep_param="mean_cure_month",
        sweep_values=[5.0, 55.0],
        base_params=DGPParams(pc=0.2, prd=0.3),
        n_exposures=5000,
        n_replications=20,
        rng=np.random.default_rng(0),
    )
    naive = result[result["regime"] == "naive"]
    merged_share = naive.groupby("mean_cure_month").apply(
        lambda g: g["n_merged"].sum() / g["n_redefault"].sum(), include_groups=False
    )
    assert merged_share[55.0] > merged_share[5.0]
