"""Decomposition of the joint difference into the contact and sending margins.

Specification (2), g = weekly or monthly versus less than monthly (L).
For respondent i the joint probability is P_i(g) * Q_i(g), with P from
Stage 1 (reported contact) and Q from Stage 2 (sending money given contact).
Specification (2) has no interaction terms, so P_i(g) - P_i(L) = b1_g and
Q_i(g) - Q_i(L) = b2_g for every respondent, and averaging the identity
P_i(g) Q_i(g) - P_i(L) Q_i(L) over the full sample gives exactly

    product difference = contact margin + sending margin
    contact margin     = b1_g * (Qbar_L + b2_g / 2)
    sending margin     = b2_g * (Pbar_L + b1_g / 2)

Pbar_L and Qbar_L are the Stage 1 and Stage 2 predictions with everyone's
frequency set to L, averaged with `wgt` over the SAME full sample (the Stage 1
sample, N = 16,251). Stage 2 is still estimated on contacted respondents; its
prediction is extended to everyone. The midterm version averaged Q over the
contacted subsample only; that value is reported for reference.

Inference. b1 and b2 come from different samples but the same 75 economies,
so their covariance is estimated jointly: for each economy the cluster scores
of the two regressions are stacked, and the CRV1 formula is applied to the
stacked scores. Each margin is a smooth function of (b1, b2), so the delta
method gives its standard error; intervals use t(74). A second interval comes
from an unrestricted wild cluster bootstrap (Rademacher, one draw per economy
applied to both regressions, percentile-t). The share of the contact margin is
a ratio whose denominator can be close to zero, so it is reported without an
interval.

Also reported: the direct Stage 3 estimate and the minimum detectable
difference of Stage 2 (80% power, 5% two-sided).

Outputs: Output/analysis/joint_decomposition.{csv,md}

Run from the project root, as part of run_analysis.py or alone:
    python -m Analysis_Pipeline.joint_decomposition
"""

from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from DataClean_Pipeline.build_sample import build_common_sample, load_raw
from Model_Pipeline.lpm import COUNTRY, WEIGHT, fit_lpm, linear_combination
from Model_Pipeline.stages import MAIN_SPEC, OUTCOME, SPECS, stage1_contact, stage2_send, stage3_joint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "Output" / "analysis"

CONTRASTS = {"weekly - less than monthly": "weekly", "monthly - less than monthly": "monthly"}
MARGINS = ["contact_margin", "sending_margin", "product_difference"]

B = 9999                # bootstrap draws
SEED = 20261026         # same seed as Robustness_Pipeline/wild_cluster_bootstrap.py
POWER = 0.80
ALPHA = 0.05
TOLERANCE = 1e-8        # largest gap to statsmodels accepted in the self-check


# ---------------------------------------------------------------------------
# Pieces of each regression, taken from the statsmodels fit
# ---------------------------------------------------------------------------

def regression_parts(fit, sample):
    """What the delta method and the bootstrap need from one fitted regression.

    WLS with weights w equals OLS after multiplying every row by sqrt(w), so
    X and the residuals u are in sqrt(wgt) units. P = (X'X)^-1 X' gives the
    coefficients as P @ y. H is the G x N indicator of each respondent's economy.
    """
    root_w = np.sqrt(np.asarray(fit.model.weights, dtype=float))
    X = np.asarray(fit.model.exog) * root_w[:, None]
    N, K = X.shape
    clusters = sample[COUNTRY].astype("category").cat.codes.to_numpy()
    G = clusters.max() + 1
    H = (np.arange(G)[:, None] == clusters[None, :]).astype(float)
    return {
        "names": list(fit.model.exog_names),
        "beta": fit.params.to_numpy(),
        "X": X,
        "P": np.linalg.pinv(X),
        "u": np.asarray(fit.wresid),
        "H": H,
        "correction": G / (G - 1) * (N - 1) / (N - K),   # CRV1, as statsmodels
    }


def cluster_scores(parts, residuals):
    """K x G matrix: for each economy, the sum over its respondents of P[:, i] * u_i.

    The coefficient error b - beta equals the row sums of this matrix, and the
    CRV1 covariance is correction * (scores @ scores.T).
    """
    return (parts["P"] * residuals[None, :]) @ parts["H"].T


def check_against_statsmodels(parts, fit):
    """Coefficients are the fit's own; the standard errors must match fit.bse."""
    scores = cluster_scores(parts, parts["u"])
    se = np.sqrt(parts["correction"] * (scores ** 2).sum(axis=1))
    gap = np.abs(se - fit.bse.to_numpy()).max()
    if gap > TOLERANCE:
        raise RuntimeError(f"Cluster SE differs from statsmodels by {gap:.2e}")


