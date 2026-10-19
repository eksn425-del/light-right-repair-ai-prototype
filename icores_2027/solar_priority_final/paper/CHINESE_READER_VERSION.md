# 日照优先候选筛选：完整中文通俗解释与结果解读

## 一、先说结论

这轮实验已经真实运行。结论是：目前不应把新的筛选清单直接包装成全面优于原来45/35/15/5的替代方案。六种预先规定的实验情景，没有一种通过全部“支持替换”的判定条件。这个结果必须保留，不能为了论文创新改门槛。

但“没有通过替换条件”不等于毫无收获。新方法在两种“日照权重合计至少70%或80%”的情景中，保留最优候选的能力确实更好；它对不同偏好的前十名覆盖也略有改善。然而改善幅度较小，部分情景还牺牲了另一项日照指标，而且新增方案不一定已经有Honeybee专业复核。因此，我们保留上一轮正式论文原件，本轮新增的是完整实验报告、失败与权衡解释、可选择的修订建议，供作者决定如何修改，而不是冒称新投稿终稿已通过科学验收。

## 二、建筑师真正要解决什么

研究对象是旧街区日照不足。我们已有630个受约束的双建筑减高组合，希望用计算比较这些组合，先找到日照改善有价值的选择，再控制建筑干预，最后交给建筑师选方案、深化设计。

这630个组合只是规则生成的候选。它们不是630套完成设计，也不是十套已验证可以施工的建筑。筛选的作用是缩小进一步研究范围，不能代替建筑师判断空间、结构、使用、法规、成本、居民影响与实施条件。

指标含义如下：
- A：低日照面积减少量，单位平方米。越大，意味着更多原本日照不足的面积得到改善。
- H：平均日照时长增益，单位小时。它与A有关，但并不是同一个指标。
- V：名义建筑改动体积，单位立方米。越小表示规则层面的干预体量较少；不能把它直接解释为预算、拆迁成本或施工难度。
- N：新增低日照面积。本轮核查630个候选均为0，因此它不能区分候选名次，但仍须作为后续几何设计转译的有效性检查。

## 三、原45/35/15/5与新方法有什么区别

旧方法先把指标按冻结的全场范围归一化，再采用固定分值：0.45A + 0.35H + 0.15(1−V) + 0.05(1−N)。这里的字母代表归一化值，不是原始平方米、小时和立方米直接相加。因为N恒为0，最后一项对所有候选相同。真正影响排序的三项权重相当于9/19、7/19、3/19。

这组数是一种明确的偏好假设，没有经过专家群体验证，不能说是行业公认标准。但“未经专家验证”并不意味着原清单没用，也不意味着换一套复杂算法就一定更好。

本轮新方法不只看一个固定权重，而是先规定允许怎样重视A、H和V，再统计每个候选在这些偏好下进入前十的频率，选出十个最常进入前十的候选。这样做优化的是“在不同偏好下，尽量保留更多高排名选择”。

另一个保护版本会先保留训练样本里出现过的所有第一名，再补足十个名额。若训练中第一名的种类超过十个，就明确报告不可行，不放宽规则。实际六个情景中，普通版本与保护版本选出了相同集合。这并不证明两个目标普遍相同，只是本数据中的结果。

上一轮Robust10优化的是避免错失最佳效用，即决策遗憾。它可以保住第一名，却未必保住偏好下第二名至第十名。这是为什么本轮必须同时看“有没有第一名”和“十个高排名方案保留了多少”，不能只看零遗憾。

## 四、怎样定义“日照优先”

本轮冻结了六个情景，不能事后只挑最好看的一个。

1. ordered：wA≥wH≥wV≥0，三项之和为1。这是A权重最高、H其次、V最低。
2. solar70：A与H合计权重至少70%，即V权重不超过30%。
3. solar80：A与H合计权重至少80%，即V权重不超过20%。
4. A90_solar70：先要求A至少90平方米，再按solar70研究偏好。
5. A180_solar70：先要求A至少180平方米，再按solar70研究偏好。
6. A270_solar70：先要求A至少270平方米，再按solar70研究偏好。

70%、80%、90/180/270平方米都只是实验情景，不是法规，也不是经访谈确认的建筑师要求。权重总和限制不等于严格的“任何日照收益都压倒任何体量节省”的字典序优先，更不保证每个入选方案的A都足够大。尤其solar70和solar80没有规定A与H谁更重要，纯H权重也在允许范围内。因此，不能把这两个空间简单理解为“低日照面积改善优先”。

A阈值提高后，符合条件的候选分别剩166、50、12个。阈值越高，未必越好：它会剔除一些A较低但H表现有价值的选择。归一化范围始终使用原630个候选的冻结范围，没有按过滤后的数据重算。

## 五、怎样保证比较公平与数据真实

