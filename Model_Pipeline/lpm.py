"""Weighted linear probability model with country fixed effects.

    Y = b_W * weekly + b_M * monthly + controls + country effect + error

- Country fixed effects enter as one dummy variable per economy.
- `wgt` is a sampling weight, so coefficients are weighted least squares.
- Standard errors are clustered by economy (CRV1).
- Confidence intervals and p-values use the t distribution with
  (number of economies - 1) = 74 degrees of freedom.

Why CRV1 and t(G - 1). Respondents in the same economy share the sampling
design, the survey vendor and the national scam environment, so their
errors are correlated and the economy is the natural cluster. CRV1 is the
cluster-robust sandwich with the finite-sample factor
G/(G - 1) x (N - 1)/(N - K); with 75 clusters the asymptotic (G -> infinity)
approximation is not reliable, so the factor is applied and inference uses
the t distribution with G - 1 degrees of freedom rather than the normal.
This is the convention of Stata's `regress ..., vce(cluster)` and of
Cameron and Miller (2015). K counts the country dummies as parameters,
which is what statsmodels does when the dummies are explicit regressors;
absorbing them instead (as reghdfe does) would shrink the standard errors
by less than 1 percent. Robustness_Pipeline/wild_cluster_bootstrap.py
checks the resulting p-values against a wild cluster bootstrap.

Input:  an estimation sample from Model_Pipeline.stages
Output: a statsmodels results object; nothing is written
Paper:  the estimator behind Tables 3 and 4, Figures 1 and 2
"""

import numpy as np
import statsmodels.formula.api as smf

COUNTRY = "economycode"
WEIGHT = "wgt"


def fit_lpm(sample, y_col, x_cols):
    if sample[[y_col, WEIGHT, COUNTRY] + x_cols].isna().any().any():
        raise ValueError("The sample has missing values. Filter it before fitting.")

    formula = f"{y_col} ~ {' + '.join(x_cols)} + C({COUNTRY})"
    model = smf.wls(formula, data=sample, weights=sample[WEIGHT])

    if np.linalg.matrix_rank(model.exog) < model.exog.shape[1]:
        raise ValueError("A regressor is collinear with the others or with the country dummies.")

    economy_codes = sample[COUNTRY].astype("category").cat.codes
    return model.fit(cov_type="cluster", cov_kwds={"groups": economy_codes}, use_t=True)


def linear_combination(fit, expression):
    """Estimate, standard error, 95% CI and p-value of a combination of coefficients.

    Example: "weekly - monthly" gives b_W - b_M.
    """
    row = fit.t_test(expression).summary_frame().iloc[0]
    return {
        "estimate": row["coef"],
        "se": row["std err"],
        "ci_low": row["Conf. Int. Low"],
        "ci_high": row["Conf. Int. Upp."],
        "t": row["t"],
        "p_value": row["P>|t|"],
    }


def predicted_probability(fit, sample, weekly, monthly):
    """Weighted mean prediction if everyone had the given payment frequency.

    All other characteristics keep their observed values.
    """
    counterfactual = sample.assign(weekly=weekly, monthly=monthly)
    prediction = fit.predict(counterfactual)
    return float(np.average(prediction, weights=sample[WEIGHT]))
