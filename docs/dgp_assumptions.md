# Data-generating process: assumptions and decisions

Every assumption the simulation depends on gets a decision recorded here before any simulation code is written. This covers the full DGP: recovery rates, exposure at default, cure and re-default timing, maturity, and the portfolio-level PC/Prd parameters. There is no macroeconomic (GDP) assumption in the model; PC and Prd are fixed scalars with no macro dependence, as noted below.

## Summary

| Component | Baseline | Misspecification variant |
|---|---|---|
| Recovery rates | `rr`, `rr_after_redefault` i.i.d. `Beta(0.3, 0.3)` | `rr_after_redefault ~ Beta(0.15, 0.4)` (lower mean) |
| EAD | `N(1, 0.2)`, drawn once per exposure, carried through unchanged | Deterministic function of time since cure |
| Cure timing | `t_cure ~ Poisson(mean_cure_month)` | unchanged |
| Re-default timing | `t_rd ~ Discrete-Uniform(0, T_maturity - t_cure)` (flat hazard) | Front-loaded hazard, decaying after cure |
| Maturity | Fixed at `T_maturity = 60` months | unchanged |
| PC, Prd | Fixed portfolio-level scalars, no covariates or macro effects | unchanged |
| Re-default cycles | One cure-to-re-default cycle per exposure | unchanged |
| Sensitivity sweep | `PC`, `Prd` swept 0-50%, base case `PC` ~20%, `Prd` ~10% | n/a |
| Formula inputs | `PC`, `Prd`, `RR`, `RR_brd` re-estimated from the simulated reference dataset (inflated-denominator `PC`), not the true generating parameters | unchanged |

## Recovery rate distributions

`rr` and `rr_after_redefault` are both drawn i.i.d. from `Beta(0.3, 0.3)` in the baseline scenario. The derivation of the re-default-aware formula only holds if the true population recovery rate is the same for first-default and re-default recoveries, so this assumption carries real weight. It stays as the baseline for the confirmatory comparison. The misspecification experiment reruns the comparison with re-default recovery drawn from a distribution with a lower mean (`Beta(0.15, 0.4)`) to check whether the correction still holds up when that assumption fails.

`rr` applies to exposures that never cure. `rr_after_redefault` applies to exposures that cure and then re-default: once re-defaulted, an exposure is treated as a fresh terminal default, and `rr_after_redefault` is the recovery rate on whatever balance is still outstanding at that point. That remaining balance already reflects the paydown credited through `rr_before_redefault` (derivation.md's "pre-re-default recovery term"), so the two combine multiplicatively rather than by simple subtraction, since the second recovery rate acts on what's left of the exposure, not on the original balance:

$$\text{loss fraction} = (1 - rr_{before\_rd})(1 - rr_{after\_rd})$$

This per-exposure realized loss, applied to the exposure's `EAD`, is what the simulation sums to compute `LGD_true` - the ground truth that the closed-form `LGD_new` is designed to recover from the formula side.

## Exposure at default (EAD)

`EAD ~ N(1, 0.2)`, drawn once per exposure at first default and carried through unchanged for the rest of its lifecycle, whether it never cures, cures and stays cured, or cures and later re-defaults. The balance paid down between cure and re-default is captured separately through `rr_before_redefault` (see derivation.md's "pre-re-default recovery term"), not by shrinking EAD itself. The baseline keeps EAD fixed at its first-default value for simplicity. A misspecification variant instead makes EAD at re-default a deterministic function of time since cure, an alternative amortization channel layered on top of the fixed baseline.

## Cure timing

`t_cure ~ Poisson(mean_cure_month)`, unchanged across all experiments. Reasonable default, and not something the central result is sensitive to.

## Re-default timing

`t_rd ~ Discrete-Uniform(0, T_maturity - t_cure)`. This is a flat hazard: an exposure is just as likely to re-default one month after curing as forty months after curing. It's probably the least defensible assumption in the whole DGP, and it matters here specifically because the recovery collected before re-default is a function of elapsed time. The baseline keeps the flat hazard for simplicity. A front-loaded hazard (re-default risk highest right after cure, then decaying) is tested as a misspecification variant. The DGP's parameter list only exposes what it actually uses, no leftover arguments hinting at a mechanism that was never wired up.

## Maturity

Fixed at `T_maturity = 60` months for every exposure. Heterogeneous maturities are outside the scope of this study.

## Cure probability and re-default probability

Both `PC` and `Prd` are fixed portfolio-level scalars with no loan-level covariates and no macro effects. This is a deliberate scope boundary: modeling `PC` from covariates is its own existing research direction (Lohmann & Ohliger) and isn't attempted here.

## Re-default cycles

Only one cure-to-re-default cycle per exposure is modeled. Repeated cycles are outside the scope of this study, a boundary stated here rather than left implicit.

## Estimating formula inputs from the simulated data

The four LGD formulas aren't evaluated on the true generating `PC` and `Prd` directly. Each simulation run re-estimates `PC`, `Prd`, `RR`, and `RR_brd` from the generated reference dataset the way a bank actually would: `PC` as cured exposures divided by all logged default observations, where a re-default counts as its own observation per EBA/GL/2016/07, not divided by first defaults alone. That denominator inflation is a second, smaller source of bias, layered on top of the main one (treating the whole cured population as zero-loss regardless of later re-default, see derivation.md), and it's what makes the simulation's formula inputs match what an analyst would actually compute from a real reference dataset rather than an idealized one. `LGD_true` is computed separately, directly from each exposure's realized loss, and never goes through this re-estimation step.

## Sensitivity sweep ranges

`Prd` and `PC` are swept from 0% to 50%. The base case used for headline results is PC around 20%, Prd around 10%, a starting point that needs checking against published figures once the relevant sources are read in full. The 0-50% sweep range is chosen for coverage around that base case, and the write-up says so plainly rather than implying it was calibrated.