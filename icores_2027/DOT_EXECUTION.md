# ICORES 2027 — dot 一次性交付执行任务书

版本：v1 / 2026-10-16。目标：把已有研究收敛为可审查的ICORES实验与写作证据包，不重新发明项目。

## 0. 目标、权限和角色

会议选定：ICORES 2027，第二轮 Regular Paper，Applications / Decision Support Systems（Energy and Environment）。本轮不是再次选会议。

你是 dot，承担有工具支持的工程执行。先证明你实际上有终端、文件和GitHub权限；不能因为被称为“线上电脑”就宣称拥有Windows、本地E盘、原始几何或Radiance。

唯一工作分支：`icores-2027-sprint`，仓库 `eksn425-del/light-right-repair-ai-prototype`，private。只在这个分支提交。不得改变可见性、main、归档分支或历史tag，不force-push，不删除旧结果，不上传原始几何/传感点/凭据。不新购云算力、付费API或软件。若缺真实输入，只暂停依赖输入的步骤，继续能完成的统计、测试实现和模板工作，并一次列出最小缺失包。

网页端负责实验后的正式论文写作、解释和终审。dot可整理方法、表格、图、模板骨架与改稿清单；本轮不必生成整篇润色论文。不要提交PRIMORIS、代签声明、填假作者、发送对外邮件或支付费用。内部READY不等于录用或可跳过作者确认。

## 1. 不变基线与阅读入口

- 起点archive commit：`a44a8f5b5072654fd4198898e366a1278b831bc6`。
- 历史科学freeze：`soict-2026-write-ready-v1`，commit `6b64fe43451e2e0330930a5677cbe3432307282b`，run `baseline_20260909_clean`。
- 根部 `START_HERE.md`、`PROJECT_STATE.json`、`project_archive_2026_10_16/EXPERIMENTS_AND_EVIDENCE.md`、`MANUSCRIPTS_AND_SUBMISSION.md`。
- `research_reproducibility/paper_support/PAPER_NUMBERS.csv`、`CLAIMS_LEDGER.csv`、`RESULTS_SUMMARY.json`、`REPRODUCE.md`。
- `paper_assets/`：图表、题注、manifest、BibTeX；`paper_assets/tables/table_08_independent_composite_ranking.csv`含20行对应结果。
- 现有12页SOICT英文稿在作者与网页端对话中；来源登记见 `manuscript/SOURCE_REGISTER.json`。二进制稿件未因登记而自动进入仓库。你不必等待该稿才能做实验，不能将六月旧稿冒充它。

历史参考：45建筑/36合格/630组合/2031点；23 curated候选；20额外冻结验证；33 operational、20 research-only、53 HB计时场景。四项评分45/35/15/5；独立面积rho约0.997668、MAE0.45m²，复合排序rho1。55.40秒是旧完整2.5D计时；51.11秒是旧HB单场景中位；8.94小时只是外推。

这些不是新结果的目标值。相同条件下可作回归；发现错误要保留旧值、生成更正值和原因，不得反调代码追数字。

## 2. 执行顺序与目录

严格顺序：能力/数据检查 → 预登记本轮协议 → 几何与时间语义审计 → 必要的局部复算 → 效率对照 → 旧样本统计复核 → 汇总与模板 → GitHub交接。

新增目录使用 `icores_2027/`：
- `audit/`：能力、输入manifest、几何、时间、差异、问题结论；
- `configs/`、`scripts/`、`tests/`：本轮独立代码与协议；
- `runs/<run_id>/`：新派生汇总结果与经过脱敏的日志，不放受限原始输入；
- `paper_support/`：数字/主张台账、方法、图表与更正说明；
- `formatting/`：官方模板来源、版本、编译日志、匿名检查；
- `manuscript/`：稿件来源登记和后续改稿建议；
- `HANDOFF_TO_WEB.md`、`RESULTS_SUMMARY.json`、`STATUS.json`。

优先通过小模块/包装器复用Route B。需要修生产逻辑时仅改当前分支，明确变更；旧freeze仍可checkout。所有新CSV保留run_id/config_hash/code_commit/input_hash/measurement_class。

## 3. G0 能力与输入门槛（第一件事）

