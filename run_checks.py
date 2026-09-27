"""Cross-check the estimator against independent calculations.

For each of the nine main regressions:
1. Coefficients are compared with scikit-learn's weighted regression.
2. Coefficients, standard errors and confidence intervals are compared
   with the textbook formulas written out in numpy.
3. Predicted probabilities must satisfy P_W - P_L = b_W and P_M - P_L = b_M.

Run from the project root:
    python run_checks.py
"""

import sys

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.linear_model import LinearRegression

from DataClean_Pipeline.build_sample import build_common_sample, load_raw
from Model_Pipeline.lpm import COUNTRY, WEIGHT, fit_lpm, predicted_probability
from Model_Pipeline.stages import OUTCOME, SPECS, STAGES

TOLERANCE = 1e-8


def design_matrix(sample, x_cols):
    """Regressors followed by one dummy per economy. The dummies replace the intercept."""
    country_dummies = pd.get_dummies(sample[COUNTRY], dtype=float)
    return pd.concat([sample[x_cols], country_dummies], axis=1)


def sklearn_coefficients(sample, x_cols):
    model = LinearRegression(fit_intercept=False)
    model.fit(design_matrix(sample, x_cols), sample[OUTCOME], sample_weight=sample[WEIGHT])
    return model.coef_[:len(x_cols)]


def numpy_estimate(sample, x_cols):
    """Returns (coefficients, clustered standard errors) of the regressors."""
    X = design_matrix(sample, x_cols).to_numpy()
    y = sample[OUTCOME].to_numpy(float)
    w = sample[WEIGHT].to_numpy(float)

    # Weighted least squares: beta = (X'WX)^-1 X'Wy
    XtW = (X * w[:, None]).T
    XtWX_inv = np.linalg.inv(XtW @ X)
    beta = XtWX_inv @ XtW @ y
    residual = y - X @ beta

    # Cluster-robust variance. The score of one observation is x * w * residual.
    # Scores are summed within each economy before forming the sandwich.
    scores = pd.DataFrame(X * (w * residual)[:, None])
    economy_scores = scores.groupby(sample[COUNTRY].to_numpy()).sum().to_numpy()
    sandwich = XtWX_inv @ (economy_scores.T @ economy_scores) @ XtWX_inv

    # Small-sample correction. Every column counts as a parameter,
    # including the country dummies.
    n_obs, n_params = X.shape
    n_economies = sample[COUNTRY].nunique()
    correction = n_economies / (n_economies - 1) * (n_obs - 1) / (n_obs - n_params)

    k = len(x_cols)
    return beta[:k], np.sqrt(correction * np.diag(sandwich)[:k])


def largest_gap(sample, x_cols):
    """Largest absolute difference between the estimator and the cross-checks."""
    fit = fit_lpm(sample, OUTCOME, x_cols)
    beta = fit.params[x_cols].to_numpy()
    se = fit.bse[x_cols].to_numpy()
    ci = fit.conf_int().loc[x_cols].to_numpy()

    numpy_beta, numpy_se = numpy_estimate(sample, x_cols)
    critical_value = stats.t.ppf(0.975, sample[COUNTRY].nunique() - 1)
    numpy_ci = np.column_stack([
        numpy_beta - critical_value * numpy_se,
        numpy_beta + critical_value * numpy_se,
    ])

    p_weekly = predicted_probability(fit, sample, weekly=1.0, monthly=0.0)
    p_monthly = predicted_probability(fit, sample, weekly=0.0, monthly=1.0)
    p_less = predicted_probability(fit, sample, weekly=0.0, monthly=0.0)

    gaps = [
        np.abs(beta - sklearn_coefficients(sample, x_cols)).max(),
        np.abs(beta - numpy_beta).max(),
        np.abs(se - numpy_se).max(),
        np.abs(ci - numpy_ci).max(),
        abs(p_weekly - p_less - fit.params["weekly"]),
        abs(p_monthly - p_less - fit.params["monthly"]),
    ]
    return max(gaps)


def main():
    common, _ = build_common_sample(load_raw())
    all_passed = True

    for stage in STAGES:
        sample = stage.build_sample(common)
        for spec, x_cols in SPECS.items():
            gap = largest_gap(sample, x_cols)
            passed = gap < TOLERANCE
            all_passed = all_passed and passed
            status = "pass" if passed else "FAIL"
            print(f"{status}  {stage.key} {spec}  largest gap {gap:.1e}")

    print("\nAll checks passed" if all_passed else "\nSome checks failed")
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
