"""Economy-level composition of the payment-frequency groups (Section 3.4).

Who lives where: the less-than-monthly group is concentrated in economies
with higher scam-contact rates, which is why the pooled and within-economy
comparisons differ. All rates and shares are weighted by `wgt`.

(a) By economy: reported-contact rate (Stage 1 sample), joint-event rate
    (Stage 3 sample), share of less-than-monthly payers and share of weekly
    payers (common sample).
(b) Exposure of a group: for all less-than-monthly payers, the `wgt`-weighted
    mean of the contact rate and of the joint rate of each payer's own
    economy. The same for weekly payers.
(c) Economies split into terciles (25 / 25 / 25) of the less-than-monthly
    share. The paper reports the simple mean of the economy rates in each
    tercile; the sample-size-weighted mean is given next to it in the CSV.
(d) Pearson correlation across economies between the weekly share and the
    joint rate, which Figure 1 also reports. Figure 1 computes the weekly
    share on the Stage 3 sample (two respondents fewer than the common
    sample); both versions are given.

Input:  common sample from DataClean_Pipeline.build_sample
Output: Output/analysis/economy_composition.csv           one row per economy, (a)
        Output/analysis/economy_composition_terciles.csv  (c)
Paper:  Section 3.4; consistency with Figure 1 (figure1_economy_level.csv)

Run from the project root, as part of run_pipeline.py or alone:
    python -m Analysis_Pipeline.economy_composition
"""

import numpy as np
import pandas as pd

from Analysis_Pipeline.paper_targets import compare, comparison_table, print_comparison
from DataClean_Pipeline.build_sample import PROJECT_ROOT, build_common_sample, load_raw
from Model_Pipeline.lpm import COUNTRY, WEIGHT
from Model_Pipeline.stages import OUTCOME, stage1_contact, stage3_joint

OUTPUT_DIR = PROJECT_ROOT / "Output" / "analysis"
TITLE = "Section 3.4, economy-level composition (economy_composition.py)"

# fin25e3 code -> group name.
GROUPS = {3: "less than monthly", 1: "weekly"}
TERCILES = ["lowest", "middle", "highest"]      # terciles of the less-than-monthly share

# Numbers written in the paper, in percent (correlation as a plain number).
EXPOSURE_TARGETS = {
    ("less than monthly", "contact_rate"): 31.3,
    ("less than monthly", "joint_rate"): 3.5,
    ("weekly", "contact_rate"): 27.3,
    ("weekly", "joint_rate"): 2.1,
}
TERCILE_TARGETS = {
    ("highest", "contact_rate"): 34.4,
    ("highest", "joint_rate"): 5.3,
    ("lowest", "contact_rate"): 28.1,
    ("lowest", "joint_rate"): 2.1,
}
CORRELATION_TARGET = -0.19


def weighted_mean(values, weights):
    return float(np.average(np.asarray(values, dtype=float), weights=weights))


def economy_table(common):
    """(a): one row per economy."""
    stage1 = stage1_contact(common)
    stage3 = stage3_joint(common)
    rows = []
    for code, group in stage1.groupby(COUNTRY):
        joint = stage3[stage3[COUNTRY] == code]
        rows.append({
            "economycode": code,
            "economy": group["economy"].iloc[0],
            "n": len(group),
            "contact_rate": weighted_mean(group[OUTCOME], group[WEIGHT]),
            "joint_rate": weighted_mean(joint[OUTCOME], joint[WEIGHT]),
            "less_than_monthly_share": weighted_mean(group["fin25e3"] == 3, group[WEIGHT]),
            "weekly_share": weighted_mean(group["weekly"], group[WEIGHT]),
            "weekly_share_stage3_sample": weighted_mean(joint["weekly"], joint[WEIGHT]),
        })
    table = pd.DataFrame(rows)
    table["less_than_monthly_tercile"] = pd.qcut(
        table["less_than_monthly_share"], 3, labels=TERCILES)
    return table


def exposure(common, economies, code):
    """(b): weighted mean, over the respondents of one group, of their own economy's rates."""
    group = common[common["fin25e3"] == code]
    own_economy = economies.set_index("economycode").loc[group[COUNTRY]]
    return {
        "contact_rate": weighted_mean(own_economy["contact_rate"], group[WEIGHT]),
        "joint_rate": weighted_mean(own_economy["joint_rate"], group[WEIGHT]),
    }


def tercile_table(economies):
    """(c): simple and sample-size-weighted means of the economy rates in each tercile."""
    rows = []
    for tercile, group in economies.groupby("less_than_monthly_tercile", observed=True):
        rows.append({
            "tercile": tercile,
            "economies": len(group),
            "respondents": int(group["n"].sum()),
            "less_than_monthly_share_min": group["less_than_monthly_share"].min(),
            "less_than_monthly_share_max": group["less_than_monthly_share"].max(),
            "contact_rate_simple_mean": group["contact_rate"].mean(),
            "joint_rate_simple_mean": group["joint_rate"].mean(),
            "contact_rate_n_weighted": weighted_mean(group["contact_rate"], group["n"]),
            "joint_rate_n_weighted": weighted_mean(group["joint_rate"], group["n"]),
        })
    return pd.DataFrame(rows)


def correlation(economies, weekly_column):
    """(d): Pearson correlation across economies, unweighted as in Figure 1."""
    return float(np.corrcoef(economies[weekly_column], economies["joint_rate"])[0, 1])


def comparison(common, economies, terciles):
    rows = []
    for code, name in GROUPS.items():
        rates = exposure(common, economies, code)
        for rate in ["contact_rate", "joint_rate"]:
            rows.append(compare(f"Mean {rate.replace('_', ' ')} of the own economy, {name} payers (%)",
                                100 * rates[rate], EXPOSURE_TARGETS[(name, rate)]))
    by_tercile = terciles.set_index("tercile")
    for (tercile, rate), target in TERCILE_TARGETS.items():
        rows.append(compare(f"Mean {rate.replace('_', ' ')}, {tercile} tercile of the "
                            f"less-than-monthly share, simple mean of economies (%)",
                            100 * by_tercile.loc[tercile, f"{rate}_simple_mean"], target))
    rows.append(compare("Correlation of weekly share and joint rate across economies "
                        "(weekly share on the common sample)",
                        correlation(economies, "weekly_share"), CORRELATION_TARGET))
    rows.append(compare("Correlation of weekly share and joint rate across economies "
                        "(weekly share on the Stage 3 sample, as Figure 1)",
                        correlation(economies, "weekly_share_stage3_sample"), CORRELATION_TARGET))
    return comparison_table(rows)


def run(common):
    """Write the CSV files and return the comparison with the paper."""
    economies = economy_table(common)
    terciles = tercile_table(economies)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    economies.to_csv(OUTPUT_DIR / "economy_composition.csv", index=False)
    terciles.to_csv(OUTPUT_DIR / "economy_composition_terciles.csv", index=False)

    pd.set_option("display.width", 200)
    print("Terciles of the less-than-monthly share (rates in %):")
    shown = terciles.copy()
    for column in shown.columns[3:]:
        shown[column] = (100 * shown[column]).round(2)
    print(shown.to_string(index=False))
    print()
    return comparison(common, economies, terciles)


def main():
    common, _ = build_common_sample(load_raw())
    print_comparison(TITLE, run(common))


if __name__ == "__main__":
    main()
