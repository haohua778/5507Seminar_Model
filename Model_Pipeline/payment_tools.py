"""Task 7 supplement using the existing stages, WLS and inference functions."""

import pandas as pd

from DataClean_Pipeline.payment_tools import (
    PAYMENT_VARIABLE, age100_by_economy, age_audit, answer_audit, build_payment_samples,
)
from Model_Pipeline.results import estimate_stage
from Model_Pipeline.stages import MAIN_SPEC, OUTCOME, SPECS, STAGES

# Supplement definitions approved in this task; these are not definitions found
# in the upstream repository. Country FE/weights/clustering are supplied by lpm.py.
ABC = {"(1)": "A", "(2)": "B", "(3)": "C"}
VARIANTS = ("original", "same_sample", "fin25e1_added")


def supplemental_specs(specs=None):
    source = SPECS if specs is None else specs
    return {key: [*columns, PAYMENT_VARIABLE] for key, columns in source.items()}


def run_payment_analysis(raw, *, progress=print):
    """27 primary fits plus 9 age-100 sensitivity fits (main specification only)."""
    summaries, coefficients, flows, counts = [], [], [], []
    legacy_common, legacy_matched, _ = build_payment_samples(raw)
    scopes = {"raw": raw, "common": legacy_common, "fin25e1_complete": legacy_matched}
    for age_policy in ("legacy", "exclude_100"):
        common, matched, flow = build_payment_samples(raw, exclude_age100=age_policy == "exclude_100")
        flows.append(flow.assign(age_policy=age_policy))
        specs = SPECS if age_policy == "legacy" else {MAIN_SPEC: SPECS[MAIN_SPEC]}
        for stage in STAGES:
            original = stage.build_sample(common)
            comparison = stage.build_sample(matched)
            counts.append({
                "age_policy": age_policy, "stage": stage.key,
                "original_N": len(original), "matched_N": len(comparison),
                "excluded_fin25e1_N": len(original) - len(comparison),
                "original_events": int(original[OUTCOME].sum()),
                "matched_events": int(comparison[OUTCOME].sum()),
                "original_economies": original["economycode"].nunique(),
                "matched_economies": comparison["economycode"].nunique(),
            })
            for variant in VARIANTS:
                sample = original if variant == "original" else comparison
                predictors = supplemental_specs(specs) if variant == "fin25e1_added" else specs
                progress(f"{age_policy}: {stage.key}, {variant}, N={len(sample):,}")
                summary, coef = estimate_stage(sample, specifications=predictors)
                metadata = {"age_policy": age_policy, "stage": stage.key, "variant": variant,
                            "events": int(sample[OUTCOME].sum())}
                summaries.append(summary.assign(**metadata, equation=summary["spec"].map(ABC)))
                coefficients.append(coef.assign(**metadata, equation=coef["spec"].map(ABC),
                                                N=len(sample), economies=sample["economycode"].nunique()))
    return {
        "summary": pd.concat(summaries, ignore_index=True),
        "coefficients": pd.concat(coefficients, ignore_index=True),
        "sample_flow": pd.concat(flows, ignore_index=True),
        "sample_counts": pd.DataFrame(counts),
        "answer_audit": answer_audit(scopes),
        "age_audit": age_audit(scopes),
        "age_by_economy": age100_by_economy(scopes),
    }


def compare_variants(summary):
    """Separate changes due to sample exclusions from added fin25e1 adjustment.

    Differences of fitted coefficients are descriptive, not independent tests.
    """
    keys = ["age_policy", "stage", "spec", "equation", "quantity"]
    baseline = summary.loc[summary.variant.eq("original"), keys + ["estimate", "N"]]
    baseline = baseline.rename(columns={"estimate": "original_estimate", "N": "original_N"})
    matched = summary.loc[summary.variant.eq("same_sample"), keys + ["estimate", "N"]]
    matched = matched.rename(columns={"estimate": "same_sample_estimate", "N": "matched_N"})
    adjusted = summary.loc[summary.variant.eq("fin25e1_added"), keys + ["estimate", "se", "ci_low", "ci_high", "p_value", "N"]]
    adjusted = adjusted.rename(columns={"estimate": "adjusted_estimate", "N": "adjusted_N"})
    result = baseline.merge(matched, on=keys, validate="one_to_one").merge(adjusted, on=keys, validate="one_to_one")
    if not result["matched_N"].equals(result["adjusted_N"]):
        raise AssertionError("Baseline and adjusted models must use the same respondents.")
    result["sample_change_pp"] = 100 * (result.same_sample_estimate - result.original_estimate)
    result["adjustment_change_pp"] = 100 * (result.adjusted_estimate - result.same_sample_estimate)
    return result
