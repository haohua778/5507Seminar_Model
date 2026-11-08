"""Write Task 7 tables and a measurement-limitations section beside main results."""

import hashlib
import json
import os

from DataClean_Pipeline.build_sample import PROJECT_ROOT
from DataClean_Pipeline.payment_tools import PAYMENT_VARIABLE
from Model_Pipeline.payment_tools import compare_variants
from Model_Pipeline.report import format_difference, format_p, markdown_table
from Model_Pipeline.stages import STAGES

STAGE_NAMES = {"stage1_contact": "1 被联系", "stage2_send": "2 被联系后转钱", "stage3_joint": "3 被联系且转钱"}


def _row(summary, stage, variant, *, age_policy="legacy", spec="(2)", quantity="beta_W"):
    selected = summary.loc[(summary.stage == stage) & (summary.variant == variant)
                           & (summary.age_policy == age_policy) & (summary.spec == spec)
                           & (summary.quantity == quantity)]
    if len(selected) != 1:
        raise ValueError("Expected exactly one report row.")
    return selected.iloc[0]


def _difference(row):
    return format_difference(row)


def _effect_table(summary, quantity):
    rows = []
    for stage in STAGES:
        for spec, equation in [("(1)", "A"), ("(2)", "B"), ("(3)", "C")]:
            values = [_row(summary, stage.key, variant, spec=spec, quantity=quantity)
                      for variant in ("original", "same_sample", "fin25e1_added")]
            rows.append([STAGE_NAMES[stage.key], equation,
                         f"{int(values[0]['N']):,} / {int(values[1]['N']):,}",
                         *[_difference(value) for value in values],
                         f"{100 * (values[2]['estimate'] - values[1]['estimate']):+.3f}"])
    return markdown_table(["阶段", "设置", "原样本 / 比较样本 N", "原结果", "同样本基准", "+fin25e1", "加入后差值变化(pp)"], rows)


def _probability_table(summary):
    rows = []
    for stage in STAGES:
        for spec, equation in [("(1)", "A"), ("(2)", "B"), ("(3)", "C")]:
            for variant, label in [("same_sample", "同样本基准"), ("fin25e1_added", "+fin25e1")]:
                values = [_row(summary, stage.key, variant, spec=spec, quantity=q)
                          for q in ("P_weekly", "P_monthly", "P_less_than_monthly")]
                rows.append([STAGE_NAMES[stage.key], equation, label,
                             *[f"{100 * value['estimate']:.2f}" for value in values]])
    return markdown_table(["阶段", "设置", "模型", "P_W (%)", "P_M (%)", "P_L (%)"], rows)


def _age_table(summary):
    rows = []
    for stage in STAGES:
        for variant, label in [("original", "原设定"), ("same_sample", "fin25e1 同样本基准"),
                               ("fin25e1_added", "+fin25e1")]:
            old = _row(summary, stage.key, variant)
            new = _row(summary, stage.key, variant, age_policy="exclude_100")
            rows.append([STAGE_NAMES[stage.key], label,
                         f"{int(old['N']):,} → {int(new['N']):,}", _difference(old), _difference(new),
                         f"{100 * (new['estimate'] - old['estimate']):+.3f}"])
    return markdown_table(["阶段", "模型（设置 B）", "N", "保留 age=100", "排除 age=100", "差值变化(pp)"], rows)


