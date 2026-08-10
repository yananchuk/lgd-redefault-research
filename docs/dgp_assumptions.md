# Data-generating process: assumptions and decisions

Every assumption the simulation depends on gets a decision recorded here before any simulation code is written. This covers the full DGP: recovery rates, exposure at default, cure and re-default timing, maturity, and the portfolio-level $PC$ (cure probability) and $P_{rd}$ (re-default probability) parameters - see `derivation.md`'s Setup section for how $PC$, $P_{rd}$, $RR$ (recovery rate), and $RR_{brd}$ (recovery collected before re-default) enter the closed-form formulas. There is no macroeconomic (GDP) assumption in the model; $PC$ and $P_{rd}$ are fixed scalars with no macro dependence, as noted below.

## Summary

| Component | Baseline | Alternative scenario tested |
|---|---|---|
| Recovery rates | $rr$, $rr_{ard}$ i.i.d. $\text{Beta}(0.3, 0.3)$ | Misspecification: $rr_{ard} \sim \text{Beta}(0.15, 0.4)$ (lower mean) |
| EAD | $ead \sim \mathcal{N}(1, 0.2)$, drawn once per exposure, carried through unchanged | Misspecification: deterministic function of time since cure |
| Cure timing | $t_{cure} \sim \text{Poisson}(\text{mean cure month})$ | unchanged |
| Re-default timing | $t_{rd} \sim \text{Discrete-Uniform}(0, T_{maturity} - t_{cure})$ (flat hazard) | unchanged |
| Maturity | Fixed at $T_{maturity} = 60$ months | unchanged |
| $PC$, $P_{rd}$ | Fixed portfolio-level scalars, no covariates or macro effects | unchanged |
| Re-default cycles | One cure-to-re-default cycle per exposure | unchanged |
| Sensitivity sweep | $PC$, $P_{rd}$ swept 0-50%, base case $PC$ ~20%, $P_{rd}$ ~10% | n/a |
| Formula inputs | $PC$, $P_{rd}$, $RR$, $RR_{brd}$ re-estimated from the simulated reference dataset (inflated-denominator $PC$), not the true generating parameters | Reference-dataset construction check: nine-month re-default merge rule (EBA/GL/2017/16 §101) applied or not |

## Recovery rate distributions

$rr$ and $rr_{ard}$ are both drawn i.i.d. from $\text{Beta}(0.3, 0.3)$ in the baseline scenario. The derivation of the re-default-aware formula only holds if the true population recovery rate is the same for first-default and re-default recoveries, so this assumption carries real weight. It stays as the baseline for the confirmatory comparison. The misspecification experiment reruns the comparison with re-default recovery drawn from a distribution with a lower mean ($\text{Beta}(0.15, 0.4)$) to check whether the correction still holds up when that assumption fails.

