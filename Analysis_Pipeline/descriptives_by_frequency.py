"""Descriptive statistics by payment frequency (Table: who pays weekly within an economy).

Common sample, weights `wgt`. For each characteristic the table gives
- the weighted mean in the weekly, monthly and less-than-monthly groups
- the within-economy difference (weekly - less than monthly and monthly - less
  than monthly) from the same weighted regression as the main results but
  with no controls: variable ~ weekly + monthly + country effect,
  standard errors clustered by economy

The Stage 2 rate is computed in the contacted sample (Stage 2 sample).

Outputs: Output/analysis/descriptives_by_frequency.{csv,md}

Run from the project root, as part of run_analysis.py or alone:
    python -m Analysis_Pipeline.descriptives_by_frequency
"""

from pathlib import Path

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

from DataClean_Pipeline.build_sample import FREQUENCY, build_common_sample, load_raw
from Model_Pipeline.lpm import COUNTRY, WEIGHT, fit_lpm, linear_combination
from Model_Pipeline.stages import OUTCOME, stage1_contact, stage2_send, stage3_joint

OUTPUT_DIR = PROJECT_ROOT / "Output" / "analysis"

# fin25e3 code -> output column.
GROUP_COLUMNS = {1: "weekly", 2: "monthly", 3: "less_than_monthly"}


def variable_list(common):
    """(label, column, sample) for every row of the table."""
    no_lesotho = common[common[COUNTRY] != "LSO"]  # Lesotho has no income data
    return [
        ("Age (years)", "age", common),
        ("Female", "female_d", common),
        ("Tertiary education", "educ_3", common),
        ("Income quintile 5", "inc_q5", no_lesotho),
        ("In the labor force", "labor_force", common),
        ("Rural", "rural", common),
        ("Uses the internet", "internet_use", common),
        ("Owns a smartphone", "smartphone", common),
        ("Has an account", "account", common),
        ("Reported scam contact (Stage 1)", OUTCOME, stage1_contact(common)),
        ("Sent money, among contacted (Stage 2)", OUTCOME, stage2_send(common)),
        ("Contact and sent money (Stage 3)", OUTCOME, stage3_joint(common)),
    ]


def weighted_group_means(sample, column):
    means = {}
    for code, name in GROUP_COLUMNS.items():
        group = sample[sample["fin25e3"] == code]
        means[name] = np.average(group[column], weights=group[WEIGHT])
    return means


def within_economy_differences(sample, column):
    """Weekly and monthly coefficients from: column ~ weekly + monthly + country effect."""
    fit = fit_lpm(sample, column, FREQUENCY)
    weekly = linear_combination(fit, "weekly")
    monthly = linear_combination(fit, "monthly")
    return {
        "within_W_minus_L": weekly["estimate"],
        "within_W_minus_L_p": weekly["p_value"],
        "within_M_minus_L": monthly["estimate"],
        "within_M_minus_L_p": monthly["p_value"],
    }


def group_counts(sample, label):
    counts = sample["fin25e3"].value_counts()
    return {"variable": label,
            **{name: float(counts[code]) for code, name in GROUP_COLUMNS.items()}}


def build_table(common):
    rows = [group_counts(common, "N (unweighted)")]
    for label, column, sample in variable_list(common):
        rows.append({
            "variable": label,
            **weighted_group_means(sample, column),
            **within_economy_differences(sample, column),
        })
    rows.append(group_counts(stage2_send(common), "N (unweighted), contacted sample"))
    return pd.DataFrame(rows)


def format_cell(row, column):
    """Shares in percent, age in years, counts as integers. Two decimals."""
    if row["variable"].startswith("N ("):
        return f"{row[column]:,.0f}"
    scale = 1 if row["variable"].startswith("Age") else 100
    return f"{scale * row[column]:.2f}"


def format_difference(row, column):
    if pd.isna(row[column]):
        return ""
    scale = 1 if row["variable"].startswith("Age") else 100
    return f"{scale * row[column]:+.2f} (p = {row[f'{column}_p']:.3f})"


def markdown_table(table):
    header = ["", "Weekly", "Monthly", "Less than monthly",
              "Within-economy W - L", "Within-economy M - L"]
    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    for _, row in table.iterrows():
        cells = [format_cell(row, c) for c in GROUP_COLUMNS.values()]
        cells += [format_difference(row, "within_W_minus_L"),
                  format_difference(row, "within_M_minus_L")]
        lines.append("| " + " | ".join([row["variable"]] + cells) + " |")
    return "\n".join(lines)


def write_markdown(table, common):
    n_economies = common[COUNTRY].nunique()
    n_contacted = len(stage2_send(common))
    notes = [
        "# Descriptive statistics by in-store digital payment frequency",
        "",
        markdown_table(table),
        "",
        f"Notes. Sample: common sample of the Global Findex 2025 scam module, "
        f"N = {len(common):,} respondents in {n_economies} economies; all respondents own a "
        "mobile phone, paid in store by phone or card, and have complete controls. "
        "Payment frequency is `fin25e3` (1 = weekly, 2 = monthly, 3 = less than monthly). "
        "Group columns are means weighted by the Findex sampling weight `wgt`; "
        "shares are in percent, age in years. "
        "Within-economy columns report the coefficients on the weekly and monthly dummies "
        "from a weighted least squares regression of the characteristic on the two dummies "
        "and economy fixed effects, with standard errors clustered by economy "
        f"(t distribution, {n_economies - 1} degrees of freedom); "
        "the reference group is less than monthly. "
        "Income quintile 5 excludes Lesotho, which has no income data. "
        f"The Stage 2 rate is computed among contacted respondents who answered the sending "
        f"question (N = {n_contacted:,}); the Stage 3 rate uses the Stage 3 sample, which drops "
        "contacted respondents with an unknown sending outcome.",
    ]
    (OUTPUT_DIR / "descriptives_by_frequency.md").write_text(
        "\n".join(notes) + "\n", encoding="utf-8")


def main():
    common, _ = build_common_sample(load_raw())
    table = build_table(common)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUTPUT_DIR / "descriptives_by_frequency.csv", index=False)
    write_markdown(table, common)

    pd.set_option("display.width", 200)
    print(table.to_string(index=False))
    print(f"\nResults written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
