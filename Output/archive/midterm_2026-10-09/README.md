# Results prepared for the meeting on 9 October 2026

Everything in this folder is produced by the scripts in `Oct9/`, run from the project root with
`.venv/bin/python Oct9/<script>.py`. All scripts reuse the sample construction and the estimator of
the main pipeline (`DataClean_Pipeline/build_sample.py`, `Model_Pipeline/lpm.py`,
`Model_Pipeline/stages.py`, `Model_Pipeline/results.py`): weighted LPM (`wgt`), country fixed
effects, standard errors clustered by economy, t distribution with 74 degrees of freedom,
reference group less than monthly. Specification (2) is the main specification.

Run the scripts in order: Step 4 reads the minimum detectable difference from the Step 3 output and
appends to the figure notes written by Step 2.

| File | Content | Script |
|---|---|---|
| `descriptives_by_frequency.csv` | Weighted means by payment frequency and within-economy differences, raw values | `Oct9/step1_descriptives_by_frequency.py` |
| `descriptives_by_frequency.md` | Same as a formatted table with notes | `Oct9/step1_descriptives_by_frequency.py` |
| `figure1_between_within.png`, `.pdf` | Figure 1: economy-level scatter and pooled versus within-economy Stage 3 estimates | `Oct9/step2_figure1_between_within.py` |
| `figure1_economy_level.csv` | Sample size, weekly share and joint-event rate by economy (data for Figure 1, panel A) | `Oct9/step2_figure1_between_within.py` |
| `joint_decomposition.csv` | Joint difference split into the contact and sending margins, direct Stage 3 estimate, Stage 2 minimum detectable difference | `Oct9/step3_joint_decomposition.py` |
| `joint_decomposition.md` | Same as a formatted table, with notes and the explanation of the product-based versus direct estimate | `Oct9/step3_joint_decomposition.py` |
| `figure2_predicted_probabilities.png`, `.pdf` | Figure 2: predicted probabilities P_W, P_M, P_L with 95% CI for the three stages | `Oct9/step4_figure2_predicted_probabilities.py` |
| `figure2_predicted_probabilities.csv` | Predicted probabilities, confidence intervals and b_W behind Figure 2 | `Oct9/step4_figure2_predicted_probabilities.py` |
| `figure_notes.md` | Captions, reading and key numbers for Figures 1 and 2 | Figure 1 section by `Oct9/step2_figure1_between_within.py`, Figure 2 section by `Oct9/step4_figure2_predicted_probabilities.py` |

## Checks against earlier numbers

- Step 1 reproduces the within-economy differences computed for the 30 September meeting
  (`Output/meeting_2026-09-30/descriptives_by_frequency.csv`).
- Step 2 reproduces the correlation of -0.19, the tercile joint rates (1.8% and 4.6%) and the
  within-economy estimate of +1.16.
- Step 3 reproduces the decomposition (0.93 = 0.45 + 0.48) in
  `Output/meeting_2026-09-30/joint_decomposition.csv`.
- Step 4 verifies programmatically that every point estimate, interval and p-value equals
  specification (2) in `Output/<stage>/summary.csv`, the source of `Output/main_results.md`.

One difference in sample definition: the 30 September files computed Stage 3 quantities on all
16,251 respondents, coding the two contacted respondents with an unknown sending outcome as 0.
The scripts here use the Stage 3 sample of the main pipeline (16,249), as in `main_results.md`.
The effect is in the third decimal place.
