"""Figure 1: between versus within economies.

Left panel: one point per economy. x = weighted share of weekly payers,
y = weighted joint-event rate, marker area proportional to sample size,
sample-size-weighted fit line, Pearson correlation across economies.

Right panel: weekly - less than monthly difference in the Stage 3 outcome,
(i) pooled with no country fixed effects and (ii) specification (2) with
country fixed effects. Both weighted by `wgt`, clustered by economy, 95% CI.

Input:  common sample from DataClean_Pipeline.build_sample
Output: Output/analysis/figure1_between_within.{png,pdf},
        Output/analysis/figure1_economy_level.csv, Output/analysis/figure_notes.md
Paper:  Figure 1

Run from the project root, as part of run_analysis.py or alone:
    python -m Analysis_Pipeline.figure1_between_within
"""

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

PROJECT_ROOT = Path(__file__).resolve().parents[1]

from DataClean_Pipeline.build_sample import FREQUENCY, build_common_sample, load_raw
from Model_Pipeline.lpm import COUNTRY, WEIGHT, fit_lpm, linear_combination
from Model_Pipeline.stages import MAIN_SPEC, OUTCOME, SPECS, stage3_joint

matplotlib.use("Agg")

OUTPUT_DIR = PROJECT_ROOT / "Output" / "analysis"
FIGURE_STEM = "figure1_between_within"

# Colorblind-safe pair (validated with the dataviz palette checker).
BLUE = "#2a78d6"
ORANGE = "#eb6834"
GRAY = "#52514e"