def mean_design_row(fit, sample):
    """Weighted mean of the design rows with weekly = monthly = 0 (frequency set to L)."""
    X = np.asarray(fit.model.exog).copy()
    names = list(fit.model.exog_names)
    X[:, names.index("weekly")] = 0
    X[:, names.index("monthly")] = 0
    return np.average(X, axis=0, weights=sample[WEIGHT].to_numpy(dtype=float))


# ---------------------------------------------------------------------------
# The margins and their gradients
# ---------------------------------------------------------------------------

def margins(b1, b2, xbar_L, names, group):
    """Margins for one contrast and their gradients with respect to the stacked (b1, b2).

    Pbar_L = xbar_L @ b1 and Qbar_L = xbar_L @ b2 are linear in the
    coefficients, so each margin is a product of two linear functions and
    its gradient follows from the product rule.
    """
    K = len(names)
    e = np.zeros(K)
    e[names.index(group)] = 1
    b1_g, b2_g = b1 @ e, b2 @ e
    P_L, Q_L = xbar_L @ b1, xbar_L @ b2

    contact = b1_g * (Q_L + b2_g / 2)
    sending = b2_g * (P_L + b1_g / 2)
    grad_contact = np.concatenate([(Q_L + b2_g / 2) * e, b1_g * (xbar_L + e / 2)])
    grad_sending = np.concatenate([b2_g * (xbar_L + e / 2), (P_L + b1_g / 2) * e])

    estimates = {"contact_margin": contact, "sending_margin": sending,
                 "product_difference": contact + sending}
    gradients = {"contact_margin": grad_contact, "sending_margin": grad_sending,
                 "product_difference": grad_contact + grad_sending}
    return estimates, gradients


def delta_se(gradient, V):
    return float(np.sqrt(gradient @ V @ gradient))


# ---------------------------------------------------------------------------
# Wild cluster bootstrap (unrestricted, percentile-t)
# ---------------------------------------------------------------------------

def bootstrap_t(parts1, parts2, xbar_L, names, group, estimates, rng):
    """t statistics of the three margins in B wild cluster bootstrap draws.

    Each draw multiplies the residuals of every respondent in economy g by the
    same v_g = +1 or -1 in both regressions. The bootstrap coefficients are
    b + P @ (v * u); the bootstrap residuals are (v * u) - X @ (b* - b). The
    t statistic is (margin* - margin) / SE*, with SE* the delta-method
    standard error computed from the bootstrap residuals of that draw.
    """
    G = parts1["H"].shape[0]
    K = len(names)
    t_stats = {name: np.empty(B) for name in MARGINS}

    for draw in range(B):
        v = rng.choice([-1.0, 1.0], size=G)
        boot = []
        for parts in (parts1, parts2):
            v_u = parts["u"] * (v @ parts["H"])            # v_g of each respondent's economy
            shift = parts["P"] @ v_u                       # b* - b
            residuals = v_u - parts["X"] @ shift
            boot.append((parts["beta"] + shift, residuals))
        (b1_star, u1_star), (b2_star, u2_star) = boot

        star, gradients = margins(b1_star, b2_star, xbar_L, names, group)
        for name in MARGINS:
            g1, g2 = gradients[name][:K], gradients[name][K:]
            # Cluster contributions to the variance of the margin, both regressions stacked.
            a1 = np.sqrt(parts1["correction"]) * parts1["H"] @ ((g1 @ parts1["P"]) * u1_star)
            a2 = np.sqrt(parts2["correction"]) * parts2["H"] @ ((g2 @ parts2["P"]) * u2_star)
            se_star = np.sqrt(((a1 + a2) ** 2).sum())
            t_stats[name][draw] = (star[name] - estimates[name]) / se_star
    return t_stats


# ---------------------------------------------------------------------------
# Table
# ---------------------------------------------------------------------------

def minimum_detectable_difference(se, df):
    """(t_{1 - alpha/2} + t_{power}) * SE: smallest true difference detected with the given power."""
    return (stats.t.ppf(1 - ALPHA / 2, df) + stats.t.ppf(POWER, df)) * se


