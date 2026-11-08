# Python 环境使用说明

本项目使用 Python 3.12，虚拟环境位于项目根目录的 `.venv`。依赖版本记录在 `requirements.txt` 中。

## 在 VS Code 中使用

1. 用 VS Code 打开整个 `5507Seminar_Model` 文件夹。
2. macOS 按 `Cmd + Shift + P`，运行 `Python: Select Interpreter`。
3. 选择项目的 `.venv/bin/python`。如果列表没有它，选择 `Enter interpreter path...` 并定位到该文件。
4. 新建终端，在项目根目录运行：

   ```bash
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   python run_pipeline.py
   ```

`.vscode/settings.json` 已配置默认环境；如果此前选过其他解释器，仍需按上述步骤手动切换一次。

## 运行建模流程

在项目根目录运行，结果写到 `Output/`。四个入口按顺序执行：

```bash
python run_pipeline.py      # 样本漏斗、三个 Stage、九个主回归 -> Output/；论文数字核对 -> Output/analysis/
python run_checks.py        # 估计器交叉验证，只打印不写文件
python run_analysis.py      # 按频率的描述统计、图 1、联合差异分解、图 2 -> Output/analysis/
python run_robustness.py    # 六个频率系数的 wild cluster bootstrap -> Output/robustness/
```

`run_analysis.py` 和 `run_robustness.py` 依赖 `run_pipeline.py` 写出的 `Output/<stage>/`。
单独跑其中一步用模块方式，例如：

```bash
python -m Analysis_Pipeline.joint_decomposition
```

## 目录结构

```text
5507Seminar_Model/
├── run_pipeline.py              入口：样本与九个主回归，以及论文数字核对
├── run_checks.py                入口：交叉验证估计器
├── run_analysis.py              入口：描述统计、两张图、联合差异分解
├── run_robustness.py            入口：稳健性检验
├── DataBase/                    原始数据，只读，不上传
│   ├── Data_Source.csv
│   └── GlobalFindexDatabase2025.xlsx
├── DataClean_Pipeline/          第一步：构建样本
│   ├── build_sample.py          四道门槛、变量编码、公共样本
│   └── basic_check.py           早期的数据探查脚本
├── Model_Pipeline/              第二步：估计并写出主结果
│   ├── stages.py                三个 Stage 的样本与结果变量，三个设定
│   ├── lpm.py                   加权 LPM，国家固定效应，按经济体聚类（statsmodels）
│   ├── results.py               每个 Stage 的预测概率、差值与检验
│   └── report.py                写出 CSV 和 Markdown 报告
├── Analysis_Pipeline/           第三步：主结果之外的分析
│   ├── descriptives_by_frequency.py    按支付频率分组的描述统计、国家内差异
│   ├── figure1_between_within.py       图 1：国家间 vs 国家内
│   ├── joint_decomposition.py          联合差异分解（全量样本），delta method 与 WCB 区间
│   ├── figure2_predicted_probabilities.py  图 2：三个 Stage 的预测概率
│   ├── paper_targets.py                论文数字核对的公共函数：计算值与论文值的对照表
│   ├── descriptives_full_sample.py     Table 2 全样本列：加权均值、年龄标准差、三组份额
│   ├── economy_composition.py          3.4 节：经济体层面的接触率、联合事件率与频率构成
│   ├── cluster_sizes.py                3.6 节：各经济体样本量、汇款者集中度、无汇款者的经济体
│   ├── decomposition_checks.py         3.5、4.2 节：拟合值越界比例、截断后的乘积差、交互项归属
│   └── stage2_power.py                 4.2 节：Stage 2 的最小可检测差异与 TOST 等价性检验
├── Robustness_Pipeline/         第四步：稳健性
│   └── wild_cluster_bootstrap.py       六个频率系数的 WCR wild cluster bootstrap
├── Output/                      结果，可用上面四个入口重新生成
│   ├── sample_flow.csv
│   ├── main_results.md          九个主回归与解读，含 Y 的均值和 R²
│   ├── main_results_table.md    论文用主结果表（9 列，系数、聚类标准误、星号、底部行），.csv 同内容
│   ├── stage1_contact/          report.md、summary.csv、coefficients.csv
│   ├── stage2_send/
│   ├── stage3_joint/
│   ├── analysis/                run_analysis.py 的输出和 run_pipeline.py 的论文数字核对，见其中的 README.md
│   ├── robustness/              run_robustness.py 的输出
│   └── archive/                 按日期归档的快照（PDF、截图、9/30 组会、10/9 期中），见其中的 README.md
├── Memo/                        交给教授的 Progress Memo，含个人信息，不上传
├── README.md
└── requirements.txt
```

数据流向：`DataBase` → `DataClean_Pipeline` → `Model_Pipeline` → `Output`；`Analysis_Pipeline` 和 `Robustness_Pipeline` 复用前两步的样本和估计器，结果写到 `Output/analysis/` 和 `Output/robustness/`。

论文正文里引用的、主表之外的数字（Table 2 全样本列、3.4 节经济体构成、3.6 节簇大小、3.5 和 4.2 节的分解检查与功效）由 `run_pipeline.py` 末尾的五个核对模块复现。每个模块把论文里的数字写成目标值，用数据重新计算后打印对照表，并汇总到 `Output/analysis/paper_number_checks.md`；对不上的行标为 NO，不调整定义去凑。

## 以后安装其他包

在项目根目录激活环境后安装，例如：

```bash
source .venv/bin/activate
python -m pip install matplotlib
```

这里的 `matplotlib` 只是安装示例，本次配置未安装它。项目实际需要的新依赖应补充到 `requirements.txt`。

安装名与代码中的导入名不一定相同，本项目使用：

| 安装名 | 导入方式 | 用途 |
| --- | --- | --- |
| numpy | `import numpy as np` | 数组与数值计算 |
| pandas | `import pandas as pd` | 表格数据处理 |
| statsmodels | `import statsmodels.formula.api as smf` | 回归与聚类标准误 |
| scikit-learn | `import sklearn` | 只在 `run_checks.py` 里核对系数 |
| scipy | `from scipy import stats` | t 分布分位数：`run_checks.py`、分解、bootstrap |
| matplotlib | `import matplotlib.pyplot as plt` | `Analysis_Pipeline/` 的两张图和 bootstrap 的图 |
| wildboottest | `from wildboottest.wildboottest import wildboottest` | 只在 `Robustness_Pipeline/` 里核对 bootstrap |
| openpyxl | 通常由 pandas 自动调用 | 读取 `.xlsx` 文件 |

如果遇到 `ModuleNotFoundError`，先确认 VS Code 选择的解释器与终端安装包使用的 Python 一致：

```bash
python -c "import sys; print(sys.executable)"
python -m pip --version
```

输出路径应指向本项目的 `.venv`。也可以直接使用 `.venv/bin/python -m pip install 包名`，明确指定安装位置。

## 在其他电脑重建环境

安装 Python 3.12 后，在项目根目录运行（下面假设命令名为 `python3.12`）：

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

不要复制或提交 `.venv`。四个入口脚本按项目根目录定位数据，迁移后不用改路径；`basic_check.py` 用的是本机绝对路径，迁移后需要调整。

参考：[VS Code Python 环境](https://code.visualstudio.com/docs/python/environments)、[pip 用法](https://pip.pypa.io/en/latest/user_guide/#running-pip)。
