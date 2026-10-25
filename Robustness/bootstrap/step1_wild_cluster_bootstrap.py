"""Step 1 of the robustness checks: wild cluster bootstrap for specification (2).

The main results cluster standard errors by economy and read p-values from
the t distribution with 74 degrees of freedom (75 economies). This script
computes a second p-value for the same tests with the restricted wild cluster
bootstrap (WCR), which does not rely on that t distribution. Six tests, each
of H0: b = 0: the weekly and the monthly coefficient in Stages 1, 2 and 3.

Sample, outcome, regressors, weights and clusters are those of fit_lpm:
weighted LPM (`wgt`), specification (2), one dummy per economy, standard
errors clustered by economy.

The script also runs four checks and prints them:
0. The matrix code below reproduces fit_lpm (statsmodels) and the saved
   Output/<stage>/coefficients.csv within 1e-8. Otherwise it stops.
1. B = 999 next to B = 9999.
2. A second seed (12345) next to the main seed (20261026).
3. The wildboottest package on the same sqrt(wgt)-transformed OLS model.

Outputs: Output/bootstrap/wild_cluster_bootstrap_2026-10-26.{csv,md}
         Output/bootstrap/wild_cluster_bootstrap_stage3_weekly_2026-10-26.png

Run from the project root:
    .venv/bin/python Robustness/bootstrap/step1_wild_cluster_bootstrap.py
"""

import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats
from wildboottest.wildboottest import wildboottest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from DataClean_Pipeline.build_sample import build_common_sample, load_raw
from Model_Pipeline.lpm import COUNTRY, WEIGHT, fit_lpm
from Model_Pipeline.stages import MAIN_SPEC, OUTCOME, SPECS, stage1_contact, stage2_send, stage3_joint

matplotlib.use("Agg")

OUTPUT_DIR = PROJECT_ROOT / "Output" / "bootstrap"
DATE = "2026-10-26"

# (folder name under Output/, label for the report, function that builds the sample)
STAGE_SAMPLES = [
    ("stage1_contact", "Stage 1: reported contact", stage1_contact),
    ("stage2_send", "Stage 2: sending money given contact", stage2_send),
    ("stage3_joint", "Stage 3: contact and sending money", stage3_joint),
]
TESTED = ["weekly", "monthly"]

B_MAIN = 9999
B_QUICK = 999
SEED_MAIN = 20261026
SEED_CHECK = 12345
TOLERANCE = 1e-8    # largest gap to statsmodels accepted in check 0
BATCH = 500         # bootstrap draws per matrix product, to limit memory use

FIGURE_STAGE = "stage3_joint"
FIGURE_VARIABLE = "weekly"
FIGURE_NAME = f"wild_cluster_bootstrap_stage3_weekly_{DATE}.png"

# Same colors as the Oct9 figures (validated with the dataviz palette checker).
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
})


# ---------------------------------------------------------------------------
# Regression by matrix algebra
# ---------------------------------------------------------------------------

def weighted_design(sample, x_cols):
    """Outcome and design matrix of the weighted LPM, multiplied by sqrt(wgt).

    WLS with weights w gives the same coefficients as OLS after every row is
    multiplied by sqrt(w). So the outcome, the constant, the regressors and the
    country dummies are all multiplied by sqrt(wgt). After that, plain OLS
    formulas apply, and the residuals are the weighted residuals that
    statsmodels uses for clustered standard errors.

    Columns as in fit_lpm: a constant, the regressors, and one dummy for each
    economy except the first in alphabetical order (the constant covers it).
    Column names follow statsmodels, so check 0 can match every coefficient
    by name.

    Returns (y, X as a DataFrame, cluster number of each respondent).
    """
    root_w = np.sqrt(sample[WEIGHT].to_numpy(dtype=float))
    economies = sorted(sample[COUNTRY].unique())

    columns = {"Intercept": np.ones(len(sample))}
    for x in x_cols:
        columns[x] = sample[x].to_numpy(dtype=float)
    for code in economies[1:]:
        columns[f"C({COUNTRY})[T.{code}]"] = (sample[COUNTRY] == code).to_numpy(dtype=float)

    X = pd.DataFrame(columns).mul(root_w, axis=0)
    y = sample[OUTCOME].to_numpy(dtype=float) * root_w

    # Economies numbered 0 to G-1 in alphabetical order, as in fit_lpm.
    clusters = sample[COUNTRY].astype("category").cat.codes.to_numpy()
    return y, X, clusters