研究协议先提交GitHub，再产生新权重、排名和筛选结果。冻结提交为94ba70a567030b9736140b3c7ac69c6160e44d49。输入来自既有真实归档的630个候选，没有用AI生成观测数据。

每个权重空间使用20,000个训练样本、20,000个独立测试样本、20,000个独立重复验证样本。三个空间合计180,000个唯一权重。三个A门槛情景复用solar70的同一批权重，方便同条件比较，并不额外声称它们是新的独立样本。随机种子、抽样方法和规则在协议中固定。所有候选选择仅使用训练集，测试集不参与挑选。

比较六种方法：固定权重historical10、上一轮robust10、A/V Pareto后选十个的AV10、A/H/V Pareto后选十个的AHV10、coverage10、protected_coverage10。所有清单均为十个名额。

有A门槛时，旧清单若存在不合格项，会按协议形成明确标注的门槛适配版本；不能偷偷把适配版当作原来那份不变的清单。原清单有多少项违反门槛也单独记录。Pareto前沿超过十个时按预定排序截取，不足时按预定规则补足，不借用更多名额获得优势。

新计算在dot云端执行，用时约52.01秒。这个用时是本次归档数据决策分析的运行时间，不是新Honeybee/Radiance物理模拟时间，也不是整篇研究完成时间。

## 六、我们如何判断是否值得替换

在看结果前，规定新保护清单必须同时满足：
- 测试与重复验证中，Top-10平均恢复率各提高至少0.02，即2个百分点；
- 两个独立分组中的配对95%蒙特卡洛区间下界均为正；
- 最优候选覆盖、平均遗憾、连续权重空间最坏遗憾均不能出现协议所不允许的下降；
- 清单平均A与平均H各不得低于相应旧清单的95%。

2个百分点与95%同样是研究者预先规定的决策门槛，不能冒充专家认可的实际重要性标准。它们用于防止只凭一点点数字变化就宣布改进。

Top-10恢复率指：对于某个权重，如果630个候选中前十名与我们的十个清单重合七个，恢复率就是70%。它不是建模准确率，也不是正确建筑设计的百分比。

遗憾指：在某个权重下，全部合格候选的最佳归一化效用，减去十个清单中最佳效用。零遗憾只表示没有损失该效用下的最佳机会，不代表十项都优秀，更不代表任何一项可施工。

蒙特卡洛区间描述规定抽样分布下数值积分的精度；不能当作不同城市、真实建筑师偏好或物理模拟误差的置信区间。

## 七、最核心的独立测试结果

下表直接由本轮CSV生成；所有提升均为绝对百分点。新清单指保护版本，实际与普通coverage10相同。

| 情景 | 旧恢复率 | 新恢复率 | 测试提升/百分点 | 重复验证提升/百分点 | 旧第一名覆盖 | 新第一名覆盖 |
| --- | --- | --- | --- | --- | --- | --- |
| ordered | 89.4950% | 89.9380% | 0.4430 | 0.3815 | 100.000% | 100.000% |
| solar70 | 64.9650% | 66.0935% | 1.1285 | 1.0385 | 89.080% | 100.000% |
| solar80 | 65.5725% | 66.9465% | 1.3740 | 1.4770 | 84.435% | 100.000% |
| A90_solar70 | 64.9650% | 66.0935% | 1.1285 | 1.0385 | 89.080% | 100.000% |
| A180_solar70 | 69.3290% | 70.6795% | 1.3505 | 1.1640 | 89.080% | 100.000% |
| A270_solar70 | 99.6625% | 99.6625% | 0.0000 | 0.0000 | 100.000% | 100.000% |

解读：
- ordered里，旧清单本来就保留了所有规定偏好下的最佳机会，连续审计的最坏遗憾也为0。新清单恢复率只提高0.4430个百分点，重复验证提高0.3815个百分点，达不到2个百分点门槛，且平均H下降超过5%。因此不能宣布新方法更优。
- solar70里，第一名覆盖从89.080%提高到100%；solar80里，从84.435%提高到100%。这是明确的情景内价值，不应被“总体失败”掩盖。
- 但这两种情景的Top-10恢复率只提高1.1285和1.3740个百分点，仍达不到预定2个百分点门槛。solar80还使平均A下降超过5%。
- A90的结果与solar70在主要比较中相同，没有额外创造改善。
- A180恢复率提高1.3505个百分点，仍不足门槛，而且平均A下降超过5%。
- A270中，新旧集合完全相同，恢复率没有改善。

新方法在solar70/80的连续权重空间最坏遗憾为0，而旧固定清单约为0.019380。这比只检查有限随机样本更强，但仍是对当前固定630个候选、归一化方式和权重空间的结论，不是对任何城市或任何未来设计的保证。上一轮Robust10与AHV10在这两个空间的连续遗憾同样为0，因此“保住最优候选”本身也不能证明本轮选择器是唯一或全新的解决办法。

