"""Build the analysis sample from the Global Findex 2025 microdata.

The sample narrows in three steps:
1. Four gates give the base sample.
2. Raw survey answers are recoded into model variables.
3. Respondents with any missing control are dropped. The result is the
   common sample. Every stage and every specification is estimated on it.
"""

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "DataBase" / "Data_Source.csv"

RAW_COLUMNS = [
    "economy", "economycode", "wgt",
    "con1", "fin25e2", "fin25e3", "con21", "con22",
    "age", "female", "educ", "inc_q", "emp_in", "urbanicity",
    "internet_use", "con9", "account",
]

# Right-hand-side variables.
# Reference groups: less than monthly, primary education or less, income Q1.
FREQUENCY = ["weekly", "monthly"]
DEMOGRAPHICS = [
    "age", "age_sq", "female_d", "educ_2", "educ_3",
    "inc_q2", "inc_q3", "inc_q4", "inc_q5", "labor_force", "rural",
]
DIGITAL = ["internet_use", "smartphone", "account"]

# A respondent enters the common sample only if all of these are present.
REQUIRED_CONTROLS = [
    "age", "female_d", "educ", "inc_q_model", "labor_force", "rural",
    "internet_use", "smartphone", "account",
]

# Age codes to treat as missing. Whether 99 and 100 are special codes is
# still undecided, so nothing is dropped for now.
AGE_MISSING_CODES = []


def load_raw():
    return pd.read_csv(DATA_PATH, usecols=RAW_COLUMNS, low_memory=False)


def apply_gates(raw):
    """Apply the four gates. Returns a list of (label, sample), one per step."""
    # con21 was only asked of phone owners, so a scam-module economy is one
    # where at least one respondent answered it.
    module_economies = raw.loc[raw["con21"].notna(), "economycode"].unique()

    in_module = raw[raw["economycode"].isin(module_economies)]
    owns_phone = in_module[in_module["con1"] == 1]
    paid_in_store = owns_phone[owns_phone["fin25e2"] == 1]

    valid_frequency = paid_in_store["fin25e3"].isin([1, 2, 3])
    valid_contact = paid_in_store["con21"].isin([1, 2])
    base = paid_in_store[valid_frequency & valid_contact]

    return [
        ("All respondents", raw),
        ("Scam-module economies", in_module),
        ("Owns a mobile phone (con1 = 1)", owns_phone),
        ("Paid in store by phone or card (fin25e2 = 1)", paid_in_store),
        ("Base sample: fin25e3 in {1,2,3} and con21 in {1,2}", base),
    ]


def code_variables(base):
    """Recode raw answers. Answers that cannot be used become missing."""
    out = base.copy()
    yes_no = {1: 1.0, 2: 0.0}

    out["weekly"] = (out["fin25e3"] == 1).astype(float)
    out["monthly"] = (out["fin25e3"] == 2).astype(float)

    out["age"] = out["age"].astype(float)
    out.loc[out["age"].isin(AGE_MISSING_CODES), "age"] = None
    out["age_sq"] = out["age"] ** 2 / 100    # divided by 100 so the coefficient is readable

    out["female_d"] = out["female"].map(yes_no)       # 1 = female, 2 = male
    out["labor_force"] = out["emp_in"].map(yes_no)    # 1 = in the labor force
    out["rural"] = out["urbanicity"].map(yes_no)      # 1 = rural, 2 = urban
    out["smartphone"] = out["con9"].map(yes_no)       # 8 and 9 become missing
    out["internet_use"] = out["internet_use"].astype(float)
    out["account"] = out["account"].astype(float)

    # Lesotho has no income data. Filling a constant keeps the country in the
    # sample, and the country fixed effect absorbs the constant.
    out["inc_q_model"] = out["inc_q"]
    out.loc[out["economycode"] == "LSO", "inc_q_model"] = 1
    return out


def add_category_dummies(common):
    """Dummies for education and income. Call this after missing rows are dropped."""
    for level in [2, 3]:
        common[f"educ_{level}"] = (common["educ"] == level).astype(float)
    for quintile in [2, 3, 4, 5]:
        common[f"inc_q{quintile}"] = (common["inc_q_model"] == quintile).astype(float)


def flow_table(steps):
    """Sample size, number of economies, and weighted share of the previous step."""
    rows = []
    previous = steps[0][1]
    for label, sample in steps:
        rows.append({
            "step": label,
            "N": len(sample),
            "economies": sample["economycode"].nunique(),
            "weighted_share_of_previous": sample["wgt"].sum() / previous["wgt"].sum(),
        })
        previous = sample
    return pd.DataFrame(rows)


def build_common_sample(raw):
    """Returns (common sample, sample flow table)."""
    steps = apply_gates(raw)
    base = steps[-1][1]

    coded = code_variables(base)
    common = coded.dropna(subset=REQUIRED_CONTROLS).copy()
    add_category_dummies(common)

    steps.append(("Common sample: all controls present", common))
    return common, flow_table(steps)
