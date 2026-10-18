# 光权修复 / ICORES 2027：建筑师决策主线云端冲刺入口

**建立：2026-10-18。状态：任务书已建立，尚未有本分支的新实验或新论文。**
**会议：ICORES 2027 第二轮 Regular Paper；截稿：2026-10-22 AoE（UTC+8约2026-10-23 19:59）。**
**项目：光权修复——帮助建筑师从受约束的旧街区采光改造候选中快速缩小方案选择范围。**

## 本轮唯一研究问题
> 在固定的旧街区模型与明确的低干预减高规则下，能否快速评价630个建筑组合，筛出Top-10/非支配候选，并把有依据、经适当复核的选择空间交给建筑师？计算复用与几何包含检查是这套流程可信的条件，不应取代建筑师决策主线。

**不是**任意城市、一键输出能施工的十张方案；不是训练式AI；不是证明建筑师不需要参与。

## 给 dot 的顺序
1. 阅读 `icores_2027/architect_first_cloud/CLOUD_EXECUTION.md` 全文。
2. 阅读 `icores_2027/architect_first_cloud/OFFICIAL_SUBMISSION.md`，通过官网重新核对。
3. 阅读 `icores_2027/architect_first_cloud/TASKS.md` 和 `STATUS.json`。
4. 读取本分支起点 `icores_2027/HANDOFF_TO_WEB.md`、`RESULTS_SUMMARY.json`、`paper_support/PAPER_NUMBERS_ICORES.csv`，现有 `manuscript_author_review/manuscript.tex`、完整630候选表和原始2026年6月20日中文论文。
5. 执行云端能力与输入审计；只做有真实数据支撑的运算；按阶段提交GitHub；最后交付匿名英文正式稿+通俗中文核查稿+可追溯候选表+投稿检查清单。

## 事实源与禁止混淆
- 原始项目目标：`project_archive_2026_10_16/readable_manuscripts/context/source_documents/光权修复_终版执行大纲.md`、`.../光权修复AI项目完整介绍_给网页端AI_2026-06-05.txt`（历史想法，不等于均已实现）。
- 论文“面向建筑师筛选候选”中期主线：`project_archive_2026_10_16/readable_manuscripts/history/route_b_june/光权修复论文_EI会议_中文学术定稿版_投稿前小修.md`。
- 科学实验冻结：`icores-2027-evidence-v1` (evidence SHA `af486946b210b12853b83f9dbdaf708255754d56`)；不得覆盖。
- 本分支起点 `df2f5ef28975c6a11376c1389f1773d215c9446c`，之前的ICORES v3论文可为写作素材，但必须先核对与本分支源文件版本/用户提供的v3 PDF是否相同。
- 630-candidate derived data: `icores_2027/runs/local_ablation_20261016/aggregate_B_m630_r1_run.csv`（与另外两次全量A/B记录及2026年冻结论文数字台账交叉核对）。**不要把文件年份误写。**
- 当前仅要求云端工作；不得访问/要求远程控制用户Windows、E盘、USB或本地Codex。

## 工程目录
`icores_2027/architect_first_cloud/` 是本轮唯一新增产物路径，旧文件保持可追溯。
- `audit/`：权限、输入、完整性、版本、缺口、数值差异
- `analysis/`：可运行脚本、输出CSV、参数、完整日志
- `paper/`：英文匿名稿源、PDF、中文通俗稿、图表、引用核查、QA
- `handoff/`：最终给网页端/作者的审阅材料及投稿说明

**停止线：dot不得自行向PRIMORIS提交、付费、填写作者声明或公开研究仓库。作者审批后由用户操作。**
