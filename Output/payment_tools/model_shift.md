# Task 7 follow-up: Is the coefficient change distinguishable from zero?

This checks the change in the weekly-versus-less-than-monthly coefficient when fin25e1 is added to main specification B. Both regressions use the same people. Each economy's contributions to both estimates are paired before calculating the uncertainty of their difference.

| Outcome | N | Baseline (pp) | With fin25e1 (pp) | Change (pp) | 95% CI for change (pp) | p-value |
|---|---:|---:|---:|---:|---:|---:|
| Stage 1: reported contact | 16,235 | +5.46 | +4.57 | -0.89 | [-1.46, -0.33] | 0.002 |
| Stage 2: sending money after contact | 4,763 | +1.69 | +1.28 | -0.42 | [-1.05, +0.22] | 0.198 |
| Stage 3: contact and sending money | 16,233 | +1.16 | +0.92 | -0.24 | [-0.45, -0.03] | 0.026 |

## 大白话怎么读

这里比的是同一批人、同一种主模型：第一次不加 fin25e1，第二次加上它。‘变化’等于第二次的每周差距减去第一次的每周差距；负数表示差距缩小。
第一阶段的变化为 -0.89 个百分点，第二阶段为 -0.42 个百分点，第三阶段为 -0.24 个百分点。请看上表的变化区间是否跨过零，再判断变化是否明确。
第三阶段‘新模型里的每周差距’和‘加变量前后差距的变化’是两个不同问题，两种 p 值即使落在 0.05 的两边，也不矛盾。

## Method note

The change is the augmented coefficient minus the same-sample baseline coefficient. The standard error uses a paired country-cluster sandwich calculation with each regression's CR1 finite-sample correction; the interval and two-sided p-value use each stage's number of economies minus one degrees of freedom. This tests the change between two fitted associations, not whether fin25e1 causally explains it. It does not turn a nonsignificant Stage 3 augmented coefficient into proof that the original association vanished.

The corresponding unrounded estimates are in model_shift.csv. The existing Task 7 report and group memo are unchanged.
