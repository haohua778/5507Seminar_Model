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

在项目根目录运行，结果写到 `Output/`：

```bash
python run_pipeline.py    # 样本漏斗、三个 Stage、九个主回归
python run_checks.py      # 估计器交叉验证
```

## 目录结构

```text
5507Seminar_Model/
├── run_pipeline.py              入口：跑完整个分析
├── run_checks.py                入口：交叉验证估计器
├── DataBase/                    原始数据，只读
│   ├── Data_Source.csv
│   └── GlobalFindexDatabase2025.xlsx
├── DataClean_Pipeline/          第一步：构建样本
│   ├── build_sample.py          四道门槛、变量编码、公共样本
│   └── basic_check.py           早期的数据探查脚本
├── Model_Pipeline/              第二步：估计并写出结果
│   ├── stages.py                三个 Stage 的样本与结果变量，三个设定
│   ├── lpm.py                   加权 LPM，国家固定效应，按经济体聚类（statsmodels）
│   ├── results.py               每个 Stage 的预测概率、差值与检验
│   └── report.py                写出 CSV 和 Markdown 报告
├── Output/                      结果，可以随时重新生成
│   ├── sample_flow.csv
│   ├── main_results.md          九个主回归与解读
│   ├── stage_results_2026-09-27.pdf   当天结果的 PDF 快照，不随 run_pipeline.py 更新
│   ├── stage1_contact/          report.md、summary.csv、coefficients.csv
│   ├── stage2_send/
│   └── stage3_joint/
├── README.md
└── requirements.txt
```

数据流向：`DataBase` → `DataClean_Pipeline` → `Model_Pipeline` → `Output`。

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
| scipy | `from scipy import stats` | 只在 `run_checks.py` 里核对置信区间 |
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

不要复制或提交 `.venv`。`run_pipeline.py` 和 `run_checks.py` 按项目根目录定位数据，迁移后不用改路径；`basic_check.py` 用的是本机绝对路径，迁移后需要调整。

参考：[VS Code Python 环境](https://code.visualstudio.com/docs/python/environments)、[pip 用法](https://pip.pypa.io/en/latest/user_guide/#running-pip)。