def measurement_limitations(tables, docs_link="../../Docs/task7"):
    summary, counts = tables["summary"], tables["sample_counts"]
    c = counts.loc[(counts.age_policy == "legacy") & (counts.stage == "stage1_contact")].iloc[0]
    age = tables["age_audit"]
    n100 = int(age.loc[(age.scope == "common") & (age.age == 100), "N"].sum())
    results = []
    for stage in STAGES:
        before = _row(summary, stage.key, "same_sample")
        after = _row(summary, stage.key, "fin25e1_added")
        results.append(f"Stage {STAGE_NAMES[stage.key]}：同样本基准 {_difference(before)}；加入 fin25e1 后 {_difference(after)}。")
    english_results = []
    for stage in STAGES:
        before = _row(summary, stage.key, "same_sample")
        after = _row(summary, stage.key, "fin25e1_added")
        english_results.append(f"{stage.title}: the weekly contrast changes from {100 * before['estimate']:.2f} "
                               f"to {100 * after['estimate']:.2f} percentage points "
                               f"(augmented-model 95% CI: {100 * after['ci_low']:.2f} to "
                               f"{100 * after['ci_high']:.2f} percentage points; {format_p(after['p_value'])}).")
    joint = _row(summary, "stage3_joint", "fin25e1_added")
    joint_note = (
        "The augmented Stage 3 weekly contrast includes zero in its 95% interval. Evidence for the joint outcome "
        "is therefore sensitive to this adjustment at the 5% threshold; this is not evidence that the true association is zero."
        if joint["ci_low"] <= 0 <= joint["ci_high"] else
        "The augmented Stage 3 weekly contrast excludes zero in its 95% interval."
    )
    return "\n\n".join([
        "# Task 7: measurement limitations / 测量局限",
        "## English text for the report",
        "The payment measures combine mobile-phone and card payments and do not distinguish between the two instruments. "
        "The questionnaire wording of fin25e1 concerns typical payment for household food or cleaning supplies, whereas "
        "fin25e3 concerns the frequency of digital in-store purchases. These measures capture related but distinct aspects "
        "of payment behaviour. The fin25e3 interviewer instruction assigns a response of never to less than monthly. "
        "Thus that reference category does not necessarily imply current occasional use. We therefore add the binary fin25e1 indicator as an additional covariate rather than "
        "interpret it as a phone-versus-card comparison or a measure of payment frequency. Because fin25e1 and fin25e3 "
        "are related contemporaneous behaviours, this adjustment is a sensitivity comparison; it does not establish "
        "that fin25e1 is a pre-existing confounder or that the augmented model is less biased.",
        f"For this supplement, A/B/C are explicitly defined as the project's existing specifications (1)/(2)/(3), "
        f"each augmented with fin25e1 (yes=1, no=0). These labels were adopted for this task and were not specified "
        f"in the upstream repository. We exclude don't-know, refusal and missing responses to fin25e1, reducing the common "
        f"sample from {int(c.original_N):,} to {int(c.matched_N):,}. Each augmented model is compared with its unaugmented "
        f"counterpart on exactly the same respondents. A difference between these fitted coefficients is reported "
        f"descriptively and is not itself a significance test.",
        "The outcome items are self-reported. con21 records a call or message from an unknown person asking for money "
        "in the past 12 months; it does not independently verify fraudulent intent. Sending money is likewise not "
        "independent confirmation of a fraud loss. The project uses these items as proxies for scam contact and sending. "
        "For respondents with multiple contacts, the con22 interviewer instruction refers to the most recent such contact; "
        "it does not establish total losses or whether any money was sent over all contacts in the year. con23 concerns "
        "unwanted and offensive messages, photos or videos, and does not establish a request for money or a monetary loss. "
        "It is documented here but not substituted for a scam outcome or included as a control in the Task 7 regressions.",
        f"Age requires a separate coding qualification. The public codebook describes age in years but does not label "
        f"the value 100. The World Bank reproduction code maps age through agenumber to wp1220 and explicitly treats "
        f"wp1220=100 as missing when constructing age categories. The legacy common sample contains {n100} such records. "
        "We retain the legacy model for reproducible comparison and separately report the main-specification results "
        "after treating 100 as missing. The inspected code establishes a rule for its age categories, but does not "
        "establish whether the raw value 100 is a true age, a nonresponse code or another convention. It also gives "
        "no basis for deleting age=99. Results should not describe age=100 observations as verified centenarians. "
        "The shared main pipeline still retains these records; adopting the alternative rule project-wide would "
        "require regenerating its tables.",
        "All estimates inherit the project's survey weights, country fixed effects and country-clustered inference. "
        "They describe associations within the selected sample of phone owners with digital in-store payment experience. "
        "Pooled predictions under the inherited wgt weighting are not automatically population-weighted rates for all "
        "adults worldwide. They do not identify a causal effect, and a non-significant conditional-sending estimate does not establish "
        "equivalence or the absence of an association.",
        "For the main specification B, the matched-sample comparisons are as follows. " + " ".join(english_results) + " " + joint_note,
        "## 中文说明",
        "fin25e1 同时包括手机和卡，不能据此比较‘手机付款比刷卡更危险’。它问的是通常购买家庭食品或清洁用品时怎样付款，"
        "不能把它解释成每周付款频率。我们在现有三种设置中额外考虑这项付款习惯，并让增加前后的模型使用完全相同的人。"
        "这两个问题反映同一时期的相关习惯，多加一个因素不代表一定更接近因果关系。"
        "fin25e3 的访员说明还把‘从不’归入‘低于每月’，所以这一组不能都称为目前偶尔付款的人。",
        "con21 问陌生人是否索款，问卷没有另外核实对方确实是骗子；汇钱也不等于已经核实的诈骗损失。"
        "con23 问的是不受欢迎且冒犯性的内容，不等于诈骗联系或损失。con22 在多次联系情况下只问最近一次，"
        "因此第三阶段也不能直接解释为全年所有诈骗中的总受害率。",
        "age=100 的官方处理依据来自复现代码，不能仅凭网页标出的数值范围判断它是实际年龄。"
        "本补充保留原结果供核对，并单独列出按缺失处理后的结果；主程序尚未统一改用这一年龄规则。",
        "## 主要结果（B；每周相对少于每月，单位为百分点）",
        *results,
        "## Sources",
        f"完整原题、页码、官方代码链条及链接见 [codebook audit]({docs_link}/codebook_audit.md)。"
        f"A/B/C 定义及运行方式见 [Task 7 integration]({docs_link}/README.md)。",
    ]) + "\n"


