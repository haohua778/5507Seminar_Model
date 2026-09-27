"""Weighted linear probability model with country fixed effects.

    Y = b_W * weekly + b_M * monthly + controls + country effect + error

- Country fixed effects enter as one dummy variable per economy.
- `wgt` is a sampling weight, so coefficients are weighted least squares.
- Standard errors are clustered by economy.
- Confidence intervals and p-values use the t distribution with
  (number of economies - 1) degrees of freedom.
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