def cluster_matrix(clusters):
    """G x N matrix with a 1 where respondent i belongs to economy g, else 0.

    Multiplying a column of N numbers by it gives the G economy totals.
    """
    G = clusters.max() + 1
    return (np.arange(G)[:, None] == clusters[None, :]).astype(float)


def small_sample_correction(N, K, G):
    """CRV1 factor G/(G-1) * (N-1)/(N-K), the same as statsmodels and Stata use.

    K counts every column of X, the country dummies included, as in fit_lpm.
    """
    return G / (G - 1) * (N - 1) / (N - K)


def cluster_se(p_row, residuals, H, correction):
    """CRV1 cluster-robust standard error of one coefficient.

    p_row is the coefficient's row of (X'X)^-1 X', so the coefficient equals
    p_row @ y. Its clustered variance is
        correction * sum over economies g of (sum over i in g of p_row[i] * u[i])^2,
    which is its diagonal element of (X'X)^-1 [sum_g X_g' u_g u_g' X_g] (X'X)^-1.

    residuals has one column per sample (the original data, or one column per
    bootstrap draw); the result has one standard error per column.
    """
    scores = H @ (p_row[:, None] * residuals)    # G x number of columns
    return np.sqrt(correction * (scores ** 2).sum(axis=0))


def fit_full_model(y, X, H):
    """Coefficients, CRV1 standard errors, t and p of the full model.

    Also returns P = (X'X)^-1 X'. X is the same in every bootstrap draw, so P
    is computed once here and reused for all draws.
    """
    N, K = X.shape
    G = H.shape[0]
    correction = small_sample_correction(N, K, G)

    # pinv(X) equals (X'X)^-1 X' when X has full column rank (fit_lpm checks
    # the rank). statsmodels solves least squares the same way.
    P = np.linalg.pinv(X)
    beta = P @ y
    residuals = y - X @ beta

    se = np.array([cluster_se(P[k], residuals[:, None], H, correction)[0] for k in range(K)])
    t = beta / se
    # Two-sided p-value from the t distribution with G - 1 = 74 degrees of freedom.
    p = 2 * stats.t.sf(np.abs(t), G - 1)
    return {"P": P, "beta": beta, "se": se, "t": t, "p": p, "correction": correction}


def fit_restricted_model(y, X, k):
    """The model under H0: b_k = 0, which is the model without column k.

    Every other regressor, the country dummies and the weights stay in.
    Returns (fitted values, residuals, coefficients), in sqrt(wgt) units.
    """
    X_r = np.delete(X, k, axis=1)
    beta_r = np.linalg.pinv(X_r) @ y
    fitted_r = X_r @ beta_r
    return fitted_r, y - fitted_r, beta_r


# ---------------------------------------------------------------------------
# Wild cluster bootstrap
# ---------------------------------------------------------------------------

def bootstrap_t(X, P, H, clusters, k, fitted_r, residuals_r, correction, B, seed):
    """t statistics of coefficient k in B restricted wild cluster bootstrap samples.

    Each draw builds y* = restricted fitted values + v_g * restricted residuals,
    with v_g = +1 or -1 for economy g, re-estimates the full model on y*, and
    computes the CRV1 t statistic of coefficient k.
    """
    G = H.shape[0]

    # Rademacher weights: +1 or -1, each with probability 1/2, one per economy
    # and draw. All B draws are made at once, so the result does not depend
    # on BATCH.
    rng = np.random.default_rng(seed)
    weights = rng.choice([-1, 1], size=(G, B))

    t_boot = np.empty(B)
    for start in range(0, B, BATCH):
        v = weights[:, start:start + BATCH]    # G x b

        # v[clusters] gives each respondent the weight of their economy, so
        # all residuals of one economy keep or flip their sign together. This
        # keeps the correlation of errors within an economy.
        y_star = fitted_r[:, None] + v[clusters] * residuals_r[:, None]    # N x b

        # Full model on every bootstrap outcome: one matrix product with P.
        beta_star = P @ y_star                     # K x b
        residuals_star = y_star - X @ beta_star    # N x b
        se_star = cluster_se(P[k], residuals_star, H, correction)

        # The bootstrap data were built with b_k = 0, so the t statistic is
        # measured from 0, the value under H0.
        t_boot[start:start + BATCH] = (beta_star[k] - 0) / se_star
    return t_boot


