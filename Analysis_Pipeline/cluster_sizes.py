"""Cluster sizes and concentration of senders (Section 3.6).

By economy: respondents in the Stage 1, Stage 2 and Stage 3 samples, and
senders (Stage 2 outcome = 1). From these:
- smallest, largest and median Stage 1 cluster (respondents per economy)
- share of all senders in the ten economies with the most senders
- economies with no sender, and how many there are
- Lesotho's counts in the common sample and in the Stage 2 sample. The
  paper draft writes 52 for Stage 2 and an earlier draft wrote 28; the
  comparison below settles which one the data give.

Input:  common sample from DataClean_Pipeline.build_sample
Output: Output/analysis/cluster_sizes.csv  (one row per economy)
Paper:  Section 3.6

Run from the project root, as part of run_pipeline.py or alone:
    python -m Analysis_Pipeline.cluster_sizes
"""

import pandas as pd

from Analysis_Pipeline.paper_targets import compare, comparison_table, print_comparison
from DataClean_Pipeline.build_sample import PROJECT_ROOT, build_common_sample, load_raw
from Model_Pipeline.lpm import COUNTRY
from Model_Pipeline.stages import OUTCOME, stage1_contact, stage2_send, stage3_joint

OUTPUT_DIR = PROJECT_ROOT / "Output" / "analysis"
TITLE = "Section 3.6, cluster sizes and concentration of senders (cluster_sizes.py)"

TOP_ECONOMIES = 10
LESOTHO = "LSO"

# Numbers written in the paper.
TARGETS = {
    "Stage 1 cluster size, smallest": 15,
    "Stage 1 cluster size, largest": 939,
    "Stage 1 cluster size, median": 139,
    "Senders": 445,
    f"Share of senders in the {TOP_ECONOMIES} economies with the most senders (%)": 42,
    "Economies with no sender": 7,
    "Economies with no sender, names":
        "Belize, Honduras, Madagascar, Morocco, Sri Lanka, Tunisia, Zimbabwe",
    "Lesotho, respondents in the common sample": 171,
    "Lesotho, respondents in the Stage 2 sample": 52,
}


def cluster_table(common):
    stage1, stage2, stage3 = stage1_contact(common), stage2_send(common), stage3_joint(common)
    senders = stage2[stage2[OUTCOME] == 1]
    table = pd.DataFrame({
        "economy": common.groupby(COUNTRY)["economy"].first(),
        "n_stage1": stage1.groupby(COUNTRY).size(),
        "n_stage2": stage2.groupby(COUNTRY).size(),
        "senders": senders.groupby(COUNTRY).size(),
        "n_stage3": stage3.groupby(COUNTRY).size(),
    })
    for column in ["n_stage1", "n_stage2", "senders", "n_stage3"]:
        table[column] = table[column].fillna(0).astype(int)
    return table.rename_axis("economycode").reset_index()


def comparison(table):
    by_senders = table.sort_values("senders", ascending=False)
    top = by_senders.head(TOP_ECONOMIES)
    no_sender = table[table["senders"] == 0]
    lesotho = table.set_index("economycode").loc[LESOTHO]

    computed = {
        "Stage 1 cluster size, smallest": int(table["n_stage1"].min()),
        "Stage 1 cluster size, largest": int(table["n_stage1"].max()),
        "Stage 1 cluster size, median": float(table["n_stage1"].median()),
        "Senders": int(table["senders"].sum()),
        f"Share of senders in the {TOP_ECONOMIES} economies with the most senders (%)":
            100 * top["senders"].sum() / table["senders"].sum(),
        "Economies with no sender": len(no_sender),
        "Economies with no sender, names": ", ".join(sorted(no_sender["economy"])),
        "Lesotho, respondents in the common sample": int(lesotho["n_stage1"]),
        "Lesotho, respondents in the Stage 2 sample": int(lesotho["n_stage2"]),
    }
    return comparison_table([compare(label, computed[label], target)
                             for label, target in TARGETS.items()])


def run(common):
    """Write the CSV and return the comparison with the paper."""
    table = cluster_table(common)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    table.to_csv(OUTPUT_DIR / "cluster_sizes.csv", index=False)

    top = table.sort_values("senders", ascending=False).head(TOP_ECONOMIES)
    print(f"The {TOP_ECONOMIES} economies with the most senders:")
    print(top[["economycode", "economy", "n_stage2", "senders"]].to_string(index=False))
    print()
    return comparison(table)


def main():
    common, _ = build_common_sample(load_raw())
    print_comparison(TITLE, run(common))


if __name__ == "__main__":
    main()
