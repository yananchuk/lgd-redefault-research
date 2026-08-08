# LGD Re-default Modeling

Quantifying the bias in Loss Given Default estimation caused by loans that default, recover, and default again, and testing how well the fix for that bias holds up under stress.

This project builds on research from the author's master's thesis at SGH Warsaw School of Economics.

## The problem

Loss Given Default (LGD) is the fraction of a loan's exposure a lender expects to lose once a borrower defaults. It's one of the core inputs banks use to calculate regulatory capital, and it's typically estimated from a historical dataset of past defaults and how much was ultimately recovered on each one.

Some defaulted borrowers cure: they catch up on payments and return to performing status. Under EU banking regulation (CRR, with EBA GL/2017/16 and GL/2016/07 setting the operational detail), if a cured borrower later falls back into default, that re-default has to be logged as a brand new, independent default observation rather than as a continuation of the first one. That creates a bookkeeping problem: the same loan now contributes two default events to the historical dataset used to calibrate LGD, and a formula that doesn't account for that double-counting will produce a biased estimate.

Three formulas for estimating LGD are compared here:

- The **basic two-factor model** treats every cured loan as if it will never lose any further value, ignoring the possibility of re-default entirely.
- The **loss-given-cure (LGC) add-on** adds a flat surcharge for cured loans, estimated empirically from how much cured loans actually lose on average, without modeling why.
- The **re-default-aware model** treats a cured loan as genuinely re-entering the pool of at-risk loans, and introduces two more explicit inputs: `Prd`, the probability that a cured loan re-defaults before the loan's maturity, and `RR_brd`, the recovery collected during the time the loan spent cured, before it fell back into default.

The re-default-aware formula, the one this project centers on:

$$LGD_{new} = \frac{(1-PC)(1-RR) - PC \cdot Prd \cdot RR_{brd}}{1 - PC \cdot Prd}$$

where `PC` is the probability that a defaulted loan cures, and `RR` is the recovery rate on loans that default and never cure at all.

The full derivation of all three formulas, including the consistency check that they collapse to each other when `Prd = 0` (no re-defaults, nothing left to correct for), is in [`docs/derivation.md`](docs/derivation.md).

## Research goals

1. **Baseline bias.** Under correctly specified assumptions, how much do the basic and LGC formulas diverge from the re-default-aware one, and how does that gap move with `Prd`, `PC`, and cure timing?
2. **Complexity vs. robustness.** At what reference-dataset size or re-default count does the added estimation variance from the more complex formula's extra parameters offset its lower structural bias?
3. **Misspecification.** Does the more complex formula's advantage survive when the data is generated under assumptions it doesn't know about?

## Docs

- [`docs/dgp_assumptions.md`](docs/dgp_assumptions.md): every distributional and structural assumption behind the simulated data
- [`docs/derivation.md`](docs/derivation.md): the four LGD formulas derived from cash-flow accounting
- [`docs/literature.md`](docs/literature.md): regulatory grounding and the wider LGD literature

## Results



## Reproducing this