$rr$ applies to exposures that never cure. $rr_{ard}$ applies to exposures that cure and then re-default: once re-defaulted, an exposure is treated as a fresh terminal default, and $rr_{ard}$ is the recovery rate on whatever balance is still outstanding at that point. That remaining balance already reflects the paydown credited through $rr_{brd}$ (derivation.md's "pre-re-default recovery term"), so the two combine multiplicatively rather than by simple subtraction, since the second recovery rate acts on what's left of the exposure, not on the original balance:

$$\text{loss fraction} = (1 - rr_{brd})(1 - rr_{ard})$$

This per-exposure realized loss, applied to the exposure's $ead$, is what the simulation sums to compute $LGD_{true}$ - the ground truth that the closed-form $LGD_{new}$ is designed to recover from the formula side.

## Exposure at default (EAD)

$ead \sim \mathcal{N}(1, 0.2)$, drawn once per exposure at first default and carried through unchanged for the rest of its lifecycle, whether it never cures, cures and stays cured, or cures and later re-defaults. The balance paid down between cure and re-default is captured separately through $rr_{brd}$ (see derivation.md's "pre-re-default recovery term"), not by shrinking $ead$ itself. The baseline keeps $ead$ fixed at its first-default value for simplicity. A misspecification variant instead makes $ead$ at re-default a deterministic function of time since cure, an alternative amortization channel layered on top of the fixed baseline.

## Cure timing

$t_{cure} \sim \text{Poisson}(\text{mean cure month})$, capped at $T_{maturity} - 1$, unchanged across all experiments. The cap only matters when mean cure month is pushed well past its baseline value of 5: an uncapped draw can occasionally exceed $T_{maturity}$, which would model a cure happening after the loan's own contractual maturity and produce a negative re-default window downstream. Reasonable default otherwise, and not something the central result is sensitive to.

## Re-default timing

$t_{rd} \sim \text{Discrete-Uniform}(0, T_{maturity} - t_{cure})$. This is a flat hazard: an exposure is just as likely to re-default one month after curing as forty months after curing. It's probably the least defensible assumption in the whole DGP, and it matters here specifically because the recovery collected before re-default is a function of elapsed time. It's kept flat across every experiment in this project, including the reference-dataset construction check: shifting the shape of $t_{rd}$'s distribution alone doesn't change what the formulas estimate, since both the true loss and the estimated inputs read the same realized $t_{rd}$ value for a given exposure either way. What $t_{rd}$'s value is used *for* downstream, not its distribution, is where that check finds something - see "Re-default independence: the nine-month merge rule" below. The DGP's parameter list only exposes what it actually uses, no leftover arguments hinting at a mechanism that was never wired up.

## Re-default independence: the nine-month merge rule

EBA/GL/2017/16 §101 requires institutions to treat a re-default occurring within nine months of an exposure's return to non-defaulted status as a continuation of the original default, not a second independent observation, for the purpose of LGD estimation. This is a distinct rule from the probation period EBA/GL/2016/07 defines before an exposure can exit default status in the first place - GL/2017/16 states explicitly that the nine months apply in addition to the probation period, not in place of it.

Neither this project's own `dgp.py` nor the prior R implementation it's derived from applied this rule before this check: every re-default was counted as an independent observation regardless of how soon after curing it happened. `estimate_formula_inputs`'s `merge_threshold_months` argument adds the compliant treatment as an option (default `None`, preserving the original naive behavior) rather than changing the default, so the baseline and complexity/robustness experiments are unaffected. A re-default with $t_{rd}$ under the threshold is excluded from the cured and re-defaulted counts, and its whole cure-to-re-default episode is folded into the same recovery-rate pool as a genuine first default, using its combined realized recovery $1-(1-rr_{brd})(1-rr_{ard})$ in place of a plain $rr$ draw.

## Maturity

Fixed at $T_{maturity} = 60$ months for every exposure. Heterogeneous maturities are outside the scope of this study.

## Cure probability and re-default probability

Both $PC$ and $P_{rd}$ are fixed portfolio-level scalars with no loan-level covariates and no macro effects. This is a deliberate scope boundary: modeling $PC$ from covariates is its own existing research direction (Lohmann & Ohliger) and isn't attempted here.

## Re-default cycles

Only one cure-to-re-default cycle per exposure is modeled. Repeated cycles are outside the scope of this study, a boundary stated here rather than left implicit.

## Estimating formula inputs from the simulated data

The four LGD formulas aren't evaluated on the true generating $PC$ and $P_{rd}$ directly. Each simulation run re-estimates $PC$, $P_{rd}$, $RR$, and $RR_{brd}$ from the generated reference dataset the way a bank actually would: $PC$ as cured exposures divided by all logged default observations, not divided by first defaults alone. By default, every re-default counts as its own observation regardless of timing (the naive treatment used throughout the baseline and complexity/robustness experiments); whether that's the right thing to do under EBA/GL/2017/16 §101 is a separate question, addressed in "Re-default independence: the nine-month merge rule" above, not assumed here. That denominator inflation is a second, smaller source of bias, layered on top of the main one (treating the whole cured population as zero-loss regardless of later re-default, see derivation.md), and it's what makes the simulation's formula inputs match what an analyst would actually compute from a real reference dataset rather than an idealized one. $LGD_{true}$ is computed separately, directly from each exposure's realized loss, and never goes through this re-estimation step.

$RR_{brd}$ is estimated as a plain sample mean of $rr_{brd}$ over the re-defaulted subsample, matching how $RR$ is estimated. Both enter the closed form as scalar rates (derivation.md, $PC \cdot P_{rd} \cdot RR_{brd}$). This matches the CRR/EBA calibration convention for LGD parameters. CRR Article 181(1)(a) requires LGD to be estimated as a default-weighted average, and EBA/GL/2017/16 states this explicitly for the observed average LGD (§154: "weighted by the number of defaults included in the calculation") and the long-run average LGD (§150: "weighted by a number of defaults"). $LGC$ and $LGD_{true}$ are loss-dollars-over-EAD-dollars ratios by definition, a separate kind of quantity from a sample-average LGD parameter, so they carry their own EAD weighting under that definition.

## Sensitivity sweep ranges

$P_{rd}$ and $PC$ are swept from 0% to 50%. The base case used for headline results is $PC$ around 20%, $P_{rd}$ around 10%, a starting point that needs checking against published figures once the relevant sources are read in full. The 0-50% sweep range is chosen for coverage around that base case, and the write-up says so plainly rather than implying it was calibrated.