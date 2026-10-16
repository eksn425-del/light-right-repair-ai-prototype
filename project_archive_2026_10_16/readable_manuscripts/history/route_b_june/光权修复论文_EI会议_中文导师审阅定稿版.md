# Archived Word Document

Source: `history/route_b_june/光权修复论文_EI会议_中文导师审阅定稿版.docx`

Status: historical text; reconcile every numeric claim against the frozen paper ledger.

旧街区早期更新中的直射日照可达性诊断与低干预候选生成：规则启发式工作流研究

——以厦门灌口沿湖休闲片区为例

作者姓名：洪禄

摘  要：本文针对旧街区早期更新中低直射日照区定位、低干预候选筛选和结果复核困难的问题，构建了“规范几何统一—2.5D 规则诊断—候选枚举—HB-Radiance 正式三维复核—设计师复核”的工作流。研究以厦门灌口沿湖休闲片区 C1—C45 建筑数据为对象，先对 CSV、DXF、OBJ 与旧 Ladybug-ready 模型进行坐标、尺度、编号和高度审计，建立 canonical_site_v2；再在统一冬至日、3 m 地面传感点、30 分钟时间步长和相同掩膜条件下枚举双建筑低干预减高候选。结果表明，旧 C6/C33 方案在正式三维复核下收益较小，不能作为唯一最终方案；C13/C24 虽为正向候选，但在追加复核集合中不处于 HB-Radiance Pareto 前沿。最终建议将 C9/C15 与 C9/C13 作为经正式三维复核和设计转译复算后较稳健的优先候选区间，C9/C24 作为高收益但需重点复核的候选。本研究输出的是早期候选筛查与设计师复核依据，不替代专业日照审查、室内照度模拟或法定合规报告。

关键词：旧街区更新；直射日照可达性；规则启发式；候选生成；HB-Radiance；设计师复核

1 引言

旧街区更新中的公共空间环境品质往往受高密度建筑、狭窄街巷和多层级体量遮挡影响。早期方案阶段需要快速判断低直射日照区在哪里、哪些建筑局部调整可能有效、以及候选是否值得设计师继续复核。过早进入专业日照审查或室内照度模拟会增加建模成本，而仅凭经验又难以比较不同候选。本文将原项目内部简称“光权修复”降级为背景性称呼，并明确其不等同于法律意义上的日照权裁定。

本文研究问题收敛为三点：第一，如何把 CAD/SKP/OBJ/DXF/CSV 调研资料统一成可计算的规范几何；第二，如何在低干预约束下生成可比较的直射日照候选；第三，如何用正式三维参考模拟和设计师复核避免把规则模型输出误读为唯一最优方案。

2 规范几何与数据来源

本轮以原始 SKP/DXF 与 buildings.csv 为优先依据，建立 canonical_site_v2。DXF 到规范坐标采用 x=dxf_x_mm/1000-317.890127、y=dxf_y_mm/1000-2426.142342；OBJ 检查采用 x=obj_x_mm/1000-191.792、y=-obj_z_mm/1000-95.982、z=obj_y_mm/1000。审计显示 C6、C33、C13、C24 在旧 OBJ/CSV/DXF 间存在 footprint 或质心差异，因此旧 Ladybug-ready OBJ 不再作为正式验证输入。

图1  全场规范几何叠加核对。图表说明：本图用于证明旧模型与规范模型之间存在需要说明的几何差异。

3 方法

3.1 直射日照诊断

算法 A 计算地面传感点在冬至日指定时段内获得的直射日照时长。统一参数为厦门灌口近似经纬度 24.55°N、118.03°E，Asia/Shanghai 时区，冬至日 08:15—15:45，30 分钟步长，3 m 地面网格，传感点高度 0.1 m，低直射日照阈值 2 h、3 h 和 4 h，其中 3 h 作为主结果。

3.2 候选生成与体量口径

算法 B 仅保留低干预减高/退台候选，不再把 add、reorganize 写作主实验操作。规则高度为 h_new=max(3 m, h-min(3 m,0.25h))。所有干预体量统一为真实 m³，即 footprint 面积乘以高度削减量。旧稿中的 28.125 不再作为真实体量使用。

3.3 正式三维参考模拟

正式参考采用 Honeybee/LBT direct-sun-hours recipe 与 Radiance 6.0.2 命令行路径。Rhino/Grasshopper GUI 本机未检出，未伪造截图或 .gh 文件。HB-Radiance 与 Python 2.5D 使用同一规范几何、同一传感点、同一时段、同一时间步长和同一掩膜。

4 结果

4.1 全候选枚举与追加复核

在 canonical_site_v2 下，合法可减高建筑为 36 栋，共生成 C(36,2)=630 个双建筑候选。根据 2.5D Top10、非零 Pareto、C6/C33、C13/C24、高度优先基线和低日照邻近基线形成 23 个去重规则候选，并全部完成 HB-Radiance 追加复核。

