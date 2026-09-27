# Stage 2: sending money conditional on reported contact

- Sample: Common sample with con21 = 1 and con22 in {1,2} (conditional on reported contact)
- N = 4,768 in 75 economies
- Outcome: con22: 1 -> 1, 2 -> 0; 8 and 9 dropped
- Outcome = 1 for 445 respondents, in 68 of 75 economies
- Estimation: weighted LPM (`wgt`), country fixed effects, standard errors clustered by economy
- Reference group: less than monthly (`fin25e3` = 3)
- Unit: percentage points; 95% CI in brackets

## Main table

|  | (1) Country FE only | (2) Main: demographics | (3) Plus digital engagement |
|---|---|---|---|
| P_W: weekly | 9.31 | 9.34 | 9.35 |
| P_M: monthly | 10.03 | 10.03 | 10.08 |
| P_L: less than monthly | 7.71 | 7.64 | 7.57 |
| b_W: weekly - less than monthly | +1.60 [-1.07, +4.27], p = 0.237 | +1.71 [-1.03, +4.44], p = 0.218 | +1.78 [-0.96, +4.52], p = 0.199 |
| b_M: monthly - less than monthly | +2.32 [-0.55, +5.19], p = 0.112 | +2.39 [-0.51, +5.30], p = 0.105 | +2.51 [-0.41, +5.43], p = 0.091 |
| b_W - b_M: weekly - monthly | -0.72 [-3.34, +1.90], p = 0.585 | -0.69 [-3.21, +1.84], p = 0.589 | -0.73 [-3.25, +1.79], p = 0.566 |

All three specifications use the same sample. A predicted probability sets everyone's payment frequency to one level, keeps all other variables at their observed values, and takes the weighted mean.

## Raw weighted rates by payment frequency (no controls)

| Frequency | N | Outcome = 1 | Weighted rate (%) |
|---|---|---|---|
| weekly | 2,136 | 184 | 8.12 |
| monthly | 1,396 | 145 | 10.29 |
| less than monthly | 1,236 | 116 | 9.73 |