def bootstrap_p(t_boot, t_original):
    """Two-sided p-value: share of draws with |t*| at least as large as |t|."""
    return np.mean(np.abs(t_boot) >= abs(t_original))


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def stop_if_too_large(gaps, what):
    for label, gap in gaps.items():
        if not gap < TOLERANCE:
            raise ValueError(f"{what}: {label} differs by {gap:.2e}, more than {TOLERANCE:.0e}.")


def check_full_model(sample, x_cols, names, full):
    """Check 0: every coefficient, SE, t and p of the full model against fit_lpm.

    Returns the largest absolute gap of each quantity.
    """
    fit = fit_lpm(sample, OUTCOME, x_cols)
    gaps = {
        "gap_coefficient": np.max(np.abs(full["beta"] - fit.params[names].to_numpy())),
        "gap_cluster_se": np.max(np.abs(full["se"] - fit.bse[names].to_numpy())),
        "gap_t": np.max(np.abs(full["t"] - fit.tvalues[names].to_numpy())),
        "gap_p": np.max(np.abs(full["p"] - fit.pvalues[names].to_numpy())),
    }
    stop_if_too_large(gaps, "full model vs fit_lpm")
    return gaps


def check_restricted_model(sample, x_cols, variable, names_r, beta_r):
    """Check 0: restricted coefficients against fit_lpm without the tested variable."""
    fit = fit_lpm(sample, OUTCOME, [x for x in x_cols if x != variable])
    gaps = {"gap_restricted_coefficient": np.max(np.abs(beta_r - fit.params[names_r].to_numpy()))}
    stop_if_too_large(gaps, f"restricted model without {variable} vs fit_lpm")
    return gaps


def check_saved_coefficients(stage_key, variable, full, k):
    """Check 0: against specification (2) in Output/<stage>/coefficients.csv."""
    saved = pd.read_csv(PROJECT_ROOT / "Output" / stage_key / "coefficients.csv")
    row = saved[(saved["spec"] == MAIN_SPEC) & (saved["variable"] == variable)].iloc[0]
    gaps = {
        "gap_saved_estimate": abs(full["beta"][k] - row["estimate"]),
        "gap_saved_se": abs(full["se"][k] - row["se"]),
        "gap_saved_t": abs(full["t"][k] - row["t"]),
        "gap_saved_p": abs(full["p"][k] - row["p_value"]),
    }
    stop_if_too_large(gaps, f"{stage_key} {variable} vs coefficients.csv")
    return gaps


def wildboottest_package(y, X, clusters, variable, B, seed):
    """Check 3: (t, p) from the wildboottest package on the same OLS model.

    The package takes an unfitted statsmodels OLS model and ignores regression
    weights, so it gets the sqrt(wgt)-transformed y and X, which is the same
    model. bootstrap_type "11" with impose_null=True is WCR with CRV1 standard
    errors and both small-sample factors. The package counts draws with
    |t*| > |t| (strictly greater), this script |t*| >= |t|.
    """
    model = sm.OLS(y, X)
    result = wildboottest(model, B=B, cluster=clusters, param=variable,
                          weights_type="rademacher", impose_null=True,
                          bootstrap_type="11", seed=seed, show=False)
    return float(result.loc[variable, "statistic"]), float(result.loc[variable, "p-value"])


# ---------------------------------------------------------------------------
# One stage
# ---------------------------------------------------------------------------

