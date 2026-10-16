# ICORES执行进度

本轮已实际开始；状态以各项证据为准。负责人dot；网页端负责结果审查和论文。请勿引用旧SOICT_READY代替当前状态。

| ID | 优先级 | 工作 | 前置条件 | 验收文件 | 状态 |
|---|---|---|---|---|---|
| G0 | P0 | 实际执行能力、私有输入、官方规则复核 | GitHub/工具连接 | audit/EXECUTION_CAPABILITIES.json、MISSING_INPUTS.md | PASS |
| G1 | P0 | 冻结新协议、容差、benchmark子集 | G0 | configs/ICORES_PROTOCOL.json+commit | PASS |
| G2 | P0 | 5方案包含性/实际体积/恶化点审计及必要复算 | 真实几何、点位、HB | audit/GEOMETRY_FINDINGS.md、重算差异 | RUNNING |
| G3 | P0 | 同条件naive vs cached遮挡对照 | 固定输入和终端 | ablation_summary/equivalence/records | RUNNING |
| G4 | P0 | N常量、样本性质、同指标统计、时间语义 | 现有表及必要模拟输入 | METHOD_SPEC、CLAIM_CORRECTIONS | RUNNING |
| G5 | P0 | 实际tests、数字/主张/图表台账、差异 | G2–G4 | PAPER_NUMBERS_ICORES、pytest日志 | RUNNING |
| G6 | P1 | 官方面板/模板下载、匿名骨架编译 | 联网、文档环境 | TEMPLATE_MANIFEST、编译日志 | PASS |
| G7 | P0 | GitHub evidence freeze与网页端交接 | P0无未解项 | HANDOFF_TO_WEB、RESULTS_SUMMARY | BLOCKED |
| W1 | 后续 | 正式英文稿、引用、版式、逐页QA | 网页端通过G7 | 稿件与QA报告 | NOT_STARTED |
| A1 | 后续 | 作者/权益/披露/单投确认与投递 | W1及作者批准 | 系统回执 | NOT_STARTED |

状态只能使用NOT_STARTED/RUNNING/PASS/COMPLETED_WITH_LIMITATIONS/BLOCKED/FAIL；PASS需要证据，不要求结果好看。

## 云端部分交接

96项本轮集成测试通过，G6模板验证完成。G2/G3真实输入依赖仍阻断；G7仅部分证据冻结，科学验收未通过。请按 LOCAL_CODEX_HANDOFF.md 在本机继续；云端最终交接提交后停止分支写入。

## 本机接续（尚未完成）

真实45建筑、2031点、六个历史HB场景均已找到并核验。六个实际模型与生产函数重新生成的面字典在JSON规范化后完全一致；点位与太阳时间映射通过。旧C9/C24和C13/C24的8个恶化射线事件均定位到C24越出原轮廓的上层墙面。四个越界配对已准备 contained_v2，不把准备完成当作复算完成。新103项集成测试通过，包含7项重放解析回归。完整真实A/B测试仍在运行，pilot仅按时间选择了5/20/60/630、各3次。HB受控重放安排在速度测试结束后，避免主动并发重求解影响计时。所有就绪/稿件/作者/提交标志仍为false。
