# 直接复制给 dot 的启动 Prompt

你现在接管“光权修复”ICORES 2027建筑师决策主线的**纯云端**冲刺。本任务一站式完成：云端检查→已有真实结果重算→Top10候选决策包→英文匿名论文→中文通俗核查稿→官方模板QA→上传私有GitHub交付。**不调用、控制或依赖用户本地电脑，也不等用户开启本地Codex。**

仓库（必须private）：`eksn425-del/light-right-repair-ai-prototype`
工作分支：`icores-2027-architect-first-cloud`
入口：`ARCHITECT_DECISION_START_HERE.md`
任务全文：`icores_2027/architect_first_cloud/CLOUD_EXECUTION.md`
会议规则：`icores_2027/architect_first_cloud/OFFICIAL_SUBMISSION.md`
状态与任务：`icores_2027/architect_first_cloud/TASKS.md`、`STATUS.json`

**真正研究目标**：建筑师在旧街区前期更新中，从规则定义的630个双建筑减高候选中，利用轻量采光分析得到可解释的Top10/非支配候选，送选择性HB-Radiance复核后，由建筑师而非算法做最终决策。效率复用与几何包含纠错用来证明筛选工具高效、可靠，不能替代这个故事。

你的第一件事不是写论文，而是核查你当前云电脑能否真读/写此私有仓库、运行Python/LaTeX、获取哪些实际数据。受限CAD/OBJ/逐点和HB场景原件目前可能只在本地，请确认云端是否真的持有。**不要假定能访问我的E盘；不要把历史HB结果冒充新云端实验**。缺原始模型就用GitHub里真实的630候选aggregate_B_m630_r1_run.csv及冻结科研台账进行可复算的候选表、排序、指标与图表工作，并标明CLOUD_RECOMPUTED_FROM_ARCHIVE。只有实际具备完整输入并真实运行才可以写NEW_REAL_SIMULATION；若关键素材无法取得，请写明缺口而不是伪造。

必须对照2026年4月初始大纲、6月初旧稿、6月20日候选筛选论文与最新ICORES论文，恢复“建筑师辅助决策”主线。不要把旧4月设想的模拟退火/安全路径/任意模型/AI自动设计写成已完成。必须验证Top10与23复核候选的选择来源；原20 frozen same-site覆盖样本不可重选。10月C24旧几何越界纠错按实际修正结果写，不能还说减法必然产生新阴影。482.9x只能用于既有两个同原语单线程实现。

请阅读所有任务书与官方链接后，从C0开始自动执行。各阶段完成即更新STATUS和TASKS、提交GitHub，直到输出：
1. `analysis/top10_rule_candidates.csv`及可读的10个候选决策卡；
2. 正式英文匿名ICORES Regular Paper源文件与PDF；
3. `paper/CHINESE_READER_VERSION.md`（面向建筑本科生）和`CHINESE_FAITHFUL_TRANSLATION.md`（逐段对照）；
4. 全部图表、数字来源台账、交叉验证、双盲/字符数/逐页QA；
5. `handoff/WEB_AUTHOR_HANDOFF.md`、`FINAL_STATUS.json`及精确GitHub commit、下载路径、缺口。

必须优先满足10月22日AoE截稿时效；若时间不够，先保证学术真实性和匿名送审，不得为了赶时间填假数。不要修改旧论文/冻结tag、不要公开研究仓库、不要上传未授权的原始场地文件。**不要代我登录PRIMORIS、付款、填写作者/版权声明或点击正式提交；最终由我和共同作者确认后操作。**

现在开始实做，不要只给我一个计划。先输出真实的云端能力审计并继续完成所有能完成的任务。只在确有必须由我提供的权限、原件或作者决定时一次性列出最小问题，其余自主推进并保留证据。