plt.rcParams.update({
    "font.size": 13,
    "axes.labelsize": 14,
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


def economy_level(sample):
    """Weighted weekly share and weighted joint-event rate by economy."""
    rows = []
    for code, group in sample.groupby(COUNTRY):
        w = group[WEIGHT]
        rows.append({
            "economycode": code,
            "n": len(group),
            "weekly_share": np.average(group["weekly"], weights=w),
            "joint_rate": np.average(group[OUTCOME], weights=w),
        })
    return pd.DataFrame(rows)


def tercile_rates(economies):
    """Mean joint rate in the bottom, middle and top tercile of the weekly share."""
    tercile = pd.qcut(economies["weekly_share"], 3, labels=["bottom", "middle", "top"])
    return economies.groupby(tercile, observed=True)["joint_rate"].mean()


def pooled_difference(sample):
    """Weekly - less than monthly with no country fixed effects.

    Same settings as Model_Pipeline.lpm.fit_lpm (weights, cluster by economy,
    t distribution) but without the economy dummies. The estimate equals the
    difference in weighted group means.
    """
    formula = f"{OUTCOME} ~ {' + '.join(FREQUENCY)}"
    model = smf.wls(formula, data=sample, weights=sample[WEIGHT])
    economy_codes = sample[COUNTRY].astype("category").cat.codes
    fit = model.fit(cov_type="cluster", cov_kwds={"groups": economy_codes}, use_t=True)
    return linear_combination(fit, "weekly")


def within_difference(sample):
    """Weekly - less than monthly in the main specification with country fixed effects."""
    fit = fit_lpm(sample, OUTCOME, SPECS[MAIN_SPEC])
    return linear_combination(fit, "weekly")


def draw_left(ax, economies):
    x = 100 * economies["weekly_share"]
    y = 100 * economies["joint_rate"]
    n = economies["n"]

    sizes = 600 * n / n.max() + 15
    ax.scatter(x, y, s=sizes, color=BLUE, alpha=0.55, edgecolor="white", linewidth=0.8)

    # Fit line weighted by sample size (polyfit weights multiply residuals, so sqrt).
    slope, intercept = np.polyfit(x, y, 1, w=np.sqrt(n))
    grid = np.linspace(0, 100, 50)
    ax.plot(grid, intercept + slope * grid, color=ORANGE, linewidth=2.2)

    r = np.corrcoef(x, y)[0, 1]
    ax.text(0.97, 0.95, f"r = {r:.2f} across {len(economies)} economies",
            transform=ax.transAxes, ha="right", va="top", fontsize=13, color=GRAY)

    # Reference marker sizes.
    for ref_n in [100, 500]:
        ax.scatter([], [], s=600 * ref_n / n.max() + 15, color=BLUE, alpha=0.55,
                   edgecolor="white", label=f"n = {ref_n}")
    ax.legend(title="Sample size", loc="upper left", frameon=False, fontsize=11,
              title_fontsize=11, labelspacing=1.4, borderpad=0.6)

    ax.set_xlim(0, 100)
    ax.set_ylim(bottom=0)
    ax.set_xlabel("Weekly payers in the economy (%, weighted)")
    ax.set_ylabel("Contacted and sent money (%, weighted)")
    return r


def draw_right(ax, pooled, within):
    estimates = [pooled, within]
    labels = ["Pooled\n(no country FE)", "Within economy\n(spec. (2), country FE)"]
    colors = [ORANGE, BLUE]

    ax.axhline(0, color=GRAY, linewidth=1.2, linestyle="--")
    for i, (est, color) in enumerate(zip(estimates, colors)):
        value = 100 * est["estimate"]
        low, high = 100 * est["ci_low"], 100 * est["ci_high"]
        ax.errorbar(i, value, yerr=[[value - low], [high - value]], fmt="o", color=color,
                    markersize=10, capsize=6, linewidth=2, markeredgecolor="white")
        ax.text(i + 0.1, value, f"{value:+.2f}\n[{low:+.2f}, {high:+.2f}]",
                ha="left", va="center", fontsize=12, color=GRAY)

    ax.set_xlim(-0.5, 1.7)
    ax.set_xticks([0, 1], labels)
    ax.set_ylabel("Weekly - less than monthly (percentage points)")
    ax.grid(axis="x", visible=False)


def make_figure(economies, pooled, within):
    fig, (ax_left, ax_right) = plt.subplots(
        1, 2, figsize=(13, 5.6), gridspec_kw={"width_ratios": [1.45, 1]})
    r = draw_left(ax_left, economies)
    draw_right(ax_right, pooled, within)
    for ax, letter in [(ax_left, "A"), (ax_right, "B")]:
        ax.text(-0.08, 1.04, letter, transform=ax.transAxes, fontsize=16,
                fontweight="bold", va="bottom")
    fig.tight_layout(w_pad=3)
    fig.savefig(OUTPUT_DIR / f"{FIGURE_STEM}.png", dpi=300)
    fig.savefig(OUTPUT_DIR / f"{FIGURE_STEM}.pdf")
    plt.close(fig)
    return r


def format_estimate(est):
    return (f"{100 * est['estimate']:+.2f} percentage points "
            f"[{100 * est['ci_low']:+.2f}, {100 * est['ci_high']:+.2f}], p = {est['p_value']:.3f}")


def write_notes(sample, economies, terciles, r, pooled, within):
    n_economies = sample[COUNTRY].nunique()
    text = f"""# Figure 1. Weekly in-store digital payment and scam losses: between versus within economies

Files: `figure1_between_within.png` (300 dpi), `figure1_between_within.pdf`, data in `figure1_economy_level.csv`.

**Caption.** Panel A plots the {n_economies} economies in the Stage 3 sample (N = {len(sample):,}).
The horizontal axis is the weighted share of respondents who pay in store by phone or card at least
weekly (`fin25e3` = 1); the vertical axis is the weighted share who report scam contact and sent
money (the Stage 3 outcome). Marker area is proportional to the economy's sample size. The line is a
least squares fit weighted by sample size. The Pearson correlation across economies (unweighted) is
r = {r:.2f}. Panel B shows the weekly minus less-than-monthly difference in the same outcome from two
weighted linear probability models with 95% confidence intervals: pooled across economies with no
country fixed effects, and specification (2) with country fixed effects and demographic controls
(age, age squared, female, education, income quintile, labor force, rural). Both use the Findex
sampling weight `wgt`; standard errors are clustered by economy (t distribution,
{n_economies - 1} degrees of freedom). The dashed line marks zero.

**Reading.** Across economies the association is negative: economies where more people pay weekly
have lower joint-event rates (mean joint rate {100 * terciles['top']:.1f}% in the top tercile of the
weekly share, {100 * terciles['bottom']:.1f}% in the bottom tercile). Pooling all respondents, weekly
payers have a lower joint rate than less-than-monthly payers ({format_estimate(pooled)}). Within an
economy the sign reverses: {format_estimate(within)}. The country fixed effects therefore carry the
between-economy pattern, and the within-economy comparison is the one the paper interprets.

**Numbers.**

| Quantity | Value |
|---|---|
| Economies / respondents | {n_economies} / {len(sample):,} |
| Correlation, weekly share vs joint rate (unweighted Pearson) | {r:.3f} |
| Mean joint rate, bottom tercile of weekly share | {100 * terciles['bottom']:.2f}% |
| Mean joint rate, middle tercile | {100 * terciles['middle']:.2f}% |
| Mean joint rate, top tercile | {100 * terciles['top']:.2f}% |
| Pooled difference, no country FE | {format_estimate(pooled)} |
| Within-economy difference, specification (2) | {format_estimate(within)} |
"""
    (OUTPUT_DIR / "figure_notes.md").write_text(text, encoding="utf-8")


def main():
    common, _ = build_common_sample(load_raw())
    sample = stage3_joint(common)

    economies = economy_level(sample)
    terciles = tercile_rates(economies)
    pooled = pooled_difference(sample)
    within = within_difference(sample)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    economies.to_csv(OUTPUT_DIR / "figure1_economy_level.csv", index=False)
    r = make_figure(economies, pooled, within)
    write_notes(sample, economies, terciles, r, pooled, within)

    print(f"Economies: {len(economies)}, N = {len(sample):,}")
    print(f"Correlation (unweighted): {r:.3f}")
    print("Mean joint rate by tercile of weekly share (%):")
    print((100 * terciles).round(2).to_string())
    print(f"Pooled, no FE:   {format_estimate(pooled)}")
    print(f"Spec (2), FE:    {format_estimate(within)}")
    print(f"Figure and notes written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
