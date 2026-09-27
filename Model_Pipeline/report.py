"""Write the results to Output/ as CSV files and Markdown reports.

Output/
    sample_flow.csv
    main_results.md           nine main regressions and the interpretation
    <stage key>/
        report.md
        summary.csv
        coefficients.csv
"""

from DataClean_Pipeline.build_sample import PROJECT_ROOT
from Model_Pipeline.lpm import COUNTRY
from Model_Pipeline.stages import MAIN_SPEC, OUTCOME, SPEC_LABELS, SPECS

OUTPUT_DIR = PROJECT_ROOT / "Output"

QUANTITY_LABELS = {
    "P_weekly": "P_W: weekly",
    "P_monthly": "P_M: monthly",
    "P_less_than_monthly": "P_L: less than monthly",
    "beta_W": "b_W: weekly - less than monthly",
    "beta_M": "b_M: monthly - less than monthly",
    "beta_W_minus_beta_M": "b_W - b_M: weekly - monthly",
}

METHOD_NOTES = [
    "Estimation: weighted LPM (`wgt`), country fixed effects, "
    "standard errors clustered by economy",
    "Reference group: less than monthly (`fin25e3` = 3)",
    "Unit: percentage points; 95% CI in brackets",
]

SIGNIFICANCE_LEVEL = 0.05


def markdown_table(header, rows):
    lines = ["| " + " | ".join(header) + " |"]
    lines.append("|" + "---|" * len(header))
    for row in rows:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def bullet_list(items):
    return "\n".join(f"- {item}" for item in items)


def format_p(p_value):
    if p_value < 0.001:
        return "p < 0.001"
    return f"p = {p_value:.3f}"


def format_difference(row):
    """Example: +5.36 [+2.89, +7.83], p < 0.001"""
    estimate = 100 * row["estimate"]
    ci_low = 100 * row["ci_low"]
    ci_high = 100 * row["ci_high"]
    return f"{estimate:+.2f} [{ci_low:+.2f}, {ci_high:+.2f}], {format_p(row['p_value'])}"


def results_rows(summary):
    """One table row per quantity, one column per specification."""
    lookup = summary.set_index(["quantity", "spec"])
    rows = []
    for quantity, label in QUANTITY_LABELS.items():
        cells = []
        for spec in SPECS:
            row = lookup.loc[(quantity, spec)]
            if quantity.startswith("P_"):
                cells.append(f"{100 * row['estimate']:.2f}")
            else:
                cells.append(format_difference(row))
        rows.append([label] + cells)
    return rows


def results_header():
    return [""] + [f"{spec} {SPEC_LABELS[spec]}" for spec in SPECS]


def write_sample_flow(flow):
    OUTPUT_DIR.mkdir(exist_ok=True)
    flow.to_csv(OUTPUT_DIR / "sample_flow.csv", index=False)


def write_stage_report(stage, sample, summary, coefficients, rates):
    stage_dir = OUTPUT_DIR / stage.key
    stage_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(stage_dir / "summary.csv", index=False)
    coefficients.to_csv(stage_dir / "coefficients.csv", index=False)

    n_obs = len(sample)
    n_economies = sample[COUNTRY].nunique()
    n_events = int(sample[OUTCOME].sum())
    events_by_economy = sample.groupby(COUNTRY)[OUTCOME].sum()
    n_economies_with_events = int((events_by_economy > 0).sum())

    sample_notes = [
        f"Sample: {stage.sample_note}",
        f"N = {n_obs:,} in {n_economies} economies",
        f"Outcome: {stage.outcome_note}",
        f"Outcome = 1 for {n_events:,} respondents, "
        f"in {n_economies_with_events} of {n_economies} economies",
    ]

    rate_rows = []
    for _, row in rates.iterrows():
        rate_rows.append([
            row["frequency"],
            f"{row['N']:,}",
            f"{row['events']:,}",
            f"{100 * row['weighted_rate']:.2f}",
        ])

    sections = [
        f"# {stage.title}",
        bullet_list(sample_notes + METHOD_NOTES),
        "## Main table",
        markdown_table(results_header(), results_rows(summary)),
        "All three specifications use the same sample. A predicted probability "
        "sets everyone's payment frequency to one level, keeps all other "
        "variables at their observed values, and takes the weighted mean.",
        "## Raw weighted rates by payment frequency (no controls)",
        markdown_table(["Frequency", "N", "Outcome = 1", "Weighted rate (%)"], rate_rows),
    ]
    (stage_dir / "report.md").write_text("\n\n".join(sections) + "\n", encoding="utf-8")


def main_beta_w(summary):
    """b_W in the main specification."""
    is_main = (summary["spec"] == MAIN_SPEC) & (summary["quantity"] == "beta_W")
    return summary[is_main].iloc[0]


def interpret(stage1, stage2):
    """Wording rule for the paper, based on b_W of Stage 1 and Stage 2."""
    stage1_significant = stage1["p_value"] < SIGNIFICANCE_LEVEL
    stage2_significant = stage2["p_value"] < SIGNIFICANCE_LEVEL
    same_sign = (stage1["estimate"] > 0) == (stage2["estimate"] > 0)

    if stage1_significant and stage2_significant and not same_sign:
        return "tradeoff"
    if stage1_significant and stage2_significant and same_sign:
        return "a compounding pattern of consumer scam risk"
    if stage1_significant and stage1["estimate"] > 0:
        return "higher reported contact with no detectable difference in conditional sending"
    if stage1_significant:
        return "lower reported contact with no detectable difference in conditional sending"
    return "describe the results as they are; do not use the word tradeoff"


def write_main_results(stages, summaries):
    """Nine main regressions in one table. `summaries` follows the order of `stages`."""
    rows = []
    for stage, summary in zip(stages, summaries):
        n_obs = summary["N"].iloc[0]
        rows.append([f"**{stage.title}**"] + [f"N = {n_obs:,}"] * len(SPECS))
        rows += results_rows(summary)

    stage1, stage2, stage3 = [main_beta_w(summary) for summary in summaries]
    interpretation = [
        f"Stage 1: {format_difference(stage1)}",
        f"Stage 2: {format_difference(stage2)}",
        f"Stage 3 (overall association): {format_difference(stage3)}",
        f"Wording for the paper: **{interpret(stage1, stage2)}**",
    ]

    sections = [
        "# Nine main regressions",
        bullet_list(METHOD_NOTES + [
            "Stage 2 uses a selected sample; its results are conditional on reported contact",
        ]),
        markdown_table(results_header(), rows),
        f"## Interpretation: b_W in specification {MAIN_SPEC}, "
        f"{SIGNIFICANCE_LEVEL:.0%} significance level",
        bullet_list(interpretation),
    ]
    report = "\n\n".join(sections) + "\n"
    (OUTPUT_DIR / "main_results.md").write_text(report, encoding="utf-8")
    return report