solar70的变化尤其具体：与旧清单九项相同，只把C9/C27换成C24/C35。后者有利于保留偏好H的最优机会，但会带来A与其他指标的权衡，而且缺少规则HB及转译复核。这更接近一个可解释的一项候选替换实验，不能写成全新算法带来的全面突破。

连续权重审计去重后实际执行了10,504次线性规划，26个不同的集合—空间—候选域组合；展开各方法标签后有12,708行见证记录。不能把重复标签行当作实际额外求解次数。

## 八、是否用更少建筑干预换掉了日照收益

不能只看一个综合分数。下表是清单十个候选的平均值，不是最终建筑师选中的一个方案，也不是物理模拟新测结果。

| 情景 | 清单 | 平均A/平方米 | 平均H/小时 | 平均V/立方米 | 已有规则HB数量 | 已有转译检查数量 |
| --- | --- | --- | --- | --- | --- | --- |
| ordered | historical10 | 309.600000 | 0.042491 | 4542.283978 | 10 | 3 |
| ordered | protected_coverage10 | 319.500000 | 0.038996 | 4378.828553 | 9 | 3 |
| solar70 | historical10 | 309.600000 | 0.042491 | 4542.283978 | 10 | 3 |
| solar70 | protected_coverage10 | 296.100000 | 0.044953 | 4427.400313 | 9 | 3 |
| solar80 | historical10 | 309.600000 | 0.042491 | 4542.283978 | 10 | 3 |
| solar80 | protected_coverage10 | 272.700000 | 0.050197 | 5350.608195 | 7 | 2 |
| A90_solar70 | historical10 | 309.600000 | 0.042491 | 4542.283978 | 10 | 3 |
| A90_solar70 | protected_coverage10 | 296.100000 | 0.044953 | 4427.400313 | 9 | 3 |
| A180_solar70 | historical10 | 309.600000 | 0.042491 | 4542.283978 | 10 | 3 |
| A180_solar70 | protected_coverage10 | 285.300000 | 0.046603 | 4388.590606 | 9 | 4 |
| A270_solar70 | historical10 | 323.100000 | 0.036091 | 4288.020817 | 8 | 3 |
| A270_solar70 | protected_coverage10 | 323.100000 | 0.036091 | 4288.020817 | 8 | 3 |

例如solar80不是简单“牺牲日照换少改造”：它的平均A从309.6降到272.7平方米，但平均H上升，平均V反而从4542.28增加到5350.61立方米。这说明A与H对“日照改善”的表达并不相同，强调平均时长可能需要更多干预，并牺牲低日照面积改善。不能把这种权衡简化成一种统一更好的方案。

ordered则表现为平均A上升、平均V下降，但平均H下降超过冻结的5%保护线。必须把三项一起给建筑师看。列表均值也不能代替逐项数据；完整十项原值在后附对照和shortlists_evidence.csv中保留。

## 九、最低A门槛也可能丢失好机会

A至少270平方米后只剩12个候选。从12个中挑10个很容易得到接近100%的恢复率。这种条件内高分不能与原630个空间直接比较，也不能用来证明过滤越严越好。

A270的旧新清单条件内遗憾都为0，但相对于完整630个候选，独立测试中的过滤机会损失平均约0.030440，观测最大约0.228607。门槛已经把某些对H更有利的候选排除掉，筛选器在剩余空间做得再好也无法追回。

本研究因此同时记录：过滤损失 + 合格候选空间内的清单遗憾 = 相对于完整630个候选的总遗憾。不能只展示中间那一项为0。

## 十、清单稳定性与复核证据

我们把训练权重拆成十块，每块2,000个，用同样规则独立选清单，并比较与完整训练清单的Jaccard相似度。测试与重复验证没有用于重新挑选清单。下表给出保护版本十个分块与完整清单的相似度分布：

| context | min | mean | max |
| --- | --- | --- | --- |
| A180_solar70 | 0.8181818181818182 | 0.890909090909091 | 1.0 |
| A270_solar70 | 1.0 | 1.0 | 1.0 |
| A90_solar70 | 0.8181818181818182 | 0.9454545454545455 | 1.0 |
| ordered | 1.0 | 1.0 | 1.0 |
| solar70 | 0.8181818181818182 | 0.9454545454545455 | 1.0 |
| solar80 | 0.6666666666666666 | 0.8939393939393939 | 1.0 |

相似度高只表示对当前抽样的选择稳定，不能证明对输入模型误差、建筑师偏好变化或新场地稳定。

复核证据更不能混淆：
1. 630项是规则减高候选；
2. 只有既有23个选择性样本与冻结20个覆盖样本有历史Honeybee/Radiance规则层复核；
3. 少数候选另有退台设计转译与包含性纠错证据；
4. 这些都不是结构、法规、造价及施工可行性批准。

本轮没有新跑HB/Radiance，没有替换冻结样本。新清单中缺规则HB结果的组合如下，需进入后续模拟队列，不能标成已验证：

