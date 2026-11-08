"""Figure 2: predicted probabilities by stage.

Three panels, one per stage, specification (2). Each panel shows P_W, P_M, P_L
with 95% confidence intervals and the weekly - less than monthly difference
b_W with its p-value. The Stage 2 panel also shows the minimum detectable
difference from joint_decomposition.py.

A predicted probability is a weighted average of the model's prediction with
every respondent's frequency set to one level. Because the model is linear,
it is a linear combination of the coefficients, so its confidence interval
comes from the same t-test as the coefficients.

The numbers are checked against Output/<stage>/summary.csv (specification (2)).

Outputs: Output/analysis/figure2_predicted_probabilities.{png,pdf},
         Output/analysis/figure2_predicted_probabilities.csv,
         Figure 2 section appended to Output/analysis/figure_notes.md

Run from the project root, as part of run_analysis.py or alone (after
figure1_between_within.py and joint_decomposition.py, whose outputs it reads):
    python -m Analysis_Pipeline.figure2_predicted_probabilities
"""

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

from DataClean_Pipeline.build_sample import build_common_sample, load_raw
from Model_Pipeline.lpm import COUNTRY, WEIGHT, fit_lpm, linear_combination, predicted_probability
from Model_Pipeline.report import format_p
from Model_Pipeline.results import FREQUENCY_LEVELS
from Model_Pipeline.stages import MAIN_SPEC, OUTCOME, SPECS, STAGES

matplotlib.use("Agg")

OUTPUT_DIR = PROJECT_ROOT / "Output" / "analysis"
FIGURE_STEM = "figure2_predicted_probabilities"
DECOMPOSITION_PATH = OUTPUT_DIR / "joint_decomposition.csv"
NOTES_PATH = OUTPUT_DIR / "figure_notes.md"

# Same validated palette as Figure 1 (slots 1-3 pass all-pairs checks).
COLORS = {"P_weekly": "#2a78d6", "P_monthly": "#eb6834", "P_less_than_monthly": "#1baf7a"}
LABELS = {"P_weekly": "Weekly", "P_monthly": "Monthly", "P_less_than_monthly": "Less than\nmonthly"}
GRAY = "#52514e"

PANEL_TITLES = {
    "stage1_contact": "Stage 1: reported scam contact",
    "stage2_send": "Stage 2: sent money",
    "stage3_joint": "Stage 3: contact and sent money",
}

plt.rcParams.update({
    "font.size": 13,
    "axes.labelsize": 14,
    "axes.titlesize": 14,
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": "#e3e3e0",
    "grid.linewidth": 0.8,
    "axes.axisbelow": True,
    "pdf.fonttype": 42,
})


def predicted_with_ci(fit, sample, weekly, monthly):
    """Predicted probability as a linear combination of the coefficients, with 95% CI.

    The combination is the weighted mean of the design rows with the frequency
    dummies set to the counterfactual values; nothing else in the design changes.
    """
    exog = pd.DataFrame(fit.model.exog, columns=fit.model.exog_names)
    weights = np.asarray(sample[WEIGHT])
    row = pd.Series(np.average(exog, axis=0, weights=weights), index=exog.columns)
    row["weekly"] = weekly
    row["monthly"] = monthly

    result = linear_combination(fit, row.values)
    check = predicted_probability(fit, sample, weekly, monthly)
    if abs(result["estimate"] - check) > 1e-10:
        raise ValueError("Linear-combination prediction does not match predicted_probability.")
    return result


def estimate_panel(stage, common):
    sample = stage.build_sample(common)
    fit = fit_lpm(sample, OUTCOME, SPECS[MAIN_SPEC])
    rows = []
    for name, (weekly, monthly) in FREQUENCY_LEVELS.items():
        rows.append({"stage": stage.key, "quantity": name,
                     **predicted_with_ci(fit, sample, weekly, monthly)})
    rows.append({"stage": stage.key, "quantity": "beta_W", **linear_combination(fit, "weekly")})
    table = pd.DataFrame(rows)
    table["N"] = len(sample)
    table["economies"] = sample[COUNTRY].nunique()
    return table


