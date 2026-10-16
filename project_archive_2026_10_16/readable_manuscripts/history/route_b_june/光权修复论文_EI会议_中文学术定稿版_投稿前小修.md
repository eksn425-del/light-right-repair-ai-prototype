# Archived Word Document

Source: `history/route_b_june/光权修复论文_EI会议_中文学术定稿版_投稿前小修.docx`

Status: historical text; reconcile every numeric claim against the frozen paper ledger.

旧街区早期更新中的直射日照可达性诊断与低干预候选生成：规则启发式工作流研究

——以厦门灌口沿湖休闲片区为例

洪禄

摘  要：旧街区早期更新常需在几何资料精度有限、方案尚未定型的阶段，识别低直射日照区并筛选低干预候选。本文以厦门灌口沿湖休闲片区为例，构建“规范几何统一—2.5D 规则筛查—双建筑候选枚举—HB-Radiance 三维复核—建筑设计转译复算—设计师复核”的方法链条。研究在 36 栋合法可减高建筑中枚举 C(36,2)=630 个双建筑候选，并对 23 个候选完成 Honeybee/LBT direct-sun-hours 与 Radiance 6.0.2 复核。结果表明，C6/C33 的三维复核收益较小，不再作为推荐候选；C9/C15 与 C9/C13 在规则模型和设计转译复算中均保持正向且无新增低日照区，可作为优先候选区间；C9/C24 收益较高，但在局部敏感点出现副作用，应作为高收益但需重点复核的候选。本文定位为早期候选筛查与设计师复核工作流，不替代法定日照审查、结构安全、产权协调或施工可行性判断。

关键词：旧街区更新；直射日照可达性；低干预减高；HB-Radiance；候选筛查；设计师复核

1 引言

高密度旧街区的公共空间太阳可达性受街巷尺度、建筑高度、体量组合和城市形态共同影响。既有研究从城市街区形态、建筑形态与环境性能、太阳与日光可达性、太阳性能指标分类等方面表明，太阳资源在城市肌理中呈现显著空间差异，需要在规划和早期设计阶段被显式讨论[1-5]。同时，旧城更新和老旧社区改造具有明显的情境依赖与实施约束，候选方案通常需要在环境收益、干预强度、产权协调和更新目标之间进行权衡[6-8]。

在太阳可达性研究中，几何形态和邻里布局对太阳潜力的影响已形成较丰富的方法基础[9-10]。环境模拟工具方面，Ladybug/LBT、Honeybee Radiance 与 Radiance 为建筑和城市尺度光环境分析提供了常用技术路径[11-14]；太阳建筑规划流程、太阳包络与大规模城市模型快速模拟研究也提示，早期阶段需要在计算成本与模型精度之间保持清晰边界[15-18]。与面向完整方案评价的模拟不同，旧街区早期更新更需要低成本地缩小候选范围，并将少量候选交由设计师和更完整的三维模拟复核。

性能化设计和多目标优化研究强调，早期阶段的模型不应只输出单一数值排名，还应支持候选组织、设计师偏好判断和后续复核[19-24]。本文的差异在于：以规范几何统一作为前提，用 2.5D 规则模型完成全候选初筛，再以 HB-Radiance 三维参考模拟复核候选集合，并将输出限定为候选区间和复核等级，而非单一最终方案。研究对象为地面传感点在冬至日分析时段内的直射日照时长，不涉及室内照度、日照因子、sDA、ASE 或全年光环境。

2 规范几何与数据来源

研究首先对原始 CAD、SKP、OBJ、DXF 与高度属性表进行坐标、尺度、编号和高度核对，建立统一的规范几何模型。规范模型采用米制单位，水平坐标为 X/Y，竖向为 Z；建筑平面边界由 DXF 建筑边界组件与属性表共同确定，建筑高度与保护/可动属性来自统一整理后的属性数据。

模型审计显示，历史关键建筑在旧 OBJ、属性表与 DXF 之间存在 footprint、质心或组合边界差异。C6、C24、C33 等建筑表现出较明显的质心偏差或边界差异，C13、C15 等建筑也存在不同程度的 footprint 重叠不足。因此，后续候选筛查与三维复核均以规范几何模型为统一输入。该模型是可复现实验模型，不等同于竣工测绘模型或现场实测模型；本文结论仅适用于该规范几何、设定冬至日时段、地面传感网格及已完成三维复核的候选集合。

