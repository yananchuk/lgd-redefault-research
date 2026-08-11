"""LGD estimator formulas (see docs/derivation.md)."""

from __future__ import annotations

import numpy as np

FloatOrArray = float | np.ndarray


def lgd_basic(pc: FloatOrArray, rr: FloatOrArray) -> FloatOrArray:
    """Basic two-factor LGD estimate, ignoring re-default entirely (derivation.md, "Basic two-factor model").

    Args:
        pc: Cure probability.
        rr: Recovery rate on exposures that never cure.

    Returns:
        The basic LGD estimate.
    """
    return (1 - pc) * (1 - rr)


def lgd_lgc(pc: FloatOrArray, rr: FloatOrArray, lgc: FloatOrArray) -> FloatOrArray:
    """LGD estimate with a flat loss-given-cure surcharge (derivation.md, "Loss-given-cure add-on").

    Args:
        pc: Cure probability.
        rr: Recovery rate on exposures that never cure.
        lgc: Flat per-cured-exposure loss surcharge.

    Returns:
        The LGC-adjusted LGD estimate.
    """
    return (1 - pc) * (1 - rr) + pc * lgc


def lgd_prd(pc: FloatOrArray, rr: FloatOrArray, prd: FloatOrArray) -> FloatOrArray:
    """Naive re-default correction assuming zero recovery during the cured interval.

    Fixes the double-counting of cured-then-redefaulted exposures in `pc`, but
    discards any recovery collected before re-default (derivation.md,
    "Re-default-aware model"). Collapses to `lgd_basic` when `prd == 0`.

    Args:
        pc: Cure probability.
        rr: Recovery rate on exposures that never cure.
        prd: Probability that a cured exposure re-defaults before maturity.

    Returns:
        The Prd-corrected LGD estimate.
    """
    return (1 - pc) * (1 - rr) / (1 - pc * prd)


def lgd_new(
    pc: FloatOrArray, rr: FloatOrArray, prd: FloatOrArray, rr_brd: FloatOrArray
) -> FloatOrArray:
    """Re-default-aware LGD estimate crediting recovery collected before re-default.

    Derived from the accounting identity that a re-defaulted exposure's
    balance is paid down at rate `rr_brd` before the fresh loss rate `rr`
    applies to what remains (derivation.md, "Re-default-aware model").
    Collapses to `lgd_basic` when `prd == 0`.

    Args:
        pc: Cure probability.
        rr: Recovery rate on exposures that never cure.
        prd: Probability that a cured exposure re-defaults before maturity.
        rr_brd: Recovery collected between curing and re-defaulting.

    Returns:
        The re-default-aware LGD estimate.
    """
    return (1 - rr) * ((1 - pc) - pc * prd * rr_brd) / (1 - pc * prd)


def lgd_new_adj(
    pc: FloatOrArray,
    rr: FloatOrArray,
    prd: FloatOrArray,
    rr_brd: FloatOrArray,
    rr_ard: FloatOrArray,
) -> FloatOrArray:
    """Re-default-aware LGD estimate with a separate rate for the redefault fresh loss.

    `lgd_new` assumes the same recovery rate applies to a first default and
    to a redefaulted exposure's fresh loss after its `rr_brd` credit; this
    variant drops that assumption (derivation.md, "A segmented variant:
    relaxing the shared-recovery assumption") and lets the redefault fresh
    loss use its own rate `rr_ard` instead of reusing `rr`. Collapses to
    `lgd_new` when `rr_ard == rr`, to `lgd_prd` when additionally
    `rr_brd == 0`, and to `lgd_basic` when `prd == 0`.

    Args:
        pc: Cure probability.
        rr: Recovery rate on exposures that never cure.
        prd: Probability that a cured exposure re-defaults before maturity.
        rr_brd: Recovery collected between curing and re-defaulting.
        rr_ard: Recovery rate on a redefaulted exposure's fresh loss.

    Returns:
        The segmented re-default-aware LGD estimate.
    """
    return ((1 - pc - pc * prd) * (1 - rr) + pc * prd * (1 - rr_brd) * (1 - rr_ard)) / (
        1 - pc * prd
    )