def check_against_main_results(table):
    """Point estimates must equal specification (2) in Output/<stage>/summary.csv."""
    for stage_key, rows in table.groupby("stage"):
        summary = pd.read_csv(PROJECT_ROOT / "Output" / stage_key / "summary.csv")
        summary = summary[summary["spec"] == MAIN_SPEC].set_index("quantity")
        for _, row in rows.iterrows():
            reference = summary.loc[row["quantity"]]
            columns = ["estimate"] if row["quantity"].startswith("P_") else ["estimate", "ci_low", "ci_high", "p_value"]
            for column in columns:
                if abs(row[column] - reference[column]) > 1e-9:
                    raise ValueError(f"{stage_key} {row['quantity']} {column}: "
                                     f"{row[column]} vs main results {reference[column]}")


def stage2_mdd():
    """Minimum detectable difference for weekly vs less than monthly, from joint_decomposition.py."""
    decomposition = pd.read_csv(DECOMPOSITION_PATH).set_index("contrast")
    return decomposition.loc["weekly - less than monthly", "stage2_mdd"]


def draw_panel(ax, stage_key, rows, mdd=None):
    probabilities = rows[rows["quantity"].str.startswith("P_")]
    beta = rows[rows["quantity"] == "beta_W"].iloc[0]

    for i, (_, row) in enumerate(probabilities.iterrows()):
        value, low, high = 100 * row["estimate"], 100 * row["ci_low"], 100 * row["ci_high"]
        color = COLORS[row["quantity"]]
        ax.errorbar(i, value, yerr=[[value - low], [high - value]], fmt="o", color=color,
                    markersize=10, capsize=6, linewidth=2, markeredgecolor="white")
        ax.text(i + 0.13, value, f"{value:.1f}", ha="left", va="center", fontsize=12, color=GRAY)

    ax.set_xlim(-0.5, 2.6)
    ax.set_xticks(range(3), [LABELS[q] for q in probabilities["quantity"]])
    ax.set_ylim(bottom=0)
    ax.grid(axis="x", visible=False)
    ax.set_title(PANEL_TITLES[stage_key], loc="left", fontweight="bold")

    annotation = (f"b_W (weekly $-$ less than monthly)\n"
                  f"{100 * beta['estimate']:+.2f} pp, {format_p(beta['p_value'])}")
    if mdd is not None:
        annotation = ("Conditional on reported contact\n" + annotation +
                      f"\nMinimum detectable difference\n(80% power): {100 * mdd:.2f} pp")
    ax.text(0.03, 0.03, annotation, transform=ax.transAxes, ha="left", va="bottom",
            fontsize=11.5, color=GRAY, linespacing=1.4)


def make_figure(table, mdd):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.4))
    for ax, stage, letter in zip(axes, STAGES, "ABC"):
        rows = table[table["stage"] == stage.key]
        draw_panel(ax, stage.key, rows, mdd if stage.key == "stage2_send" else None)
        ax.text(-0.12, 1.06, letter, transform=ax.transAxes, fontsize=16,
                fontweight="bold", va="bottom")
    axes[0].set_ylabel("Predicted probability (%)")
    # Leave room above the points so the annotation box does not cover them.
    for ax in axes:
        ax.set_ylim(0, ax.get_ylim()[1] * 1.15)
    fig.tight_layout(w_pad=2.5)
    fig.savefig(OUTPUT_DIR / f"{FIGURE_STEM}.png", dpi=300)
    fig.savefig(OUTPUT_DIR / f"{FIGURE_STEM}.pdf")
    plt.close(fig)


