import numpy as np
import pytest

from lgd_sim.dgp import DGPParams
from lgd_sim.experiment import run_baseline, run_complexity_sweep
from lgd_sim.metrics import summarize, summarize_rmse

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
        "lgd_true_mean",
        "lgd_true_sd",
        "lgd_basic_mean",
        "lgd_basic_sd",
        "lgd_lgc_mean",
        "lgd_lgc_sd",
        "lgd_prd_mean",
        "lgd_prd_sd",
        "lgd_new_mean",
        "lgd_new_sd",
        "n_replications",
    }
    assert set(summary.columns) == expected


def test_summarize_n_replications_matches_group_size():
    results = run_baseline(
        sweep_param="prd",
        sweep_values=[0.1, 0.2],
        base_params=BASELINE,
        n_exposures=500,
        n_replications=7,
        rng=np.random.default_rng(0),
    )
    summary = summarize(results, sweep_param="prd")
    assert (summary["n_replications"] == 7).all()


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


def test_summarize_rmse_returns_one_row_per_sweep_value():
    results = run_complexity_sweep(
        n_exposures_values=[200, 1000, 5000],
        base_params=BASELINE,
        n_replications=5,
        rng=np.random.default_rng(0),
    )
    summary = summarize_rmse(results, sweep_param="n_exposures")
    assert len(summary) == 3
    assert set(summary["n_exposures"]) == {200, 1000, 5000}


def test_summarize_rmse_returns_expected_columns():
    results = run_complexity_sweep(
        n_exposures_values=[200, 1000],
        base_params=BASELINE,
        n_replications=5,
        rng=np.random.default_rng(0),
    )
    summary = summarize_rmse(results, sweep_param="n_exposures")
    expected = {
        "n_exposures",
        "lgd_basic_error_rmse",
        "lgd_lgc_error_rmse",
        "lgd_prd_error_rmse",
        "lgd_new_error_rmse",
        "n_redefault_mean",
        "n_replications",
    }
    assert set(summary.columns) == expected


def test_summarize_rmse_matches_manual_calculation():
    results = run_complexity_sweep(
        n_exposures_values=[500],
        base_params=BASELINE,
        n_replications=20,
        rng=np.random.default_rng(0),
    )
    summary = summarize_rmse(results, sweep_param="n_exposures")
    expected_rmse = (results["lgd_basic_error"] ** 2).mean() ** 0.5
    assert summary["lgd_basic_error_rmse"].iloc[0] == pytest.approx(expected_rmse)


def test_summarize_rmse_decreases_with_larger_portfolios():
    results = run_complexity_sweep(
        n_exposures_values=[200, 20_000],
        base_params=BASELINE,
        n_replications=30,
        rng=np.random.default_rng(0),
    )
    summary = summarize_rmse(results, sweep_param="n_exposures")
    rmse_by_n = summary.set_index("n_exposures")["lgd_new_error_rmse"]
    assert rmse_by_n[20_000] < rmse_by_n[200]
