# Stage 1: reported scam contact

- Sample: Common sample
- N = 16,251 in 75 economies
- Outcome: con21: 1 -> 1, 2 -> 0
- Outcome = 1 for 4,770 respondents, in 75 of 75 economies
- Estimation: weighted LPM (`wgt`), country fixed effects, standard errors clustered by economy
- Reference group: less than monthly (`fin25e3` = 3)
- Unit: percentage points; 95% CI in brackets

## Main table

|  | (1) Country FE only | (2) Main: demographics | (3) Plus digital engagement |
|---|---|---|---|
| P_W: weekly | 31.00 | 30.55 | 30.53 |
| P_M: monthly | 28.56 | 28.77 | 28.76 |
| P_L: less than monthly | 24.59 | 25.19 | 25.24 |
| b_W: weekly - less than monthly | +6.41 [+4.06, +8.77], p < 0.001 | +5.36 [+2.88, +7.83], p < 0.001 | +5.29 [+2.80, +7.78], p < 0.001 |
| b_M: monthly - less than monthly | +3.97 [+1.60, +6.34], p = 0.001 | +3.58 [+1.21, +5.96], p = 0.004 | +3.51 [+1.11, +5.91], p = 0.005 |
| b_W - b_M: weekly - monthly | +2.44 [+0.23, +4.65], p = 0.031 | +1.77 [-0.60, +4.15], p = 0.142 | +1.77 [-0.59, +4.14], p = 0.140 |

All three specifications use the same sample. A predicted probability sets everyone's payment frequency to one level, keeps all other variables at their observed values, and takes the weighted mean.

## Raw weighted rates by payment frequency (no controls)

| Frequency | N | Outcome = 1 | Weighted rate (%) |
|---|---|---|---|
| weekly | 7,358 | 2,138 | 29.16 |
| monthly | 4,761 | 1,396 | 28.74 |
| less than monthly | 4,132 | 1,236 | 27.82 |