实际检查并写 `audit/EXECUTION_CAPABILITIES.json`：
- 当前日期/时区、OS、Python、工作目录是否可持久化；
- 终端能否执行一个小型Python测试、git读取/分支写入权限；
- CPU型号、物理/逻辑核心、内存、虚拟化限制（未知写UNKNOWN）；
- Radiance关键可执行文件及版本、lbt-recipes及依赖，允许在隔离环境安装免费依赖；
- 必要真实输入是否存在且可读，以及数据许可/来源；
- 不能以“写出一段命令”充当“已经执行”。

依照归档索引寻找而非猜路径。实验最小输入可能包括规范建筑属性、规范footprint geometry、固定有序sensor表、旧baseline及候选逐点/逐时结果、太阳时刻/WEA/recipe配置。优先使用已有规范数据，不必索取全部CAD/SKP。

现仓库明确未包含若干本地原始输入。没有输入时生成 `audit/MISSING_INPUTS.md`，每项给出逻辑文件名、已知来源索引、需要它的任务和最小字节/格式要求。要求作者通过获授权的dot私有运行环境提供；不要建议直接公开或上传GitHub这些受限输入。不得从图片反推“真实坐标”、拿toy数据顶替实景、声称自己可以读E盘。

若有工具但环境与历史不同，建立新隔离环境并记录差异；不能沿用旧Windows计时当新机器速度。若只有GitHub读写、没有计算工具，准确标记BLOCKED_NO_EXECUTOR并提交可执行脚本/缺口，不虚构成功。

## 4. G1 先冻结本轮协议，不看结果调目标

在运行新仿真/benchmark前提交 `configs/ICORES_PROTOCOL.json`，列明：
- 数据hash/场地/点位/太阳配置、代码基础、容差；
- 几何审计的5个既有配对：C9,C24；C9,C15；C9,C13；C13,C24；C6,C33；
- benchmark的共同候选顺序/子集和重复次数；
- 真实与合成测试明确隔离；统计不做后验挑样；
- 冻结N=20维持原配对，不重抽、不改原SHA；
- 结果不理想仍交付，不以rho/加速比达标作为实验“成功”标准。

基线分析：同一3m网格、0.1m接收点，3h阈值；原分析日2026-12-21、08:15–15:45、30min、UTC+8、north=0；高度floor3m/cap3m/fraction0.25。若发现定义错误，先记录新旧协议与影响范围，不静默替换。

## 5. G2 必做：退台几何与日照单调性审计

### 已核查的代码事实
`research_reproducibility/src/legacy_route_b/route_b_prepare_hb_batch.py` 的design_stepback围绕多边形质心缩放上层轮廓；没有在该函数强制验证它包含于原footprint。`face()`遇异常直接返回None。移除体积字段沿用规则减高公式。

### 待检验假设，而非既定结论
凹多边形的质心缩放可能产生原轮廓外的部分；也可能存在建面遗漏、holes处理、相交部件、坐标/接收点/时间映射或射线容差问题。不能尚未检测就宣布某一原因成立。

对固定不透明几何、固定太阳射线和固定接收点，若modified solid确为baseline solid的子集，仅删除遮挡不应降低直接日照。旧记录“4恶化点/9m²新低日照”需要解释，不能直接当真实设计副作用。