其中，C6 的较大质心偏差主要与旧 OBJ 中多组件聚合、DXF 建筑边界组件分拆及历史模型定位口径不同有关，而非建筑高度属性不一致。为避免该差异影响候选比较，本文后续筛查与三维复核均以统一的规范几何模型作为唯一输入。

建筑

质心差 / m

高差 / m

footprint IoU

审计说明

C6

18.59

0.00

0.42

需按规范几何重算

C9

1.49

0.00

0.66

存在局部质心偏差

C13

0.09

0.00

0.54

存在明显边界差异

C15

0.21

0.00

0.42

存在明显边界差异

C24

1.73

0.00

0.64

需按规范几何重算

C33

2.56

0.00

0.53

需按规范几何重算

表1  关键建筑的规范几何审计摘要。注：质心差和 IoU 用于说明旧 OBJ、属性表与 DXF 之间的几何差异，不作为建筑质量评价。

图1  规范几何与关键建筑叠加关系。

3 方法

3.1 地面点位直射日照诊断

2.5D 规则模型用于计算地面传感点的直射太阳可见时长。模型在每个有效传感点处按太阳方向发射射线，并根据建筑 footprint 与高度判断遮挡。建筑内部点、场地外点和掩膜之外的无效点不进入统计。统一分析参数包括：冬至日、08:15-15:45、30 分钟时间步长、3 m 地面传感网格、传感点高度 0.1 m，并以 3 h 阈值作为低直射日照区的主评价口径。

3.2 低干预候选生成与体量口径

候选生成仅考虑低干预减高/退台操作。本文将单栋建筑高度削减不超过原高度 25%，且最大削减高度不超过 3 m 的操作定义为低干预减高。高度更新规则为 h_new = max(3 m, h - min(3 m, 0.25h))，其中最低保留高度为 3 m。干预体量统一按真实 m³ 计算，即建筑 footprint 面积乘以高度削减量。

3.3 HB-Radiance 三维参考模拟

三维参考采用 Honeybee/LBT direct-sun-hours 与 Radiance 6.0.2。三维复核与 2.5D 初筛使用相同规范几何、同一传感点、同一日期、同一时段、同一时间步长和同一分析掩膜。HB-Radiance 在本文中作为相对于 2.5D 更完整的独立三维参考，而非现场实测替代。

HB-Radiance 项目由 Python 脚本根据规范几何、统一传感点网格和分析参数生成；随后通过 Ladybug Tools 命令行配方 lbt-recipes run direct-sun-hours 执行 Direct Sun Hours 计算。计算完成后，脚本读取各场景的 Radiance 结果文件，汇总传感点直射日照时长、低直射日照区面积、改善点与恶化点等指标，并生成候选排名与 Pareto 分布。该路径避免了依赖 Rhino/Grasshopper 图形界面，但仍保留统一模型、统一传感点和统一时间参数的可复现计算过程。

3.4 规则模型与设计转译模型

为避免将规则整体减高直接等同于建筑设计方案，本文对候选建立两类几何版本：规则整体减高模型用于统一排序和体量比较，设计转译模型采用上部退台方式保留底层街巷界面。候选身份由规则模型收益、设计转译复算、是否新增低直射日照区和是否出现恶化点共同决定。

4 结果

4.1 2.5D 全候选搜索与候选缩小

在规范几何模型下，合法可减高建筑为 36 栋，共形成 C(36,2)=630 个双建筑候选。2.5D 规则筛查用于从全候选中识别 Top、Pareto 与基线对照候选，去重后形成 23 个候选并进入 HB-Radiance 三维复核。

复核候选由四类来源合并形成：2.5D 总分 Top10 候选 10 组，2.5D 非零 Pareto 候选 12 组，历史候选 C6/C33 与 C13/C24 共 2 组，以及固定基线候选 C3/C19 与 C26/C35 共 2 组。其中 Top10 与 Pareto 候选重叠 3 组，合并去重后得到 23 组唯一候选，全部进入 HB-Radiance 三维复核。

来源类别

数量

候选或说明

2.5D 总分 Top10 候选

10

C9/C24、C9/C15、C9/C12、C15/C24、C9/C35、C9/C13、C12/C24、C9/C21、C9/C26、C9/C27

2.5D 非零 Pareto 候选

12

