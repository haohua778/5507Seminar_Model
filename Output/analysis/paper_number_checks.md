# Paper numbers reproduced by the pipeline

Written by `run_pipeline.py`. Each table lists a quantity the paper reports, the value computed from the data by the module named in the section title, the value written in the paper, and whether the computed value rounds to the paper's value at the paper's precision. Full-precision values are in the CSV files of `Output/analysis/`.

## Table 2, full-sample column (descriptives_full_sample.py)

| Quantity | Computed | Paper | Computed - paper | Matches |
|---|---|---|---|---|
| Age, weighted mean (years) | 34.8917 | 34.8900 | 0.0017 | yes |
| Age, weighted SD (years) | 13.4889 | 13.4900 | -0.0011 | yes |
| Female, weighted mean (%) | 44.9572 | 44.9600 | -0.0028 | yes |
| Tertiary education, weighted mean (%) | 20.7935 | 20.7900 | 0.0035 | yes |
| Income quintile 5, weighted mean (%) | 33.2675 | 33.2700 | -0.0025 | yes |
| In the labor force, weighted mean (%) | 74.6903 | 74.6900 | 0.0003 | yes |
| Rural, weighted mean (%) | 49.2540 | 49.2500 | 0.0040 | yes |
| Uses the internet, weighted mean (%) | 90.1956 | 90.2000 | -0.0044 | yes |
| Owns a smartphone, weighted mean (%) | 87.4297 | 87.4300 | -0.0003 | yes |
| Has an account, weighted mean (%) | 98.7003 | 98.7000 | 0.0003 | yes |
| Reported scam contact (Stage 1), weighted mean (%) | 28.7089 | 28.7100 | -0.0011 | yes |
| Sent money, among contacted (Stage 2), weighted mean (%) | 9.1332 | 9.1300 | 0.0032 | yes |
| Contact and sent money (Stage 3), weighted mean (%) | 2.6215 | 2.6200 | 0.0015 | yes |
| Age (years), N | 16,251 | 16,251 | 0 | yes |
| Sent money, among contacted (Stage 2), N | 4,768 | 4,768 | 0 | yes |
| Contact and sent money (Stage 3), N | 16,249 | 16,249 | 0 | yes |
| Share of the sample: weekly (%) | 46.3766 | 46.4000 | -0.0234 | yes |
| Share of the sample: monthly (%) | 28.8833 | 28.9000 | -0.0167 | yes |
| Share of the sample: less_than_monthly (%) | 24.7401 | 24.7000 | 0.0401 | yes |

## Section 3.4, economy-level composition (economy_composition.py)

| Quantity | Computed | Paper | Computed - paper | Matches |
|---|---|---|---|---|
| Mean contact rate of the own economy, less than monthly payers (%) | 31.2505 | 31.3000 | -0.0495 | yes |
| Mean joint rate of the own economy, less than monthly payers (%) | 3.4540 | 3.5000 | -0.0460 | yes |
| Mean contact rate of the own economy, weekly payers (%) | 27.3150 | 27.3000 | 0.0150 | yes |
| Mean joint rate of the own economy, weekly payers (%) | 2.1390 | 2.1000 | 0.0390 | yes |
| Mean contact rate, highest tercile of the less-than-monthly share, simple mean of economies (%) | 34.4036 | 34.4000 | 0.0036 | yes |
| Mean joint rate, highest tercile of the less-than-monthly share, simple mean of economies (%) | 5.2515 | 5.3000 | -0.0485 | yes |
| Mean contact rate, lowest tercile of the less-than-monthly share, simple mean of economies (%) | 28.1285 | 28.1000 | 0.0285 | yes |
| Mean joint rate, lowest tercile of the less-than-monthly share, simple mean of economies (%) | 2.1288 | 2.1000 | 0.0288 | yes |
| Correlation of weekly share and joint rate across economies (weekly share on the common sample) | -0.1877 | -0.1900 | 0.0023 | yes |
| Correlation of weekly share and joint rate across economies (weekly share on the Stage 3 sample, as Figure 1) | -0.1877 | -0.1900 | 0.0023 | yes |

## Section 3.6, cluster sizes and concentration of senders (cluster_sizes.py)