def analyse_stage(stage_key, build_sample, common):
    """Check 0 and the bootstrap for the weekly and monthly coefficients of one stage.

    Returns (result rows, check rows, main bootstrap t statistics by variable).
    """
    sample = build_sample(common)
    x_cols = SPECS[MAIN_SPEC]
    y, X_frame, clusters = weighted_design(sample, x_cols)
    names = list(X_frame.columns)
    X = X_frame.to_numpy()
    H = cluster_matrix(clusters)

    full = fit_full_model(y, X, H)
    gaps_full = check_full_model(sample, x_cols, names, full)

    results, checks, t_boot_by_variable = [], [], {}
    for variable in TESTED:
        k = names.index(variable)
        gaps_saved = check_saved_coefficients(stage_key, variable, full, k)

        fitted_r, residuals_r, beta_r = fit_restricted_model(y, X, k)
        names_r = [name for name in names if name != variable]
        gaps_restricted = check_restricted_model(sample, x_cols, variable, names_r, beta_r)

        t_quick = bootstrap_t(X, full["P"], H, clusters, k, fitted_r, residuals_r,
                              full["correction"], B_QUICK, SEED_MAIN)
        t_main = bootstrap_t(X, full["P"], H, clusters, k, fitted_r, residuals_r,
                             full["correction"], B_MAIN, SEED_MAIN)
        t_other_seed = bootstrap_t(X, full["P"], H, clusters, k, fitted_r, residuals_r,
                                   full["correction"], B_MAIN, SEED_CHECK)
        t_package, p_package = wildboottest_package(y, X_frame, clusters, variable,
                                                    B_MAIN, SEED_MAIN)

        t_original = full["t"][k]
        p_main = bootstrap_p(t_main, t_original)
        results.append({
            "stage": stage_key,
            "variable": variable,
            "N": len(sample),
            "economies": H.shape[0],
            "events": int(sample[OUTCOME].sum()),
            "estimate": full["beta"][k],
            "cluster_se": full["se"][k],
            "t": t_original,
            "p_cluster_t74": full["p"][k],
            "p_wild_bootstrap": p_main,
            "B": B_MAIN,
            "seed": SEED_MAIN,
        })
        checks.append({
            "stage": stage_key,
            "variable": variable,
            **gaps_full,
            **gaps_saved,
            **gaps_restricted,
            "p_B999": bootstrap_p(t_quick, t_original),
            "p_B9999": p_main,
            "p_B9999_seed12345": bootstrap_p(t_other_seed, t_original),
            "p_wildboottest": p_package,
            "gap_t_wildboottest": abs(t_package - t_original),
        })
        t_boot_by_variable[variable] = t_main
    return results, checks, t_boot_by_variable


# ---------------------------------------------------------------------------
# Outputs
# ---------------------------------------------------------------------------

def format_p(p):
    return "< 0.0001" if p < 0.0001 else f"{p:.4f}"


def markdown_report(results):
    labels = {key: label for key, label, _ in STAGE_SAMPLES}
    lines = [
        "| Stage | Coefficient | N | Economies | Events | Estimate (pp) | Cluster SE (pp) "
        "| t | p, cluster t(74) | p, wild bootstrap |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for _, r in results.iterrows():
        cells = [
            labels[r["stage"]], f"b_{r['variable'][0].upper()} ({r['variable']})",
            f"{r['N']:,}", f"{r['economies']}", f"{r['events']:,}",
            f"{100 * r['estimate']:+.2f}", f"{100 * r['cluster_se']:.2f}", f"{r['t']:.2f}",
            format_p(r["p_cluster_t74"]), format_p(r["p_wild_bootstrap"]),
        ]
        lines.append("| " + " | ".join(cells) + " |")

    n_params = 1 + len(SPECS[MAIN_SPEC]) + (results["economies"].iloc[0] - 1)
    notes = (
        "Notes. Specification (2): linear probability model weighted by `wgt`, with one dummy "
        "per economy and the demographic controls; reference group: pays less than monthly. "
        "Each row tests H0: b = 0. Events is the number of respondents with outcome 1. "
        "Estimate, cluster SE and t equal the main results; p, cluster t(74) uses CRV1 standard "
        "errors clustered by economy and the t distribution with G - 1 = 74 degrees of freedom. "
        "p, wild bootstrap is from the restricted wild cluster bootstrap (WCR; Cameron, Gelbach "
        "and Miller 2008). (i) The model is re-estimated without the tested regressor, keeping "
        "all other regressors, the country dummies and the weights, so the bootstrap data "
        "satisfy H0. (ii) In each of B = 9,999 draws every economy receives one Rademacher "
        "weight (+1 or -1, each with probability 1/2), and all restricted residuals of that "
        "economy are multiplied by it. (iii) The bootstrap outcome is the restricted fitted "
        "value plus the weighted residual; the full model is re-estimated on it. (iv) The CRV1 "
        "t statistic of the tested coefficient is computed as for the original estimate, "
        "measured from the null value 0. The p-value is the share of draws with "
        "|t*| >= |t|, and it does not use the t(74) distribution; a bootstrap p-value shown as "
        "< 0.0001 means that none of the 9,999 draws had |t*| >= |t|. The economy is both the "
        f"cluster and the unit that receives a bootstrap weight ({results['economies'].iloc[0]} "
        "economies in every stage). The weights `wgt` enter by multiplying the outcome and "
        "every column of the design matrix, including the constant and the country dummies, "
        "by sqrt(wgt), which turns weighted least squares into ordinary least squares. The "
        "CRV1 variance includes the factor G/(G - 1) x (N - 1)/(N - K), with K = "
        f"{n_params} parameters including the country dummies; the factor scales the original "
        "and every bootstrap t statistic by the same constant, so it does not change the "
        f"bootstrap p-value. Random seed {SEED_MAIN}, set before each test, so all six tests "
        "use the same matrix of Rademacher weights. The simulation standard error of a "
        "bootstrap p-value is sqrt(p(1 - p)/B), at most 0.005 with B = 9,999."
    )
    return "\n".join([
        "# Wild cluster bootstrap p-values for the frequency coefficients, specification (2)",
        "", "\n".join(lines), "", notes,
    ]) + "\n"


def bootstrap_histogram(t_boot, t_original, p_boot, df, path):
    """Histogram of the bootstrap t statistics with the original t marked.

    Bin edges fall exactly on -|t| and +|t|, so the bars beyond them are the
    draws counted in the p-value; they are drawn in orange. The t distribution
    with 74 degrees of freedom, used for the cluster-robust p-value, is shown
    for reference.
    """
    t_abs = abs(t_original)
    width = t_abs / 20
    n_bins_per_side = int(np.ceil(np.abs(t_boot).max() / width))
    edges = width * np.arange(-n_bins_per_side, n_bins_per_side + 1)

    inside = t_boot[np.abs(t_boot) < t_abs]
    outside = t_boot[np.abs(t_boot) >= t_abs]

    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.hist(inside, bins=edges, color=BLUE, edgecolor="white", linewidth=0.6,
            label="Bootstrap draws")
    ax.hist(outside, bins=edges, color=ORANGE, edgecolor="white", linewidth=0.6,
            label=f"|t*| ≥ |t|: {len(outside):,} of {len(t_boot):,} draws, p = {p_boot:.4f}")

    grid = np.linspace(edges[0], edges[-1], 400)
    ax.plot(grid, stats.t.pdf(grid, df) * len(t_boot) * width, color=GRAY, linewidth=1.6,
            label=f"t distribution, {df} df (scaled to the draws)")

    top = ax.get_ylim()[1]
    for x, text, align in [(t_abs, f" t = {t_original:.2f}", "left"),
                           (-t_abs, f"−{t_abs:.2f} ", "right")]:
        ax.axvline(x, color=GRAY, linewidth=1.2, linestyle="--")
        ax.text(x, top * 0.55, text, ha=align, va="center", fontsize=12, color=GRAY)

    ax.set_xlabel("Bootstrap t statistic of the weekly coefficient (H0: b_W = 0 imposed)")
    ax.set_ylabel("Number of draws")
    ax.set_title(f"Stage 3, weekly coefficient: restricted wild cluster bootstrap, "
                 f"B = {len(t_boot):,}", fontsize=14, loc="left")
    ax.legend(loc="upper left", fontsize=11, framealpha=1, edgecolor="none")
    ax.grid(axis="x", visible=False)
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)


