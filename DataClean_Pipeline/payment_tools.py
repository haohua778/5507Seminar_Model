"""Task 7: audit payment questions and prepare a matched comparison sample.

The original common sample is built by build_sample.py, not reimplemented here.
No raw file or shared main-analysis setting is modified.
"""

import numpy as np
import pandas as pd

from DataClean_Pipeline.build_sample import DATA_PATH, RAW_COLUMNS, build_common_sample

PAYMENT_VARIABLE = "usual_digital_payment"
EXTRA_COLUMNS = ["fin25e1", "con23"]
ANSWER_LABELS = {
    "fin25e1": {1: "Yes", 2: "No", 3: "Don't know", 4: "Refused"},
    "con23": {1: "Yes", 2: "No", 8: "Don't know", 9: "Refused"},
}


def load_payment_raw(path=DATA_PATH):
    """Read core and supplementary columns in one pass to preserve row alignment."""
    columns = list(dict.fromkeys(RAW_COLUMNS + EXTRA_COLUMNS))
    raw = pd.read_csv(path, usecols=columns, low_memory=False)
    for column, labels in ANSWER_LABELS.items():
        unexpected = set(raw[column].dropna().unique()) - set(labels)
        if unexpected:
            raise ValueError(f"Unexpected {column} codes: {sorted(unexpected)}")
    weights = raw["wgt"].to_numpy(float)
    if not np.isfinite(weights).all() or (weights <= 0).any():
        raise ValueError("Task 7 requires finite, positive survey weights.")
    return raw


def payment_complete_cases(common):
    """fin25e1: yes=1, no=0; don't-know/refusal/missing are excluded, never no.

    con23 is audited only. It is not a sample gate or a regression control.
    """
    sample = common.loc[common["fin25e1"].isin([1, 2])].copy()
    sample[PAYMENT_VARIABLE] = sample["fin25e1"].map({1: 1.0, 2: 0.0})
    return sample


def build_payment_samples(raw, *, exclude_age100=False):
    """Return original and matched common samples plus their sample flow.

    The optional age rule reproduces the official age-category cleaning for
    code 100. It is explicit and leaves the project's main baseline intact.
    """
    working = raw.copy()
    if exclude_age100:
        working.loc[working["age"].eq(100), "age"] = np.nan
    common, flow = build_common_sample(working)
    matched = payment_complete_cases(common)
    if common.empty or matched.empty:
        raise ValueError("No usable observations for the Task 7 comparison.")
    flow = pd.concat([flow, pd.DataFrame([{
        "step": "Task 7: fin25e1 in {1,2}",
        "N": len(matched),
        "economies": matched["economycode"].nunique(),
        "weighted_share_of_previous": matched["wgt"].sum() / common["wgt"].sum(),
    }])], ignore_index=True)
    return common, matched, flow


def answer_audit(scopes):
    """Unweighted counts and survey-weighted shares, including missing answers."""
    rows = []
    for scope, sample in scopes.items():
        denominator = sample["wgt"].sum()
        for variable, labels in ANSWER_LABELS.items():
            for code, label in [*labels.items(), (None, "Missing / not asked")]:
                mask = sample[variable].isna() if code is None else sample[variable].eq(code)
                rows.append({
                    "scope": scope, "variable": variable,
                    "code": "missing" if code is None else str(code), "label": label,
                    "N": int(mask.sum()), "scope_N": len(sample),
                    "weight_sum": sample.loc[mask, "wgt"].sum(),
                    "weighted_share": sample.loc[mask, "wgt"].sum() / denominator,
                })
    return pd.DataFrame(rows)


def age_audit(scopes):
    rows = []
    for scope, sample in scopes.items():
        for age in sorted(sample["age"].dropna().unique()):
            mask = sample["age"].eq(age)
            rows.append({"scope": scope, "age": age, "N": int(mask.sum()),
                         "weight_sum": sample.loc[mask, "wgt"].sum()})
    return pd.DataFrame(rows)


def age100_by_economy(scopes):
    rows = []
    for scope, sample in scopes.items():
        for economy, group in sample.groupby("economycode", sort=True):
            rows.append({"scope": scope, "economycode": economy,
                         "N": len(group), "age_99_N": int(group["age"].eq(99).sum()),
                         "age_100_N": int(group["age"].eq(100).sum())})
    return pd.DataFrame(rows)