图2  HB-Radiance 已复核候选 Pareto 分布。图表说明：本图证明最终判断应基于三维复核后的体量—收益关系。

候选

HB排名

低日照下降/m²

均值提升/h

体量/m³

HB Pareto

C9,C24

1

396.000

0.052

5551.333

True

C9,C15

2

351.000

0.037

3127.755

True

C9,C27

3

333.000

0.041

7340.881

False

C9,C21

4

333.000

0.034

4251.977

False

C9,C13

5

333.000

0.032

2975.156

True

C9,C26

6

315.000

0.037

3906.127

False

C9,C12

7

306.000

0.046

4030.543

False

C9,C35

8

297.000

0.047

5303.320

False

C9,C29

9

270.000

0.017

2550.280

True

C9,C25

10

252.000

0.019

2499.710

True

表1  HB-Radiance 已复核规则候选 Top10。图表说明：本表用于证明 C9 相关候选在正式三维复核中整体优于旧 C6/C33 与 C13/C24。

4.2 2.5D 与 HB-Radiance 一致性

在 23 个已复核规则候选中，2.5D 排名与 HB-Radiance 低日照面积下降排名 Spearman rho 为 0.883，p=2.35e-08。Top3 召回为 0.667，Top5 召回为 0.4，Top10 召回为 0.8；HB Pareto 与 2.5D Pareto 在已复核集合中重叠数为 12。该结果说明规则模型可用于早期缩小候选范围，但不能自动给出唯一最优方案。

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

图3  已复核候选的模型分歧图组。图表说明：本图证明统一几何后总体趋势一致，但低体量候选排序仍需三维复核。

4.3 规则模型与设计转译复算

对最终候选建立两类几何：A 为规则整体减高模型；B 为保留底层街巷界面的上部退台设计转译模型。C9/C15 与 C9/C13 在设计转译后仍保持正向改善，且没有新增低日照区或恶化点；C9/C24 在规则模型中收益最高，但设计转译后出现 4 个恶化点和 9 m² 新增低日照区，因此降级为高收益但需重点复核候选。

候选

判断

规则下降/m²

设计下降/m²

设计恶化点

新增低日照/m²

C9,C15

优先候选区间

351.000

342.000

0

0.000

C9,C13

优先候选区间

333.000

333.000

0

0.000

C9,C24

高收益复核候选

396.000

342.000

4

9.000

C13,C24

历史候选/对照

225.000

207.000

4

9.000

C6,C33

不作为最终推荐

9.000

18.000

0

0.000

图4  最终候选规则模型与设计转译模型对比。图表说明：本图证明规则模型效果不能直接等同于建筑设计转译效果。

5 讨论

本轮结果推翻了旧稿中把 C6/C33 作为唯一保守型推荐的写法。C6/C33 在 HB-Radiance 下 3 h 低直射日照区面积仅下降 9 m²，设计转译后下降 18 m²，属于正向但收益较小的历史对照。C13/C24 也不应被规则模型结果直接替换为新唯一方案；它在正式三维复核中正向，但追加复核后不在 HB Pareto 前沿。

最终更诚实的论文定位是：该工作流在统一输入条件下提供可复核的低直射日照候选筛查能力，其价值在于缩小设计师需要重点复核的候选范围，而非替代专业环境模拟或自动给出唯一最优方案。结构、产权、功能置换、施工可行性和法定日照审查仍需后续专业流程处理。

6 结论

本文完成了从几何审计、规则模型重跑、正式 HB-Radiance 复核到设计转译复算的中文收敛。结果支持将 C9/C15 与 C9/C13 写为优先候选区间，将 C9/C24 写为高收益但需重点复核候选；C13/C24 与 C6/C33 保留为方法演进中的对照。该结论仅适用于本轮 canonical_site_v2、冬至日、3 m 地面传感网格和已完成三维复核的候选集合。

参考文献

[1] CZACHURA A, KANTERS J, GENTILE N, WALL M. Solar Performance Metrics in Urban Planning: A Review and Taxonomy[J]. Buildings, 2022, 12(4): 393.

[2] COMPAGNON R. Solar and daylight availability in the urban fabric[J]. Energy and Buildings, 2004, 36(4): 321-328.

[3] SADEGHIPOUR ROUDSARI M, PAK M, VIOLA A. Ladybug: A parametric environmental plugin for Grasshopper[C]//BS2013. 2013: 3128-3135.

[4] WARD G J. The RADIANCE lighting simulation and rendering system[C]//SIGGRAPH 1994: 459-472.

[5] REINHART C F, WALKENHORST O. Validation of dynamic RADIANCE-based daylight simulations[J]. Energy and Buildings, 2001, 33(7): 683-697.

[6] NGUYEN A T, REITER S, RIGO P. A review on simulation-based optimization methods applied to building performance analysis[J]. Applied Energy, 2014, 113: 1043-1058.