def write_payment_report(tables, output_dir, manifest):
    output_dir.mkdir(parents=True, exist_ok=True)
    docs_link = os.path.relpath((PROJECT_ROOT / "Docs/task7").resolve(), output_dir.resolve()).replace(os.sep, "/")
    tables = dict(tables)
    tables["comparison"] = compare_variants(tables["summary"])
    for name, frame in tables.items():
        frame.to_csv(output_dir / f"{name}.csv", index=False)
    summary = tables["summary"]
    counts = tables["sample_counts"]
    counts = counts.loc[counts.age_policy == "legacy"]
    count_rows = [[STAGE_NAMES[r.stage], f"{r.original_N:,}", f"{r.matched_N:,}",
                   str(r.excluded_fin25e1_N), str(r.original_events), str(r.matched_events),
                   f"{r.original_economies} / {r.matched_economies}"] for r in counts.itertuples()]
    habit = tables["coefficients"]
    habit = habit.loc[(habit.age_policy == "legacy") & (habit.variant == "fin25e1_added")
                      & (habit.variable == PAYMENT_VARIABLE)]
    habit_rows = [[STAGE_NAMES[r.stage], r.equation, _difference(r._asdict())] for r in habit.itertuples()]
    headline_rows = []
    for stage in STAGES:
        before = _row(summary, stage.key, "same_sample")
        after = _row(summary, stage.key, "fin25e1_added")
        inference = "区间包含 0，不能确定差异方向" if after["ci_low"] <= 0 <= after["ci_high"] else "区间不含 0"
        headline_rows.append([STAGE_NAMES[stage.key], f"{100 * before['estimate']:+.2f}",
                              _difference(after), inference])
    sections = [
        "# 第 7 项：支付工具与数据核查",
        "本次补充定义：A/B/C 分别沿用主表 (1)/(2)/(3) 的变量清单，再增加 fin25e1。"
        "此定义经本次任务确认，不是从上游仓库找到的既定方程。fin25e1 衡量日常食品/清洁用品的数字付款习惯，不区分手机和卡。",
        "## 先看主要设置 B 的结果（每周相对少于每月）",
        markdown_table(["阶段", "同样本基准(pp)", "+fin25e1 (pp)", "按 95% 区间判断"], headline_rows),
        "不能仅因点估计保持正值就称所有结论稳健；请同时看区间和 p 值。差距缩小也不证明 fin25e1 在因果上解释了差距。",
        "原主模型的筛选、国家固定效应、wgt、按国家聚类的误差计算全部复用。下表的‘原结果’使用原共同样本；"
        "‘同样本基准’和‘+fin25e1’都仅使用 fin25e1=1/2 的相同受访者。先看样本改变，再看加入新信息的改变。"
        "阶段 1 的‘被联系’具体指过去 12 个月收到陌生人索款电话或信息，问卷未独立核实诈骗。"
        "阶段 2/3 的转钱针对最近一次此类联系，不能直接说成核实的全年诈骗损失。",
        "## 人数与事件数",
        markdown_table(["阶段", "原 N", "比较 N", "fin25e1 排除人数", "原事件数", "比较事件数", "国家数 原/比较"], count_rows),
        "## 每周相对少于每月（beta_W）", _effect_table(summary, "beta_W"),
        "## 每月相对少于每月（beta_M）", _effect_table(summary, "beta_M"),
        "## 每周相对每月（beta_W - beta_M）", _effect_table(summary, "beta_W_minus_beta_M"),
        "差距和区间的单位是百分点，方括号为 95% 区间；p 值检验的是该模型内的组间差距。"
        "‘加入后差值变化’只是两个模型点估计相减，未作两模型差异的显著性检验。",
        "## 模型预测比例", _probability_table(summary),
        "预测比例：把同一批人的付款频率依次设为每周、每月、少于每月，再按 wgt 汇总。"
        "同样本基准没有加入 fin25e1；在‘+fin25e1’模型中，该项保留受访者的实际回答。",
        "## fin25e1 自身的关联（是相对否）",
        markdown_table(["阶段", "设置", "差值 [95% CI], p"], habit_rows),
        "## age=100 核查后的补算（主要设置 B）", _age_table(summary),
        "官方复现代码在年龄分组中将 100 视为缺失。此表分别给出原设定、同样本基准、增加 fin25e1 三者的年龄敏感性结果，"
        "不把 99 一并删除。原主表保持原年龄口径，以便团队逐项核对。",
        "## 文件与单位",
        "`summary.csv` 和 `coefficients.csv` 保留模型的原始比例尺度（0.01 = 1 个百分点）；"
        "`comparison.csv` 中名字以 `_pp` 结尾的列已乘 100。`answer_audit.csv` 包括未知和未提问记录；"
        "`age_audit.csv`、`age_by_economy.csv` 给出年龄核对。`manifest.json` 记录输入 SHA-256、源码和运行版本。",
        "可用于正文的中英文段落见 [measurement_limitations.md](measurement_limitations.md)。"
        f"原题及出处见 [codebook_audit.md]({docs_link}/codebook_audit.md)。",
    ]
    (output_dir / "report.md").write_text("\n\n".join(sections) + "\n", encoding="utf-8")
    (output_dir / "measurement_limitations.md").write_text(measurement_limitations(tables, docs_link), encoding="utf-8")
    # Invalidate a previous validation record whenever results are regenerated.
    (output_dir / "validation.csv").unlink(missing_ok=True)
    manifest["output_sha256"] = {
        name: hashlib.sha256((output_dir / name).read_bytes()).hexdigest()
        for name in [*[f"{name}.csv" for name in tables], "report.md", "measurement_limitations.md"]
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