def decomposition_row(contrast, group, parts1, parts2, V, xbar_L, Q_L_contacted,
                      fit2, fit3, df, rng):
    names = parts1["names"]
    estimates, gradients = margins(parts1["beta"], parts2["beta"], xbar_L, names, group)
    t_boot = bootstrap_t(parts1, parts2, xbar_L, names, group, estimates, rng)
    t_crit = stats.t.ppf(1 - ALPHA / 2, df)

    row = {"contrast": contrast,
           "P_L": xbar_L @ parts1["beta"],
           "Q_L": xbar_L @ parts2["beta"],
           "Q_L_contacted_sample": Q_L_contacted,
           "b1": parts1["beta"][names.index(group)],
           "b2": parts2["beta"][names.index(group)]}
    row["P_g"] = row["P_L"] + row["b1"]
    row["Q_g"] = row["Q_L"] + row["b2"]

    for name in MARGINS:
        estimate = estimates[name]
        se = delta_se(gradients[name], V)
        t = estimate / se
        q_low, q_high = np.quantile(t_boot[name], [ALPHA / 2, 1 - ALPHA / 2])
        row[name] = estimate
        row[f"{name}_se"] = se
        row[f"{name}_ci_low"] = estimate - t_crit * se
        row[f"{name}_ci_high"] = estimate + t_crit * se
        row[f"{name}_p"] = 2 * stats.t.sf(abs(t), df)
        row[f"{name}_wcb_ci_low"] = estimate - q_high * se      # percentile-t
        row[f"{name}_wcb_ci_high"] = estimate - q_low * se
        row[f"{name}_wcb_p"] = float(np.mean(np.abs(t_boot[name]) >= abs(t)))
    row["share_from_contact"] = row["contact_margin"] / row["product_difference"]

    direct = linear_combination(fit3, group)
    stage2 = linear_combination(fit2, group)
    mdd = minimum_detectable_difference(stage2["se"], df)
    row.update({
        "direct_stage3_estimate": direct["estimate"],
        "direct_ci_low": direct["ci_low"],
        "direct_ci_high": direct["ci_high"],
        "direct_p": direct["p_value"],
        "stage2_estimate": stage2["estimate"],
        "stage2_se": stage2["se"],
        "stage2_mdd": mdd,
        "baseline_sending_rate_Q_L": row["Q_L"],
        "mdd_over_baseline": mdd / row["Q_L"],
    })
    return row


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def pct(value):
    return f"{100 * value:.2f}"


def signed(value):
    return f"{100 * value:+.2f}"


def interval(row, name, prefix=""):
    return f"[{signed(row[f'{name}_{prefix}ci_low'])}, {signed(row[f'{name}_{prefix}ci_high'])}]"


def format_p(p):
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


