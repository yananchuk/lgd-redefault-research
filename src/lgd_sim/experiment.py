"""Experiment runners for the LGD re-default bias study (see docs/dgp_assumptions.md)."""

from __future__ import annotations

import dataclasses
from collections.abc import Sequence
from typing import Literal

import numpy as np
import pandas as pd

from lgd_sim.dgp import DGPParams, estimate_formula_inputs, simulate_portfolio, true_lgd
from lgd_sim.formulas import lgd_basic, lgd_lgc, lgd_new, lgd_new_adj, lgd_prd

SweepParam = Literal["prd", "pc", "mean_cure_month"]


def _formula_values(inputs: dict[str, float], lgd_true_value: float) -> dict[str, float]:
    """Compute each formula's LGD estimate and relative error from pre-estimated inputs."""
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


def _formula_row(exposures: pd.DataFrame) -> dict[str, float]:
    """Compute LGD_true, each formula's estimate, and each formula's relative error for one replication."""
    lgd_true_value = true_lgd(exposures)
    inputs = estimate_formula_inputs(exposures)
    return _formula_values(inputs, lgd_true_value)


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


def run_merge_compliance(
    sweep_param: SweepParam,
    sweep_values: Sequence[float],
    base_params: DGPParams,
    n_exposures: int,
    n_replications: int,
    rng: np.random.Generator,
    merge_threshold_months: float = 9.0,
) -> pd.DataFrame:
    """Sweep one DGP parameter and compare naive vs merge-compliant reference-dataset estimation.

    The simulated portfolio is identical between regimes within a given
    replication; only how the reference dataset is built from it differs.
    Naive estimation counts every re-default as an independent observation
    regardless of timing. Compliant estimation applies EBA/GL/2017/16 §101:
    a re-default within `merge_threshold_months` of curing is merged into
    the original default rather than counted as a second observation. This
    tests reference-dataset construction correctness under a correctly
    specified DGP, not a misspecified one; the DGP's own assumptions aren't
    varied here.

    Args:
        sweep_param: Which `DGPParams` field to vary ("prd", "pc", or "mean_cure_month").
        sweep_values: Values to substitute for `sweep_param`, holding the rest of
            `base_params` fixed.
        base_params: Baseline DGP parameters; `sweep_param` is overridden per sweep value.
        n_exposures: Number of exposures simulated per replication.
        n_replications: Number of independent replications per sweep value.
        rng: Seeded random generator, advanced across every replication.
        merge_threshold_months: The independence threshold the compliant regime
            applies (default: the regulatory nine months).

    Returns:
        One row per (sweep value, replication, regime), with the swept
        parameter's value, `regime` ("naive" or "compliant"), `n_redefault`
        and `n_merged` (the observed re-default count and how many of those
        fell under `merge_threshold_months`, identical between the two
        regime rows of a replication since they share the same simulated
        portfolio), `lgd_true`, each formula's raw predicted value, and each
        formula's relative error against `lgd_true`.
    """
    rows = []
    for value in sweep_values:
        params = dataclasses.replace(base_params, **{sweep_param: value})
        for _ in range(n_replications):
            exposures = simulate_portfolio(params, n_exposures, rng)
            lgd_true_value = true_lgd(exposures)
            redefaulted = exposures["redefaulted"]
            n_redefault = int(redefaulted.sum())
            n_merged = int((redefaulted & (exposures["t_rd"] < merge_threshold_months)).sum())
            for regime, threshold in (("naive", None), ("compliant", merge_threshold_months)):
                inputs = estimate_formula_inputs(exposures, merge_threshold_months=threshold)
                rows.append(
                    {
                        sweep_param: value,
                        "regime": regime,
                        "n_redefault": n_redefault,
                        "n_merged": n_merged,
                        **_formula_values(inputs, lgd_true_value),
                    }
                )

    return pd.DataFrame(rows)