- ordered：C9/C28。
- solar70：C24/C35。
- solar80：C24/C35；C24/C27；C24/C26。
- A90_solar70：C24/C35。
- A180_solar70：C24/C35。
- A270_solar70：C9/C28；C9/C20。

## 十一、理论依据与创新边界

SMAA-2、稳健序回归、最小最大遗憾、代表性集合、多准则决策分析已有成熟文献。本轮没有发明这些数学思想。coverage10的目标尤其简单：十项交集数量的平均值可以拆成各候选入选前十的概率之和，所以直接选择十个最大概率就是训练目标的精确最优解。这是加性目标的性质，不应包装成新的通用优化算法。

可写的真实贡献是：围绕建筑师的日照优先问题，明确不同优先定义，做同十名额、同候选、训练测试分离的比较，展示何时固定权重已经足够、何时会漏掉最优机会、何时提高覆盖需要付出A/H/V权衡，并把模拟与几何证据接到候选清单上。

不能声称：新方法普遍优于固定权重、证明建筑师偏好分布、得到十套施工方案、真实日照已全部复核、或者发现了全新的SMAA/Pareto算法。

## 十二、建筑师实际怎么用

第一步，明确日照目标：更关注“让多少低日照面积改善”，还是“平均时长增加”，或者两者都要？不要让权重名称代替真实讨论。

第二步，查看原固定权重清单作为可解释的起点，连同A/H/V原值及证据状态。若明确接受A≥H≥V的权重顺序，本轮没有支持全面替换它。

第三步，如果允许H显著高于A，可把solar70/80下的候选作为讨论补充，查看旧清单漏掉的高H机会。但要明确这是不同偏好下的比较，不宣称十项新集合全面胜出。

第四步，若确实要求最低A改善，先由作者或实际项目任务书确定要求，再看过滤会排除多少方案以及损失什么机会。本轮90/180/270仅是敏感性情景，不能直接当施工约束。

第五步，对考虑推进但未做HB的组合逐项补模拟，再做空间、结构和法规等设计深化。以最终设计几何重新验证日照，不把规则减高结果直接转移为退台方案真实性。

第六步，由建筑师最终选方案。算法交付的是有指标、有边界、有复核状态的候选证据，不替人做最终决定。

## 十三、论文现在怎么处理

本轮按预先规定的失败路径：保留上一轮正式英文稿与原始证据，不覆盖。另交英文实验补充报告、完整中文忠实译稿、本中文解释、全部数据与QA。

作者可选择的修订方向是“日照优先约束下的可解释候选筛选及偏好敏感性决策支持”。如采用这一方向，应把本轮正反结果写入叙事，清楚区分“太阳总收益权重约束”和“A优先”的不同含义；不要只把上一轮完全开放权重空间的优势换个标题说成日照优先创新。

这不意味着旧稿已经自动适合投稿。会议适配、最终论证结构、参考文献、匿名、AI披露、作者权利与学术声明仍需作者审核。没有自动提交PRIMORIS、付款或公开私有数据。

## 十四、完整独立测试对照表

以下保留六种方法、六种情景，不只展示新方法获益的部分。带A门槛情景中的旧方法按协议进行了适配，具体标志见shortlists_evidence.csv。这里的0遗憾是该情景合格集合内的值。