| Quantity | Computed | Paper | Computed - paper | Matches |
|---|---|---|---|---|
| Stage 1 cluster size, smallest | 15 | 15 | 0 | yes |
| Stage 1 cluster size, largest | 939 | 939 | 0 | yes |
| Stage 1 cluster size, median | 139.0000 | 139 | 0.0000 | yes |
| Senders | 445 | 445 | 0 | yes |
| Share of senders in the 10 economies with the most senders (%) | 42.2472 | 42 | 0.2472 | yes |
| Economies with no sender | 7 | 7 | 0 | yes |
| Economies with no sender, names | Belize, Honduras, Madagascar, Morocco, Sri Lanka, Tunisia, Zimbabwe | Belize, Honduras, Madagascar, Morocco, Sri Lanka, Tunisia, Zimbabwe |  | yes |
| Lesotho, respondents in the common sample | 171 | 171 | 0 | yes |
| Lesotho, respondents in the Stage 2 sample | 28 | 28 | 0 | yes |

## Sections 3.5 and 4.2, decomposition checks (decomposition_checks.py)

| Quantity | Computed | Paper | Computed - paper | Matches |
|---|---|---|---|---|
| stage1_contact: fitted values below 0 (%) | 1.1445 | 1.1000 | 0.0445 | yes |
| stage1_contact: fitted values above 1 (count) | 0 | 0 | 0 | yes |
| stage2_send: fitted values below 0 (%) | 5.1804 | 5.2000 | -0.0196 | yes |
| stage2_send: fitted values above 1 (count) | 0 | 0 | 0 | yes |
| stage3_joint: fitted values below 0 (%) | 11.2253 | 11.2000 | 0.0253 | yes |
| stage3_joint: fitted values above 1 (count) | 0 | 0 | 0 | yes |
| Stage 2 prediction at L below 0, full sample (%) | 12.4608 | 12.5000 | -0.0392 | yes |
| Product difference, truncated, weekly (pp) | 0.9171 | 0.9200 | -0.0029 | yes |
| Product difference, untruncated, weekly (pp) | 0.9537 | 0.9500 | 0.0037 | yes |
| Product difference, truncated, monthly (pp) | 0.9326 | 0.9300 | 0.0026 | yes |
| Product difference, untruncated, monthly (pp) | 0.9777 | 0.9800 | -0.0023 | yes |
| Interaction b1 b2, weekly (pp) | 0.0914 | 0.0900 | 0.0014 | yes |
| Contact margin, interaction to sending, weekly (pp) | 0.4327 | 0.4300 | 0.0027 | yes |
| Contact margin, interaction to contact, weekly (pp) | 0.5240 | 0.5200 | 0.0040 | yes |
| Interaction b1 b2, monthly (pp) | 0.0857 | 0.0900 | -0.0043 | yes |
| Contact margin, interaction to sending, monthly (pp) | 0.2895 | 0.2900 | -0.0005 | yes |
| Contact margin, interaction to contact, monthly (pp) | 0.3752 | 0.3800 | -0.0048 | yes |
| Qbar_L, full sample (%) | 8.0774 | 8.0800 | -0.0026 | yes |
| Qbar_L, contacted sample (%) | 7.6382 | 7.6400 | -0.0018 | yes |

## Section 4.2, power of Stage 2 (stage2_power.py)

| Quantity | Computed | Paper | Computed - paper | Matches |
|---|---|---|---|---|
| Stage 2 coefficient, weekly (pp) | 1.7056 | 1.7060 | -0.0004 | yes |
| Stage 2 SE, weekly (pp) | 1.3723 | 1.3720 | 0.0003 | yes |
| Minimum detectable difference, weekly (pp) | 3.8961 | 3.8960 | 0.0001 | yes |
| Stage 2 coefficient, monthly (pp) | 2.3919 | 2.3920 | -0.0001 | yes |
| Stage 2 SE, monthly (pp) | 1.4577 | 1.4580 | -0.0003 | yes |
| Minimum detectable difference, monthly (pp) | 4.1386 | 4.1390 | -0.0004 | yes |
| TOST p-value, weekly, bound +-2 pp | 0.4154 | 0.4154 | -0.0000 | yes |
| TOST p-value, weekly, bound +-3 pp | 0.1743 | 0.1743 | 0.0000 | yes |
| TOST p-value, weekly, bound +-3.9 pp | 0.0570 | 0.0570 | 0.0000 | yes |
| TOST p-value, weekly, bound +-4 pp | 0.0494 | 0.0494 | -0.0000 | yes |
| TOST p-value, weekly, bound +-5 pp | 0.0094 | 0.0094 | 0.0000 | yes |
