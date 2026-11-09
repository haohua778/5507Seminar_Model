# 第 7 项：支付工具 + 数据

任务要求：核对 fin25e1、con23 的原题，查清 age=100，运行 fin25e1 补充方程 A/B/C，并撰写测量局限。

## A/B/C 的来源和定义

2026-10-24 核查上游 `haohua778/5507Seminar_Model`：只有 main 分支，HEAD 为
`163c57b71121739ddda5df9c34d9659e2128cf24`；两次提交，没有 Issues 或 PR，Discussions 未启用，Wiki 仓库不可读取。
README、源码和结果 PDF 均没有第 7 项 A/B/C 方程定义。
本次任务中，用户明确确认以下补充定义。**不能写成“原项目已经规定的 A/B/C”。**

令 T=1 表示 fin25e1=1，T=0 表示 fin25e1=2。不知道、拒答、空值不当作 0。
W、M 是原项目的 weekly、monthly；少于每月为参照。Y 分别沿用三个 Stage 的 outcome。

| 补充方程 | 右侧变量 | 对应原设置 |
|---|---|---|
| A | W + M + T + 国家固定效应 | (1) 增加 T |
| B | W + M + T + DEMOGRAPHICS + 国家固定效应 | (2) 增加 T；主要设置 |
| C | W + M + T + DEMOGRAPHICS + DIGITAL + 国家固定效应 | (3) 增加 T |

所有方程使用原 `wgt`、加权线性概率模型、按经济体聚类的标准误、经济体数减 1 自由度的 t 推断。
不将 T 称为手机/卡的工具类型变量，也不把它作为工具变量（instrumental variable）。

每个阶段/设置给出三列对照：

1. `original`：原共同样本上的原方程，复现原项目结果。
2. `same_sample`：只保留 fin25e1=1/2，在这批人上重跑原方程。
3. `fin25e1_added`：同一批人，额外加入 T。

`same_sample` 和 `fin25e1_added` 的参与者必须完全相同。
这使样本筛选变化与新增变量变化可以分别查看。原 `comparison.csv` 中的系数变化仅作描述；新增的跨模型差值检验见下文。
con23 在本任务仅核查题目和分布；未增加其他组负责的 placebo 回归。

## 年龄处理

官方复现程序给出 `wp1220=100` 在年龄分类中设为缺失的直接依据，详见
[codebook_audit.md](codebook_audit.md)。原主模型保留 100，作为历史对照继续保留这一默认行为。
本补充单独将 100 设为缺失，再调用原 `build_common_sample()`，并重跑主要设置 B 的三个阶段，
分别展示原设定、fin25e1 同样本基准和增加 T 的结果。不将 99 一并删去。

因此完整运行包含 27 个常规模型（3 阶段 × 3 设置 × 3 对照）以及 9 个年龄处理模型。
年龄核查完成不等于主项目全部表格已迁移到新年龄口径；团队若采用修正后的主样本，需统一更新主表。

## 与现有项目的连接

- `DataClean_Pipeline/payment_tools.py` 一次读取原清单及 fin25e1/con23，保留行索引，调用现有筛选函数。
- `Model_Pipeline/payment_tools.py` 复用原 STAGES、SPECS、estimate_stage 和 lpm.py；不复制回归公式实现。
- `results.estimate_stage()` 新增可选关键字参数 `specifications`；不传时与原入口相同。
- `Model_Pipeline/payment_tools_report.py` 输出 CSV、中文结果说明和中英文测量局限段落。
- `run_payment_tools.py` 是独立补充入口，默认只写 `Output/payment_tools/`。
- 原 `run_pipeline.py`、Logit 扩展、原始数据及原主结果文件不由此入口改写。

## 运行

使用原项目 Python 3.12 环境及 requirements.txt 中的依赖，无新增第三方包。
先将个人微观数据放到 `DataBase/Data_Source.csv`；也可传 `--data` 指定该文件。
`GlobalFindexDatabase2025.xlsx` 是国家级汇总表，不能替代个人微观数据或 codebook。

