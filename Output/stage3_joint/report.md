# Stage 3: reported contact and sending money

- Sample: Common sample without con21 = 1 and con22 in {8,9}
- N = 16,249 in 75 economies
- Outcome: 1 = contacted and sent money; 0 = not contacted, or contacted but did not send
- Outcome = 1 for 445 respondents, in 68 of 75 economies
- Estimation: weighted LPM (`wgt`), country fixed effects, standard errors clustered by economy
- Reference group: less than monthly (`fin25e3` = 3)
- Unit: percentage points; 95% CI in brackets

## Main table

|  | (1) Country FE only | (2) Main: demographics | (3) Plus digital engagement |
|---|---|---|---|
| P_W: weekly | 2.92 | 2.91 | 2.92 |
| P_M: monthly | 2.89 | 2.90 | 2.89 |
| P_L: less than monthly | 1.75 | 1.75 | 1.75 |
| b_W: weekly - less than monthly | +1.17 [+0.24, +2.09], p = 0.014 | +1.16 [+0.23, +2.10], p = 0.016 | +1.17 [+0.23, +2.11], p = 0.015 |
| b_M: monthly - less than monthly | +1.14 [+0.14, +2.14], p = 0.026 | +1.14 [+0.15, +2.14], p = 0.025 | +1.14 [+0.13, +2.15], p = 0.028 |
| b_W - b_M: weekly - monthly | +0.03 [-0.86, +0.91], p = 0.950 | +0.02 [-0.89, +0.93], p = 0.967 | +0.03 [-0.88, +0.94], p = 0.943 |

All three specifications use the same sample. A predicted probability sets everyone's payment frequency to one level, keeps all other variables at their observed values, and takes the weighted mean.

## Raw weighted rates by payment frequency (no controls)

| Frequency | N | Outcome = 1 | Weighted rate (%) |
|---|---|---|---|
| weekly | 7,356 | 184 | 2.37 |
| monthly | 4,761 | 145 | 2.96 |
| less than monthly | 4,132 | 116 | 2.71 |
