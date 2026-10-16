# ICORES执行进度

截至建档：全部NOT_STARTED。负责人dot；网页端负责结果审查和论文。请勿引用旧SOICT_READY代替当前状态。

| ID | 优先级 | 工作 | 前置条件 | 验收文件 | 状态 |
|---|---|---|---|---|---|
| G0 | P0 | 实际执行能力、私有输入、官方规则复核 | GitHub/工具连接 | audit/EXECUTION_CAPABILITIES.json、MISSING_INPUTS.md | NOT_STARTED |
| G1 | P0 | 冻结新协议、容差、benchmark子集 | G0 | configs/ICORES_PROTOCOL.json+commit | NOT_STARTED |
| G2 | P0 | 5方案包含性/实际体积/恶化点审计及必要复算 | 真实几何、点位、HB | audit/GEOMETRY_FINDINGS.md、重算差异 | NOT_STARTED |
| G3 | P0 | 同条件naive vs cached遮挡对照 | 固定输入和终端 | ablation_summary/equivalence/records | NOT_STARTED |
| G4 | P0 | N常量、样本性质、同指标统计、时间语义 | 现有表及必要模拟输入 | METHOD_SPEC、CLAIM_CORRECTIONS | NOT_STARTED |
| G5 | P0 | 实际tests、数字/主张/图表台账、差异 | G2–G4 | PAPER_NUMBERS_ICORES、pytest日志 | NOT_STARTED |
| G6 | P1 | 官方面板/模板下载、匿名骨架编译 | 联网、文档环境 | TEMPLATE_MANIFEST、编译日志 | NOT_STARTED |
| G7 | P0 | GitHub evidence freeze与网页端交接 | P0无未解项 | HANDOFF_TO_WEB、RESULTS_SUMMARY | NOT_STARTED |
| W1 | 后续 | 正式英文稿、引用、版式、逐页QA | 网页端通过G7 | 稿件与QA报告 | NOT_STARTED |
| A1 | 后续 | 作者/权益/披露/单投确认与投递 | W1及作者批准 | 系统回执 | NOT_STARTED |

状态只能使用NOT_STARTED/RUNNING/PASS/COMPLETED_WITH_LIMITATIONS/BLOCKED/FAIL；PASS需要证据，不要求结果好看。
