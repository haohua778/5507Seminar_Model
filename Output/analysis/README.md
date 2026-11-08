# Additional analyses

Everything in this folder is produced by `run_analysis.py` (project root), which runs the four
modules of `Analysis_Pipeline/` in order. All modules reuse the sample construction and the
estimator of the main pipeline (`DataClean_Pipeline/build_sample.py`, `Model_Pipeline/`):
weighted LPM (`wgt`), country fixed effects, standard errors clustered by economy, t distribution
with 74 degrees of freedom, reference group less than monthly. Specification (2) is the main
specification. `run_pipeline.py` must have been run first (Figure 2 checks its numbers against
`Output/<stage>/summary.csv`).

A single step can be run alone from the project root, for example
`python -m Analysis_Pipeline.joint_decomposition`. Figure 2 reads the outputs of Figure 1 and of
the decomposition, so run those two before it.

| File | Content | Module |
|---|---|---|
| `descriptives_by_frequency.csv`, `.md` | Weighted means by payment frequency and within-economy differences | `descriptives_by_frequency.py` |
| `figure1_between_within.png`, `.pdf` | Figure 1: economy-level scatter and pooled versus within-economy Stage 3 estimates | `figure1_between_within.py` |
| `figure1_economy_level.csv` | Sample size, weekly share and joint-event rate by economy (data for Figure 1, panel A) | `figure1_between_within.py` |
| `joint_decomposition.csv`, `.md` | Joint difference split into the contact and sending margins on the full sample, with delta-method and wild-cluster-bootstrap intervals; direct Stage 3 estimate; Stage 2 minimum detectable difference | `joint_decomposition.py` |
| `figure2_predicted_probabilities.png`, `.pdf`, `.csv` | Figure 2: predicted probabilities P_W, P_M, P_L with 95% CI for the three stages | `figure2_predicted_probabilities.py` |
| `figure_notes.md` | Captions, reading and key numbers for Figures 1 and 2 | Figure 1 section by `figure1_between_within.py`, Figure 2 section by `figure2_predicted_probabilities.py` |

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

- Descriptive statistics, the Figure 1 data and the Figure 2 data are byte-identical to the midterm
  files in `Output/archive/midterm_2026-10-09/`.
- `joint_decomposition.py` recomputes the clustered standard errors of Stages 1 and 2 from the
  stacked scores and stops if they differ from statsmodels by more than 1e-8.
- `figure2_predicted_probabilities.py` verifies that every point estimate, interval and p-value
  equals specification (2) in `Output/<stage>/summary.csv`.