def figure_notes(table, mdd):
    def cell(stage_key, quantity):
        row = table[(table["stage"] == stage_key) & (table["quantity"] == quantity)].iloc[0]
        return f"{100 * row['estimate']:.2f} [{100 * row['ci_low']:.2f}, {100 * row['ci_high']:.2f}]"

    def beta(stage_key):
        row = table[(table["stage"] == stage_key) & (table["quantity"] == "beta_W")].iloc[0]
        return (f"{100 * row['estimate']:+.2f} [{100 * row['ci_low']:+.2f}, "
                f"{100 * row['ci_high']:+.2f}], {format_p(row['p_value'])}")

    n = {s.key: int(table[table["stage"] == s.key]["N"].iloc[0]) for s in STAGES}
    header = "| | Stage 1: contact | Stage 2: sent money, given contact | Stage 3: contact and sent money |"
    lines = [header, "|---|---|---|---|",
             "| N | " + " | ".join(f"{n[s.key]:,}" for s in STAGES) + " |"]
    for quantity, label in [("P_weekly", "P_W: weekly"), ("P_monthly", "P_M: monthly"),
                            ("P_less_than_monthly", "P_L: less than monthly")]:
        lines.append(f"| {label} (%) [95% CI] | " + " | ".join(cell(s.key, quantity) for s in STAGES) + " |")
    lines.append("| b_W = P_W - P_L (pp) [95% CI] | " + " | ".join(beta(s.key) for s in STAGES) + " |")

    return f"""
# Figure 2. Predicted probabilities by payment frequency, three stages

Files: `figure2_predicted_probabilities.png` (300 dpi), `figure2_predicted_probabilities.pdf`, data in `figure2_predicted_probabilities.csv`.

**Caption.** Each panel shows the predicted probability of the stage outcome if every respondent
paid in store at the given frequency, with all other characteristics at their observed values,
from specification (2): weighted LPM (`wgt`), country fixed effects, demographic controls (age, age
squared, female, education, income quintile, labor force, rural), standard errors clustered by
economy (t distribution, 74 degrees of freedom), 95% confidence intervals. Panel A: reported scam
contact, common sample (N = {n['stage1_contact']:,}). Panel B: sent money, conditional on reported
contact (N = {n['stage2_send']:,}); the minimum detectable difference is the smallest true weekly minus
less-than-monthly difference this sample would detect with 80% power at the 5% level,
{100 * mdd:.2f} percentage points, about half of the less-than-monthly rate. Panel C: contacted and
sent money, one joint outcome (N = {n['stage3_joint']:,}). b_W is the weekly minus less-than-monthly
difference, equal to the coefficient on the weekly dummy. All numbers equal specification (2) in
`Output/main_results.md`.

**Reading.** Weekly payers are more likely to report scam contact (Panel A, b_W = {beta('stage1_contact')})
and more likely to report contact and sending money (Panel C, b_W = {beta('stage3_joint')}).
Conditional on contact, the sending rate is higher in point estimate for weekly and monthly payers
but the difference is not significant (Panel B, b_W = {beta('stage2_send')}), and the sample could
only detect a difference of about {100 * mdd:.1f} points, so Panel B neither supports nor rules out
a sending-margin effect.

**Numbers.**

{chr(10).join(lines)}
"""


def update_notes(section):
    """Replace the Figure 2 section of figure_notes.md, keeping the Figure 1 section."""
    marker = "\n# Figure 2."
    existing = NOTES_PATH.read_text(encoding="utf-8") if NOTES_PATH.exists() else ""
    if marker in existing:
        existing = existing[:existing.index(marker)]
    NOTES_PATH.write_text(existing.rstrip("\n") + "\n" + section, encoding="utf-8")


def main():
    common, _ = build_common_sample(load_raw())
    table = pd.concat([estimate_panel(stage, common) for stage in STAGES], ignore_index=True)
    check_against_main_results(table)
    mdd = stage2_mdd()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUTPUT_DIR / f"{FIGURE_STEM}.csv", index=False)
    make_figure(table, mdd)
    update_notes(figure_notes(table, mdd))

    pd.set_option("display.width", 200)
    print(table.to_string(index=False))
    print(f"\nStage 2 minimum detectable difference (from joint_decomposition.py): {100 * mdd:.2f} pp")
    print("All point estimates, CIs and p-values match specification (2) in Output/<stage>/summary.csv")
    print(f"Figure and notes written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
