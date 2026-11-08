"""Checks on the linear predictions behind the decomposition (Sections 3.5 and 4.2).

Specification (2), weights `wgt`. P is the Stage 1 prediction (reported
contact), Q the Stage 2 prediction (sending given contact); L is less than
monthly, g is weekly or monthly.

(a) Share of fitted values below 0 on each stage's estimation sample, and
    the number above 1 (expected to be zero).
(b) Stage 2 extended to the full sample with everyone's frequency set to L:
    share of predictions below 0.
(c) Product-based joint difference with the individual full-sample
    predictions truncated to [0, 1] before multiplying and averaging,
        mean_w[ P_i(g) Q_i(g) ] - mean_w[ P_i(L) Q_i(L) ],
    next to the untruncated difference, which equals the product difference
    of joint_decomposition.py (the module checks this identity).
(d) Interaction term b1 b2 of the decomposition and the range of the
    contact margin: b1 Qbar_L when the interaction is assigned entirely to
    the sending margin, b1 (Qbar_L + b2) when it is assigned entirely to the
    contact margin.
(e) Qbar_L, the Stage 2 prediction with frequency set to L, averaged over
    the full sample (as in joint_decomposition.py) and over the contacted
    sample (the midterm version).

Input:  common sample from DataClean_Pipeline.build_sample
Output: Output/analysis/decomposition_checks.csv  (quantity, contrast, value)
Paper:  Sections 3.5 and 4.2

Run from the project root, as part of run_pipeline.py or alone:
    python -m Analysis_Pipeline.decomposition_checks
"""

import numpy as np
import pandas as pd

from Analysis_Pipeline.paper_targets import compare, comparison_table, print_comparison
from DataClean_Pipeline.build_sample import PROJECT_ROOT, build_common_sample, load_raw
from Model_Pipeline.lpm import WEIGHT, fit_lpm
from Model_Pipeline.stages import MAIN_SPEC, OUTCOME, SPECS, STAGES

OUTPUT_DIR = PROJECT_ROOT / "Output" / "analysis"
TITLE = "Sections 3.5 and 4.2, decomposition checks (decomposition_checks.py)"

CONTRASTS = {"weekly": (1.0, 0.0), "monthly": (0.0, 1.0)}
TOLERANCE = 1e-10

# Numbers written in the paper, in percent or percentage points.
NEGATIVE_FITTED_TARGETS = {"stage1_contact": 1.1, "stage2_send": 5.2, "stage3_joint": 11.2}
NEGATIVE_Q_L_FULL_SAMPLE_TARGET = 12.5
PRODUCT_TARGETS = {          # contrast -> (truncated, untruncated)
    "weekly": (0.92, 0.95),
    "monthly": (0.93, 0.98),
}
INTERACTION_TARGET = 0.09
CONTACT_RANGE_TARGETS = {    # contrast -> (interaction to sending, interaction to contact)
    "weekly": (0.43, 0.52),
    "monthly": (0.29, 0.38),
}
Q_L_TARGETS = {"full sample": 8.08, "contacted sample": 7.64}


def predict(fit, sample, weekly, monthly):
    """Prediction with everyone's frequency set to (weekly, monthly)."""
    return np.asarray(fit.predict(sample.assign(weekly=weekly, monthly=monthly)))


def fitted_value_checks(fits):
    """(a) for the three stages."""
    rows = []
    for key, fit in fits.items():
        fitted = np.asarray(fit.fittedvalues)
        rows.append({"quantity": "fitted values below 0, share", "contrast": key,
                     "value": float(np.mean(fitted < 0))})
        rows.append({"quantity": "fitted values above 1, count", "contrast": key,
                     "value": int(np.sum(fitted > 1))})
        rows.append({"quantity": "largest fitted value", "contrast": key,
                     "value": float(fitted.max())})
    return rows


def product_difference(P_g, Q_g, P_L, Q_L, weights, truncate):
    if truncate:
        P_g, Q_g, P_L, Q_L = [np.clip(x, 0, 1) for x in (P_g, Q_g, P_L, Q_L)]
    return float(np.average(P_g * Q_g, weights=weights) - np.average(P_L * Q_L, weights=weights))


