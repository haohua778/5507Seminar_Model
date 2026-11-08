# Decomposition of the joint difference into the contact and sending margins

|  | Weekly vs less than monthly | Monthly vs less than monthly |
|---|---|---|
| **Predicted probabilities (%)** |  |  |
| P_g: contact, group g | 30.55 | 28.77 |
| P_L: contact, less than monthly | 25.19 | 25.19 |
| Q_g: sending given contact, group g | 9.34 | 10.03 |
| Q_L: sending given contact, less than monthly | 7.64 | 7.64 |
| **Joint difference (percentage points)** |  |  |
| Product-based difference, P_g Q_g - P_L Q_L | +0.93 | +0.96 |
| Contact margin, (P_g - P_L)(Q_g + Q_L)/2 | +0.45 | +0.32 |
| Sending margin, (Q_g - Q_L)(P_g + P_L)/2 | +0.48 | +0.65 |
| Share from the contact margin | 49% | 33% |
| Direct Stage 3 estimate [95% CI] | +1.16 [+0.23, +2.10], p = 0.016 | +1.14 [+0.15, +2.14], p = 0.025 |
| **Power of Stage 2 (percentage points)** |  |  |
| Stage 2 estimate, Q_g - Q_L (SE) | +1.71 (1.37) | +2.39 (1.46) |
| Minimum detectable difference (80% power, 5% two-sided) | 3.90 | 4.14 |
| Baseline sending rate, Q_L | 7.64 | 7.64 |
| Minimum detectable difference / baseline | 0.51 | 0.54 |

Notes. All quantities from specification (2): weighted LPM (`wgt`), country fixed effects, demographic controls, standard errors clustered by economy (75 economies, t distribution with 74 degrees of freedom). P_g is the Stage 1 predicted probability of reported scam contact (N = 16,251), Q_g the Stage 2 predicted probability of sending money among contacted respondents (N = 4,768); each sets every respondent's payment frequency to g and averages the prediction with `wgt`. The product-based difference equals the contact margin plus the sending margin exactly. The direct Stage 3 estimate is the coefficient on g in the LPM for the joint outcome (contacted and sent money, N = 16,249). The minimum detectable difference is (t_{0.975} + t_{0.80}) times the clustered standard error of the Stage 2 coefficient, which is the smallest true difference in conditional sending that the Stage 2 sample would detect with 80% power at the 5% level.

Why the product-based and direct estimates differ. The product multiplies two sample-average probabilities, but the joint outcome for a respondent is the product of that respondent's own contact and sending probabilities, and the average of a product is not the product of averages when the two vary together across people within a frequency group. Q_g is also estimated on the contacted subsample with its own country effects and controls, while the direct estimate fits one linear model to the joint outcome on the full sample, so the two use different weights and a slightly different sample (N = 16,249 versus 16,251). The gap is within the Stage 3 confidence interval.
