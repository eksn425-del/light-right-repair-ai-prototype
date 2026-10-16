# ICORES 2027 云端部分证据交接

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
