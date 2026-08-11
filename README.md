# LGD Re-default Modeling

Quantifying the bias in Loss Given Default estimation caused by loans that default, recover, and default again, then testing how far the fix holds up under stress.

This project builds on research from the author's master's thesis at SGH Warsaw School of Economics.

## The problem

Loss Given Default (LGD) is the fraction of a loan's exposure a lender expects to lose once a borrower defaults. It's one of the core inputs banks use to calculate regulatory capital, and it's typically estimated from a historical dataset of past defaults and how much was ultimately recovered on each one.

Some defaulted borrowers cure: they catch up on payments and return to performing status. Under EU banking regulation (CRR, with EBA GL/2017/16 and GL/2016/07 setting the operational detail), if a cured borrower later falls back into default, that re-default has to be logged as a brand new, independent default observation rather than as a continuation of the first one. That creates a bookkeeping problem: the same loan now contributes two default events to the historical dataset used to calibrate LGD, and a formula that doesn't account for that double-counting will produce a biased estimate.

Five formulas for estimating LGD are compared here:

- The **basic two-factor model** treats every cured loan as if it will never lose any further value, ignoring the possibility of re-default entirely.
- The **loss-given-cure (LGC) add-on** adds a flat surcharge for cured loans, estimated empirically from how much cured loans actually lose on average, without modeling why.
- The **Prd-correction** accounts for the re-default probability itself but assumes zero recovery during the time a loan spent cured, discarding real information.
- The **re-default-aware model** treats a cured loan as genuinely re-entering the pool of at-risk loans, and introduces two more explicit inputs on top of the cure probability ($PC$) and recovery rate ($RR$) the simpler models already use: $P_{rd}$, the probability that a cured loan re-defaults before the loan's maturity, and $RR_{brd}$, the recovery collected during the time the loan spent cured, before it fell back into default.
- A **segmented variant** of the re-default-aware model relaxes its one load-bearing assumption, that recovery after re-default follows the same distribution as first-default recovery, by estimating the two separately.

The re-default-aware formula, the one this project centers on:

$$LGD_{new} = \frac{(1-RR)\big[(1-PC) - PC \cdot P_{rd} \cdot RR_{brd}\big]}{1 - PC \cdot P_{rd}}$$

Its segmented variant, used when recovery after re-default can't be assumed to match first-default recovery, replaces $RR$ with $RR_{ard}$, the recovery rate on redefaulted exposures estimated separately from $RR$, in the redefault-loss term only:

$$LGD_{adj} = \frac{\big(1 - PC - PC \cdot P_{rd}\big)(1-RR) + PC \cdot P_{rd}(1-RR_{brd})(1-RR_{ard})}{1 - PC \cdot P_{rd}}$$

## Research goals

1. **Baseline bias.** Under correctly specified assumptions, how much do the basic, LGC, and Prd-correction formulas diverge from the re-default-aware one, and how does that gap move with $P_{rd}$, $PC$, and cure timing?
2. **Complexity vs. robustness.** At what reference-dataset size or re-default count does the added estimation variance from the more complex formula's extra parameters offset its lower structural bias?
3. **Reference-dataset construction.** Does the reference dataset itself correctly apply the nine-month re-default independence rule (EBA/GL/2017/16 §101), and what happens to each formula's bias if it doesn't?
4. **Misspecification.** Does the more complex formula's advantage survive when the data is generated under a broken assumption that first-default and redefault recovery rates are equal?

## Docs

- [`docs/dgp_assumptions.md`](docs/dgp_assumptions.md): every distributional and structural assumption behind the simulated data
- [`docs/derivation.md`](docs/derivation.md): the five LGD formulas derived from cash-flow accounting
- [`docs/literature.md`](docs/literature.md): regulatory grounding and the wider LGD literature
- [`docs/results.md`](docs/results.md): full walkthrough of all four experiments, with every committed chart
- [`docs/synthesis.md`](docs/synthesis.md): the practical decision rule for which formula to use and when

## Results

The re-default-aware formula's bias stays within noise of zero wherever the DGP is correctly specified, at every portfolio size and re-default count tested, while the basic, LGC, and Prd-correction formulas each diverge by several percentage points. That advantage holds up under a data-construction check on the nine-month merge rule, with only a small residual bias remaining. It does not hold up unconditionally: if recovery after re-default differs from first-default recovery, the re-default-aware formula's bias can exceed the basic model's, the one it was built to improve on. The segmented variant removes that failure mode entirely. Full numbers, all charts, and the reasoning behind each finding are in [`docs/results.md`](docs/results.md); the practical takeaway is in [`docs/synthesis.md`](docs/synthesis.md).

<img src="results/baseline_summary_grid.png" alt="Relative error of all four original formulas against LGD_true, across the Prd, PC, and mean-cure-month sweeps" width="1000">

*Baseline bias across all three sweeps. See [`docs/results.md`](docs/results.md#baseline-bias).*

<img src="results/misspec_recovery_comparison.png" alt="Relative error of all four original formulas under correctly specified vs misspecified recovery, by Prd" width="1000">

*The re-default-aware formula's advantage reversing under misspecified recovery. See [`docs/results.md`](docs/results.md#misspecification-stress-test).*

<img src="results/misspec_adjustment_merge_comparison.png" alt="Relative error of the re-default-aware formula vs its segmented variant, under misspecified recovery, by merge fraction" width="1000">

*The segmented variant's bias staying at noise level under misspecified recovery, where the unmodified formula's keeps growing. See [`docs/results.md`](docs/results.md#misspecification-stress-test).*

## Reproducing this

Requires [uv](https://docs.astral.sh/uv/) and Python 3.12 (pinned in `.python-version`).

```
uv sync
```

Each notebook fixes its own seed (`SEED = 42`) and writes its charts and summary CSVs to `results/`, so re-running a notebook top to bottom reproduces the committed artifacts exactly. To re-execute one in place:

```
uv run jupyter nbconvert --to notebook --execute --inplace notebooks/01_baseline_sensitivity.ipynb
```

Substitute the notebook filename for `02_complexity_robustness_tradeoff.ipynb`, `03_reference_dataset_construction.ipynb`, or `04_misspecification_stress_test.ipynb` to reproduce the others. To work through them interactively instead:

```
uv run jupyter lab
```

Tests and linting:

```
uv run pytest
uv run ruff check .
uv run ruff format --check .
```
