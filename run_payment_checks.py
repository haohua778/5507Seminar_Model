"""Validate Task 7 outputs, matched samples and independent WLS calculations."""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from DataClean_Pipeline.build_sample import DATA_PATH, PROJECT_ROOT, RAW_COLUMNS, build_common_sample
from DataClean_Pipeline.payment_tools import PAYMENT_VARIABLE, build_payment_samples, load_payment_raw
from Model_Pipeline.payment_tools import ABC, VARIANTS, compare_variants, supplemental_specs
from Model_Pipeline.report import OUTPUT_DIR
from Model_Pipeline.stages import MAIN_SPEC, SPECS, STAGES
from run_checks import TOLERANCE, design_matrix
from scipy import stats
from DataClean_Pipeline.payment_tools import answer_audit, age_audit, age100_by_economy
from run_payment_tools import sha256


def independent_tables(sample, columns):
    """Rebuild every reported value using NumPy, including full cluster covariance.

    Unlike checking two freshly fitted estimators, these tables are compared to
    the actual CSV artifacts. Country dummies replace the intercept here.
    """
    X = design_matrix(sample, columns).to_numpy(float)
    y = sample["outcome"].to_numpy(float)
    w = sample["wgt"].to_numpy(float)
    Xw = X * np.sqrt(w)[:, None]
    beta, _, rank, _ = np.linalg.lstsq(Xw, y * np.sqrt(w), rcond=None)
    if rank != X.shape[1]:
        raise ValueError("Independent check found a rank-deficient model.")
    bread = np.linalg.inv(Xw.T @ Xw)
    scores = pd.DataFrame(X * (w * (y - X @ beta))[:, None])
    grouped = scores.groupby(sample.economycode.to_numpy()).sum().to_numpy()
    n, k = X.shape
    g = sample.economycode.nunique()
    covariance = bread @ (grouped.T @ grouped) @ bread
    covariance *= g / (g - 1) * (n - 1) / (n - k)
    critical = stats.t.ppf(.975, g - 1)

    def contrast(vector):
        estimate = float(vector @ beta)
        se = float(np.sqrt(vector @ covariance @ vector))
        t = estimate / se
        return dict(estimate=estimate, se=se, ci_low=estimate-critical*se,
                    ci_high=estimate+critical*se, t=t,
                    p_value=float(2 * stats.t.sf(abs(t), g - 1)))

    weekly, monthly = columns.index("weekly"), columns.index("monthly")
    rows = []
    for quantity, w_value, m_value in [("P_weekly", 1., 0.), ("P_monthly", 0., 1.),
                                      ("P_less_than_monthly", 0., 0.)]:
        average = np.average(X, axis=0, weights=w)
        average[weekly], average[monthly] = w_value, m_value
        rows.append(dict(quantity=quantity, estimate=float(average @ beta)))
    for quantity, w_value, m_value in [("beta_W", 1., 0.), ("beta_M", 0., 1.),
                                      ("beta_W_minus_beta_M", 1., -1.)]:
        vector = np.zeros(k)
        vector[weekly], vector[monthly] = w_value, m_value
        rows.append(dict(quantity=quantity, **contrast(vector)))
    coefs = [dict(variable=name, **contrast(np.eye(k)[i])) for i, name in enumerate(columns)]
    return pd.DataFrame(rows), pd.DataFrame(coefs)


def table_matches(actual, expected, keys, values):
    """Compare keys AND numeric content, including NaN placement; fail closed."""
    if actual.duplicated(keys).any() or expected.duplicated(keys).any():
        return False, "duplicate keys"
    a = actual.set_index(keys).sort_index()
    b = expected.set_index(keys).sort_index()
    if not a.index.equals(b.index):
        return False, "different keys"
    left, right = a[values].to_numpy(float), b[values].to_numpy(float)
    same = np.allclose(left, right, atol=TOLERANCE, rtol=0, equal_nan=True)
    finite = np.isfinite(left) & np.isfinite(right)
    gap = np.max(np.abs(left[finite] - right[finite]), initial=0.)
    return same, f"max finite gap={gap:.2e}"