def markdown_report(table, n1, n2, n3, n_economies):
    w, m = table.iloc[0], table.iloc[1]
    lines = ["|  | Weekly vs less than monthly | Monthly vs less than monthly |", "|---|---|---|"]

    def row(label, cells):
        lines.append("| " + " | ".join([label] + list(cells)) + " |")

    def both(f):
        return [f(w), f(m)]

    row("**Predicted probabilities, full sample (%)**", ["", ""])
    row("P_g: contact, group g", both(lambda r: pct(r["P_g"])))
    row("P_L: contact, less than monthly", both(lambda r: pct(r["P_L"])))
    row("Q_g: sending given contact, group g", both(lambda r: pct(r["Q_g"])))
    row("Q_L: sending given contact, less than monthly", both(lambda r: pct(r["Q_L"])))
    row("Q_L averaged over contacted respondents only (midterm version)",
        both(lambda r: pct(r["Q_L_contacted_sample"])))
    row("**Joint difference (percentage points), 95% CI, p**", ["", ""])
    for name, label in [("contact_margin", "Contact margin, b1 (Q_L + b2/2)"),
                        ("sending_margin", "Sending margin, b2 (P_L + b1/2)"),
                        ("product_difference", "Product-based difference, contact + sending")]:
        row(label, both(lambda r: f"{signed(r[name])} ({pct(r[f'{name}_se'])})"))
        row(f"&nbsp;&nbsp;delta method, t({n_economies - 1})",
            both(lambda r: f"{interval(r, name)}, {format_p(r[f'{name}_p'])}"))
        row("&nbsp;&nbsp;wild cluster bootstrap, percentile-t",
            both(lambda r: f"{interval(r, name, 'wcb_')}, {format_p(r[f'{name}_wcb_p'])}"))
    row("Share from the contact margin (point estimate)",
        both(lambda r: f"{100 * r['share_from_contact']:.0f}%"))
    row("Direct Stage 3 estimate [95% CI]",
        both(lambda r: f"{signed(r['direct_stage3_estimate'])} {interval(r, 'direct')}, "
                       f"{format_p(r['direct_p'])}"))
    row("**Power of Stage 2 (percentage points)**", ["", ""])
    row("Stage 2 estimate, b2 (SE)", both(lambda r: f"{signed(r['stage2_estimate'])} ({pct(r['stage2_se'])})"))
    row(f"Minimum detectable difference ({POWER:.0%} power, {ALPHA:.0%} two-sided)",
        both(lambda r: pct(r["stage2_mdd"])))
    row("Minimum detectable difference / Q_L", both(lambda r: f"{r['mdd_over_baseline']:.2f}"))

    notes = (
        f"Notes. Specification (2): weighted LPM (`wgt`), country fixed effects, demographic "
        f"controls, standard errors clustered by economy ({n_economies} economies). b1 is the "
        f"coefficient on g in Stage 1 (reported contact, N = {n1:,}), b2 the coefficient on g in "
        f"Stage 2 (sending money among contacted respondents, N = {n2:,}). P_L and Q_L set every "
        f"respondent's payment frequency to less than monthly and average the Stage 1 and Stage 2 "
        f"predictions with `wgt` over the same full sample (N = {n1:,}); P_g = P_L + b1 and "
        f"Q_g = Q_L + b2 because the specification has no interaction terms. With these averages "
        f"the product-based difference P_g Q_g - P_L Q_L equals the contact margin plus the sending "
        f"margin exactly. The midterm table averaged Q over the contacted subsample (N = {n2:,}), "
        f"which is not the population the product refers to; that value is shown for reference. "
        f"Standard errors in parentheses are from the delta method with the joint cluster "
        f"covariance of (b1, b2): the economy-level scores of the two regressions are stacked, so "
        f"the covariance between the two coefficient vectors is estimated rather than assumed zero. "
        f"The wild cluster bootstrap is unrestricted: in each of B = {B:,} draws every economy "
        f"receives one Rademacher weight that multiplies its residuals in both regressions; the "
        f"interval is percentile-t and the p-value is the share of draws with |t*| at least |t|. "
        f"Seed {SEED}. The share from the contact margin is a ratio whose denominator is itself "
        f"uncertain, so no interval is reported for it. The direct Stage 3 estimate is the "
        f"coefficient on g in the LPM for the joint outcome (contacted and sent money, N = {n3:,}). "
        f"The minimum detectable difference is (t_{{0.975}} + t_{{0.80}}) times the clustered "
        f"standard error of b2."
    )
    why = (
        "Why the product-based and direct estimates differ. Both are estimated on the same "
        "population now, so the remaining gap is functional form: the direct estimate fits one "
        "linear model to the joint outcome, while the product of two linear models is quadratic in "
        "the covariates. The two intervals overlap almost entirely."
    )
    return "\n".join([
        "# Decomposition of the joint difference into the contact and sending margins",
        "", "\n".join(lines), "", notes, "", why,
    ]) + "\n"


# ---------------------------------------------------------------------------

def main():
    common, _ = build_common_sample(load_raw())
    stage1, stage2, stage3 = stage1_contact(common), stage2_send(common), stage3_joint(common)
    n_economies = common[COUNTRY].nunique()
    df = n_economies - 1

    fit1 = fit_lpm(stage1, OUTCOME, SPECS[MAIN_SPEC])
    fit2 = fit_lpm(stage2, OUTCOME, SPECS[MAIN_SPEC])
    fit3 = fit_lpm(stage3, OUTCOME, SPECS[MAIN_SPEC])
    parts1, parts2 = regression_parts(fit1, stage1), regression_parts(fit2, stage2)
    check_against_statsmodels(parts1, fit1)
    check_against_statsmodels(parts2, fit2)
    if parts1["names"] != parts2["names"]:
        raise RuntimeError("Stage 1 and Stage 2 must have the same regressors and economies")

    # Joint CRV1 covariance of (b1, b2) from the stacked economy-level scores.
    scores = np.vstack([np.sqrt(parts1["correction"]) * cluster_scores(parts1, parts1["u"]),
                        np.sqrt(parts2["correction"]) * cluster_scores(parts2, parts2["u"])])
    V = scores @ scores.T

    xbar_L = mean_design_row(fit1, stage1)                      # full sample
    Q_L_contacted = mean_design_row(fit2, stage2) @ parts2["beta"]  # midterm version, for reference

    rng = np.random.default_rng(SEED)
    rows = [decomposition_row(contrast, group, parts1, parts2, V, xbar_L, Q_L_contacted,
                              fit2, fit3, df, rng)
            for contrast, group in CONTRASTS.items()]
    table = pd.DataFrame(rows)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUTPUT_DIR / "joint_decomposition.csv", index=False)
    report = markdown_report(table, len(stage1), len(stage2), len(stage3), n_economies)
    (OUTPUT_DIR / "joint_decomposition.md").write_text(report, encoding="utf-8")

    print(report)
    print(f"Results written to {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