| context | set | top10_recovery | winner_coverage | regret_mean | regret_max | list_A_mean | list_H_mean | list_V_mean | rule_HB_count | translation_checked_count |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ordered | historical10 | 0.894950 | 1.000000 | 0.000000 | 0.000000 | 309.600000 | 0.042491 | 4542.283978 | 10 | 3 |
| ordered | robust10 | 0.444360 | 1.000000 | 0.000000 | 0.000000 | 208.800000 | 0.041630 | 3312.565625 | 7 | 2 |
| ordered | AV10 | 0.290815 | 1.000000 | 0.000000 | 0.000000 | 225.900000 | 0.029099 | 2414.392784 | 10 | 3 |
| ordered | AHV10 | 0.741410 | 1.000000 | 0.000000 | 0.000000 | 285.300000 | 0.046603 | 4388.590606 | 9 | 4 |
| ordered | coverage10 | 0.899380 | 1.000000 | 0.000000 | 0.000000 | 319.500000 | 0.038996 | 4378.828553 | 9 | 3 |
| ordered | protected_coverage10 | 0.899380 | 1.000000 | 0.000000 | 0.000000 | 319.500000 | 0.038996 | 4378.828553 | 9 | 3 |
| solar70 | historical10 | 0.649650 | 0.890800 | 0.000750 | 0.018651 | 309.600000 | 0.042491 | 4542.283978 | 10 | 3 |
| solar70 | robust10 | 0.456385 | 1.000000 | 0.000000 | 0.000000 | 208.800000 | 0.041630 | 3312.565625 | 7 | 2 |
| solar70 | AV10 | 0.211580 | 0.685050 | 0.030440 | 0.228607 | 225.900000 | 0.029099 | 2414.392784 | 10 | 3 |
| solar70 | AHV10 | 0.656835 | 1.000000 | 0.000000 | 0.000000 | 285.300000 | 0.046603 | 4388.590606 | 9 | 4 |
| solar70 | coverage10 | 0.660935 | 1.000000 | 0.000000 | 0.000000 | 296.100000 | 0.044953 | 4427.400313 | 9 | 3 |
| solar70 | protected_coverage10 | 0.660935 | 1.000000 | 0.000000 | 0.000000 | 296.100000 | 0.044953 | 4427.400313 | 9 | 3 |
| solar80 | historical10 | 0.655725 | 0.844350 | 0.001073 | 0.019141 | 309.600000 | 0.042491 | 4542.283978 | 10 | 3 |
| solar80 | robust10 | 0.450710 | 1.000000 | 0.000000 | 0.000000 | 208.800000 | 0.041630 | 3312.565625 | 7 | 2 |
| solar80 | AV10 | 0.205810 | 0.689750 | 0.031419 | 0.231087 | 225.900000 | 0.029099 | 2414.392784 | 10 | 3 |
| solar80 | AHV10 | 0.649560 | 1.000000 | 0.000000 | 0.000000 | 285.300000 | 0.046603 | 4388.590606 | 9 | 4 |
| solar80 | coverage10 | 0.669465 | 1.000000 | 0.000000 | 0.000000 | 272.700000 | 0.050197 | 5350.608195 | 7 | 2 |
| solar80 | protected_coverage10 | 0.669465 | 1.000000 | 0.000000 | 0.000000 | 272.700000 | 0.050197 | 5350.608195 | 7 | 2 |
| A90_solar70 | historical10 | 0.649650 | 0.890800 | 0.000750 | 0.018651 | 309.600000 | 0.042491 | 4542.283978 | 10 | 3 |
| A90_solar70 | robust10 | 0.529890 | 1.000000 | 0.000000 | 0.000000 | 236.700000 | 0.045790 | 3804.159358 | 7 | 2 |
| A90_solar70 | AV10 | 0.211580 | 0.685050 | 0.030440 | 0.228607 | 225.900000 | 0.029099 | 2414.392784 | 10 | 3 |
| A90_solar70 | AHV10 | 0.656835 | 1.000000 | 0.000000 | 0.000000 | 285.300000 | 0.046603 | 4388.590606 | 9 | 4 |
| A90_solar70 | coverage10 | 0.660935 | 1.000000 | 0.000000 | 0.000000 | 296.100000 | 0.044953 | 4427.400313 | 9 | 3 |
| A90_solar70 | protected_coverage10 | 0.660935 | 1.000000 | 0.000000 | 0.000000 | 296.100000 | 0.044953 | 4427.400313 | 9 | 3 |
| A180_solar70 | historical10 | 0.693290 | 0.890800 | 0.000750 | 0.018651 | 309.600000 | 0.042491 | 4542.283978 | 10 | 3 |
| A180_solar70 | robust10 | 0.704565 | 1.000000 | 0.000000 | 0.000000 | 296.100000 | 0.044953 | 4427.400313 | 9 | 3 |
| A180_solar70 | AV10 | 0.601720 | 0.890800 | 0.000750 | 0.018651 | 297.900000 | 0.038405 | 3922.582216 | 10 | 3 |
| A180_solar70 | AHV10 | 0.706795 | 1.000000 | 0.000000 | 0.000000 | 285.300000 | 0.046603 | 4388.590606 | 9 | 4 |
| A180_solar70 | coverage10 | 0.706795 | 1.000000 | 0.000000 | 0.000000 | 285.300000 | 0.046603 | 4388.590606 | 9 | 4 |
| A180_solar70 | protected_coverage10 | 0.706795 | 1.000000 | 0.000000 | 0.000000 | 285.300000 | 0.046603 | 4388.590606 | 9 | 4 |
| A270_solar70 | historical10 | 0.996625 | 1.000000 | 0.000000 | 0.000000 | 323.100000 | 0.036091 | 4288.020817 | 8 | 3 |
| A270_solar70 | robust10 | 0.996625 | 1.000000 | 0.000000 | 0.000000 | 323.100000 | 0.036091 | 4288.020817 | 8 | 3 |
| A270_solar70 | AV10 | 0.900000 | 1.000000 | 0.000000 | 0.000000 | 322.200000 | 0.035180 | 4232.208586 | 9 | 3 |
| A270_solar70 | AHV10 | 0.900000 | 1.000000 | 0.000000 | 0.000000 | 322.200000 | 0.035180 | 4232.208586 | 9 | 3 |
| A270_solar70 | coverage10 | 0.996625 | 1.000000 | 0.000000 | 0.000000 | 323.100000 | 0.036091 | 4288.020817 | 8 | 3 |
| A270_solar70 | protected_coverage10 | 0.996625 | 1.000000 | 0.000000 | 0.000000 | 323.100000 | 0.036091 | 4288.020817 | 8 | 3 |