def run_adjustment_comparison(
    sweep_param: SweepParam,
    sweep_values: Sequence[float],
    base_params: DGPParams,
    n_exposures: int,
    n_replications: int,
    rng: np.random.Generator,
    merge_threshold_months: float = 9.0,
) -> pd.DataFrame:
    """Sweep one DGP parameter and compare `lgd_new` against its segmented-recovery variant.

    `lgd_new` assumes the same recovery rate applies to a first default and
    to a redefaulted exposure's fresh loss; `lgd_new_adj` doesn't, using the
    separately estimated `rr_homogeneous` and `rr_ard` `estimate_formula_inputs`
    computes but the other four formulas never touch (docs/derivation.md, "A
    segmented variant: relaxing the shared-recovery assumption"; docs/dgp_assumptions.md,
    "Estimating formula inputs from the simulated data"). Both formulas are
    evaluated under naive and merge-compliant estimation, the same regime
    split `run_merge_compliance` applies to the original four formulas,
    since `rr_ard` is estimated only from re-defaults `estimate_formula_inputs`
    doesn't merge into the cured population, and so moves between regimes
    exactly as `rr_brd` does.

    Args:
        sweep_param: Which `DGPParams` field to vary ("prd", "pc", or "mean_cure_month").
        sweep_values: Values to substitute for `sweep_param`, holding the rest of
            `base_params` fixed.
        base_params: Baseline DGP parameters; `sweep_param` is overridden per sweep value.
        n_exposures: Number of exposures simulated per replication.
        n_replications: Number of independent replications per sweep value.
        rng: Seeded random generator, advanced across every replication.
        merge_threshold_months: The independence threshold the compliant regime
            applies (default: the regulatory nine months).

    Returns:
        One row per (sweep value, replication, regime), with the swept
        parameter's value, `regime` ("naive" or "compliant"), `lgd_true`,
        `lgd_new`, `lgd_new_adj`, and each formula's relative error against
        `lgd_true`.
    """
    rows = []
    for value in sweep_values:
        params = dataclasses.replace(base_params, **{sweep_param: value})
        for _ in range(n_replications):
            exposures = simulate_portfolio(params, n_exposures, rng)
            lgd_true_value = true_lgd(exposures)
            for regime, threshold in (("naive", None), ("compliant", merge_threshold_months)):
                inputs = estimate_formula_inputs(exposures, merge_threshold_months=threshold)
                lgd_new_value = lgd_new(inputs["pc"], inputs["rr"], inputs["prd"], inputs["rr_brd"])
                lgd_new_adj_value = lgd_new_adj(
                    inputs["pc"],
                    inputs["rr_homogeneous"],
                    inputs["prd"],
                    inputs["rr_brd"],
                    inputs["rr_ard"],
                )
                rows.append(
                    {
                        sweep_param: value,
                        "regime": regime,
                        "lgd_true": lgd_true_value,
                        "lgd_new": lgd_new_value,
                        "lgd_new_adj": lgd_new_adj_value,
                        "lgd_new_error": lgd_new_value / lgd_true_value - 1,
                        "lgd_new_adj_error": lgd_new_adj_value / lgd_true_value - 1,
                    }
                )

    return pd.DataFrame(rows)


def run_adjustment_complexity_sweep(
    n_exposures_values: Sequence[int],
    base_params: DGPParams,
    n_replications: int,
    rng: np.random.Generator,
    merge_threshold_months: float = 9.0,
) -> pd.DataFrame:
    """Sweep portfolio size and compare `lgd_new` against its segmented-recovery variant.

    Tests whether the segmented variant's unbiasedness under misspecified
    recovery (`run_adjustment_comparison`) holds at smaller portfolio sizes,
    where the independent-redefault pool its `rr_ard` estimate draws from
    has fewer observations to work with than at the portfolio size used
    elsewhere in that comparison.

    Args:
        n_exposures_values: Portfolio sizes to simulate.
        base_params: DGP parameters, held fixed across every sweep value.
        n_replications: Number of independent replications per sweep value.
        rng: Seeded random generator, advanced across every replication.
        merge_threshold_months: The independence threshold the compliant regime
            applies (default: the regulatory nine months).

    Returns:
        One row per (n_exposures, replication, regime), with `n_exposures`,
        `regime` ("naive" or "compliant"), `lgd_true`, `lgd_new`,
        `lgd_new_adj`, and each formula's relative error against `lgd_true`.
    """
    rows = []
    for n in n_exposures_values:
        for _ in range(n_replications):
            exposures = simulate_portfolio(base_params, n, rng)
            lgd_true_value = true_lgd(exposures)
            for regime, threshold in (("naive", None), ("compliant", merge_threshold_months)):
                inputs = estimate_formula_inputs(exposures, merge_threshold_months=threshold)
                lgd_new_value = lgd_new(inputs["pc"], inputs["rr"], inputs["prd"], inputs["rr_brd"])
                lgd_new_adj_value = lgd_new_adj(
                    inputs["pc"],
                    inputs["rr_homogeneous"],
                    inputs["prd"],
                    inputs["rr_brd"],
                    inputs["rr_ard"],
                )
                rows.append(
                    {
                        "n_exposures": n,
                        "regime": regime,
                        "lgd_true": lgd_true_value,
                        "lgd_new": lgd_new_value,
                        "lgd_new_adj": lgd_new_adj_value,
                        "lgd_new_error": lgd_new_value / lgd_true_value - 1,
                        "lgd_new_adj_error": lgd_new_adj_value / lgd_true_value - 1,
                    }
                )

    return pd.DataFrame(rows)
