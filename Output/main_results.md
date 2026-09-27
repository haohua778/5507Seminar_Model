# Nine main regressions

- Estimation: weighted LPM (`wgt`), country fixed effects, standard errors clustered by economy
- Reference group: less than monthly (`fin25e3` = 3)
- Unit: percentage points; 95% CI in brackets
- Stage 2 uses a selected sample; its results are conditional on reported contact

|  | (1) Country FE only | (2) Main: demographics | (3) Plus digital engagement |
|---|---|---|---|
| **Stage 1: reported scam contact** | N = 16,251 | N = 16,251 | N = 16,251 |
| P_W: weekly | 31.00 | 30.55 | 30.53 |
| P_M: monthly | 28.56 | 28.77 | 28.76 |
| P_L: less than monthly | 24.59 | 25.19 | 25.24 |
| b_W: weekly - less than monthly | +6.41 [+4.06, +8.77], p < 0.001 | +5.36 [+2.88, +7.83], p < 0.001 | +5.29 [+2.80, +7.78], p < 0.001 |
| b_M: monthly - less than monthly | +3.97 [+1.60, +6.34], p = 0.001 | +3.58 [+1.21, +5.96], p = 0.004 | +3.51 [+1.11, +5.91], p = 0.005 |
| b_W - b_M: weekly - monthly | +2.44 [+0.23, +4.65], p = 0.031 | +1.77 [-0.60, +4.15], p = 0.142 | +1.77 [-0.59, +4.14], p = 0.140 |
| **Stage 2: sending money conditional on reported contact** | N = 4,768 | N = 4,768 | N = 4,768 |
| P_W: weekly | 9.31 | 9.34 | 9.35 |
| P_M: monthly | 10.03 | 10.03 | 10.08 |
| P_L: less than monthly | 7.71 | 7.64 | 7.57 |
| b_W: weekly - less than monthly | +1.60 [-1.07, +4.27], p = 0.237 | +1.71 [-1.03, +4.44], p = 0.218 | +1.78 [-0.96, +4.52], p = 0.199 |
| b_M: monthly - less than monthly | +2.32 [-0.55, +5.19], p = 0.112 | +2.39 [-0.51, +5.30], p = 0.105 | +2.51 [-0.41, +5.43], p = 0.091 |
| b_W - b_M: weekly - monthly | -0.72 [-3.34, +1.90], p = 0.585 | -0.69 [-3.21, +1.84], p = 0.589 | -0.73 [-3.25, +1.79], p = 0.566 |
| **Stage 3: reported contact and sending money** | N = 16,249 | N = 16,249 | N = 16,249 |
| P_W: weekly | 2.92 | 2.91 | 2.92 |
| P_M: monthly | 2.89 | 2.90 | 2.89 |
| P_L: less than monthly | 1.75 | 1.75 | 1.75 |
| b_W: weekly - less than monthly | +1.17 [+0.24, +2.09], p = 0.014 | +1.16 [+0.23, +2.10], p = 0.016 | +1.17 [+0.23, +2.11], p = 0.015 |
| b_M: monthly - less than monthly | +1.14 [+0.14, +2.14], p = 0.026 | +1.14 [+0.15, +2.14], p = 0.025 | +1.14 [+0.13, +2.15], p = 0.028 |
| b_W - b_M: weekly - monthly | +0.03 [-0.86, +0.91], p = 0.950 | +0.02 [-0.89, +0.93], p = 0.967 | +0.03 [-0.88, +0.94], p = 0.943 |

## Interpretation: b_W in specification (2), 5% significance level

- Stage 1: +5.36 [+2.88, +7.83], p < 0.001
- Stage 2: +1.71 [-1.03, +4.44], p = 0.218
- Stage 3 (overall association): +1.16 [+0.23, +2.10], p = 0.016
- Wording for the paper: **higher reported contact with no detectable difference in conditional sending**