def validate(data_path, output_dir, main_output=None):
    # Never leave a stale passing record after a failed or interrupted recheck.
    (output_dir / "validation.csv").unlink(missing_ok=True)
    raw = load_payment_raw(data_path)
    summary = pd.read_csv(output_dir / "summary.csv")
    coefficients = pd.read_csv(output_dir / "coefficients.csv")
    manifest = json.loads((output_dir / "manifest.json").read_text())
    rows = []

    def record(name, passed, detail=""):
        rows.append({"check": name, "passed": bool(passed), "detail": str(detail)})
        print(f"{'pass' if passed else 'FAIL'} {name} {detail}", flush=True)

    record("input_hash", sha256(data_path) == manifest["data_sha256"])
    for relative, digest in manifest["code_sha256"].items():
        record(f"code_hash:{relative}", sha256(PROJECT_ROOT / relative) == digest)
    for relative, digest in manifest.get("output_sha256", {}).items():
        record(f"output_hash:{relative}", sha256(output_dir / relative) == digest)
    record("sources_hash", sha256(PROJECT_ROOT / "Docs/task7/sources.json") == manifest.get("source_manifest_sha256"))

    keys = ["age_policy", "stage", "variant", "spec"]
    required_quantities = {"P_weekly", "P_monthly", "P_less_than_monthly", "beta_W", "beta_M", "beta_W_minus_beta_M"}
    expected_models = {
        (policy, stage.key, variant, spec)
        for policy in ("legacy", "exclude_100") for stage in STAGES for variant in VARIANTS
        for spec in (SPECS if policy == "legacy" else [MAIN_SPEC])
    }
    actual_models = set(summary[keys].itertuples(index=False, name=None))
    record("all_36_models", actual_models == expected_models, f"models={len(actual_models)}")
    record("all_coefficient_models", set(coefficients[keys].itertuples(index=False, name=None)) == expected_models)
    record("unique_summary_rows", not summary.duplicated(keys + ["quantity"]).any())
    record("unique_coefficient_rows", not coefficients.duplicated(keys + ["variable"]).any())
    for model, part in summary.groupby(keys, sort=False):
        label = "/".join(model)
        record(f"six_outputs:{label}", set(part.quantity) == required_quantities and len(part) == 6)
        vals = part.set_index("quantity").estimate
        gap = max(abs(vals.P_weekly - vals.P_less_than_monthly - vals.beta_W),
                  abs(vals.P_monthly - vals.P_less_than_monthly - vals.beta_M),
                  abs(vals.beta_W - vals.beta_M - vals.beta_W_minus_beta_M))
        record(f"prediction_identity:{label}", gap < TOLERANCE, f"gap={gap:.2e}")
        differences = part.loc[part.quantity.str.startswith("beta")]
        finite = np.isfinite(differences[["estimate", "se", "ci_low", "ci_high", "p_value"]]).all().all()
        record(f"finite_inference:{label}", finite and differences.p_value.between(0, 1).all())

    core_common, _ = build_common_sample(raw[RAW_COLUMNS])
    common, _, _ = build_payment_samples(raw)
    pd.testing.assert_frame_equal(common[core_common.columns], core_common)
    record("same_core_common_sample", True, f"N={len(common)}")

    # A previous team's main tables are optional: they may use another input file.
    if main_output is not None:
        fields = ["estimate", "se", "ci_low", "ci_high", "t", "p_value", "N", "economies"]
        for stage in STAGES:
            expected = pd.read_csv(main_output / stage.key / "summary.csv")
            actual = summary.loc[(summary.age_policy == "legacy") & (summary.stage == stage.key)
                                 & (summary.variant == "original")]
            passed, detail = table_matches(actual, expected, ["spec", "quantity"], fields)
            record(f"main_baseline:{stage.key}", passed, detail)

    # Check actual saved values for ALL 36 models, not just a new fit's algorithm.
    expected_flows, expected_counts = [], []
    for policy in ("legacy", "exclude_100"):
        common, matched, flow = build_payment_samples(raw, exclude_age100=policy == "exclude_100")
        expected_flows.append(flow.assign(age_policy=policy))
        specs = SPECS if policy == "legacy" else {MAIN_SPEC: SPECS[MAIN_SPEC]}
        if policy == "exclude_100":
            record("age100_excluded", not common.age.eq(100).any())
            record("age99_retained", set(common.index[common.age.eq(99)]) == set(core_common.index[core_common.age.eq(99)]))
        for stage in STAGES:
            original = stage.build_sample(common)
            comparison = stage.build_sample(matched)
            intended = original.index[original.fin25e1.isin([1, 2])]
            record(f"matched_rows:{policy}/{stage.key}", comparison.index.equals(intended))
            expected_counts.append(dict(age_policy=policy, stage=stage.key,
                original_N=len(original), matched_N=len(comparison),
                excluded_fin25e1_N=len(original)-len(comparison),
                original_events=int(original.outcome.sum()), matched_events=int(comparison.outcome.sum()),
                original_economies=original.economycode.nunique(), matched_economies=comparison.economycode.nunique()))
            for variant in VARIANTS:
                sample = original if variant == "original" else comparison
                predictors = supplemental_specs(specs) if variant == "fin25e1_added" else specs
                for spec, columns in predictors.items():
                    label = f"{policy}/{stage.key}/{variant}/{ABC[spec]}"
                    expected_summary, expected_coef = independent_tables(sample, columns)
                    selected = summary.loc[(summary.age_policy == policy) & (summary.stage == stage.key)
                                           & (summary.variant == variant) & (summary.spec == spec)]
                    selected_coef = coefficients.loc[(coefficients.age_policy == policy) & (coefficients.stage == stage.key)
                                           & (coefficients.variant == variant) & (coefficients.spec == spec)]
                    values = ["estimate", "se", "ci_low", "ci_high", "t", "p_value"]
                    for kind, actual, expected, key in [("summary", selected, expected_summary, "quantity"),
                                                        ("coefficients", selected_coef, expected_coef, "variable")]:
                        passed, detail = table_matches(actual, expected, [key], values)
                        record(f"saved_{kind}:{label}", passed, detail)
                        valid_metadata = (actual.N.eq(len(sample)).all()
                                          and actual.economies.eq(sample.economycode.nunique()).all()
                                          and actual.events.eq(sample.outcome.sum()).all()
                                          and actual.equation.eq(ABC[spec]).all())
                        record(f"metadata_{kind}:{label}", valid_metadata)

    common, matched, _ = build_payment_samples(raw)
    scopes = {"raw": raw, "common": common, "fin25e1_complete": matched}
    audits = {
        "sample_flow": (pd.concat(expected_flows, ignore_index=True), ["age_policy", "step"]),
        "sample_counts": (pd.DataFrame(expected_counts), ["age_policy", "stage"]),
        "answer_audit": (answer_audit(scopes), ["scope", "variable", "code", "label"]),
        "age_audit": (age_audit(scopes), ["scope", "age"]),
        "age_by_economy": (age100_by_economy(scopes), ["scope", "economycode"]),
        "comparison": (compare_variants(summary), keys[:2] + ["spec", "equation", "quantity"]),
    }
    for name, (expected, index) in audits.items():
        actual = pd.read_csv(output_dir / f"{name}.csv")
        passed, detail = table_matches(actual, expected, index, [col for col in expected if col not in index])
        record(f"saved_audit:{name}", passed, detail)
    result = pd.DataFrame(rows)
    result.to_csv(output_dir / "validation.csv", index=False)
    return bool(result.passed.all())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR / "payment_tools")
    parser.add_argument("--main-output", type=Path, help="Optional original main-table directory; must use the same input data.")
    args = parser.parse_args()
    passed = validate(args.data, args.output, args.main_output)
    print("All Task 7 checks passed" if passed else "Some Task 7 checks failed")
    raise SystemExit(0 if passed else 1)


if __name__ == "__main__":
    main()