### 审计步骤
1. 复核baseline、rule_flat、legacy_stepback的真实输入hash、建筑ID、接收点顺序、太阳样本、单位和北向；点位用ID/坐标双重匹配，不能只比较行数。
2. 逐部件检查polygon有效性、凹性、holes、多部件union、上层轮廓outside area、z范围、实际面构造及退台实体包含性。容差按模型单位提前声明，既报绝对值又报相对值。
3. 使用适合当前棱柱的分层截面/布尔并集计算实际剩余体积；避免重叠部件重复计积。分别报告target removed volume和actual removed volume。不得把规则A*(h-h_rule)无条件当成转译实测移除量。
4. 取消本轮运行中静默吞建面异常：记录建筑/面ID/异常并fail-fast或标明无效场景，不自动buffer(0)改变几何而不留记录。
5. 对旧恶化点逐时定位：比较同一baseline与translated的可见性、遮挡面和射线高度。区分物理新增遮挡、点序错配、时间向量差异、表面数值问题。
6. 在有输入/环境时重放一个baseline和5个原转译场景（只需必要最小集合；旧rule/20验证不默认全部重跑），检查能否复现旧差异。
7. 如证实legacy转译越界/无效，保留原场景作错误审计；新增明确标记的 `contained_stepback_v2` 候选修正供审查。可使用合法向内收缩或显式裁交等方法，但报告真实几何/体积变化。不得直接改写历史设计意图。若难以同时满足内含与同移除体积，分别报告，不宣称体积匹配。
8. 修正版本需同一solver/config下baseline+受影响候选重新计算；总计通常6–11场景的规划范围，不是实际已跑数量。若发现共用baseline/时间/输出解析错误，立即扩大影响分析，标记CORRECTION_SCOPE_EXPANDED；不能保留受污染的23/20旧结论继续写。

输出：`audit/GEOMETRY_MONOTONICITY.csv`、`audit/ADVERSE_RAY_AUDIT.csv`（不得含受限完整坐标）、`audit/GEOMETRY_FINDINGS.md`、`runs/<id>/design_translation_recheck.csv`、`paper_support/CLAIM_CORRECTIONS.csv`。

结论必须有证据分类：LEGACY_REPRODUCED_AND_EXPLAINED / GEOMETRY_BUG_CONFIRMED / MAPPING_OR_NUMERIC_ISSUE / UNRESOLVED。若UNRESOLVED，本轮不能标可投稿；允许写不依赖这项结论的方法初稿。不能只删掉负结果掩盖问题。

## 6. G3 必做：预计算复用的公平效率对照

目的：隔离建筑级遮挡预计算/复用的收益，不把Python与Radiance启动开销差异全部归于算法创新。

- A：逐候选重新做几何求交，不跨候选复用blocker状态；允许正常共享读取、太阳向量和输入准备。
- B：预计算原高度/减高blocker数组，再用组合更新评估候选。
- 二者同一场地、同一太阳/网格、同一几何求交原语/容差、同一硬件/线程约束、同一候选集合、同一指标。不得故意写低效循环、关闭仅A的正常优化或人为延时制造加速。
- 显式核对逐点DSH、A/H/V/N、分数与排序。指标容差先写协议；不相等就先修，不报告等价加速。
- 将加载、太阳准备、几何precompute、候选evaluation、排序/Pareto、I/O以及end-to-end拆开。B的总时间必须包括precompute；不得只拿热缓存评估时间对比A的总时间。

先小样本pilot只用运行时间决定规模。预登记嵌套固定子集m=5/20/60及完整630，子集不按HB好坏选。B全630至少3次独立测量；A在同样子集至少3次，与B对同样m计算加速比。可分离warm-up但两边一致处理。

若pilot显示完整630的A三轮可在12小时以内完成，就完成全630匹配对照；否则在可完成的最大固定子集做真实匹配实验，明确只在该子集测得加速，完整630的A只允许外推且显著标记。不得把A的60候选时间和B的630时间相除当公平speedup。单项超预算就保留已完成记录并继续其他任务，不花钱换机器。

输出 `runs/<id>/ablation_runtime_records.csv`、`ablation_summary.csv`、`ablation_equivalence.csv`、`audit/HARDWARE_ENVIRONMENT.md`。记录重复id、命令、起止时间、CPU/内存/线程、状态、warmup、样本规模、input/config/code hash。

HB只作另一求解器的辅助成本参考：旧53场景的混合workers（initial2，其他4）须披露；跨机器不混算总加速比。需要同机参照时，可固定workers复测baseline和代表场景。原630-HB的8.94h始终是外推，不能升级为实测。

## 7. G4 必做但低成本：统计与方法语义修订

### 7.1 四项公式和N=0
保留真实45/35/15/5实现。确认630行N的min=max=0，零极差normalization设0；写明N项为常量，实际不能区分本次减高候选。只改变N权重、其余不变时排名应不变。旧NEW_LOW_SENSITIVE同时变其他权重，因此不能解释成“新增阴影惩罚本身有效”。无需为这一事实重跑HB或重调权重。

