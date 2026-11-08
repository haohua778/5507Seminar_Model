"""Table 2, full-sample column (Section 3, data).

Weighted means over all respondents for every row of the descriptive table,
with the same variables and samples as descriptives_by_frequency.py: the
common sample for the characteristics (income quintile 5 without Lesotho,
which has no income data), the Stage 1, Stage 2 and Stage 3 samples for the
three outcome rates. Age also gets its weighted standard deviation. The
weighted share of the three payment-frequency groups is added at the end.

Input:  common sample from DataClean_Pipeline.build_sample, weights `wgt`
Output: Output/analysis/descriptives_full_sample.csv
        The complete Table 2 (full sample next to the three groups and the
        within-economy differences) is descriptives_by_frequency.{csv,md},
        written by run_analysis.py with the same helper functions.
Paper:  Table 2, column "Full sample"; group shares in Section 3

Run from the project root, as part of run_pipeline.py or alone:
    python -m Analysis_Pipeline.descriptives_full_sample
"""

import numpy as np
import pandas as pd

from Analysis_Pipeline.descriptives_by_frequency import (
    GROUP_COLUMNS, OUTPUT_DIR, group_share, variable_list, weighted_mean, weighted_sd)
from Analysis_Pipeline.paper_targets import compare, comparison_table, print_comparison
from DataClean_Pipeline.build_sample import build_common_sample, load_raw

TITLE = "Table 2, full-sample column (descriptives_full_sample.py)"

# Numbers written in the paper. Means in percent, age in years.
MEAN_TARGETS = {
    "Age (years)": 34.89,
    "Female": 44.96,
    "Tertiary education": 20.79,
    "Income quintile 5": 33.27,
    "In the labor force": 74.69,
    "Rural": 49.25,
    "Uses the internet": 90.20,
    "Owns a smartphone": 87.43,
    "Has an account": 98.70,
    "Reported scam contact (Stage 1)": 28.71,
    "Sent money, among contacted (Stage 2)": 9.13,
    "Contact and sent money (Stage 3)": 2.62,
}
AGE_SD_TARGET = 13.49
N_TARGETS = {
    "Age (years)": 16251,
    "Sent money, among contacted (Stage 2)": 4768,
    "Contact and sent money (Stage 3)": 16249,
}
SHARE_TARGETS = {"weekly": 46.4, "monthly": 28.9, "less_than_monthly": 24.7}


def share_label(name):
    return f"Share of the sample: {name}"


def full_sample_table(common):
    rows = []
    for label, column, sample in variable_list(common):
        rows.append({
            "variable": label,
            "N": len(sample),
            "weighted_mean": weighted_mean(sample, column),
            "weighted_sd": weighted_sd(sample, column) if column == "age" else np.nan,
        })
    for code, name in GROUP_COLUMNS.items():
        rows.append({
            "variable": share_label(name),
            "N": len(common),
            "weighted_mean": group_share(common, code),
            "weighted_sd": np.nan,
        })
    return pd.DataFrame(rows)


def comparison(table):
    values = table.set_index("variable")
    rows = []
    for label, target in MEAN_TARGETS.items():
        if label.startswith("Age"):
            rows.append(compare("Age, weighted mean (years)", values.loc[label, "weighted_mean"], target))
            rows.append(compare("Age, weighted SD (years)", values.loc[label, "weighted_sd"], AGE_SD_TARGET))
        else:
            rows.append(compare(f"{label}, weighted mean (%)", 100 * values.loc[label, "weighted_mean"], target))
    for label, target in N_TARGETS.items():
        rows.append(compare(f"{label}, N", int(values.loc[label, "N"]), target))
    for name, target in SHARE_TARGETS.items():
        rows.append(compare(f"{share_label(name)} (%)",
                            100 * values.loc[share_label(name), "weighted_mean"], target))
    return comparison_table(rows)


def run(common):
    """Write the CSV and return the comparison with the paper."""
    table = full_sample_table(common)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUTPUT_DIR / "descriptives_full_sample.csv", index=False)
    return comparison(table)


def main():
    common, _ = build_common_sample(load_raw())
    print_comparison(TITLE, run(common))


if __name__ == "__main__":
    main()
