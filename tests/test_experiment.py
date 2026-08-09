import math

import numpy as np
import pandas as pd
import pytest

from lgd_sim.dgp import DGPParams
from lgd_sim.experiment import run_baseline

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
