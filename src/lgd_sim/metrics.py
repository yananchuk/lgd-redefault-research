"""Aggregation of raw experiment output into summary statistics."""

from __future__ import annotations

import pandas as pd

ERROR_COLUMNS = ["lgd_basic_error", "lgd_lgc_error", "lgd_prd_error", "lgd_new_error"]


def summarize(results: pd.DataFrame, sweep_param: str) -> pd.DataFrame:
    """Aggregate per-replication relative errors into mean and SD per sweep value.

    Args:
        results: Raw output of `experiment.run_baseline`, one row per
            (sweep value, replication).
        sweep_param: Name of the swept column to group by.

    Returns:
        One row per sweep value, with `{column}_mean` and `{column}_sd` for
        each formula's relative error column.
    """
    stat_suffix = {"mean": "mean", "std": "sd"}
    summary = results.groupby(sweep_param)[ERROR_COLUMNS].agg(["mean", "std"])
    summary.columns = [f"{column}_{stat_suffix[stat]}" for column, stat in summary.columns]
    return summary.reset_index()