def main():
    common, _ = build_common_sample(load_raw())

    results, checks = [], []
    for stage_key, _, build_sample in STAGE_SAMPLES:
        print(f"Running {stage_key} ...")
        stage_results, stage_checks, t_boot = analyse_stage(stage_key, build_sample, common)
        results += stage_results
        checks += stage_checks
        if stage_key == FIGURE_STAGE:
            figure_t_boot = t_boot[FIGURE_VARIABLE]
    results = pd.DataFrame(results)
    checks = pd.DataFrame(checks)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUTPUT_DIR / f"wild_cluster_bootstrap_{DATE}.csv", index=False)
    (OUTPUT_DIR / f"wild_cluster_bootstrap_{DATE}.md").write_text(
        markdown_report(results), encoding="utf-8")

    figure_row = results[(results["stage"] == FIGURE_STAGE)
                         & (results["variable"] == FIGURE_VARIABLE)].iloc[0]
    bootstrap_histogram(
        figure_t_boot, figure_row["t"], figure_row["p_wild_bootstrap"],
        figure_row["economies"] - 1, OUTPUT_DIR / FIGURE_NAME)

    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    print("\nResults")
    print(results.to_string(index=False))
    print("\nCheck 0: largest absolute gaps (full model and restricted model vs fit_lpm, "
          "tested coefficients vs coefficients.csv)")
    print(checks[["stage", "variable"] + [c for c in checks.columns if c.startswith("gap_")]]
          .to_string(index=False))
    print("\nChecks 1-3: bootstrap p-values")
    p_columns = ["p_B999", "p_B9999", "p_B9999_seed12345", "p_wildboottest"]
    print(checks[["stage", "variable"] + p_columns].to_string(index=False))
    print(f"\nResults written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
