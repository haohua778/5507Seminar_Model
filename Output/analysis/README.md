# Additional analyses

Everything in this folder is produced by two entry scripts in the project root. `run_analysis.py`
runs the four analysis modules of `Analysis_Pipeline/` in order (descriptives, Figure 1,
decomposition, Figure 2). `run_pipeline.py` runs, after the main regressions, the five
paper-number modules that reproduce numbers quoted in the paper outside the main tables. All
modules reuse the sample construction and the estimator of the main pipeline
(`DataClean_Pipeline/build_sample.py`, `Model_Pipeline/`): weighted LPM (`wgt`), country fixed
effects, standard errors clustered by economy, t distribution with 74 degrees of freedom,
reference group less than monthly. Specification (2) is the main specification.
`run_pipeline.py` must have been run before `run_analysis.py` (Figure 2 checks its numbers
against `Output/<stage>/summary.csv`).

A single step can be run alone from the project root, for example
`python -m Analysis_Pipeline.joint_decomposition`. Figure 2 reads the outputs of Figure 1 and of
the decomposition, so run those two before it.

## Files written by run_analysis.py

| File | Content | Module |
|---|---|---|
| `descriptives_by_frequency.csv`, `.md` | Table 2: weighted means in the full sample and by payment frequency, weighted group shares, within-economy differences | `descriptives_by_frequency.py` |
| `figure1_between_within.png`, `.pdf` | Figure 1: economy-level scatter and pooled versus within-economy Stage 3 estimates | `figure1_between_within.py` |
| `figure1_economy_level.csv` | Sample size, weekly share and joint-event rate by economy (data for Figure 1, panel A) | `figure1_between_within.py` |
| `joint_decomposition.csv`, `.md` | Joint difference split into the contact and sending margins on the full sample, with delta-method and wild-cluster-bootstrap intervals; direct Stage 3 estimate; Stage 2 minimum detectable difference | `joint_decomposition.py` |
| `figure2_predicted_probabilities.png`, `.pdf`, `.csv` | Figure 2: predicted probabilities P_W, P_M, P_L with 95% CI for the three stages | `figure2_predicted_probabilities.py` |
| `figure_notes.md` | Captions, reading and key numbers for Figures 1 and 2 | Figure 1 section by `figure1_between_within.py`, Figure 2 section by `figure2_predicted_probabilities.py` |

## Files written by run_pipeline.py (paper-number checks)

Each module lists the numbers written in the paper as targets, computes the same quantities from
the data, and returns a comparison table; `run_pipeline.py` prints the tables and collects them
in `paper_number_checks.md`. A row matches when the computed value rounds to the paper's value
at the paper's precision. Nothing is tuned to hit a target: a row marked NO points to a number in
the paper, or a definition, that needs a second look. All modules use the common sample
(16,251 respondents, 75 economies) and the Findex weight `wgt`.

| File | Content | Module | Paper |
|---|---|---|---|
| `descriptives_full_sample.csv` | Full-sample weighted means (weighted SD for age), N of each row's sample, weighted share of the three frequency groups | `descriptives_full_sample.py` | Table 2, full-sample column |
| `economy_composition.csv` | By economy: contact rate, joint-event rate, less-than-monthly share, weekly share, tercile of the less-than-monthly share | `economy_composition.py` | Section 3.4 |
| `economy_composition_terciles.csv` | Mean contact and joint rates in the terciles of the less-than-monthly share, simple and sample-size-weighted means | `economy_composition.py` | Section 3.4 |
| `cluster_sizes.csv` | By economy: respondents in the Stage 1, 2 and 3 samples and number of senders | `cluster_sizes.py` | Section 3.6 |
| `decomposition_checks.csv` | Fitted values outside [0, 1], Stage 2 predictions on the full sample, product difference with truncated predictions, interaction term and contact-margin range, Qbar_L on the full and contacted samples | `decomposition_checks.py` | Sections 3.5 and 4.2 |
| `stage2_power.csv` | Stage 2 coefficients, standard errors, minimum detectable differences, TOST p-values for bounds of 2, 3, 3.9, 4 and 5 points | `stage2_power.py` | Section 4.2 |
| `paper_number_checks.md` | All comparison tables: computed value, paper value, difference, match | `run_pipeline.py` via `paper_targets.py` | |

Findings recorded by the checks (8 November 2026): every number matches except Lesotho's Stage 2
count, which is 28 in the data (the paper writes 52; 28 was the earlier draft). The tercile means
of Section 3.4 match with the simple mean of the economy rates, not the sample-size-weighted mean.
The truncated product difference of Section 4.2 matches when the individual predictions are
clipped to [0, 1] before multiplying and averaging (0.917 and 0.933 points); clipping the averages
instead gives 0.912 and 0.926.

## Change from the midterm version of the decomposition

The midterm table (`Output/archive/midterm_2026-10-09/joint_decomposition.md`) averaged the Stage 2
prediction Q over the contacted subsample (N = 4,768) while P was averaged over the full sample
(N = 16,251), so the two averages referred to different populations. The decomposition now averages
both over the full sample; Stage 2 is still estimated on contacted respondents, only its prediction
is extended to everyone. Because specification (2) has no interaction terms, the formulas reduce to
contact margin = b1 (Q_L + b2/2) and sending margin = b2 (P_L + b1/2), and the change only moves Q_L
(7.64 to 8.08). Weekly versus less than monthly: contact margin 0.45 to 0.48, sending margin 0.48
unchanged, product-based difference 0.93 to 0.95; the direct Stage 3 estimate is 1.16 in both
versions. The new table adds standard errors and intervals (delta method with the joint cluster
covariance of the two regressions, and an unrestricted wild cluster bootstrap) and reports the
share from the contact margin as a point estimate only.

## Checks

- The group columns and within-economy differences of the descriptive statistics, the Figure 1
  data and the Figure 2 data are identical to the midterm files in
  `Output/archive/midterm_2026-10-09/`; the descriptive table has since gained the full-sample
  column and the share row.
- `joint_decomposition.py` recomputes the clustered standard errors of Stages 1 and 2 from the
  stacked scores and stops if they differ from statsmodels by more than 1e-8.
- `figure2_predicted_probabilities.py` verifies that every point estimate, interval and p-value
  equals specification (2) in `Output/<stage>/summary.csv`.