C9/C24、C9/C15、C9/C13、C15/C26、C9/C29、C9/C25、C13/C15、C15/C28、C15/C29、C13/C29、C13/C25、C25/C29

历史候选

2

C6/C33、C13/C24

固定基线候选

2

C3/C19（高度优先）、C26/C35（低日照邻近）

Top10 与 Pareto 重叠

-3

C9/C24、C9/C15、C9/C13

合并去重后进入 HB-Radiance 复核

23

23 组唯一候选

表2  HB-Radiance 复核候选的预先筛选与去重过程。

在统一的 3 m 地面传感网格和 3 h 阈值下，基线方案的低直射日照区总面积为 3051 m²。后续候选的低日照区面积下降均相对于该基线计算。

候选

HB排名

低日照区下降 / m²

改善比例 / %

平均提升 / h

体量 / m³

Pareto

C9/C24

1

396

13.0

0.052

5551

是

C9/C15

2

351

11.5

0.037

3128

是

C9/C27

3

333

10.9

0.041

7341

否

C9/C21

4

333

10.9

0.034

4252

否

C9/C13

5

333

10.9

0.032

2975

是

C9/C26

6

315

10.3

0.037

3906

否

C9/C12

7

306

10.0

0.046

4031

否

C9/C35

8

297

9.7

0.047

5303

否

C9/C29

9

270

8.8

0.017

2550

是

C9/C25

10

252

8.3

0.019

2500

是

表3  已复核候选的 HB-Radiance 结果。

4.2 HB-Radiance 已复核候选的 Pareto 关系

三维复核结果显示，C9/C24 的规则模型 3 h 低直射日照区面积下降 396 m²，为已复核集合中收益较高的候选；C9/C15 下降 351 m²，C9/C13 下降 333 m²，二者均处于 HB Pareto 前沿，并在设计转译后保持无新增低日照区和无恶化点。C13/C24 下降 225 m²，但不在 HB Pareto 前沿；C6/C33 下降 9 m²，收益较小。

图2  已复核候选的 HB-Radiance 体量—低日照区改善 Pareto 分布（仅限 23 个已复核候选）。

4.3 2.5D 与 HB-Radiance 一致性

在 23 个已复核规则候选中，2.5D 候选排序与 HB-Radiance 低直射日照区面积下降排序的 Spearman rho 为 0.883。Top3、Top5、Top10 召回率分别为 0.667、0.400 和 0.800；HB Pareto 与 2.5D Pareto 在已复核集合中重叠 12 个，召回率为 1.000。该结果支持将 2.5D 规则模型用于前期候选缩小，但仍需三维复核确认候选身份。

K

重叠数

召回率

3

2

0.667

5

2

0.400

10

8

0.800

Pareto

12

1.000

表4  2.5D 与 HB-Radiance 候选排序一致性。

图3  2.5D 规则模型与 HB-Radiance 复核结果的一致性。

4.4 设计转译复算与候选身份判断

候选身份判断不只依据规则模型收益，还结合设计转译后是否继续正向、是否新增低直射日照区以及是否出现恶化点。C9/C15 设计转译后低直射日照区下降 342 m²，C9/C13 设计转译后下降 333 m²，二者均无新增低日照区和无恶化点，因此作为优先候选区间。C9/C24 规则模型收益较高，设计转译后下降 342 m²，但出现 4 个恶化点和 9 m² 新增低日照区，因此作为高收益但需重点复核候选。

C13/C24 设计转译后下降 207 m²，且不在 HB Pareto 前沿，保留为历史对照。C6/C33 设计转译后下降 18 m²，不作为推荐候选。补充点位核查显示，C9/C24 与 C13/C24 在同一组局部敏感传感点上产生等量副作用，但其整体低日照区收益和 Pareto 状态不同。

候选

候选身份

规则下降 / m²

改善比例 / %

设计下降 / m²

恶化点

新增低日照 / m²

C9/C15

优先候选区间

351

11.5

342

0

0

C9/C13

优先候选区间

333

10.9

333

0

0

C9/C24

高收益复核候选

396

13.0

342

4

9

C13/C24

历史候选/对照

225

7.4

207

4

9

C6/C33

不作为最终推荐

9

0.3

18

0

0

表5  最终候选的规则模型与设计转译结果。注：C9/C24 与 C13/C24 的恶化点数量和新增低直射日照面积相同，且点位空间位置重合；两者整体收益不同。

