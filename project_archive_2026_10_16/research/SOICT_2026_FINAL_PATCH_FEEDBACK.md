# SOICT 2026 最终补丁执行反馈报告

日期：2026-09-10  
项目：Light Equity / Solar-Access Computational Screening Research  
研究分支：`research-repro-v1`  
运行编号：`baseline_20260909_clean`

## 1. 总体判断

本轮任务已经完成，当前包可以作为 SOICT 2026 论文初稿写作的事实与证据交接包。

`SOICT_WRITE_READY = TRUE` 的含义是：评分定义、参数来源、样本冻结、回归审计、测试、论文数字台账、主张台账和 public-safe 发布流程均已通过。本状态不表示已经完成论文正文，也不表示已经完成 630 个候选的全量高保真 HB-Radiance 模拟。

## 2. 本轮完成的核心修复

### 2.1 评分公式与配置单一事实源

生产评分统一为：

`0.45 A_norm + 0.35 H_norm + 0.15 (1 - V_norm) + 0.05 (1 - N_norm)`

四个权重现在由 `configs/research.yaml` 读取，Route B 枚举、复合排序验证和权重敏感性分析共用同一套公式。代码不再在不同脚本中分别维护评分定义。

### 2.2 Route B 参数化

以下参数已经从硬编码改为运行时配置：

- 高度下限、最大削减高度和削减比例；
- `Asia/Shanghai` 时区与 UTC+8；
- 冬至日、08:15—15:45 时间段；
- 30 分钟 timestep；
- 严格的布尔值解析；
- 3 m 网格和 0.1 m 传感器高度。

### 2.3 N=12 fallback 修复

五个分层的样本分配现在明确为：

- N=20：`4/4/4/4/4`；
- N=12：`3/3/2/2/2`。

此前 N=12 可能只返回 10 个样本的问题已修复。冻结的 N=20 样本没有重新选择，也没有重新运行其 HB 场景。

### 2.4 630 候选迁移审计

评分公式迁移后，630 个候选的以下内容全部保持一致：

- 候选 ID；
- 候选配对；
- 评分值；
- 排名；
- Top-10 成员；
- Pareto 成员。

最大绝对评分差为 `0`。

### 2.5 Composite-ranking validation

在已冻结的独立 HB 样本 N=20 上，使用与生产排序一致的四项复合指标进行验证。没有重新抽样，也没有使用 HB 结果反向选择样本。

结果：

- Spearman rho：`1.000000`；
- Top-3：`3/3`；
- Top-5：`5/5`；
- Top-10：`10/10`；
- 平均绝对排名误差：`0`；
- 中位绝对排名误差：`0`；
- 最大绝对排名误差：`0`。

论文中只能表述为“在冻结的独立 N=20 样本和本研究指标定义内的复合排序一致性”，不能表述为普遍准确率。

### 2.6 权重敏感性

敏感性分析已经改为真实四项生产公式，并包含 6 组预先定义的权重情景和 1,000 次归一化 Monte Carlo 扰动。

- 最低确定性 Spearman rho：`0.975941`；
- 最低确定性 Top-10 重叠：`6/10`；
- Monte Carlo seed：`20260909`。

这说明结果对权重存在敏感性，论文应报告稳健性范围，不应只报告 BASE 权重下的单一排名。

### 2.7 Runtime 语义修复

运行时间已经区分：

- 630 候选 2.5D screening 的实测时间；
- 单个 HB 场景的实测时间；
- 23/630 的规则候选高保真验证范围；
- 33 个 operational workflow 场景；
- 20 个 research-only independent validation 场景；
- 630 个 HB 场景的 serial-equivalent extrapolation。

630 场景的 `32197.24 s` 是根据实测单场景中位数外推的等效值，不是完成 630 场 HB 批处理后测得的墙钟时间。Operational batch elapsed time 保留为 `NOT_MEASURED`。

## 3. 当前数据规模与证据边界

- 建筑数：45；
- 规则筛选后 eligible buildings：36；
- 2.5D 候选总数：630；
- 传感点数：2,031；
- 规则候选 HB 验证：23；
- operational HB scenes：33；
- independent research-only scenes：20；
- 已测 HB scenes 总数：53；
- 2.5D screening 实测中位时间：约 55.40 s；
- HB 单场景实测中位时间：约 51.11 s。

