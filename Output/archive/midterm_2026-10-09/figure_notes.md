# Figure 1. Weekly in-store digital payment and scam losses: between versus within economies

Files: `figure1_between_within.png` (300 dpi), `figure1_between_within.pdf`, data in `figure1_economy_level.csv`.

**Caption.** Panel A plots the 75 economies in the Stage 3 sample (N = 16,249).
The horizontal axis is the weighted share of respondents who pay in store by phone or card at least
weekly (`fin25e3` = 1); the vertical axis is the weighted share who report scam contact and sent
money (the Stage 3 outcome). Marker area is proportional to the economy's sample size. The line is a
least squares fit weighted by sample size. The Pearson correlation across economies (unweighted) is
r = -0.19. Panel B shows the weekly minus less-than-monthly difference in the same outcome from two
weighted linear probability models with 95% confidence intervals: pooled across economies with no
country fixed effects, and specification (2) with country fixed effects and demographic controls
(age, age squared, female, education, income quintile, labor force, rural). Both use the Findex
sampling weight `wgt`; standard errors are clustered by economy (t distribution,
74 degrees of freedom). The dashed line marks zero.

**Reading.** Across economies the association is negative: economies where more people pay weekly
have lower joint-event rates (mean joint rate 1.8% in the top tercile of the
weekly share, 4.6% in the bottom tercile). Pooling all respondents, weekly
payers have a lower joint rate than less-than-monthly payers (-0.34 percentage points [-1.34, +0.66], p = 0.498). Within an
economy the sign reverses: +1.16 percentage points [+0.23, +2.10], p = 0.016. The country fixed effects therefore carry the
between-economy pattern, and the within-economy comparison is the one the paper interprets.

**Numbers.**

| Quantity | Value |
|---|---|
| Economies / respondents | 75 / 16,249 |
| Correlation, weekly share vs joint rate (unweighted Pearson) | -0.188 |
| Mean joint rate, bottom tercile of weekly share | 4.61% |
| Mean joint rate, middle tercile | 5.80% |
| Mean joint rate, top tercile | 1.81% |
| Pooled difference, no country FE | -0.34 percentage points [-1.34, +0.66], p = 0.498 |
| Within-economy difference, specification (2) | +1.16 percentage points [+0.23, +2.10], p = 0.016 |

# Figure 2. Predicted probabilities by payment frequency, three stages

Files: `figure2_predicted_probabilities.png` (300 dpi), `figure2_predicted_probabilities.pdf`, data in `figure2_predicted_probabilities.csv`.

**Caption.** Each panel shows the predicted probability of the stage outcome if every respondent
paid in store at the given frequency, with all other characteristics at their observed values,
from specification (2): weighted LPM (`wgt`), country fixed effects, demographic controls (age, age
squared, female, education, income quintile, labor force, rural), standard errors clustered by
economy (t distribution, 74 degrees of freedom), 95% confidence intervals. Panel A: reported scam
contact, common sample (N = 16,251). Panel B: sent money, conditional on reported
contact (N = 4,768); the minimum detectable difference is the smallest true weekly minus
less-than-monthly difference this sample would detect with 80% power at the 5% level,
3.90 percentage points, about half of the less-than-monthly rate. Panel C: contacted and
sent money, one joint outcome (N = 16,249). b_W is the weekly minus less-than-monthly
difference, equal to the coefficient on the weekly dummy. All numbers equal specification (2) in
`Output/main_results.md`.

**Reading.** Weekly payers are more likely to report scam contact (Panel A, b_W = +5.36 [+2.88, +7.83], p < 0.001)
and more likely to report contact and sending money (Panel C, b_W = +1.16 [+0.23, +2.10], p = 0.016).
Conditional on contact, the sending rate is higher in point estimate for weekly and monthly payers
but the difference is not significant (Panel B, b_W = +1.71 [-1.03, +4.44], p = 0.218), and the sample could
only detect a difference of about 3.9 points, so Panel B neither supports nor rules out
a sending-margin effect.

**Numbers.**

| | Stage 1: contact | Stage 2: sent money, given contact | Stage 3: contact and sent money |
|---|---|---|---|
| N | 16,251 | 4,768 | 16,249 |
| P_W: weekly (%) [95% CI] | 30.55 [29.41, 31.68] | 9.34 [8.19, 10.50] | 2.91 [2.50, 3.33] |
| P_M: monthly (%) [95% CI] | 28.77 [27.31, 30.24] | 10.03 [8.38, 11.68] | 2.90 [2.30, 3.49] |
| P_L: less than monthly (%) [95% CI] | 25.19 [23.57, 26.80] | 7.64 [5.72, 9.55] | 1.75 [1.11, 2.39] |
| b_W = P_W - P_L (pp) [95% CI] | +5.36 [+2.88, +7.83], p < 0.001 | +1.71 [-1.03, +4.44], p = 0.218 | +1.16 [+0.23, +2.10], p = 0.016 |