```bash
python run_payment_tools.py
python -m unittest discover -s tests -p 'test_payment_tools.py' -v
python run_payment_checks.py
# 可选：原主表也使用同一份数据时，再核对历史主表
python run_payment_checks.py --main-output Output
python run_checks.py
```

可选输入/输出路径：

```bash
python run_payment_tools.py --data /absolute/path/Data_Source.csv --output /absolute/path/payment_results
python run_payment_checks.py --data /absolute/path/Data_Source.csv --output /absolute/path/payment_results
```

本地数据可以是指向原文件的链接，程序只读；原始数据不应提交到 Git。

## 交付文件

- [结果报告](../../Output/payment_tools/report.md)：三阶段 A/B/C 对照、预测比例、T 自身系数、年龄敏感性。
- [测量局限](../../Output/payment_tools/measurement_limitations.md)：英文可用于正文，附中文说明。
- [原题与年龄证据](codebook_audit.md)：原文、编码、提问对象、来源和证据边界。
- [可编辑演示幻灯片](task7_payment_tools.pptx)：三页英文 slide，涵盖题目定义、A/B/C 结果和主要设置 B 的同样本比较；来源写入演讲备注。
- `Output/payment_tools/summary.csv` / `coefficients.csv`：未四舍五入的模型结果。
- `comparison.csv`：样本变化、新增 T 各自造成的点估计变化。
- `sample_counts.csv` / `sample_flow.csv`：人数、国家数和事件数。
- `answer_audit.csv` / `age_audit.csv` / `age_by_economy.csv`：原始数据与分析样本的分布核对。
- `manifest.json`：数据与源码 SHA-256、软件版本和模型定义。
- `validation.csv`：运行 `run_payment_checks.py` 后生成的核对记录。
- `model_shift.csv` / `model_shift.md`：后续增做的主设置 B 同样本模型间系数变化检验；与原结果报告分开保存。

## 后续深入研究：模型间差值检验

原对照表只把两个模型的系数相减，没有检验这个变化是否明显。新增入口
`python run_payment_shift.py` 在同一批受访者上拟合主设置 B 的原方程和增加 fin25e1 的方程，
按经济体把两次估计的误差配对，计算“增加前后每周差距变化”的标准误、95% 区间和 p 值。
三个阶段分别计算；结果见 [model_shift.md](../../Output/payment_tools/model_shift.md)。
这仍是观察数据中的关联变化，不说明 fin25e1 在因果上造成差距缩小。

模型 CSV 中 estimate、se、ci_low、ci_high 是比例尺度；乘 100 才是报告的百分点。
P 开头的 estimate 乘 100 后为百分比。comparison 中 `_pp` 后缀已经是百分点，不能再乘 100。
预测比例按该比较样本的实际人口特征、国家和 T 分布加权汇总；不是原始分组发生率。

数据引用：World Bank, Development Research Group, Finance and Private Sector Development Unit.
The Global Findex Database 2025: Connectivity and Financial Inclusion in the Digital Economy,
WLD_2024_FINDEX_v02_M. 官方资料核对日期 2026-10-24。

## 复核范围

检查程序独立用 NumPy 重算全部 36 个模型，再与实际保存的 summary.csv 和 coefficients.csv 逐项比较，
涵盖预测比例、全部控制变量系数、三个组间差距、完整聚类协方差对应的标准误、95% 区间和 p 值。
同时从输入重新核对人数、事件数、经济体数、样本流程、回答与年龄分布，以及比较表。
默认不依赖历史主表，因而支持 --data 指定新数据；只有显式传入 --main-output 时才比较历史主表。
若复核异常中断，旧 validation.csv 会先被清除，避免把上次通过记录误当成本次通过。
验证测试包含故意改错预测比例、p 值、区间、系数和删除记录，确保检查能识别这些问题。

本次查错、修改及验证范围见 [复核记录](review.md)。
