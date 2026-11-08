# Task 7: measurement limitations / 测量局限

## English text for the report

The payment measures combine mobile-phone and card payments and do not distinguish between the two instruments. The questionnaire wording of fin25e1 concerns typical payment for household food or cleaning supplies, whereas fin25e3 concerns the frequency of digital in-store purchases. These measures capture related but distinct aspects of payment behaviour. The fin25e3 interviewer instruction assigns a response of never to less than monthly. Thus that reference category does not necessarily imply current occasional use. We therefore add the binary fin25e1 indicator as an additional covariate rather than interpret it as a phone-versus-card comparison or a measure of payment frequency. Because fin25e1 and fin25e3 are related contemporaneous behaviours, this adjustment is a sensitivity comparison; it does not establish that fin25e1 is a pre-existing confounder or that the augmented model is less biased.

For this supplement, A/B/C are explicitly defined as the project's existing specifications (1)/(2)/(3), each augmented with fin25e1 (yes=1, no=0). These labels were adopted for this task and were not specified in the upstream repository. We exclude don't-know, refusal and missing responses to fin25e1, reducing the common sample from 16,251 to 16,235. Each augmented model is compared with its unaugmented counterpart on exactly the same respondents. A difference between these fitted coefficients is reported descriptively and is not itself a significance test.

The outcome items are self-reported. con21 records a call or message from an unknown person asking for money in the past 12 months; it does not independently verify fraudulent intent. Sending money is likewise not independent confirmation of a fraud loss. The project uses these items as proxies for scam contact and sending. For respondents with multiple contacts, the con22 interviewer instruction refers to the most recent such contact; it does not establish total losses or whether any money was sent over all contacts in the year. con23 concerns unwanted and offensive messages, photos or videos, and does not establish a request for money or a monetary loss. It is documented here but not substituted for a scam outcome or included as a control in the Task 7 regressions.

Age requires a separate coding qualification. The public codebook describes age in years but does not label the value 100. The World Bank reproduction code maps age through agenumber to wp1220 and explicitly treats wp1220=100 as missing when constructing age categories. The legacy common sample contains 6 such records. We retain the legacy model for reproducible comparison and separately report the main-specification results after treating 100 as missing. The inspected code establishes a rule for its age categories, but does not establish whether the raw value 100 is a true age, a nonresponse code or another convention. It also gives no basis for deleting age=99. Results should not describe age=100 observations as verified centenarians. The shared main pipeline still retains these records; adopting the alternative rule project-wide would require regenerating its tables.

All estimates inherit the project's survey weights, country fixed effects and country-clustered inference. They describe associations within the selected sample of phone owners with digital in-store payment experience. Pooled predictions under the inherited wgt weighting are not automatically population-weighted rates for all adults worldwide. They do not identify a causal effect, and a non-significant conditional-sending estimate does not establish equivalence or the absence of an association.

For the main specification B, the matched-sample comparisons are as follows. Stage 1: reported scam contact: the weekly contrast changes from 5.46 to 4.57 percentage points (augmented-model 95% CI: 2.26 to 6.87 percentage points; p < 0.001). Stage 2: sending money conditional on reported contact: the weekly contrast changes from 1.69 to 1.28 percentage points (augmented-model 95% CI: -1.68 to 4.24 percentage points; p = 0.393). Stage 3: reported contact and sending money: the weekly contrast changes from 1.16 to 0.92 percentage points (augmented-model 95% CI: -0.04 to 1.88 percentage points; p = 0.060). The augmented Stage 3 weekly contrast includes zero in its 95% interval. Evidence for the joint outcome is therefore sensitive to this adjustment at the 5% threshold; this is not evidence that the true association is zero.

## 中文说明

fin25e1 同时包括手机和卡，不能据此比较‘手机付款比刷卡更危险’。它问的是通常购买家庭食品或清洁用品时怎样付款，不能把它解释成每周付款频率。我们在现有三种设置中额外考虑这项付款习惯，并让增加前后的模型使用完全相同的人。这两个问题反映同一时期的相关习惯，多加一个因素不代表一定更接近因果关系。fin25e3 的访员说明还把‘从不’归入‘低于每月’，所以这一组不能都称为目前偶尔付款的人。

con21 问陌生人是否索款，问卷没有另外核实对方确实是骗子；汇钱也不等于已经核实的诈骗损失。con23 问的是不受欢迎且冒犯性的内容，不等于诈骗联系或损失。con22 在多次联系情况下只问最近一次，因此第三阶段也不能直接解释为全年所有诈骗中的总受害率。

age=100 的官方处理依据来自复现代码，不能仅凭网页标出的数值范围判断它是实际年龄。本补充保留原结果供核对，并单独列出按缺失处理后的结果；主程序尚未统一改用这一年龄规则。

## 主要结果（B；每周相对少于每月，单位为百分点）

Stage 1 被联系：同样本基准 +5.46 [+2.99, +7.92], p < 0.001；加入 fin25e1 后 +4.57 [+2.26, +6.87], p < 0.001。

Stage 2 被联系后转钱：同样本基准 +1.69 [-1.05, +4.43], p = 0.222；加入 fin25e1 后 +1.28 [-1.68, +4.24], p = 0.393。

Stage 3 被联系且转钱：同样本基准 +1.16 [+0.22, +2.09], p = 0.016；加入 fin25e1 后 +0.92 [-0.04, +1.88], p = 0.060。

## Sources

完整原题、页码、官方代码链条及链接见 [codebook audit](../../Docs/task7/codebook_audit.md)。A/B/C 定义及运行方式见 [Task 7 integration](../../Docs/task7/README.md)。
