"""Data-generating process for the LGD re-default simulation (see docs/dgp_assumptions.md)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class DGPParams:
    """Baseline data-generating process parameters (docs/dgp_assumptions.md)."""

    pc: float
    prd: float
    t_maturity: int = 60
    mean_cure_month: float = 5.0
    rr_alpha: float = 0.3
    rr_beta: float = 0.3
    rr_after_redefault_alpha: float = 0.3
    rr_after_redefault_beta: float = 0.3
    ead_mean: float = 1.0
    ead_std: float = 0.2


def simulate_portfolio(params: DGPParams, n: int, rng: np.random.Generator) -> pd.DataFrame:
    """Simulate n defaulted exposures and their realized losses.

    Each exposure draws one EAD, carried through its lifecycle unchanged.
    A cured exposure that later re-defaults is treated as a fresh terminal
    default, its loss applying to the balance left over after the recovery
    already credited during the cure interval (docs/dgp_assumptions.md,
    "Recovery rate distributions"). `t_cure` is capped at `t_maturity - 1`:
    a cure can't be modeled as happening at or after the loan's own
    maturity, since there would be no loan left to cure. Without the cap,
    a high enough `mean_cure_month` lets the uncapped Poisson draw exceed
    `t_maturity`, which would make the re-default window negative.

    Args:
        params: Distributional and portfolio-level parameters.
        n: Number of defaulted exposures to simulate.
        rng: Seeded random generator.

    Returns:
        One row per exposure: ead, cured, redefaulted, rr, t_cure, t_rd,
        rr_before_redefault, rr_after_redefault, loss. Fields that don't
        apply to a given exposure (e.g. rr for a cured one) are NaN.
    """
    ead = rng.normal(params.ead_mean, params.ead_std, n)
    cured = rng.random(n) < params.pc
    redefaulted = cured & (rng.random(n) < params.prd)
    n_cure = int(cured.sum())
    n_redefault = int(redefaulted.sum())

    rr = np.full(n, np.nan)
    rr[~cured] = rng.beta(params.rr_alpha, params.rr_beta, n - n_cure)

    t_cure = np.full(n, np.nan)
    t_cure[cured] = np.minimum(rng.poisson(params.mean_cure_month, n_cure), params.t_maturity - 1)

    t_rd = np.full(n, np.nan)
    rr_before_redefault = np.full(n, np.nan)
    rr_after_redefault = np.full(n, np.nan)
    if n_redefault > 0:
        t_rd[redefaulted] = np.floor(
            rng.random(n_redefault) * (params.t_maturity - t_cure[redefaulted])
        )
        rr_before_redefault[redefaulted] = np.clip(
            (t_cure[redefaulted] + t_rd[redefaulted] - 3) / params.t_maturity, 0.0, 1.0
        )
        rr_after_redefault[redefaulted] = rng.beta(
            params.rr_after_redefault_alpha, params.rr_after_redefault_beta, n_redefault
        )

    loss = np.zeros(n)
    loss[~cured] = ead[~cured] * (1 - rr[~cured])
    loss[redefaulted] = (
        ead[redefaulted]
        * (1 - rr_before_redefault[redefaulted])
        * (1 - rr_after_redefault[redefaulted])
    )

    return pd.DataFrame(
        {
            "ead": ead,
            "cured": cured,
            "redefaulted": redefaulted,
            "rr": rr,
            "t_cure": t_cure,
            "t_rd": t_rd,
            "rr_before_redefault": rr_before_redefault,
            "rr_after_redefault": rr_after_redefault,
            "loss": loss,
        }
    )


def true_lgd(exposures: pd.DataFrame) -> float:
    """Realized portfolio LGD from simulated exposures.

    This is the ground truth `LGD_new` is designed to recover
    (docs/dgp_assumptions.md, "Recovery rate distributions").
    """
    return exposures["loss"].sum() / exposures["ead"].sum()


def estimate_formula_inputs(
    exposures: pd.DataFrame, merge_threshold_months: float | None = None
) -> dict[str, float]:
    """Re-estimate PC, Prd, RR, RR_brd, and LGC from the simulated reference dataset.

    Mirrors how a bank would compute these from a real reference dataset. By
    default every re-default is logged as its own independent default
    observation regardless of timing (docs/dgp_assumptions.md, "Estimating
    formula inputs from the simulated data"). When a portfolio has no cures
    or no re-defaults, the corresponding rate defaults to 0.0 rather than
    NaN, since it always appears multiplied by a probability that is itself
    0 in the formulas.

    Args:
        exposures: Output of `simulate_portfolio`.
        merge_threshold_months: If set, a re-default within this many months
            of curing is merged into the original default rather than
            counted as a second independent observation, per EBA/GL/2017/16
            §101. The merged exposure's recovery is its whole cure-to-
            redefault episode, treated as one continuous default; it drops
            out of the cured/LGC population and no longer contributes an
            RR_brd credit, since there's no longer a separate pre-redefault
            interval to credit. If None (the default), every re-default is
            counted as independent regardless of timing.

    Returns:
        A dict with keys "pc", "prd", "rr", "rr_brd", "lgc".
    """
    n = len(exposures)
    cured = exposures["cured"].to_numpy()
    redefaulted = exposures["redefaulted"].to_numpy()

    merged = np.zeros(n, dtype=bool)
    if merge_threshold_months is not None:
        merged = redefaulted & (exposures["t_rd"].to_numpy() < merge_threshold_months)

    treated_as_cured = cured & ~merged
    treated_as_redefault = redefaulted & ~merged
    n_cure = int(treated_as_cured.sum())
    n_redefault = int(treated_as_redefault.sum())

    merged_rr = 1 - (1 - exposures.loc[merged, "rr_before_redefault"]) * (
        1 - exposures.loc[merged, "rr_after_redefault"]
    )
    recoveries = pd.concat(
        [
            exposures.loc[~exposures["cured"], "rr"],
            merged_rr,
            exposures.loc[treated_as_redefault, "rr_after_redefault"],
        ]
    )
    cured_ead = exposures.loc[treated_as_cured, "ead"].sum()

    return {
        "pc": n_cure / (n + n_redefault),
        "prd": n_redefault / n_cure if n_cure > 0 else 0.0,
        "rr": recoveries.mean(),
        "rr_brd": (
            exposures.loc[treated_as_redefault, "rr_before_redefault"].mean()
            if n_redefault > 0
            else 0.0
        ),
        "lgc": (exposures.loc[treated_as_cured, "loss"].sum() / cured_ead if n_cure > 0 else 0.0),
    }
