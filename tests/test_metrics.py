import numpy as np
import pytest

from lgd_sim.dgp import DGPParams
from lgd_sim.experiment import run_baseline
from lgd_sim.metrics import summarize

BASELINE = DGPParams(pc=0.2, prd=0.1)


def test_summarize_returns_one_row_per_sweep_value():
    results = run_baseline(
        sweep_param="prd",
        sweep_values=[0.0, 0.2, 0.4],
        base_params=BASELINE,
        n_exposures=500,
        n_replications=5,
        rng=np.random.default_rng(0),
    )
    summary = summarize(results, sweep_param="prd")
    assert len(summary) == 3
    assert set(summary["prd"]) == {0.0, 0.2, 0.4}


def test_summarize_returns_mean_and_sd_columns():
    results = run_baseline(
        sweep_param="pc",
        sweep_values=[0.1, 0.3],
        base_params=BASELINE,
        n_exposures=500,
        n_replications=5,
        rng=np.random.default_rng(0),
    )
    summary = summarize(results, sweep_param="pc")
    expected = {
        "pc",
        "lgd_basic_error_mean",
        "lgd_basic_error_sd",
        "lgd_lgc_error_mean",
        "lgd_lgc_error_sd",
        "lgd_prd_error_mean",
        "lgd_prd_error_sd",
        "lgd_new_error_mean",
        "lgd_new_error_sd",
    }
    assert set(summary.columns) == expected


def test_summarize_mean_matches_manual_calculation():
    results = run_baseline(
        sweep_param="prd",
        sweep_values=[0.2],
        base_params=BASELINE,
        n_exposures=500,
        n_replications=10,
        rng=np.random.default_rng(0),
    )
    summary = summarize(results, sweep_param="prd")
    expected_mean = results["lgd_basic_error"].mean()
    assert summary["lgd_basic_error_mean"].iloc[0] == pytest.approx(expected_mean)
