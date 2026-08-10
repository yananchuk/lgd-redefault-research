"""Experiment runners for the LGD re-default bias study (see docs/dgp_assumptions.md)."""

from __future__ import annotations

import dataclasses
from collections.abc import Sequence
from typing import Literal

import numpy as np
import pandas as pd

from lgd_sim.dgp import DGPParams, estimate_formula_inputs, simulate_portfolio, true_lgd
from lgd_sim.formulas import lgd_basic, lgd_lgc, lgd_new, lgd_prd

SweepParam = Literal["prd", "pc", "mean_cure_month"]


def _formula_row(exposures: pd.DataFrame) -> dict[str, float]:
    """Compute LGD_true, each formula's estimate, and each formula's relative error for one replication."""
    lgd_true_value = true_lgd(exposures)
    inputs = estimate_formula_inputs(exposures)

    lgd_basic_value = lgd_basic(inputs["pc"], inputs["rr"])
    lgd_lgc_value = lgd_lgc(inputs["pc"], inputs["rr"], inputs["lgc"])
    lgd_prd_value = lgd_prd(inputs["pc"], inputs["rr"], inputs["prd"])
    lgd_new_value = lgd_new(inputs["pc"], inputs["rr"], inputs["prd"], inputs["rr_brd"])

    return {
        "lgd_true": lgd_true_value,
        "lgd_basic": lgd_basic_value,
        "lgd_lgc": lgd_lgc_value,
        "lgd_prd": lgd_prd_value,
        "lgd_new": lgd_new_value,
        "lgd_basic_error": lgd_basic_value / lgd_true_value - 1,
        "lgd_lgc_error": lgd_lgc_value / lgd_true_value - 1,
        "lgd_prd_error": lgd_prd_value / lgd_true_value - 1,
        "lgd_new_error": lgd_new_value / lgd_true_value - 1,
    }


def run_baseline(
    sweep_param: SweepParam,
    sweep_values: Sequence[float],
    base_params: DGPParams,
    n_exposures: int,
    n_replications: int,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Sweep one DGP parameter and record each formula's relative error per replication.

    Args:
        sweep_param: Which `DGPParams` field to vary ("prd", "pc", or "mean_cure_month").
        sweep_values: Values to substitute for `sweep_param`, holding the rest of
            `base_params` fixed.
        base_params: Baseline DGP parameters; `sweep_param` is overridden per sweep value.
        n_exposures: Number of exposures simulated per replication.
        n_replications: Number of independent replications per sweep value.
        rng: Seeded random generator, advanced across every replication.

    Returns:
        One row per (sweep value, replication), with the swept parameter's value,
        `lgd_true`, each formula's raw predicted value, and each formula's relative
        error against `lgd_true`. Left unaggregated; mean and standard deviation per
        sweep value are computed in metrics.py.
    """
    rows = []
    for value in sweep_values:
        params = dataclasses.replace(base_params, **{sweep_param: value})
        for _ in range(n_replications):
            exposures = simulate_portfolio(params, n_exposures, rng)
            rows.append({sweep_param: value, **_formula_row(exposures)})

    return pd.DataFrame(rows)


def run_complexity_sweep(
    n_exposures_values: Sequence[int],
    base_params: DGPParams,
    n_replications: int,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """Sweep portfolio size and record each formula's error and observed re-default count per replication.

    Holds `base_params` fixed and varies only how many exposures are simulated,
    so estimation variance from a formula's extra parameters can be studied
    independently of the DGP's own bias (research goal 2: complexity vs.
    robustness tradeoff).

    Args:
        n_exposures_values: Portfolio sizes to simulate.
        base_params: DGP parameters, held fixed across every sweep value.
        n_replications: Number of independent replications per sweep value.
        rng: Seeded random generator, advanced across every replication.

    Returns:
        One row per (n_exposures, replication), with `n_exposures`, `n_redefault`
        (the observed re-default count in that replication), `lgd_true`, each
        formula's raw predicted value, and each formula's relative error against
        `lgd_true`. Left unaggregated; RMSE per sweep value is computed in
        metrics.py.
    """
    rows = []
    for n in n_exposures_values:
        for _ in range(n_replications):
            exposures = simulate_portfolio(base_params, n, rng)
            rows.append(
                {
                    "n_exposures": n,
                    "n_redefault": int(exposures["redefaulted"].sum()),
                    **_formula_row(exposures),
                }
            )

    return pd.DataFrame(rows)
