"""Estimate one stage: three specifications on the same sample.

For each specification the summary table holds
- three predicted probabilities: P_W, P_M, P_L
- three differences with 95% CI: b_W, b_M, b_W - b_M
"""

import numpy as np
import pandas as pd

from Model_Pipeline.lpm import COUNTRY, WEIGHT, fit_lpm, linear_combination, predicted_probability
from Model_Pipeline.stages import OUTCOME, SPECS

# Value of (weekly, monthly) for each payment frequency.
FREQUENCY_LEVELS = {
    "P_weekly": (1.0, 0.0),
    "P_monthly": (0.0, 1.0),
    "P_less_than_monthly": (0.0, 0.0),
}

DIFFERENCES = {
    "beta_W": "weekly",
    "beta_M": "monthly",
    "beta_W_minus_beta_M": "weekly - monthly",
}

# Codes of fin25e3.
FREQUENCY_CODES = {1: "weekly", 2: "monthly", 3: "less than monthly"}


def estimate_stage(sample):
    """Returns (summary table, table of all coefficients)."""
    summary_rows = []
    coefficient_rows = []

    for spec, x_cols in SPECS.items():
        fit = fit_lpm(sample, OUTCOME, x_cols)

        for name, (weekly, monthly) in FREQUENCY_LEVELS.items():
            probability = predicted_probability(fit, sample, weekly, monthly)
            summary_rows.append({"spec": spec, "quantity": name, "estimate": probability})

        for name, expression in DIFFERENCES.items():
            difference = linear_combination(fit, expression)
            summary_rows.append({"spec": spec, "quantity": name, **difference})

        for variable in x_cols:
            coefficient = linear_combination(fit, variable)
            coefficient_rows.append({"spec": spec, "variable": variable, **coefficient})

    summary = pd.DataFrame(summary_rows)
    summary["N"] = len(sample)
    summary["economies"] = sample[COUNTRY].nunique()
    return summary, pd.DataFrame(coefficient_rows)


def raw_rates(sample):
    """Weighted outcome rate by payment frequency, with no controls or fixed effects."""
    rows = []
    for code, label in FREQUENCY_CODES.items():
        group = sample[sample["fin25e3"] == code]
        rows.append({
            "frequency": label,
            "N": len(group),
            "events": int(group[OUTCOME].sum()),
            "weighted_rate": np.average(group[OUTCOME], weights=group[WEIGHT]),
        })
    return pd.DataFrame(rows)