## 十五、十项候选逐项对照

以下为每个情景的固定权重基线及新保护清单；不合并重复项，便于逐项核对。

### ordered

| set | adapted_baseline | position | pair | A | H | V | HB_review_status | translation_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| historical10 | False | 1 | C9,C24 | 396.000000 | 0.048744 | 5551.332804 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| historical10 | False | 2 | C9,C15 | 351.000000 | 0.034958 | 3127.755324 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| historical10 | False | 3 | C9,C12 | 306.000000 | 0.043575 | 4030.542903 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | False | 4 | C15,C24 | 243.000000 | 0.053668 | 4016.480100 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | False | 5 | C9,C35 | 297.000000 | 0.044806 | 5303.319767 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | False | 6 | C9,C13 | 333.000000 | 0.030281 | 2975.155637 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_ARCHIVED_UNCHANGED_RESULT_REUSED |
| historical10 | False | 7 | C12,C24 | 198.000000 | 0.062285 | 4919.267679 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | False | 8 | C9,C21 | 333.000000 | 0.032496 | 4251.977482 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | False | 9 | C9,C26 | 315.000000 | 0.035204 | 3906.126893 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | False | 10 | C9,C27 | 324.000000 | 0.038897 | 7340.881193 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 1 | C9,C24 | 396.000000 | 0.048744 | 5551.332804 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| protected_coverage10 | False | 2 | C9,C15 | 351.000000 | 0.034958 | 3127.755324 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| protected_coverage10 | False | 3 | C9,C12 | 306.000000 | 0.043575 | 4030.542903 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 4 | C9,C35 | 297.000000 | 0.044806 | 5303.319767 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 5 | C9,C21 | 333.000000 | 0.032496 | 4251.977482 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 6 | C9,C26 | 315.000000 | 0.035204 | 3906.126893 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 7 | C9,C13 | 333.000000 | 0.030281 | 2975.155637 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_ARCHIVED_UNCHANGED_RESULT_REUSED |
| protected_coverage10 | False | 8 | C9,C27 | 324.000000 | 0.038897 | 7340.881193 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 9 | C15,C24 | 243.000000 | 0.053668 | 4016.480100 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 10 | C9,C28 | 297.000000 | 0.027326 | 3284.713425 | 2P5D_ONLY | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |

### solar70

| set | adapted_baseline | position | pair | A | H | V | HB_review_status | translation_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| historical10 | False | 1 | C9,C24 | 396.000000 | 0.048744 | 5551.332804 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| historical10 | False | 2 | C9,C15 | 351.000000 | 0.034958 | 3127.755324 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| historical10 | False | 3 | C9,C12 | 306.000000 | 0.043575 | 4030.542903 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | False | 4 | C15,C24 | 243.000000 | 0.053668 | 4016.480100 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | False | 5 | C9,C35 | 297.000000 | 0.044806 | 5303.319767 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | False | 6 | C9,C13 | 333.000000 | 0.030281 | 2975.155637 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_ARCHIVED_UNCHANGED_RESULT_REUSED |
| historical10 | False | 7 | C12,C24 | 198.000000 | 0.062285 | 4919.267679 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | False | 8 | C9,C21 | 333.000000 | 0.032496 | 4251.977482 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | False | 9 | C9,C26 | 315.000000 | 0.035204 | 3906.126893 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | False | 10 | C9,C27 | 324.000000 | 0.038897 | 7340.881193 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 1 | C9,C24 | 396.000000 | 0.048744 | 5551.332804 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| protected_coverage10 | False | 2 | C12,C24 | 198.000000 | 0.062285 | 4919.267679 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 3 | C24,C35 | 189.000000 | 0.063516 | 6192.044543 | 2P5D_ONLY | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 4 | C15,C24 | 243.000000 | 0.053668 | 4016.480100 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 5 | C9,C12 | 306.000000 | 0.043575 | 4030.542903 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 6 | C9,C35 | 297.000000 | 0.044806 | 5303.319767 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 7 | C9,C15 | 351.000000 | 0.034958 | 3127.755324 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| protected_coverage10 | False | 8 | C9,C26 | 315.000000 | 0.035204 | 3906.126893 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 9 | C9,C13 | 333.000000 | 0.030281 | 2975.155637 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_ARCHIVED_UNCHANGED_RESULT_REUSED |
| protected_coverage10 | False | 10 | C9,C21 | 333.000000 | 0.032496 | 4251.977482 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |

### solar80

