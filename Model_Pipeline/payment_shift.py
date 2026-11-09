"""Paired, country-clustered test of the Task 7 coefficient change.

Both fits use exactly the same respondents. Cluster scores from the two
regressions are paired by economy, so their covariance is retained when
testing the difference between their weekly coefficients.
"""

import numpy as np
import pandas as pd
from scipy.stats import t as student_t

from DataClean_Pipeline.payment_tools import PAYMENT_VARIABLE, build_payment_samples
from Model_Pipeline.lpm import COUNTRY, fit_lpm
from Model_Pipeline.stages import MAIN_SPEC, SPECS, STAGES


def _cluster_influence(fit, groups, variable):
    """Cluster contributions to one WLS coefficient, including CR1 scaling."""
    x = fit.model.wexog
    residual = fit.wresid
    direction = np.zeros(x.shape[1])
    direction[fit.model.exog_names.index(variable)] = 1
    projection = np.linalg.solve(x.T @ x, direction)
    individual = (x @ projection) * residual
    unique, inverse = np.unique(groups, return_inverse=True)
    cluster = np.bincount(inverse, weights=individual, minlength=len(unique))
    n, k, g = len(individual), x.shape[1], len(unique)
    if g < 2 or n <= k:
        raise ValueError("Cluster inference requires at least two economies and N > K.")
    correction = (g / (g - 1)) * ((n - 1) / (n - k))
    return unique, cluster * np.sqrt(correction)


def paired_weekly_shift(sample, baseline_columns, augmented_columns):
    """Compare weekly coefficients on a matched sample, with paired clusters.

    The result is augmented minus baseline in percentage points. This is an
    association/sensitivity test, not a causal mediation test.
    """
    if PAYMENT_VARIABLE not in augmented_columns or PAYMENT_VARIABLE in baseline_columns:
        raise ValueError("Only the augmented equation should contain fin25e1.")
    groups = sample[COUNTRY].to_numpy()
    baseline = fit_lpm(sample, "outcome", baseline_columns)
    augmented = fit_lpm(sample, "outcome", augmented_columns)
    ids_0, score_0 = _cluster_influence(baseline, groups, "weekly")
    ids_1, score_1 = _cluster_influence(augmented, groups, "weekly")
    if not np.array_equal(ids_0, ids_1):
        raise AssertionError("Both regressions must use the same economies.")

    # Check that each score calculation reproduces the model's own cluster SE.
    for fit, score in ((baseline, score_0), (augmented, score_1)):
        expected = float(fit.bse["weekly"])
        if not np.isclose(np.linalg.norm(score), expected, rtol=1e-7, atol=1e-10):
            raise AssertionError("Cluster influence does not reproduce the fitted SE.")

    difference = float(augmented.params["weekly"] - baseline.params["weekly"])
    se = float(np.linalg.norm(score_1 - score_0))
    df = len(ids_0) - 1
    critical = student_t.ppf(0.975, df)
    p_value = float(2 * student_t.sf(abs(difference / se), df)) if se else float(difference == 0)
    return {
        "N": len(sample), "economies": len(ids_0),
        "baseline_weekly_pp": 100 * float(baseline.params["weekly"]),
        "augmented_weekly_pp": 100 * float(augmented.params["weekly"]),
        "shift_pp": 100 * difference, "shift_se_pp": 100 * se,
        "ci_low_pp": 100 * (difference - critical * se),
        "ci_high_pp": 100 * (difference + critical * se),
        "p_value": p_value,
    }


def main_spec_shift_table(raw):
    """Run the paired weekly-shift test for all three stages, main spec B."""
    _, matched, _ = build_payment_samples(raw)
    original = SPECS[MAIN_SPEC]
    augmented = [*original, PAYMENT_VARIABLE]
    rows = []
    for stage in STAGES:
        sample = stage.build_sample(matched)
        rows.append({"stage": stage.key, **paired_weekly_shift(sample, original, augmented)})
    return pd.DataFrame(rows)