### 7.2 验证性质
冻结20行是按评分分位、体积覆盖和ID多样性选取的额外、outcome-blind样本，不是总体概率抽样、跨场地泛化或与源数据独立。用held-out from curated review / pre-frozen coverage sample等准确用语。不要写统计独立随机抽样或preregistered trial；若只能看到当前hash而无此前时间证据，应明确冻结先于输出是执行记录所报告，hash本身不证明时间先后。

将curated23与held-out20分开；各自复算面积对面积、分数对分数的可比统计，不把curated复合分数对HB单指标rho与held-out同指标rho差异当模型进步。

20行数据中19行面积减少量相同、1行差9m²，解释MAE0.45是聚合候选误差，不是空间分辨率0.45m²。TopK注明tie规则与集合范围；p值不得把浮点0写成数学精确0。复合分数共享V和当前常量N，rho1不是独立验证所有四项、更不是100%准确率。

### 7.3 时间和天气语义
08:15–15:45有16个半小时时刻；每个计0.5h时满日照为8h。核对实际recipe输入、WEA、二进制结果和太阳向量。如果这些是08:00–16:00的bin中心，就按该定义写明；不能把推测写成已证实协议，不能把7.5h端点跨度直接叫计算积分时长。

pvlib与Ladybug太阳位置算法可能不同，核对输入日期、UTC/经度符号和有效太阳向量。WEA在当前代码中以常量DNI=1000、DHI=0生成，说明它是DSH几何计算载体，不是实测气象或全年天气验证。

测试太阳低于地平线时不能计为可见时长。若当前冬至选定时刻全在地平线上方，区分测试覆盖缺口与本次结果实际污染。

## 8. G5 运筹学应用表达与资料整理

不训练ML、不新建网站、不为了会议添加LLM。写一个 `paper_support/METHOD_SPEC.md`：
- 决策变量z_i∈{0,1}，sum z_i=2，资格是研究约束不是法定拆改许可；
- 完整限定集合C(36,2)，h_i(z)规则，A/H/V/N与单位；
- blocker更新公式、伪代码、在说明几何求交成本前提下的复杂度和内存估计；注明Pareto排序等额外开销；
- 与逐候选重算的等价性/对照，不称提出全新通用OR算法；
- 偏好权重、Pareto与可接受性不混为一谈；
- 若退台缺陷成立，以审计后的结果改贡献，不为保留“最高收益有副作用”故事而保留错误。

复用原bibliography，但逐条核对作者/题目/卷期/DOI和正文主张；含糊来源进unverified列表，不编引用。特别核对Ladybug 2013原文作者和旧稿多列作者问题，保留真实核验结果。

本轮不做多场地、大量新采样、全630HB或昂贵网格研究。只有发现共享物理/解析错误时才扩大必需重跑范围，并立即报告。

## 9. G6 官方模板、匿名与写作交接

读取 `OFFICIAL_REQUIREMENTS.md`，从ICORES官网Templates跟随到Springer下载当前Word/LaTeX与instructions，记录hash/date；只编译一个匿名骨架验证环境，不把旧SOICT的12页/单盲要求搬过来，不用旧SCITEPRESS双栏模板。

Regular的10k–50k非空白字符是当前初投规则；出版25/20页是接收分类额度。写作目标约12–16页是我们内部目标，不是官方保证。不得缩字体/压边距。

输出模板编译日志、渲染页、必要的template version manifest。保留匿名骨架的可编辑公式/表格、引用、图题样例，但不要编造实验占位值。把成稿正文留给网页端审查后写。

匿名稿必须不含作者/单位/邮箱/真实GitHub用户名/私人文件路径/致谢身份；检查PDF属性、DOCX属性、批注修订和附图元数据。案例城市不是必须隐藏的作者身份，不无故改场地事实。不得自动创建公开匿名数据仓库；先提供匿名附件本地包并标记待作者批准。

保持准确AI使用披露；官网对匿名致谢位置存在交叉要求，记录待作者确认，不自动删除披露或发送邮件。正式提交前要确认SOICT没有在审记录；没有回执不等于已撤稿，作者确认后一稿一投。

## 10. 测试与证据门槛