| set | adapted_baseline | position | pair | A | H | V | HB_review_status | translation_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| historical10 | False | 1 | C9,C24 | 396.000000 | 0.048744 | 5551.332804 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| historical10 | False | 2 | C9,C15 | 351.000000 | 0.034958 | 3127.755324 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| historical10 | False | 3 | C9,C12 | 306.000000 | 0.043575 | 4030.542903 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | False | 4 | C15,C24 | 243.000000 | 0.053668 | 4016.480100 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | False | 5 | C9,C35 | 297.000000 | 0.044806 | 5303.319767 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | False | 6 | C9,C13 | 333.000000 | 0.030281 | 2975.155637 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_ARCHIVED_UNCHANGED_RESULT_REUSED |
| historical10 | False | 7 | C12,C24 | 198.000000 | 0.062285 | 4919.267679 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | False | 8 | C9,C21 | 333.000000 | 0.032496 | 4251.977482 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | False | 9 | C9,C26 | 315.000000 | 0.035204 | 3906.126893 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | False | 10 | C9,C27 | 324.000000 | 0.038897 | 7340.881193 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 1 | C9,C24 | 396.000000 | 0.048744 | 5551.332804 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| protected_coverage10 | False | 2 | C12,C24 | 198.000000 | 0.062285 | 4919.267679 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 3 | C24,C35 | 189.000000 | 0.063516 | 6192.044543 | 2P5D_ONLY | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 4 | C15,C24 | 243.000000 | 0.053668 | 4016.480100 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 5 | C9,C12 | 306.000000 | 0.043575 | 4030.542903 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 6 | C9,C35 | 297.000000 | 0.044806 | 5303.319767 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 7 | C9,C15 | 351.000000 | 0.034958 | 3127.755324 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| protected_coverage10 | False | 8 | C9,C27 | 324.000000 | 0.038897 | 7340.881193 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 9 | C24,C27 | 216.000000 | 0.057607 | 8229.605969 | 2P5D_ONLY | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 10 | C24,C26 | 207.000000 | 0.053914 | 4794.851669 | 2P5D_ONLY | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |

### A90_solar70

| set | adapted_baseline | position | pair | A | H | V | HB_review_status | translation_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| historical10 | True | 1 | C9,C24 | 396.000000 | 0.048744 | 5551.332804 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| historical10 | True | 2 | C9,C15 | 351.000000 | 0.034958 | 3127.755324 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| historical10 | True | 3 | C9,C12 | 306.000000 | 0.043575 | 4030.542903 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | True | 4 | C15,C24 | 243.000000 | 0.053668 | 4016.480100 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | True | 5 | C9,C35 | 297.000000 | 0.044806 | 5303.319767 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | True | 6 | C9,C13 | 333.000000 | 0.030281 | 2975.155637 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_ARCHIVED_UNCHANGED_RESULT_REUSED |
| historical10 | True | 7 | C12,C24 | 198.000000 | 0.062285 | 4919.267679 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | True | 8 | C9,C21 | 333.000000 | 0.032496 | 4251.977482 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | True | 9 | C9,C26 | 315.000000 | 0.035204 | 3906.126893 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | True | 10 | C9,C27 | 324.000000 | 0.038897 | 7340.881193 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 1 | C9,C24 | 396.000000 | 0.048744 | 5551.332804 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| protected_coverage10 | False | 2 | C12,C24 | 198.000000 | 0.062285 | 4919.267679 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 3 | C24,C35 | 189.000000 | 0.063516 | 6192.044543 | 2P5D_ONLY | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 4 | C15,C24 | 243.000000 | 0.053668 | 4016.480100 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 5 | C9,C12 | 306.000000 | 0.043575 | 4030.542903 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 6 | C9,C35 | 297.000000 | 0.044806 | 5303.319767 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 7 | C9,C15 | 351.000000 | 0.034958 | 3127.755324 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| protected_coverage10 | False | 8 | C9,C26 | 315.000000 | 0.035204 | 3906.126893 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 9 | C9,C13 | 333.000000 | 0.030281 | 2975.155637 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_ARCHIVED_UNCHANGED_RESULT_REUSED |
| protected_coverage10 | False | 10 | C9,C21 | 333.000000 | 0.032496 | 4251.977482 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |

### A180_solar70

