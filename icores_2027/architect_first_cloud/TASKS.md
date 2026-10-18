# ICORES 2027 建筑师决策主线 / cloud-only 任务进度

**当前状态：NOT_STARTED；此文档是准备工作，不代表dot已执行。**

| Gate | 必须完成 | 交付证据 | 状态 |
|---|---|---|---|
| C0 | 云端终端、GitHub、原始输入能力审计；区分数据可重新分析和新真实模拟 | audit/CLOUD_CAPABILITIES.json, INPUT_MATRIX.csv | NOT_STARTED |
| C1 | 读取4月/6月初/6月20日/最新论文，冻结建筑师决策故事与实验边界 | audit/NARRATIVE_DELTA.md | NOT_STARTED |
| C2 | 从真630表重算规则Top10、Pareto、23来源、候选决策卡；回归与审计 | analysis/*csv, architect_decision_cards.md, CLOUD_RUN_LOG.md | NOT_STARTED |
| C3 | 严格引用旧23/20、10月几何纠错、效率数据；非同来源不混用 | analysis/decision_evidence_matrix.csv, audit/RESULT_RECONCILIATION.csv | NOT_STARTED |
| C4 | 新英文匿名论文以建筑师候选筛选为中心；完整BibTeX+来源、图表 | paper/manuscript.tex, references.bib, figures | NOT_STARTED |
| C5 | 中文通俗阅读稿及逐段对照翻译 | paper/CHINESE_READER_VERSION.md, CHINESE_FAITHFUL_TRANSLATION.md | NOT_STARTED |
| C6 | 官网规则、编译、字符数、匿名、全页视觉QA；生成PDF | paper/anonymous_regular_submission.pdf, QA_REPORT.md | NOT_STARTED |
| C7 | 私有GitHub保存全套文件、handoff与commit/sha，作者可直接审阅 | handoff/FINAL_STATUS.json, WEB_AUTHOR_HANDOFF.md | NOT_STARTED |
| A1 | 作者信息/权益/AI披露/单投/最终提交系统回执 | 作者行动；dot禁止执行 | WAIT_AUTHOR |

阶段可为 NOT_STARTED / RUNNING / PASS / PARTIAL / BLOCKED / FAIL。若云端缺真实几何，允许C2/C3基于真实CSV重算为PASS，**新真实HB场景必须标记NOT_RUN**。只有该输出真实存在才允许宣称"已云端实验"。

不强推、不改main/旧分支/冻结tag、不公开、不使用用户本地电脑、不提交PRIMORIS。