至少实际执行：
- eligibility/630/唯一pair，strict bool，参数来源；
- 矩形、凹形、带洞、多部件footprint的包含性与体积测试；
- 无遮挡/单遮挡/单调削减不减少日照；夜间不计时；
- 面异常不可悄悄丢弃；sensor ID一一映射；
- A/B benchmark逐点与指标等价；
- N常量和零极差；旧20样本pair/hash未变；
- 新旧统计ledger不混用；PDF匿名和模板构建测试。

合成测试不是实景验证。旧19 passed不能拷贝为本轮测试；实际pytest输出/环境/时间戳都要留。保留失败记录，执行完成与科学结果理想分开。

## 11. 交付和状态

每完成一个任务就更新TASKS/STATUS并提交。恢复前读取最新远端HEAD，遇他人变更先检查，不强推。

最终必须包括：
1. `HANDOFF_TO_WEB.md`：repo/branch、结果版本、完成项、阻断、需要更改的论文段落和数据可用性；
2. `RESULTS_SUMMARY.json`：每实验的status、run_id、code_commit、source、measured/extrapolated和警告；
3. `paper_support/PAPER_NUMBERS_ICORES.csv`：claim/metric,value,unit,source,run_id,status；历史可复用项标REUSED_FROZEN，纠正项标CORRECTED，新执行标MEASURED/RECOMPUTED；
4. `paper_support/CLAIMS_LEDGER_ICORES.csv` 和 `CLAIM_CORRECTIONS.csv`，禁止提前保证最优、准确率、EI录用；
5. `audit/RESULT_DIFF_ICORES.csv`：新旧、原因、哪些主张受影响；
6. 每张图的来源、数值表、真实栅格/矢量属性、release scope；
7. `formatting/TEMPLATE_MANIFEST.json`、`ANONYMIZATION_CHECKLIST.md`；
8. `paper_support/MANUSCRIPT_CHANGE_MAP.md`，不需要全文重写；
9. `audit/MISSING_INPUTS.md`（无缺失也写NONE）。

原始CAD/OBJ/全部接收点/WEA/.res/.ill/.hbjson保持获授权的私有运行环境，不入Git。日志脱敏。GitHub当前是私有，不代表可以忽略既定上传边界。

最终结果commit不要试图在自身文件内写自己的SHA（循环依赖）。先提交实验代码/证据得到E，再在元数据提交M中引用E，最终答复分别给 evidence_commit 与 handoff_commit。不覆盖旧tag；可创建新annotated tag `icores-2027-evidence-v1` 指向E并核实远端。

状态严格拆分：
- EXECUTION_CAPABLE：能力已实际检查；
- EVIDENCE_READY_FOR_WEB_REVIEW：关键审计、匹配对照、必要复算、统计语义、台账/tests完成，未解P0=0；
- MANUSCRIPT_DRAFT_READY：仅正式全文写完且QA完成后由写作阶段更新，本轮默认false；
- AUTHOR_APPROVED：作者确认，dot不能代填true；
- SUBMITTED：有PRIMORIS回执才true，本轮必须false。

遇数据缺失、物理矛盾未解释、A/B结果不等价，不得标EVIDENCE_READY。结果不显著本身不是失败；诚实记录并让网页端判断论文主张。

## 12. 时间与最后回复

内部目标：10月16–17日能力/数据与协议；17–18日几何审计/必要复算；18–19日匹配效率对照与统计；20日证据冻结；21日网页端写作和终检；22日作者确认后提交。它是工作安排估计，不是对dot算力/数据可用性的承诺。截稿按官网AoE，内部不压最后小时。

最终不要只说“完成”，回复：
```
repo / branch:
evidence_commit / handoff_commit / tag:
EXECUTION_CAPABLE:
EVIDENCE_READY_FOR_WEB_REVIEW:
Tasks complete / blocked:
Geometry finding and affected claims:
Matched benchmark sizes/repeats/equality/measured speedup:
Old evidence reused vs newly executed:
Critical result differences:
HANDOFF_TO_WEB.md path:
Missing inputs / author decisions:
SUBMITTED: false
```

你交付后停止。网页端读取冻结结果、审查并写正式ICORES论文，Alan最终确认投稿。