| set | adapted_baseline | position | pair | A | H | V | HB_review_status | translation_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| historical10 | True | 1 | C9,C24 | 396.000000 | 0.048744 | 5551.332804 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| historical10 | True | 2 | C9,C15 | 351.000000 | 0.034958 | 3127.755324 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| historical10 | True | 3 | C9,C12 | 306.000000 | 0.043575 | 4030.542903 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | True | 4 | C15,C24 | 243.000000 | 0.053668 | 4016.480100 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | True | 5 | C9,C35 | 297.000000 | 0.044806 | 5303.319767 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | True | 6 | C9,C13 | 333.000000 | 0.030281 | 2975.155637 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_ARCHIVED_UNCHANGED_RESULT_REUSED |
| historical10 | True | 7 | C12,C24 | 198.000000 | 0.062285 | 4919.267679 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | True | 8 | C9,C21 | 333.000000 | 0.032496 | 4251.977482 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | True | 9 | C9,C26 | 315.000000 | 0.035204 | 3906.126893 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | True | 10 | C9,C27 | 324.000000 | 0.038897 | 7340.881193 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 1 | C9,C24 | 396.000000 | 0.048744 | 5551.332804 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| protected_coverage10 | False | 2 | C12,C24 | 198.000000 | 0.062285 | 4919.267679 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 3 | C24,C35 | 189.000000 | 0.063516 | 6192.044543 | 2P5D_ONLY | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 4 | C9,C12 | 306.000000 | 0.043575 | 4030.542903 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 5 | C9,C35 | 297.000000 | 0.044806 | 5303.319767 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 6 | C15,C24 | 243.000000 | 0.053668 | 4016.480100 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 7 | C9,C15 | 351.000000 | 0.034958 | 3127.755324 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| protected_coverage10 | False | 8 | C9,C26 | 315.000000 | 0.035204 | 3906.126893 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 9 | C9,C13 | 333.000000 | 0.030281 | 2975.155637 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_ARCHIVED_UNCHANGED_RESULT_REUSED |
| protected_coverage10 | False | 10 | C13,C24 | 225.000000 | 0.048991 | 3863.880413 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |

### A270_solar70

| set | adapted_baseline | position | pair | A | H | V | HB_review_status | translation_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| historical10 | True | 1 | C9,C24 | 396.000000 | 0.048744 | 5551.332804 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| historical10 | True | 2 | C9,C15 | 351.000000 | 0.034958 | 3127.755324 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| historical10 | True | 3 | C9,C12 | 306.000000 | 0.043575 | 4030.542903 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | True | 4 | C9,C35 | 297.000000 | 0.044806 | 5303.319767 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | True | 5 | C9,C13 | 333.000000 | 0.030281 | 2975.155637 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_ARCHIVED_UNCHANGED_RESULT_REUSED |
| historical10 | True | 6 | C9,C21 | 333.000000 | 0.032496 | 4251.977482 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | True | 7 | C9,C26 | 315.000000 | 0.035204 | 3906.126893 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | True | 8 | C9,C27 | 324.000000 | 0.038897 | 7340.881193 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | True | 9 | C9,C28 | 297.000000 | 0.027326 | 3284.713425 | 2P5D_ONLY | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| historical10 | True | 10 | C9,C20 | 279.000000 | 0.024618 | 3108.402738 | 2P5D_ONLY | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 1 | C9,C24 | 396.000000 | 0.048744 | 5551.332804 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| protected_coverage10 | False | 2 | C9,C15 | 351.000000 | 0.034958 | 3127.755324 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_V2_ARCHIVED_CORRECTION_HB_CHECKED |
| protected_coverage10 | False | 3 | C9,C12 | 306.000000 | 0.043575 | 4030.542903 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 4 | C9,C13 | 333.000000 | 0.030281 | 2975.155637 | ARCHIVED_RULE_HB_REVIEWED | CONTAINED_ARCHIVED_UNCHANGED_RESULT_REUSED |
| protected_coverage10 | False | 5 | C9,C26 | 315.000000 | 0.035204 | 3906.126893 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 6 | C9,C21 | 333.000000 | 0.032496 | 4251.977482 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 7 | C9,C28 | 297.000000 | 0.027326 | 3284.713425 | 2P5D_ONLY | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 8 | C9,C35 | 297.000000 | 0.044806 | 5303.319767 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 9 | C9,C20 | 279.000000 | 0.024618 | 3108.402738 | 2P5D_ONLY | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |
| protected_coverage10 | False | 10 | C9,C27 | 324.000000 | 0.038897 | 7340.881193 | ARCHIVED_RULE_HB_REVIEWED | NO_ARCHIVED_TRANSLATED_DESIGN_VERIFICATION |

## 十六、原始证据入口

- protocol/preregistered_protocol.json：冻结定义与阈值。
- RUN_MANIFEST.json：运行环境、52.013116秒实际运行时间、输入输出哈希。
- results/shortlist_evaluation.csv：所有方法与训练、测试、重复验证结果。
- results/paired_differences.csv：配对差异与蒙特卡洛区间。
- results/continuous_worst_regret.csv：连续空间固定清单最坏遗憾。
- results/shortlists_evidence.csv：逐项候选指标与HB/转译状态。
- results/threshold_counts.csv、original_list_threshold_violations.csv：门槛后的数量及原清单违规项。
- results/selection_stability.csv：训练分块稳定性。
- results/CONCLUSIONS.json：六种情景逐条判定，没有任何情景支持全面替换。

本解释由真实CSV自动生成数值表，语言整理使用AI辅助；作者仍需阅读、核对、承担最终论证与提交责任。
