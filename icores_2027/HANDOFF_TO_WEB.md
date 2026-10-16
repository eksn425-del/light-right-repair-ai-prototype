# ICORES 2027 本机最终证据交接

## 当前本机状态，2026-10-17

EVIDENCE_READY_FOR_WEB_REVIEW=true。本机实验、验证和Git证据交付已完成。manuscript_draft_ready/author_approved/submitted仍全部false。最终状态以本节及`RESULTS_SUMMARY.json`为准；下方云端部分交接仅保留作历史。

- 仓库`eksn425-del/light-right-repair-ai-prototype`，当前GitHub connector已核验private。
- 唯一分支`icores-2027-sprint`，不改main、不强推、不移动历史tag。
- evidence_commit E：`af486946b210b12853b83f9dbdaf708255754d56`。
- handoff_commit M：本次补入E/tag和最终ready状态的元数据提交，由分支HEAD/外部交付SHA定位，避免自引用；M的父提交是E。
- annotated tag：`icores-2027-evidence-v1`已创建、推送、核验远端。tag对象`67eaba3a7af2cf6a20bd292e7a106a3ac09c5203`，peeled目标为E。
- tag固定科学证据E；E的交付元数据记录当时待Git收敛。请从分支最终M读取完成状态；不要用E的交付前状态否定最终交付，也不要改写E来回避正常的两阶段流程。

已完成：45建筑/2031点/16时槽真实归档输入核查，六个旧HB场景逐点逐时精确重放，四个contained-v2新场景实际运行；原20样本未改未重跑。四个旧转译越界，恶化射线实际命中C24越出原轮廓的上层墙面，原因已解释。四个修正版在固定模型/网格/太阳下均无新增遮挡事件、恶化点或新增暗区。C9/C13本就包含，复用其未变结果，不是第11次模拟。

5/20/60/630各三次匹配测试全部等价；630的A为实测，B含预计算。最终中位A=11608.1830554s，B=24.0371276s，比值482.9272136。只针对两个具体单线程同原语实现，不是所有CAD/HB/空间索引实现的优势。完整630旧新排序零变化。112项实际本机测试通过，失败过程和旧结果保留。

重要限制：规范几何为DXF组件包围盒并集，存在共享/重叠轮廓与旧OBJ不一致，不能当作精确实测边界。体积分列名义预算和实际并集移除，不声称等体积。实际WEA为常量载体，不是实测天气；north0为假设。HB/pvlib有效太阳向量不同。20样本仍是同场地覆盖样本，rho1、恒定N和MAE0.45m²的限定继续适用。

当前阅读顺序：`audit/LOCAL_FINAL_REPORT.md`、`paper_support/WEB_WRITING_BRIEF.md`、`METHOD_SPEC.md`、最终数字/主张/差异台账，再读`runs/local_ablation_20261016/`、`runs/local_hb_20261016/translation_outcome_comparison.csv`及源表、`runs/local_protocol_20261016/`、`runs/local_quality_20261016/`。两张新聚合图有300dpi PNG、原生SVG/PDF和各自source/run/script/hash manifest，无真实场地几何。

网页端下一步是审查最终证据和修订正式英文稿，不再补造数据或重选原20。作者仍需处理署名/权益、单投、匿名与AI披露位置、文献/模板已记录冲突及正式稿逐页QA。论文未完成、未获作者批准、未投稿。原CAD/DXF/SKP/OBJ、点位坐标、WEA、HBJSON和Radiance中间文件只留本机。

## 以下为保留的云端历史检查点，不是当前状态

EVIDENCE_READY_FOR_WEB_REVIEW=false。此包是可审查的部分检查点，不是科学验收完成或可投稿稿件。

- 仓库 eksn425-del/light-right-repair-ai-prototype 保持 private；唯一分支 icores-2027-sprint。
- evidence_commit：afc13c078965f225ea4aaa62ff3db4b2010908b3。
- handoff_commit：包含最终交接元数据的提交 M；通过 GitHub HEAD/外部交付引用解析，避免自引用。
- tag：未创建，TAG_CREATION_UNAVAILABLE。连接器没有 tag 创建接口，shell 未认证；未使用 branch 接口冒充 tag。最终本机可按 LOCAL_CODEX_HANDOFF.md 创建新 annotated tag，不覆盖旧 tag。

## 已实际执行

本轮终端和私有 GitHub 写权限已核查；Honeybee/Radiance 6.0.2 合成 smoke 真正运行成功，遮挡/无遮挡为 0/0.5h。失败尝试、安装版本和仅驱动时间记录的依赖补丁完整保留。真实场地新 HB 场景数为 0。

生产源函数合成审计确认凹形越界、courtyard 丢洞、静默面失败、低高度 clamp 体积差和夜间 latent bug。五个真实退台案例及旧恶化点因缺原始输入仍未解释；合成反例不能证明真实原因。contained_stepback_v2 不是已验收修复。

冻结 20 样本原字节及原 SHA 保留。新重算同指标面积相关系数：curated23=0.9992582518450251，heldout20=0.997668088547906；后者 MAE=0.45m²（19 个完全一致，1 个差9m²），不代表亚网格精度。N 恒定，其评分贡献0.05；旧跨指标 rho 和 Top5 tie 处理不能作改善证据。16×0.5=8h，实际 HB 时列/太阳对应仍待核查。

同原语 A/B benchmark 已实现输入 hash、协议、等价性、计时和预计算总成本契约；真实计时尚未运行，speedup 为空。不能用旧跨机器/跨求解器数字替代。

96 项集成测试通过；统计图为冻结汇总重算，SVG/PDF为真实矢量。新数字、主张和差异台账区分合成、重算、历史复用及未运行。

官方当前 LLNCS 模板编译成匿名2页 proof，15项匿名测试、两页视觉检查通过，13条引用元数据核查。该 proof 低于正式稿字数，不是论文；AI披露位置、模板字体与说明差异、Ladybug作者元数据冲突等记录在 formatting/。

## 审查入口

1. RESULTS_SUMMARY.json、STATUS.json、TASKS.md：状态与阻断。
2. audit/GEOMETRY_FINDINGS.md、STATISTICS_FINDINGS.md、MISSING_INPUTS.md。
3. paper_support/METHOD_SPEC.md、PAPER_NUMBERS_ICORES.csv、CLAIM_CORRECTIONS.csv、CLAIMS_LEDGER_ICORES.csv、MANUSCRIPT_CHANGE_MAP.md。
4. audit/RESULT_DIFF_ICORES.csv、paper_support/FIGURE_MANIFEST.json、runs/quality_20261016/。
5. formatting/G6_REPORT.md、OFFICIAL_RECHECK.md、TEMPLATE_MANIFEST.json、anonymous/skeleton.pdf、rendered/。
6. LOCAL_CODEX_HANDOFF.md：可直接复制给本机 Codex 的完整中文接续指令，明确可执行脚本及尚需开发的历史HB重放部分。

## 最小阻断包与下一步

需要 clean run 的45建筑真实footprints、2031点有序坐标、baseline与五方案实际模型/recipe/WEA/太阳时列及逐点逐时结果、来源/单位/北向/hash。按归档索引在已授权本机定位；受限原始输入和逐点结果全程留本机。缺失哪些就暂停哪些，继续其余任务。

云端已完成部分检查点，在 M 后停止所有分支写入，本机成为单一执行者。真实物理矛盾、必要复算、匹配性能和时间语义未解决前不得把 ready 设 true。网页端负责最终英文论文审核修改；权益、披露、单投、最终投稿由作者确认。未发送邮件、投稿、缴费或购买算力。
