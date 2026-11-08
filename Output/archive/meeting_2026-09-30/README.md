# Numbers prepared for the group meeting on 30 September 2026

Quick computations in response to the instructor's email of 29 September. All use the common
sample (16,251 respondents, 75 economies) and the same estimator as the main results. They have
not yet been added to the pipeline and should be reviewed before they go into the paper.

| File | Content |
| --- | --- |
| `descriptives_by_frequency.csv` | Weighted means by payment-frequency group, plus within-economy differences (country fixed effects) |
| `joint_decomposition.csv` | Joint difference split into the contact margin and the sending margin |
| `heterogeneity_cell_sizes.csv` | Contacts and senders in each subgroup x frequency cell, with the collapsed at-least-monthly grouping |
| `equal_weight_per_economy.csv` | Specification (2) with each economy given equal total weight, next to the main estimate |
| `economy_level.csv` | Share of weekly payers and outcome rates by economy, for the between-versus-within figure |

## Headline numbers

- Within an economy, weekly payers (vs less than monthly) are 9.6 points more likely to have tertiary
  education, 17.3 points more likely to be in income quintile 5, 11.0 points more likely to be in the
  labor force, 10.5 points less likely to be rural, and 5.3 points less likely to be female. Age is the same.
- Joint difference, weekly vs less than monthly: the product-based difference is 0.93 points, of which
  0.46 comes from the higher contact rate and 0.48 from the higher sending rate (49% / 51%). The direct
  Stage 3 estimate is 1.16.
- Cell sizes: with three frequency groups, two cells fall below 30 senders (low income x less than monthly
  = 29; primary education x monthly = 27). With at-least-monthly vs less-than-monthly, the only cell below
  30 is low income x less than monthly, at 29.
- Equal weight per economy, specification (2): Stage 1 weekly +5.29 [+1.02, +9.55], p = 0.016;
  Stage 2 weekly +2.07 [-3.51, +7.64], p = 0.462; Stage 3 weekly +1.46 [-0.36, +3.28], p = 0.115.
  Point estimates are similar or larger; intervals are much wider; Stage 3 is no longer significant.
- Weights: `wgt` sums to the sample size within each economy (from 18 to 936), so the pooled regression
  weights economies by sample size, not population. `pop_adult` is available for population weights.
- Phone vs card: `fin25e2` (phone or card) is 1 for everyone by construction and `fin25e3` gives one
  combined frequency. `fin25e1` varies: 11,154 respondents are coded 1 and 5,081 are coded 2. If the
  questionnaire confirms that `fin25e1` is in-store payment by mobile phone, it separates mobile payers
  from card-only payers. Among weekly payers 82% have `fin25e1` = 1; among less-than-monthly payers 49%.
- Economy level: correlation between the share of weekly payers and the joint-event rate is -0.19.
  Economies in the top tercile of weekly share have a joint rate of 1.8%; the bottom tercile 4.6%.
  Within economies the weekly-vs-less-than-monthly difference is +1.16 points.