图4  规则整体减高与设计转译模型的低日照区改善对比。

图5  从规则筛查到设计师复核的候选判断流程。

5 讨论

5.1 C6/C33 与 C13/C24 的结论边界

C6/C33 在三维复核下保持正向但收益较小，且相关建筑在旧模型与规范几何之间存在较明显的几何差异，因此不宜作为推荐候选。C13/C24 的规则与设计转译结果均为正向，但其 HB Pareto 状态和设计转译副作用使其更适合作为历史对照，而非新的单一方案。

5.2 候选区间而非单一方案

C9/C15 与 C9/C13 的共同特征是位于 HB Pareto 前沿，设计转译后仍保持正向，且无新增低日照区和无恶化点。由于二者体量与收益接近，且实际更新还需结合结构、产权、功能和街巷界面判断，将其表述为“优先候选区间”更符合早期筛查研究的证据边界。

5.3 规则模型的价值与限制

2.5D 规则模型的价值在于以较低计算成本对全候选进行统一比较，并缩小需要三维复核和设计师复核的候选范围。其限制在于对建筑几何进行简化，难以表达复杂开洞、构件细部、真实地形、植被和材料反射等因素。未来研究可进一步结合第三方复核、现场测绘与多尺度分析，以检验规范几何和候选结论在更广泛条件下的稳定性。

边界项

本文覆盖

未覆盖或需谨慎解释

研究指标

地面传感点直射日照时长

不等同于室内照度、日照因子、sDA、ASE 或全年光环境

几何模型

由 DXF 边界组件、CSV 高度与属性统一构建的规范几何

不等同于竣工测绘模型或现场实测模型

参考模拟

Honeybee/LBT direct-sun-hours 与 Radiance 6.0.2

作为三维参考复核，不代表现场实测

候选集合

23 个已完成三维复核的候选

不代表 630 个候选均完成三维复核

实施判断

低干预减高与退台候选筛查

不替代结构、产权、功能、施工和法定审查

表6  研究适用边界。

6 结论

基于规范几何统一、双建筑候选枚举、HB-Radiance 三维复核与设计转译复算，本文在设定的研究条件下形成了低干预候选的比较结果。研究表明，C9/C15 与 C9/C13 可作为优先候选区间，C9/C24 可作为高收益但需重点复核候选，C13/C24 保留为历史对照，C6/C33 不作为推荐候选。

本文提出的工作流适用于旧街区早期更新中的直射日照候选筛查，其价值在于缩小设计师需要重点复核的候选范围，而非替代法定日照审查或工程实施判断。支撑本文主要结论的模型、参数配置、候选结果与复现材料可在合理请求后向作者获取。

参考文献

[1] SANAIEIAN H, TENPIERIK M, VAN DEN LINDEN K, MEHDIZADEH SERAJ F, MOFIDI SHEMRANI S M. Review of the impact of urban block form on thermal performance, solar access and ventilation[J]. Renewable and Sustainable Energy Reviews, 2014, 38: 551-560. DOI: 10.1016/j.rser.2014.06.007.

[2] COMPAGNON R. Solar and daylight availability in the urban fabric[J]. Energy and Buildings, 2004, 36(4): 321-328. DOI: 10.1016/j.enbuild.2004.01.009.

[3] CZACHURA A, KANTERS J, GENTILE N, WALL M. Solar Performance Metrics in Urban Planning: A Review and Taxonomy[J]. Buildings, 2022, 12(4): 393. DOI: 10.3390/buildings12040393.

[4] RATTI C, RAYDAN D, STEEMERS K. Building form and environmental performance: archetypes, analysis and an arid climate[J]. Energy and Buildings, 2003, 35(1): 49-59. DOI: 10.1016/S0378-7788(02)00079-8.

[5] RATTI C, BAKER N, STEEMERS K. Energy consumption and urban texture[J]. Energy and Buildings, 2005, 37(7): 762-776. DOI: 10.1016/j.enbuild.2004.10.010.

[6] COUCH C, SYKES O, BORSTINGHAUS W. Thirty years of urban regeneration in Britain, Germany and France: The importance of context and path dependency[J]. Progress in Planning, 2011, 75(1): 1-52. DOI: 10.1016/j.progress.2010.12.001.

[7] SHEN T, YAO X, WEN F. The Urban Regeneration Engine Model: An analytical framework and case study of the renewal of old communities[J]. Land Use Policy, 2021, 108: 105571. DOI: 10.1016/j.landusepol.2021.105571.

