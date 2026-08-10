"""Aggregation of raw experiment output into summary statistics."""

from __future__ import annotations

import pandas as pd

ERROR_COLUMNS = ["lgd_basic_error", "lgd_lgc_error", "lgd_prd_error", "lgd_new_error"]
VALUE_COLUMNS = ["lgd_true", "lgd_basic", "lgd_lgc", "lgd_prd", "lgd_new"]


def summarize(results: pd.DataFrame, sweep_param: str) -> pd.DataFrame:
    """Aggregate per-replication relative errors and raw LGD values into mean and SD.

    Args:
        results: Raw output of `experiment.run_baseline`, one row per
            (sweep value, replication).
        sweep_param: Name of the swept column to group by.

    Returns:
        One row per sweep value, with `{column}_mean` and `{column}_sd` for each
        formula's relative error column and each raw LGD value column (`lgd_true`
        and each formula's own prediction), plus `n_replications`, the number of
        replications behind each row's statistics.
    """
    stat_suffix = {"mean": "mean", "std": "sd"}
    columns = ERROR_COLUMNS + VALUE_COLUMNS
    grouped = results.groupby(sweep_param)
    summary = grouped[columns].agg(["mean", "std"])
    summary.columns = [f"{column}_{stat_suffix[stat]}" for column, stat in summary.columns]
    summary = summary.reset_index()
    summary["n_replications"] = grouped.size().to_numpy()
    return summary


def summarize_rmse(results: pd.DataFrame, sweep_param: str) -> pd.DataFrame:
    """Aggregate per-replication relative errors into RMSE per sweep value.

    Args:
        results: Raw output of `experiment.run_complexity_sweep`, one row per
            (sweep value, replication).
        sweep_param: Name of the swept column to group by.

    Returns:
        One row per sweep value, with `{column}_rmse` for each formula's
        relative error column, `n_redefault_mean` (the mean observed
        re-default count across replications), and `n_replications`.
    """
    grouped = results.groupby(sweep_param)
    rmse = (results[ERROR_COLUMNS] ** 2).groupby(results[sweep_param]).mean() ** 0.5
    rmse.columns = [f"{column}_rmse" for column in rmse.columns]
    summary = rmse.reset_index()
    summary["n_redefault_mean"] = grouped["n_redefault"].mean().to_numpy()
    summary["n_replications"] = grouped.size().to_numpy()
    return summary
