# Synthesis: which formula to use

[`results.md`](results.md) walks through what each of the four experiments found. This page turns those four findings into a single practical recommendation: given a reference dataset with re-defaulted exposures, which of the five formulas should actually be used to estimate LGD.

## Default recommendation: the re-default-aware formula

Two of the four experiments point the same direction under a correctly specified DGP. [Baseline bias](results.md#baseline-bias) shows it's the only one of the four original formulas with near-zero bias across every parameter tested. [Complexity vs. robustness](results.md#complexity-vs-robustness-tradeoff) shows that advantage is never bought with extra estimation variance, at any portfolio size or re-default count. Absent a specific reason to think otherwise, it's the right default.

## Portfolio size is not a deciding factor

A natural worry with a formula that has more free parameters is that it needs a large reference dataset to estimate them reliably. That worry doesn't hold here: no crossover in RMSE shows up anywhere from 100 to 50,000 exposures, and at the smallest re-default counts the formula collapses exactly to the basic two-factor estimate rather than picking up extra noise. Portfolio size, or how many re-defaults happen to be observed, isn't a reason to prefer a simpler formula.

## Merge-rule compliance is a data problem, not a formula-choice problem

[Reference-dataset construction](results.md#reference-dataset-construction-the-nine-month-merge-rule) shows that under naive estimation, every formula's bias grows worse as more of the portfolio's re-defaults should have been merged under EBA/GL/2017/16 §101 but weren't. Switching formulas doesn't fix that: the fix is applying the merge rule at the reference-dataset-construction stage, before any formula sees the data. Once the dataset is compliant, the re-default-aware formula is again the safer choice, including at merge fractions between the two extremes where a small residual remains but stays far smaller than any of the alternatives' bias under the naive treatment.

## The one condition that changes the recommendation

[Misspecification](results.md#misspecification-stress-test) is the finding that matters most for this decision. The re-default-aware formula's advantage rests on one assumption: that recovery after re-default follows the same distribution as first-default recovery. When that assumption fails, the formula doesn't just lose its advantage, it becomes worse than the basic model it was built to improve on, once $P_{rd}$ moves past roughly 0.05, though it stays well ahead of the loss-given-cure and Prd-correction formulas throughout.

So the recommendation is conditional, not unconditional:

- If there's no specific reason to doubt the shared-recovery assumption, use the [re-default-aware formula](derivation.md#re-default-aware-model).
- If re-defaulted exposures are plausibly subject to different recovery conditions than first defaults, for example different collection or workout treatment, different loan seasoning, or a different macro environment at the time of the second default, use the [segmented variant](derivation.md#a-segmented-variant-relaxing-the-shared-recovery-assumption) instead. It removes the bias entirely under misspecification, at the cost of needing its own calibration pool for redefault recovery ([dgp_assumptions.md, "Estimating formula inputs from the simulated data"](dgp_assumptions.md#estimating-formula-inputs-from-the-simulated-data)).

## Checking which regime applies

The assumption is checkable directly, not just assumed one way or the other: compare the empirical recovery rate on never-cured exposures against the empirical recovery rate on independent re-defaults in the reference dataset. If the two are close, the shared-recovery assumption holds and the plain re-default-aware formula is safe. If they diverge meaningfully, that's the signal to move to the segmented variant, the same comparison [`03_reference_dataset_construction.ipynb`](../notebooks/03_reference_dataset_construction.ipynb) uses to diagnose its own smaller residual bias.

## Decision summary

| Situation | Recommendation |
|---|---|
| Reference dataset doesn't yet apply the nine-month merge rule | Fix data construction first; no formula choice compensates for this |
| Merge-compliant dataset, no reason to doubt shared recovery | Re-default-aware formula |
| Merge-compliant dataset, redefault recovery plausibly different from first-default recovery | Segmented variant |
| Few or no observed re-defaults | Re-default-aware formula (collapses safely to the basic estimate) |

## What this doesn't resolve

The scope limitations in [`dgp_assumptions.md`](dgp_assumptions.md) carry over unchanged: a single cure-to-re-default cycle, no loan-level covariates or macro effects on $PC$ or $P_{rd}$, fixed maturity.

One adoption question this project doesn't test at all: CRR Article 181(1)(h) requires institutions to estimate a time series of LGD for exposures already in default, with values increasing monotonically as time since default grows. The basic two-factor model handles this by estimating $PC$ and $RR$ per time-since-default bucket rather than as single portfolio scalars. Nothing about the re-default-aware formula's structure blocks the same approach, since $PC$ and $RR$ are the same two inputs it already builds on, and $P_{rd}$, $RR_{brd}$, and $RR_{ard}$ would stay scalar. That's a plausible adaptation path, not a tested one: no experiment here constructs or checks such a curve.
