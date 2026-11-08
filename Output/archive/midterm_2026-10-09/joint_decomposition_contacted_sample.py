"""Step 3 for the 9 October meeting: decompose the joint difference.

Specification (2) only. P_g is the Stage 1 predicted probability (contact),
Q_g the Stage 2 predicted probability (sending, conditional on contact),
g in {weekly, monthly, less than monthly}. For g versus less than monthly (L):

    dJ = P_g * Q_g - P_L * Q_L
       = (P_g - P_L) * (Q_g + Q_L) / 2      contact margin
       + (Q_g - Q_L) * (P_g + P_L) / 2      sending margin

The direct Stage 3 estimate (coefficient on g in the joint-outcome LPM) is
reported next to it. The table also gives the minimum detectable difference
of Stage 2 (80% power, 5% two-sided) relative to the baseline sending rate Q_L.

Outputs: Output/oct9/joint_decomposition.{csv,md}

Run from the project root:
    .venv/bin/python Oct9/step3_joint_decomposition.py
"""

import sys
from pathlib import Path

import pandas as pd
from scipy import stats

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from DataClean_Pipeline.build_sample import build_common_sample, load_raw
from Model_Pipeline.lpm import COUNTRY, fit_lpm, linear_combination, predicted_probability
from Model_Pipeline.results import FREQUENCY_LEVELS
from Model_Pipeline.stages import MAIN_SPEC, OUTCOME, SPECS, stage1_contact, stage2_send, stage3_joint

OUTPUT_DIR = PROJECT_ROOT / "Output" / "oct9"

CONTRASTS = {
    "weekly - less than monthly": ("P_weekly", "weekly"),
    "monthly - less than monthly": ("P_monthly", "monthly"),
}
REFERENCE = "P_less_than_monthly"
POWER = 0.80
ALPHA = 0.05


def predicted_by_frequency(sample):
    """(fit, {P_weekly, P_monthly, P_less_than_monthly}) in specification (2)."""
    fit = fit_lpm(sample, OUTCOME, SPECS[MAIN_SPEC])
    probabilities = {name: predicted_probability(fit, sample, weekly, monthly)
                     for name, (weekly, monthly) in FREQUENCY_LEVELS.items()}
    return fit, probabilities


def minimum_detectable_difference(se, df):
    """Smallest true difference detected with the given power at a two-sided test.

    MDD = (t_{1 - alpha/2} + t_{power}) * SE, t distribution with df degrees of freedom.
    """
    return (stats.t.ppf(1 - ALPHA / 2, df) + stats.t.ppf(POWER, df)) * se


def decomposition_table(stage1_fit, P, stage2_fit, Q, stage3_fit, df):
    rows = []
    for contrast, (level, dummy) in CONTRASTS.items():
        p_g, p_l = P[level], P[REFERENCE]
        q_g, q_l = Q[level], Q[REFERENCE]

        contact_margin = (p_g - p_l) * (q_g + q_l) / 2
        sending_margin = (q_g - q_l) * (p_g + p_l) / 2
        product_difference = p_g * q_g - p_l * q_l

        direct = linear_combination(stage3_fit, dummy)
        stage2 = linear_combination(stage2_fit, dummy)
        mdd = minimum_detectable_difference(stage2["se"], df)

        rows.append({
            "contrast": contrast,
            "P_g": p_g, "P_L": p_l, "Q_g": q_g, "Q_L": q_l,
            "product_difference": product_difference,
            "contact_margin": contact_margin,
            "sending_margin": sending_margin,
            "share_from_contact": contact_margin / product_difference,
            "direct_stage3_estimate": direct["estimate"],
            "direct_ci_low": direct["ci_low"],
            "direct_ci_high": direct["ci_high"],
            "direct_p": direct["p_value"],
            "stage2_estimate": stage2["estimate"],
            "stage2_se": stage2["se"],
            "stage2_mdd": mdd,
            "baseline_sending_rate_Q_L": q_l,
            "mdd_over_baseline": mdd / q_l,
        })
    return pd.DataFrame(rows)


def pct(value):
    return f"{100 * value:.2f}"


def signed(value):
    return f"{100 * value:+.2f}"