这些数字都已同步进入 `PAPER_NUMBERS.csv`。所有主张边界都已写入 `CLAIMS_LEDGER.csv`。

## 4. 测试与发布结果

### 私有研究包

- pytest：`19 passed`；
- Python 编译检查：通过；
- `git diff --check`：通过；
- 当前本地分支：`research-repro-v1`；
- 本地工作树：干净。

### public-safe 镜像

- pytest：`17 passed, 2 skipped`；
- 两个 skipped 测试只依赖被刻意排除的私有建筑几何表；
- 未上传真实 CAD、DXF、DWG、SKP、私有 OBJ、传感点坐标或 Radiance 中间文件；
- `main` 分支未修改；
- `research-repro-v1` 已推送到 GitHub。

## 5. GitHub 版本

仓库：<https://github.com/eksn425-del/light-right-repair-ai-prototype>  
分支：`research-repro-v1`  
证据包 release commit：`6b64fe43451e2e0330930a5677cbe3432307282b`  
Tag：`soict-2026-write-ready-v1`  
分支元数据提交：`fdad2c3810e6a105f2f441078759320fa4e59247`

Tag 指向证据包 release commit；后续的元数据提交只补写最终 commit/tag 信息，没有改动实验数字或科学定义。

## 6. 论文写作可直接使用的材料

建议网页端 AI 按以下顺序读取：

1. `SOICT_2026_PAPER_WRITING_BRIEF.md`：论文结构、事实边界、图表与证据说明；
2. `paper_support/PAPER_NUMBERS.csv`：唯一数字来源；
3. `paper_support/CLAIMS_LEDGER.csv`：允许与禁止的主张；
4. `paper_support/TABLE_INDEX.md`；
5. `paper_support/FIGURE_INDEX.md`；
6. `paper_support/RESULT_DIFF_AUDIT.csv`；
7. `audit/SCORING_FORMULA_MIGRATION_AUDIT.csv`；
8. `HANDOFF_TO_CHATGPT.md`；
9. `RESULTS_SUMMARY.json`。

写作时应重点强调：

- 这是规则驱动的 AI-assisted spatial decision workflow；
- 2.5D 方法负责全候选低成本筛选；
- HB-Radiance 是选择性验证，不是 630 候选全量真值；
- 复合排序结果只在冻结独立 N=20 样本、固定指标和当前几何范围内成立；
- 最终建筑设计接受仍是 human-in-the-loop。

## 7. 不能写成的结论

不要写：

- “99.7% accuracy”；
- “普遍准确”或“适用于所有街区”；
- “Radiance ground truth”；
- “630 个候选全部完成 HB 高保真模拟”；
- “AI 比人工设计更好”；
- “全局最优方案”；
- “自动满足施工、法规、产权或历史保护要求”。

## 8. 仍然存在的研究限制

1. 当前是单一真实场地和一个冻结独立样本，不足以支持多案例泛化结论。
2. 2.5D 筛选仍然依赖简化的建筑体块和规则化遮挡判断。
3. HB 验证是选择性的，不能替代 630 个候选的全量高保真计算。
4. Operational HB batch elapsed time 尚未直接测量。
5. 设计转译、建筑可实施性、法规、产权、历史价值和最终方案接受仍需人工审查。

## 9. 下一步建议

下一步可以开始论文初稿，但建议先完成以下工作：

1. 依据 writing brief 搭建论文结构，不直接复制生成式长段落。
2. 只从 `PAPER_NUMBERS.csv` 取数字，并在每个数字旁记录来源。
3. 用 `CLAIMS_LEDGER.csv` 逐句检查摘要、结果和结论，避免扩大主张范围。
4. 将 2.5D screening、selective HB verification、composite validation、weight sensitivity 和 runtime semantics 分开写清楚。
5. 把限制写进方法和讨论部分，而不是在投稿前临时补充。
6. 人工方案可以作为设计背景或人工复核案例，不必被包装成与算法进行优劣竞赛。

本报告是工程与研究交接反馈，不是论文正文。
