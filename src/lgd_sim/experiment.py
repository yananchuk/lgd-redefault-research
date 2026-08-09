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
        One row per (sweep value, replication), with the swept parameter's value
        and each formula's relative error against `LGD_true`. Left unaggregated;
        mean and standard deviation per sweep value are computed in metrics.py.
    """
    rows = []
    for value in sweep_values:
        params = dataclasses.replace(base_params, **{sweep_param: value})
        for _ in range(n_replications):
            exposures = simulate_portfolio(params, n_exposures, rng)
            lgd_true = true_lgd(exposures)
            inputs = estimate_formula_inputs(exposures)

            rows.append(
                {
                    sweep_param: value,
                    "lgd_basic_error": lgd_basic(inputs["pc"], inputs["rr"]) / lgd_true - 1,
                    "lgd_lgc_error": lgd_lgc(inputs["pc"], inputs["rr"], inputs["lgc"]) / lgd_true
                    - 1,
                    "lgd_prd_error": lgd_prd(inputs["pc"], inputs["rr"], inputs["prd"]) / lgd_true
                    - 1,
                    "lgd_new_error": lgd_new(
                        inputs["pc"], inputs["rr"], inputs["prd"], inputs["rr_brd"]
                    )
                    / lgd_true
                    - 1,
                }
            )

    return pd.DataFrame(rows)
