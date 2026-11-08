# Decomposition of the joint difference into the contact and sending margins

|  | Weekly vs less than monthly | Monthly vs less than monthly |
|---|---|---|
| **Predicted probabilities, full sample (%)** |  |  |
| P_g: contact, group g | 30.55 | 28.77 |
| P_L: contact, less than monthly | 25.19 | 25.19 |
| Q_g: sending given contact, group g | 9.78 | 10.47 |
| Q_L: sending given contact, less than monthly | 8.08 | 8.08 |
| Q_L averaged over contacted respondents only (midterm version) | 7.64 | 7.64 |
| **Joint difference (percentage points), 95% CI, p** |  |  |
| Contact margin, b1 (Q_L + b2/2) | +0.48 (0.11) | +0.33 (0.12) |
| &nbsp;&nbsp;delta method, t(74) | [+0.26, +0.69], p < 0.001 | [+0.10, +0.57], p = 0.006 |
| &nbsp;&nbsp;wild cluster bootstrap, percentile-t | [+0.27, +0.70], p < 0.001 | [+0.12, +0.58], p = 0.007 |
| Sending margin, b2 (P_L + b1/2) | +0.48 (0.38) | +0.65 (0.39) |
| &nbsp;&nbsp;delta method, t(74) | [-0.29, +1.24], p = 0.219 | [-0.13, +1.42], p = 0.103 |
| &nbsp;&nbsp;wild cluster bootstrap, percentile-t | [-0.27, +1.22], p = 0.209 | [-0.16, +1.45], p = 0.110 |
| Product-based difference, contact + sending | +0.95 (0.38) | +0.98 (0.41) |
| &nbsp;&nbsp;delta method, t(74) | [+0.19, +1.71], p = 0.015 | [+0.17, +1.79], p = 0.019 |
| &nbsp;&nbsp;wild cluster bootstrap, percentile-t | [+0.21, +1.68], p = 0.012 | [+0.14, +1.80], p = 0.024 |
| Share from the contact margin (point estimate) | 50% | 34% |
| Direct Stage 3 estimate [95% CI] | +1.16 [+0.23, +2.10], p = 0.016 | +1.14 [+0.15, +2.14], p = 0.025 |
| **Power of Stage 2 (percentage points)** |  |  |
| Stage 2 estimate, b2 (SE) | +1.71 (1.37) | +2.39 (1.46) |
| Minimum detectable difference (80% power, 5% two-sided) | 3.90 | 4.14 |
| Minimum detectable difference / Q_L | 0.48 | 0.51 |

Notes. Specification (2): weighted LPM (`wgt`), country fixed effects, demographic controls, standard errors clustered by economy (75 economies). b1 is the coefficient on g in Stage 1 (reported contact, N = 16,251), b2 the coefficient on g in Stage 2 (sending money among contacted respondents, N = 4,768). P_L and Q_L set every respondent's payment frequency to less than monthly and average the Stage 1 and Stage 2 predictions with `wgt` over the same full sample (N = 16,251); P_g = P_L + b1 and Q_g = Q_L + b2 because the specification has no interaction terms. With these averages the product-based difference P_g Q_g - P_L Q_L equals the contact margin plus the sending margin exactly. The midterm table averaged Q over the contacted subsample (N = 4,768), which is not the population the product refers to; that value is shown for reference. Standard errors in parentheses are from the delta method with the joint cluster covariance of (b1, b2): the economy-level scores of the two regressions are stacked, so the covariance between the two coefficient vectors is estimated rather than assumed zero. The wild cluster bootstrap is unrestricted: in each of B = 9,999 draws every economy receives one Rademacher weight that multiplies its residuals in both regressions; the interval is percentile-t and the p-value is the share of draws with |t*| at least |t|. Seed 20261026. The share from the contact margin is a ratio whose denominator is itself uncertain, so no interval is reported for it. The direct Stage 3 estimate is the coefficient on g in the LPM for the joint outcome (contacted and sent money, N = 16,249). The minimum detectable difference is (t_{0.975} + t_{0.80}) times the clustered standard error of b2.

Why the product-based and direct estimates differ. Both are estimated on the same population now, so the remaining gap is functional form: the direct estimate fits one linear model to the joint outcome, while the product of two linear models is quadratic in the covariates. The two intervals overlap almost entirely.
