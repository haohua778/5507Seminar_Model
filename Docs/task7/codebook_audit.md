# 第 7 项原题与年龄编码核查

核查日期：2026-10-24。证据来自世界银行官方 Microdata Library 与 Reproducible Research Repository。
来源地址、文件哈希、相关页码和官方代码位置记录于 [sources.json](sources.json)。
以下页码为 PDF 页序，从 1 开始。

## fin25e1

Codebook 第 15 页标签原文：

> Use a mobile phone or card to pay for household cleaning supplies

金融问卷第 11 页，FIN25E_1 / WP24004 的完整题目：

> Do you typically use a mobile phone or card to pay for household food or cleaning supplies? Yes or no?

中文：你通常是否使用手机或卡为家庭食品或清洁用品付款？

| 数字 | 原答案含义 | 本补充处理 |
|---|---|---|
| 1 | 是 | T=1 |
| 2 | 否 | T=0 |
| 3 | 不知道 | 从增加 T 的比较样本中排除 |
| 4 | 拒答 | 同上 |
| 空白 | 未提问或缺失 | 同上，不归为否 |

Codebook 说明该题针对有银行或移动货币账户的受访者。
问卷实际文字包括食品和清洁用品，且问的是通常的习惯；标签将其简写为清洁用品。
手机与卡在同一个答案里，不能区分二者，也不能识别具体支付 App、交易金额或付款次数。
回答“否”只是否认这种通常习惯，不能推断此人从不使用数字付款。
原项目筛选的 fin25e2 是过去 12 个月是否曾有店内数字付款，fin25e3 才是付款频率。
金融问卷第 11 页的 fin25e3 访员说明要求把回答“never”的人记入“less than once a month”；
因此低频参照组包括当前回答“从不”的人，不能全部解释成当前偶尔付款。

来源：[Microdata Codebook](https://microdata.worldbank.org/catalog/7860/download/351895)，
[金融问卷](https://microdata.worldbank.org/catalog/7860/download/351896)。

## con23

Codebook 第 27 页标签原文：

> Received unwanted or offensive messages

Connectivity 问卷第 5 页，CON23 / WP24046 的完整题目：

> In the PAST 12 MONTHS, have you received unwanted and offensive messages, photos or videos to your mobile phone?

中文：过去 12 个月，你的手机是否收到过不受欢迎且冒犯性的消息、照片或视频？

1=是，2=否，8=不知道，9=拒答；仅向有手机者提问。
注意标签用的是“or”，原问卷用的是“and”；本说明按实际问卷表述解释。
这道题没有要求存在索要钱财、诈骗企图或转账，因此不能将其直接命名为“收到诈骗信息”。
本任务只核对题目与回答分布，不将 con23 加入 fin25e1 补充回归，也不因为 con23=8/9 排除其他有效记录。

同页 CON22 的访员说明还规定：遇到多次陌生人索款联系，回答时以最近一次为准。
这意味着项目 Stage 2/3 的“转钱”不能等同于全年所有联系中是否曾转钱，也不能衡量损失总金额。
CON21 的题目只记录陌生人索款，没有独立核实诈骗意图；CON22 的转钱也没有独立核实为诈骗损失。
项目的 scam 标签是对这些问卷指标的研究解释，不应写成警方或其他渠道核实的诈骗事件。

来源：[Microdata Codebook](https://microdata.worldbank.org/catalog/7860/download/351895)，
[Connectivity 问卷](https://microdata.worldbank.org/catalog/7860/download/356084)。

## age=100：追到官方处理代码

公开 Codebook 第 2 页仅把 age 描述为以年计的受访者年龄，没有单独列出 100 的标签。
[官方 age 页面](https://microdata.worldbank.org/catalog/7860/variable/F1/V9?name=age)
列出数值范围 15–100，并将 144,090 条数值都列为 valid。这是数值存储统计，不能单独证明 100 是真实年龄。

向上追溯的证据链：

1. [官方变量命名脚本](https://microdata.worldbank.org/catalog/7860/download/351894)第 21 行，将公开的 age 赋为 agenumber。
2. [官方复现包](https://reproducibility.worldbank.org/catalog/299/download/912/FR_WLD_2025_361.zip)中的
   `Code/Cleaning/Identifiers.R` 第 278 行，将 agenumber 赋为 wp1220。
3. 同包 `Code/Cleaning/core_variables_gwp.R` 第 613–620 行定义 age_category，
   第 615 行明确把 wp1220 等于 100 的情况赋为缺失；第 627 行的另一种年龄分组也一样。

关键代码原文：

```r
age = agenumber
agenumber = wp1220
wp1220 == 100 ~ NA_real_
```

**核查结论：在年龄建模中将 100 当缺失，有官方处理代码依据；不能将它解释为已核实的 100 岁。**
这一依据只证明官方在上述年龄分类步骤中的做法，不能单独证明原始 age=100 一律是无效年龄。
本次查到的文件没有说明 100 究竟是真实年龄、未回答编码还是其他约定，因此不做更具体的标签判断。
也没有依据把 99 作为缺失码一并剔除。

官方包中部分早期脚本直接对 wp1220 进行年龄比较，并未统一删除 100；
因此这里准确引用的是 core_variables_gwp.R 的显式年龄分类规则，不声称所有官方输出都已删除 100。

本地原始数据：age=100 共 279 人；原共同样本中 6 人。age=99 在共同样本中有 2 人。
本补充保留原主程序默认规则用于历史对照，并另算排除 100 的主要设置。具体人数由运行时 CSV 审计文件记录。
如项目后续统一采用修正年龄规则，应更新共同样本与所有依赖结果，而不是只改报告数字。

## 资料与本地数据是否对应

官方 v02 元数据列出 144,090 人，fin25e1 的 1/2/3/4/缺失计数为
19,873 / 38,899 / 97 / 57 / 85,164；con23 对应为
8,181 / 56,296 / 162 / 24 / 79,427。它们与本地 CSV 的核对一致。
这些分布相同支持变量级对应，但不等于验证了每行数据与官方原始下载文件逐字节相同。
本补充用本地 CSV 的 SHA-256 固定实际输入；不会把网页 valid 分类当作缺失值处理规则。

## GitHub 中的方程查找

检查了 [仓库](https://github.com/haohua778/5507Seminar_Model) main 分支、全部已发布提交、README、Python 文件、
结果 Markdown 和 PDF，以及 Issues/PR 列表。未找到 fin25e1 稳健性方程 A/B/C。
本次经用户确认的定义在 [README.md](README.md) 中明确列出。