def markdown_report(table, n1, n2, n3, n_economies):
    header = ["", "Weekly vs less than monthly", "Monthly vs less than monthly"]
    lines = ["| " + " | ".join(header) + " |", "|---|---|---|"]

    def row(label, cells):
        lines.append("| " + " | ".join([label] + cells) + " |")

    w, m = table.iloc[0], table.iloc[1]
    row("**Predicted probabilities (%)**", ["", ""])
    row("P_g: contact, group g", [pct(w["P_g"]), pct(m["P_g"])])
    row("P_L: contact, less than monthly", [pct(w["P_L"]), pct(m["P_L"])])
    row("Q_g: sending given contact, group g", [pct(w["Q_g"]), pct(m["Q_g"])])
    row("Q_L: sending given contact, less than monthly", [pct(w["Q_L"]), pct(m["Q_L"])])
    row("**Joint difference (percentage points)**", ["", ""])
    row("Product-based difference, P_g Q_g - P_L Q_L",
        [signed(w["product_difference"]), signed(m["product_difference"])])
    row("Contact margin, (P_g - P_L)(Q_g + Q_L)/2",
        [signed(w["contact_margin"]), signed(m["contact_margin"])])
    row("Sending margin, (Q_g - Q_L)(P_g + P_L)/2",
        [signed(w["sending_margin"]), signed(m["sending_margin"])])
    row("Share from the contact margin",
        [f"{100 * w['share_from_contact']:.0f}%", f"{100 * m['share_from_contact']:.0f}%"])
    row("Direct Stage 3 estimate [95% CI]",
        [f"{signed(r['direct_stage3_estimate'])} [{signed(r['direct_ci_low'])}, "
         f"{signed(r['direct_ci_high'])}], p = {r['direct_p']:.3f}" for r in (w, m)])
    row("**Power of Stage 2 (percentage points)**", ["", ""])
    row("Stage 2 estimate, Q_g - Q_L (SE)",
        [f"{signed(r['stage2_estimate'])} ({pct(r['stage2_se'])})" for r in (w, m)])
    row(f"Minimum detectable difference ({POWER:.0%} power, {ALPHA:.0%} two-sided)",
        [pct(w["stage2_mdd"]), pct(m["stage2_mdd"])])
    row("Baseline sending rate, Q_L", [pct(w["Q_L"]), pct(m["Q_L"])])
    row("Minimum detectable difference / baseline",
        [f"{w['mdd_over_baseline']:.2f}", f"{m['mdd_over_baseline']:.2f}"])

    notes = (
        f"Notes. All quantities from specification (2): weighted LPM (`wgt`), country fixed "
        f"effects, demographic controls, standard errors clustered by economy "
        f"({n_economies} economies, t distribution with {n_economies - 1} degrees of freedom). "
        f"P_g is the Stage 1 predicted probability of reported scam contact (N = {n1:,}), "
        f"Q_g the Stage 2 predicted probability of sending money among contacted respondents "
        f"(N = {n2:,}); each sets every respondent's payment frequency to g and averages the "
        f"prediction with `wgt`. The product-based difference equals the contact margin plus the "
        f"sending margin exactly. The direct Stage 3 estimate is the coefficient on g in the LPM "
        f"for the joint outcome (contacted and sent money, N = {n3:,}). The minimum detectable "
        f"difference is (t_{{0.975}} + t_{{0.80}}) times the clustered standard error of the "
        f"Stage 2 coefficient, which is the smallest true difference in conditional sending that "
        f"the Stage 2 sample would detect with 80% power at the 5% level."
    )
    why = (
        "Why the product-based and direct estimates differ. The product multiplies two "
        "sample-average probabilities, but the joint outcome for a respondent is the product of "
        "that respondent's own contact and sending probabilities, and the average of a product is "
        "not the product of averages when the two vary together across people within a frequency "
        "group. Q_g is also estimated on the contacted subsample with its own country effects and "
        "controls, while the direct estimate fits one linear model to the joint outcome on the "
        "full sample, so the two use different weights and a slightly different sample "
        f"(N = {n3:,} versus {n1:,}). The gap is within the Stage 3 confidence interval."
    )
    return "\n".join([
        "# Decomposition of the joint difference into the contact and sending margins",
        "", "\n".join(lines), "", notes, "", why,
    ]) + "\n"


def main():
    common, _ = build_common_sample(load_raw())
    stage1 = stage1_contact(common)
    stage2 = stage2_send(common)
    stage3 = stage3_joint(common)
    n_economies = common[COUNTRY].nunique()

    stage1_fit, P = predicted_by_frequency(stage1)
    stage2_fit, Q = predicted_by_frequency(stage2)
    stage3_fit = fit_lpm(stage3, OUTCOME, SPECS[MAIN_SPEC])

    table = decomposition_table(stage1_fit, P, stage2_fit, Q, stage3_fit, n_economies - 1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUTPUT_DIR / "joint_decomposition.csv", index=False)
    report = markdown_report(table, len(stage1), len(stage2), len(stage3), n_economies)
    (OUTPUT_DIR / "joint_decomposition.md").write_text(report, encoding="utf-8")

    pd.set_option("display.width", 250)
    print(table.T.to_string())
    print(f"\nResults written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