[8] WANG W, YANG H, JING S. The development of priority decision model for old urban community renovation in China[J]. Scientific Reports, 2024, 14(1): 4434. DOI: 10.1038/s41598-024-54883-3.

[9] HACHEM C, ATHIENITIS A, FAZIO P. Parametric investigation of geometric form effects on solar potential of housing units[J]. Solar Energy, 2011, 85(9): 1864-1877. DOI: 10.1016/j.solener.2011.04.027.

[10] HACHEM C, ATHIENITIS A, FAZIO P. Investigation of solar potential of housing units in different neighborhood designs[J]. Energy and Buildings, 2011, 43(9): 2262-2273. DOI: 10.1016/j.enbuild.2011.05.008.

[11] SADEGHIPOUR ROUDSARI M, PAK M, VIOLA A. Ladybug: A parametric environmental plugin for Grasshopper to help designers create an environmentally-conscious design[C]//Proceedings of Building Simulation 2013. 2013: 3128-3135. DOI: 10.26868/25222708.2013.2499.

[12] LADYBUG TOOLS. Direct Sun Hours [EB/OL]. [2026-06-21]. https://docs.ladybug.tools/hb-radiance-primer/components/3_recipes/direct_sun_hours.

[13] WARD G J. The RADIANCE lighting simulation and rendering system[C]//Proceedings of SIGGRAPH 1994. 1994: 459-472. DOI: 10.1145/192161.192286.

[14] REINHART C F, WALKENHORST O. Validation of dynamic RADIANCE-based daylight simulations for a test office with external blinds[J]. Energy and Buildings, 2001, 33(7): 683-697. DOI: 10.1016/S0378-7788(01)00058-5.

[15] KANTERS J, WALL M. A planning process map for solar buildings in urban environments[J]. Renewable and Sustainable Energy Reviews, 2016, 57: 173-185. DOI: 10.1016/j.rser.2015.12.073.

[16] DE LUCA F, DOGAN T, SEPULVEDA A. Reverse solar envelope method: A new building form-finding method that can take regulatory frameworks into account[J]. Automation in Construction, 2021, 123: 103518. DOI: 10.1016/j.autcon.2020.103518.

[17] ALKADRI M F, DE LUCA F, TURRIN M, SARIYILDIZ S. Understanding computational methods for solar envelopes based on design parameters, tools, and case studies: A review[J]. Energies, 2020, 13(13): 3302. DOI: 10.3390/en13133302.

[18] DOGAN T, KASTNER P, MERMELSTEIN R. Surfer: A fast simulation algorithm to predict surface temperatures and mean radiant temperatures in large urban models[J]. Building and Environment, 2021, 196: 107762. DOI: 10.1016/j.buildenv.2021.107762.

[19] NGUYEN A T, REITER S, RIGO P. A review on simulation-based optimization methods applied to building performance analysis[J]. Applied Energy, 2014, 113: 1043-1058. DOI: 10.1016/j.apenergy.2013.08.061.

[20] MACHAIRAS V, TSANGRASSOULIS A, AXARLI K. Algorithms for optimization of building design: A review[J]. Renewable and Sustainable Energy Reviews, 2014, 31: 101-112. DOI: 10.1016/j.rser.2013.11.036.

[21] KONIS K, GAMAS A, KENSEK K. Passive performance and building form: An optimization framework for early-stage design support[J]. Solar Energy, 2016, 125: 161-179. DOI: 10.1016/j.solener.2015.12.020.

[22] MUELLER C T, OCHSENDORF J A. Combining structural performance and designer preferences in evolutionary design space exploration[J]. Automation in Construction, 2015, 52: 70-82. DOI: 10.1016/j.autcon.2015.02.011.

[23] CRUZ A S, CALDAS L R, MENDES V M, MENDES J C, BASTOS L E G. Multi-objective optimization based on surrogate models for sustainable building design: A systematic literature review[J]. Building and Environment, 2024, 266: 112147. DOI: 10.1016/j.buildenv.2024.112147.

[24] ABDOLLAHZADEH N, BILORIA N. Urban microclimate and energy consumption: A multi-objective parametric urban design approach for dense subtropical cities[J]. Frontiers of Architectural Research, 2022, 11(3): 453-465. DOI: 10.1016/j.foar.2022.02.001.