def check_rows(common, stage2, fits):
    """(b) to (e). Everything is averaged over the full sample unless the row says otherwise."""
    fit1, fit2 = fits["stage1_contact"], fits["stage2_send"]
    weights = common[WEIGHT].to_numpy(dtype=float)
    P_L, Q_L = predict(fit1, common, 0.0, 0.0), predict(fit2, common, 0.0, 0.0)
    Pbar_L, Qbar_L = np.average(P_L, weights=weights), np.average(Q_L, weights=weights)
    Qbar_L_contacted = np.average(predict(fit2, stage2, 0.0, 0.0), weights=stage2[WEIGHT])

    rows = [
        {"quantity": "Stage 2 prediction at L below 0, share (full sample)", "contrast": "",
         "value": float(np.mean(Q_L < 0))},
        {"quantity": "Qbar_L, full sample", "contrast": "", "value": float(Qbar_L)},
        {"quantity": "Qbar_L, contacted sample", "contrast": "", "value": float(Qbar_L_contacted)},
    ]
    for contrast, (weekly, monthly) in CONTRASTS.items():
        P_g, Q_g = predict(fit1, common, weekly, monthly), predict(fit2, common, weekly, monthly)
        b1, b2 = fit1.params[contrast], fit2.params[contrast]
        untruncated = product_difference(P_g, Q_g, P_L, Q_L, weights, truncate=False)
        truncated = product_difference(P_g, Q_g, P_L, Q_L, weights, truncate=True)

        # Without truncation the mean of the products equals the decomposition formula.
        formula = b1 * (Qbar_L + b2 / 2) + b2 * (Pbar_L + b1 / 2)
        if abs(untruncated - formula) > TOLERANCE:
            raise RuntimeError(f"{contrast}: product difference {untruncated} differs from "
                               f"the decomposition formula {formula}")

        rows += [
            {"quantity": "product difference, untruncated", "contrast": contrast, "value": untruncated},
            {"quantity": "product difference, predictions truncated to [0,1]",
             "contrast": contrast, "value": truncated},
            {"quantity": "interaction b1 b2", "contrast": contrast, "value": float(b1 * b2)},
            {"quantity": "contact margin, interaction assigned to sending: b1 Qbar_L",
             "contrast": contrast, "value": float(b1 * Qbar_L)},
            {"quantity": "contact margin, interaction assigned to contact: b1 (Qbar_L + b2)",
             "contrast": contrast, "value": float(b1 * (Qbar_L + b2))},
        ]
    return rows


def comparison(table):
    def value(quantity, contrast=""):
        match = (table["quantity"] == quantity) & (table["contrast"] == contrast)
        return table.loc[match, "value"].iloc[0]

    rows = []
    for key, target in NEGATIVE_FITTED_TARGETS.items():
        rows.append(compare(f"{key}: fitted values below 0 (%)",
                            100 * value("fitted values below 0, share", key), target))
        rows.append(compare(f"{key}: fitted values above 1 (count)",
                            int(value("fitted values above 1, count", key)), 0))
    rows.append(compare("Stage 2 prediction at L below 0, full sample (%)",
                        100 * value("Stage 2 prediction at L below 0, share (full sample)"),
                        NEGATIVE_Q_L_FULL_SAMPLE_TARGET))
    for contrast, (truncated, untruncated) in PRODUCT_TARGETS.items():
        rows.append(compare(f"Product difference, truncated, {contrast} (pp)",
                            100 * value("product difference, predictions truncated to [0,1]", contrast),
                            truncated))
        rows.append(compare(f"Product difference, untruncated, {contrast} (pp)",
                            100 * value("product difference, untruncated", contrast), untruncated))
    for contrast, (to_sending, to_contact) in CONTACT_RANGE_TARGETS.items():
        rows.append(compare(f"Interaction b1 b2, {contrast} (pp)",
                            100 * value("interaction b1 b2", contrast), INTERACTION_TARGET))
        rows.append(compare(f"Contact margin, interaction to sending, {contrast} (pp)",
                            100 * value("contact margin, interaction assigned to sending: b1 Qbar_L",
                                        contrast), to_sending))
        rows.append(compare(f"Contact margin, interaction to contact, {contrast} (pp)",
                            100 * value("contact margin, interaction assigned to contact: b1 (Qbar_L + b2)",
                                        contrast), to_contact))
    for sample, target in Q_L_TARGETS.items():
        rows.append(compare(f"Qbar_L, {sample} (%)", 100 * value(f"Qbar_L, {sample}"), target))
    return comparison_table(rows)


def run(common):
    """Write the CSV and return the comparison with the paper."""
    samples = {stage.key: stage.build_sample(common) for stage in STAGES}
    fits = {key: fit_lpm(sample, OUTCOME, SPECS[MAIN_SPEC]) for key, sample in samples.items()}

    table = pd.DataFrame(fitted_value_checks(fits) + check_rows(common, samples["stage2_send"], fits))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUTPUT_DIR / "decomposition_checks.csv", index=False)
    return comparison(table)


def main():
    common, _ = build_common_sample(load_raw())
    print_comparison(TITLE, run(common))


if __name__ == "__main__":
    main()
