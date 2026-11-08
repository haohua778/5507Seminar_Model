"""Power of Stage 2: minimum detectable difference and equivalence test (Section 4.2).

Specification (2) on the Stage 2 sample (sending money given reported
contact), coefficients on weekly and monthly, t distribution with 74
degrees of freedom (75 economies).

- Minimum detectable difference, MDD = (t_{0.975, 74} + t_{0.80, 74}) x SE:
  the smallest true difference the sample would detect with 80% power in a
  5% two-sided test. Same formula as joint_decomposition.py.
- TOST equivalence test for the weekly coefficient with bounds of
  +-2, 3, 3.9, 4 and 5 percentage points: two one-sided t tests,
  H0: b <= -bound and H0: b >= +bound. The TOST p-value is the larger of
  the two one-sided p-values; equivalence within the bound is supported
  when it is below 0.05. The same test is run for monthly and written to
  the CSV.

Input:  common sample from DataClean_Pipeline.build_sample
Output: Output/analysis/stage2_power.csv
Paper:  Section 4.2

Run from the project root, as part of run_pipeline.py or alone:
    python -m Analysis_Pipeline.stage2_power
"""

import pandas as pd
from scipy import stats

from Analysis_Pipeline.joint_decomposition import minimum_detectable_difference
from Analysis_Pipeline.paper_targets import compare, comparison_table, print_comparison
from DataClean_Pipeline.build_sample import FREQUENCY, PROJECT_ROOT, build_common_sample, load_raw
from Model_Pipeline.lpm import COUNTRY, fit_lpm, linear_combination
from Model_Pipeline.stages import MAIN_SPEC, OUTCOME, SPECS, stage2_send

OUTPUT_DIR = PROJECT_ROOT / "Output" / "analysis"
TITLE = "Section 4.2, power of Stage 2 (stage2_power.py)"

BOUNDS = [2, 3, 3.9, 4, 5]        # percentage points

# Numbers written in the paper, in percentage points (p-values as plain numbers).
COEFFICIENT_TARGETS = {"weekly": (1.706, 1.372), "monthly": (2.392, 1.458)}   # (estimate, SE)
MDD_TARGETS = {"weekly": 3.896, "monthly": 4.139}
TOST_TARGETS = {2: 0.4154, 3: 0.1743, 3.9: 0.0570, 4: 0.0494, 5: 0.0094}      # weekly


def tost_p_value(estimate, se, bound, df):
    """Larger of the two one-sided p-values: H0: b <= -bound and H0: b >= +bound."""
    p_above_lower_bound = stats.t.sf((estimate + bound) / se, df)
    p_below_upper_bound = stats.t.cdf((estimate - bound) / se, df)
    return float(max(p_above_lower_bound, p_below_upper_bound))


def power_table(fit, df):
    rows = []
    for variable in FREQUENCY:
        coefficient = linear_combination(fit, variable)
        estimate, se = coefficient["estimate"], coefficient["se"]
        rows.append({"variable": variable, "quantity": "estimate", "bound_pp": None, "value": estimate})
        rows.append({"variable": variable, "quantity": "se", "bound_pp": None, "value": se})
        rows.append({"variable": variable, "quantity": "mdd", "bound_pp": None,
                     "value": minimum_detectable_difference(se, df)})
        for bound in BOUNDS:
            rows.append({"variable": variable, "quantity": "tost_p_value", "bound_pp": bound,
                         "value": tost_p_value(estimate, se, bound / 100, df)})
    return pd.DataFrame(rows)


def comparison(table):
    def value(variable, quantity, bound=None):
        match = (table["variable"] == variable) & (table["quantity"] == quantity)
        if bound is not None:
            match &= table["bound_pp"] == bound
        return table.loc[match, "value"].iloc[0]

    rows = []
    for variable, (estimate, se) in COEFFICIENT_TARGETS.items():
        rows.append(compare(f"Stage 2 coefficient, {variable} (pp)", 100 * value(variable, "estimate"), estimate))
        rows.append(compare(f"Stage 2 SE, {variable} (pp)", 100 * value(variable, "se"), se))
        rows.append(compare(f"Minimum detectable difference, {variable} (pp)",
                            100 * value(variable, "mdd"), MDD_TARGETS[variable]))
    for bound, target in TOST_TARGETS.items():
        rows.append(compare(f"TOST p-value, weekly, bound +-{bound} pp",
                            value("weekly", "tost_p_value", bound), target))
    return comparison_table(rows)


def run(common):
    """Write the CSV and return the comparison with the paper."""
    stage2 = stage2_send(common)
    fit = fit_lpm(stage2, OUTCOME, SPECS[MAIN_SPEC])
    df = stage2[COUNTRY].nunique() - 1

    table = power_table(fit, df)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUTPUT_DIR / "stage2_power.csv", index=False)
    return comparison(table)


def main():
    common, _ = build_common_sample(load_raw())
    print_comparison(TITLE, run(common))


if __name__ == "__main__":
    main()
