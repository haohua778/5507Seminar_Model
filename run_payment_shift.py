"""Test whether adding fin25e1 changes the main weekly contrast.

Run from the project root: python run_payment_shift.py
"""

import argparse
from pathlib import Path

from DataClean_Pipeline.build_sample import DATA_PATH
from DataClean_Pipeline.payment_tools import load_payment_raw
from Model_Pipeline.payment_shift import main_spec_shift_table
from Model_Pipeline.report import OUTPUT_DIR


def write_shift_report(table, output):
    names = {
        "stage1_contact": "Stage 1: reported contact",
        "stage2_send": "Stage 2: sending money after contact",
        "stage3_joint": "Stage 3: contact and sending money",
    }
    by_stage = table.set_index("stage")
    first = by_stage.loc["stage1_contact"]
    second = by_stage.loc["stage2_send"]
    third = by_stage.loc["stage3_joint"]
    lines = [
        "# Task 7 follow-up: Is the coefficient change distinguishable from zero?",
        "",
        "This checks the change in the weekly-versus-less-than-monthly coefficient "
        "when fin25e1 is added to main specification B. Both regressions use the "
        "same people. Each economy's contributions to both estimates are paired "
        "before calculating the uncertainty of their difference.",
        "",
        "| Outcome | N | Baseline (pp) | With fin25e1 (pp) | Change (pp) | 95% CI for change (pp) | p-value |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in table.itertuples(index=False):
        lines.append(
            f"| {names[row.stage]} | {row.N:,} | {row.baseline_weekly_pp:+.2f} "
            f"| {row.augmented_weekly_pp:+.2f} | {row.shift_pp:+.2f} "
            f"| [{row.ci_low_pp:+.2f}, {row.ci_high_pp:+.2f}] | {row.p_value:.3f} |"
        )
    lines += [
        "",
        "## 大白话怎么读",
        "",
        "这里比的是同一批人、同一种主模型：第一次不加 fin25e1，第二次加上它。"
        "‘变化’等于第二次的每周差距减去第一次的每周差距；负数表示差距缩小。",
        f"第一阶段的变化为 {first.shift_pp:+.2f} 个百分点，"
        f"第二阶段为 {second.shift_pp:+.2f} 个百分点，"
        f"第三阶段为 {third.shift_pp:+.2f} 个百分点。"
        "请看上表的变化区间是否跨过零，再判断变化是否明确。",
        "第三阶段‘新模型里的每周差距’和‘加变量前后差距的变化’是两个不同问题，"
        "两种 p 值即使落在 0.05 的两边，也不矛盾。",
        "",
        "## Method note",
        "",
        "The change is the augmented coefficient minus the same-sample baseline "
        "coefficient. The standard error uses a paired country-cluster sandwich "
        "calculation with each regression's CR1 finite-sample correction; the "
        "interval and two-sided p-value use each stage's number of economies "
        "minus one degrees of freedom. "
        "This tests the change between two fitted associations, not whether fin25e1 "
        "causally explains it. It does not turn a nonsignificant Stage 3 augmented "
        "coefficient into proof that the original association vanished.",
        "",
        "The corresponding unrounded estimates are in model_shift.csv. "
        "The existing Task 7 report and group memo are unchanged.",
        "",
    ]
    output.mkdir(parents=True, exist_ok=True)
    table.to_csv(output / "model_shift.csv", index=False)
    (output / "model_shift.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    parser.add_argument("--output", type=Path, default=OUTPUT_DIR / "payment_tools")
    args = parser.parse_args()
    table = main_spec_shift_table(load_payment_raw(args.data))
    write_shift_report(table, args.output)
    print(table.to_string(index=False))
    print(f"Wrote {args.output / 'model_shift.csv'} and model_shift.md")


if __name__ == "__main__":
    main()
