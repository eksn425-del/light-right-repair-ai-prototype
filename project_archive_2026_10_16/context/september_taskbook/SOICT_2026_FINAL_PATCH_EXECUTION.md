# SOICT 2026 光权修复项目：最终一致性补丁、实验冻结与论文交接执行文档

**项目**：Light Equity / Solar-Access Computational Screening Research  
**目标会议**：SOICT 2026（优先冲刺），ICOCE 2027（保底）  
**执行者**：Codex  
**事实中枢**：GitHub  
**网页端职责**：最终代码审查、实验解释、正式论文写作与投稿版式  
**日期**：2026-09-10

---

## 0. 本轮任务的唯一目标

这一轮不是重新做研究，也不是重新发明算法，更不是让 Codex 写最终论文。

本轮必须完成：

1. 修正当前研究包中剩余的**科学一致性/工程一致性问题**；
2. 对所有受影响的**低成本分析与统计结果重新计算**；
3. 不重新运行没有必要重跑的 20 个独立 HB-Radiance 样本；
4. 确认 clean reproduction 的 630 候选与历史冻结结果不发生非预期变化；
5. 生成一套**SOICT 写作可直接读取**的完整 evidence package；
6. 把公开安全的代码、结果摘要、数字表、主张表和写作交接文件推送至 GitHub；
7. 最终给网页端 ChatGPT 一个明确的最终 commit SHA 与 tag。

完成后，Codex 停止。**不要擅自写最终论文正文**。网页端 ChatGPT 将从 GitHub 获取最终结果后，按照 SOICT 2026 官方 Springer CCIS 格式写正式论文。

---

# 1. 当前事实基线

当前 GitHub：

- repository: `eksn425-del/light-right-repair-ai-prototype`
- research branch: `research-repro-v1`
- 当前公开分支 HEAD（2026-09-10 检查时）：`f12434f42388ddcdf99723801435ac5d62f24d04`
- 研究目录：`research_reproducibility/`

当前 clean run：

- `baseline_20260909_clean`

当前已验证核心结果：

- 总建筑：45
- eligible buildings：36
- unordered two-building candidates：630
- fixed sensors：2031
- curated HB rule candidates：23
- frozen independent HB validation candidates：20
- curated rank Spearman：约 0.883399
- independent low-area metric Spearman：约 0.997668
- independent Pearson：约 0.999623
- independent MAE：约 0.45 m²
- independent sign agreement：1.0
- 630-candidate 2.5D screening median：约 52.33 s
- HB median per measured scene：约 51.11 s
- full 630-HB runtime：只能作为 serial-equivalent extrapolation，不是实测
- C9,C15：design translation 正向，无已观察到的新低日照面积或恶化点
- C9,C24：高收益但 design translation 有 4 个恶化点与 9 m² 新低日照面积
- C13,C24：仍存在 adverse signal

这些数字是 regression references。  
**任何新计算如果不同，必须保留真实新结果并解释，不得硬改回旧值。**

---

# 2. P0：修正真实评分公式与 single source of truth

## 2.1 当前必须解决的问题

当前 630 candidate production ranking 的实际代码使用的是四项评分：

\[
S =
0.45 A_{norm}
+ 0.35 H_{norm}
+ 0.15(1-V_{norm})
+ 0.05(1-N_{norm})
\]

其中：

- `A_norm`：low-area reduction normalized
- `H_norm`：average direct-sun-hours gain normalized
- `V_norm`：intervention volume normalized
- `N_norm`：new low-area normalized

这等价于排序意义上的：

\[
S' =
0.45 A_{norm}
+ 0.35 H_{norm}
- 0.15V_{norm}
- 0.05N_{norm}
\]

加法常数不改变 ranking。

但是当前旧论文以及 `run_weight_sensitivity.py` 的 BASE 使用三项公式：

\[
0.45 A + 0.35 H - 0.10V
\]

这是**必须修正的科学一致性问题**。

## 2.2 正确动作

不要为了匹配旧论文，把 production ranking 改回三项式。

本轮应正式冻结：

> **四项公式才是本研究真实 production screening score。**

在 `configs/research.yaml` 中新增/统一：

```yaml
screening_score:
  low_area_drop_weight: 0.45
  avg_gain_weight: 0.35
  intervention_volume_economy_weight: 0.15
  new_low_area_avoidance_weight: 0.05
```

所有正式代码都从 config/runtime 读取。

禁止在多个脚本中重复硬编码同一组权重。

## 2.3 非回归要求

修改参数来源后重新运行 630 candidate screening。

必须验证：

- candidate count = 630
- candidate IDs/pairs 不变
- ranking 与当前 clean freeze 一致
- score 在浮点容差内一致
- Top-10 一致
- Pareto set 一致

输出：

`audit/SCORING_FORMULA_MIGRATION_AUDIT.csv`

字段至少：

- candidate_id
- pair_key
- old_clean_score
- config_driven_score
- abs_diff
- old_rank
- new_rank
- rank_same
- top10_same
- pareto_same

若 ranking 变化，不得继续静默写论文；必须进入 root-cause audit。

---

# 3. P0：真正参数化 Route B 核心运行

当前配置已经声明，但部分代码仍然硬编码。全部修正为配置驱动，同时要求结果保持不变。

## 3.1 Runtime 新增字段

`Runtime` 至少新增：

- `timezone`
- `height_floor_m`
- `height_reduction_cap_m`
- `height_reduction_fraction`
- 四项 score weights

## 3.2 `reduced_height()`

不得再硬编码 3.0 / 0.25。

统一使用：

```text
new_h = max(
    height_floor_m,
    h - min(height_reduction_cap_m,
            height_reduction_fraction * h)
)
```

## 3.3 `solar_samples()`

不得硬编码 `Asia/Shanghai`。

使用 config `timezone`。

## 3.4 每个可见时间样本的小时数

当前 30 min 等于 0.5 h，所以旧结果没错。

但代码不能硬编码：

```python
visible * 0.5
```

改为：

```python
visible * (timestep_minutes / 60.0)
```

本轮 30 min 配置下必须产生与 clean freeze 相同结果。

## 3.5 Boolean

核心 production path 不再使用宽松的 `boolish()`。

统一使用 `strict_bool()`。

非法布尔值必须 fail-fast。

## 3.6 WEA/analysis-period

尽可能使日期、时间范围、时间步长、时区/UTC offset 都来自 config。

但本轮**不能为了“更优雅”改变已有太阳时刻定义**。

配置仍为：

- Xiamen approx. latitude 24.55
- longitude 118.03
- timezone Asia/Shanghai
- date 2026-12-21
- 08:15–15:45
- 30 min
- north 0°
- grid 3 m
- sensor height 0.1 m
- low-DSH threshold < 3 h

若 WEA 生成逻辑重构，必须对旧 clean WEA 的时间戳和 direct-sun-hours输出做 regression check。

---

# 4. P0：修正 N=12 fallback sampling bug，并加强 sampling tests

当前 `freeze_independent_sample.py` 允许 `N=12`，但 `per_stratum = n // 5` 会只生成 10 个样本。

当前正式运行使用 N=20，因此**已完成的 20 个 HB validation 不受影响，不重跑**。

但 publication-grade code 必须修复。

可选方案：

### 方案 A（推荐）

明确支持：

- N=20：`[4,4,4,4,4]`
- N=12：`[3,3,2,2,2]`

分配顺序固定并记录在 sampling plan。

### 方案 B

彻底取消 N=12 fallback，只允许 N=20。

如果采用 B，要同步修改文档、CLI validation 和 tests。

## 4.1 测试必须测试“真实采样函数”

不要再只测试 pandas `sample()`。

新增测试：

- same seed -> same exact pair list
- N=20 -> exactly 20
- each quintile -> 4
- all selected pairs exclude curated set
- no duplicate pair
- frozen SHA reproducible
- if N=12 retained -> exactly 12 with declared allocation

---

# 5. P0：新增独立样本 Composite Ranking Validation

这是本轮最重要的**新分析**，但不需要重新跑 HB。

## 5.1 为什么需要

目前 `rho ≈ 0.997668` 比较的是：

> 2.5D low-area reduction vs HB-Radiance low-area reduction

它证明的是**核心环境响应指标 fidelity**。

但 production screening 是四项 composite score。

因此新增：

> **2.5D composite ranking vs HB-derived composite ranking**

这样论文可以区分：

1. Metric fidelity
2. Decision-ranking fidelity

## 5.2 数据来源

只使用已经冻结并完成的 20 个独立 HB candidates。

绝对不能重新选择样本。

## 5.3 HB-reference composite score

对每个 independent candidate 构造：

- `A_HB`：HB low-area reduction
- `H_HB`：HB average DSH gain
- `V`：同一 intervention volume
- `N_HB`：HB new low-area

**Normalization 不能使用 HB outcome 后重新优化权重。**

推荐做法：

使用完整 630 个 2.5D candidate universe 在 HB 独立结果产生之前已经确定的 normalization bounds：

- `A_min/max`
- `H_min/max`
- `V_min/max`
- `N_min/max`

然后把 HB A/H/N 映射到同一固定尺度。

如果 HB 值超出 2.5D bounds：

- 不要 clip
- 保留 <0 或 >1 的 normalized value
- 在方法文档说明

HB-reference score：

\[
S_{HB} =
0.45 A_{HB,norm}
+0.35 H_{HB,norm}
+0.15(1-V_{norm})
+0.05(1-N_{HB,norm})
\]

2.5D score 使用 production score，不重新拟合。

## 5.4 输出指标

至少：

- sample size
- Spearman rho
- Spearman p-value
- Top-3 overlap / recall
- Top-5 overlap / recall
- Top-10 overlap / recall
- mean absolute rank error
- median absolute rank error
- maximum absolute rank error

可选且仅在统计实现可靠时：

- deterministic bootstrap CI for Spearman
- seed fixed at 20260909

不要称作“global Top-K recall”。

只能称：

> within-independent-sample composite-ranking agreement

## 5.5 输出文件

必须公开安全地推送：

- `results/independent_composite_ranking.csv`
- `results/independent_composite_metrics.csv`
- `figures/F09_independent_composite_ranking.png`

并进入：

- `PAPER_NUMBERS.csv`
- `CLAIMS_LEDGER.csv`
- `TABLE_INDEX.md`
- `FIGURE_INDEX.md`
- `RESULTS_SUMMARY.json`

---

# 6. P0：重做 Weight Sensitivity，BASE 必须是真实四项公式

当前三项 sensitivity 结果不得作为 SOICT 最终证据。

## 6.1 新 BASE

```text
A = 0.45
H = 0.35
V economy = 0.15
N avoidance = 0.05
```

## 6.2 建议 deterministic scenarios

所有 weights 必须非负，且四项总和建议归一为 1：

```text
BASE
0.45 / 0.35 / 0.15 / 0.05

AREA_HEAVY
0.55 / 0.25 / 0.15 / 0.05

GAIN_HEAVY
0.30 / 0.50 / 0.15 / 0.05

VOLUME_SENSITIVE
0.40 / 0.30 / 0.25 / 0.05

NEW_LOW_SENSITIVE
0.40 / 0.30 / 0.15 / 0.15

BALANCED
0.40 / 0.35 / 0.15 / 0.10
```

如果需要调整 scenario，可调整，但必须在结果计算前固定。

## 6.3 指标

- Spearman with BASE
- Top-5 overlap
- Top-10 overlap
- Top-20 overlap
- Jaccard
- C9,C15 rank
- C9,C13 rank
- C9,C24 rank
- candidate Top-10 selection frequency

## 6.4 Monte Carlo

保留 1000 次 weight perturbation，但改为四项。

围绕 BASE ±20% 做乘性扰动，然后统一 normalize weights 总和为 1。

固定 seed 20260909。

输出：

- `results/weight_sensitivity_v2.csv`
- `results/weight_sensitivity_summary_v2.csv`
- `results/candidate_rank_stability_v2.csv`
- `figures/F08_weight_robustness_v2.png`

旧三项 sensitivity 文件保留为 historical / superseded，不删除。

在 `PAPER_NUMBERS.csv` 中旧值必须标记：

`SUPERSEDED_NOT_FOR_PAPER`

---

# 7. P0：Runtime 语义修正

## 7.1 必须区分四种数量

不要混淆：

1. **rule candidates selected for HB**：23 / 630
2. **operational HB scenes**：包括 baseline / support / design translation 的实际运行场景
3. **research-only independent validation scenes**：20
4. **total measured HB scenes**

论文不能用 “33 / 630 = candidate high-fidelity fraction” 这种容易误解的说法。

更合适：

- selected rule-candidate verification fraction = `23 / 630`
- total operational HB scene count = 单独报告
- independent validation = research evaluation overhead，不计入 operational screening fraction

## 7.2 630-HB 必须标记为 extrapolation

写法固定为：

> serial-equivalent extrapolation from the measured per-scene median

禁止写：

> full HB runtime

除非真的跑了 630 场景。

## 7.3 并行语义

当前 `run_hb_batch.py` 是逐 scenario 顺序运行，但每个 `lbt-recipes` scenario 内用 `-w workers` 并行。

因此记录：

- per-scene wall time
- workers per HB scene
- CPU model
- RAM
- physical/logical cores
- OS
- Radiance version
- LBT versions

不要把“每场景 wall time 的总和”称为真实 end-to-end batch elapsed time，除非有 batch-level stopwatch。

## 7.4 如果不重跑 HB

本轮不要求重新跑 53 个场景。

可基于已有 runtime records：

- median
- IQR
- min/max
- serial-equivalent 630 estimate

如需要真实 batch elapsed time，但旧 log 的 start/end 足够恢复，则从日志恢复。

若无法可靠恢复：

标记 `NOT_MEASURED`，不要估。

## 7.5 输出

更新：

- `results/runtime_summary_v2.json`
- `results/runtime_benchmark_v2.csv`
- `ENVIRONMENT.md`
- `PAPER_NUMBERS.csv`
- `CLAIMS_LEDGER.csv`

---

# 8. P1：加强测试，而不是增加新大实验

至少新增/改进：

- production score formula regression
- config-driven reduced-height regression
- config-driven timestep hours regression
- strict bool in real production path
- actual independent sample deterministic test
- N=12 logic test（如果保留）
- independent composite score normalization test
- historical 630 ranking equality test
- no duplicated HB mapping
- `PAPER_NUMBERS.csv` unique `number_id`
- all paper numbers have source/status
- `CLAIMS_LEDGER.csv` mandatory forbidden wording exists

最终：

```bash
pytest -q
```

必须 PASS。

把：

- test count
- passed
- failed
- skipped

写入最终 handoff。

---

# 9. P1：公开安全结果文件必须补全到 GitHub

当前 public mirror 主要有 paper-support summary。

本轮将下列**不含敏感几何/坐标/原始 Radiance 中间文件**的安全结果推送至 research branch：

建议：

```text
research_reproducibility/
  results_public/
    independent_validation_metrics.csv
    independent_composite_metrics.csv
    runtime_summary_v2.json
    weight_sensitivity_summary_v2.csv
    design_translation_summary.csv
    candidate_classification_summary.csv
```

不要推送：

- raw CAD/SKP/OBJ/DXF/DWG
- full sensor coordinate table
- raw `.res/.ill`
- private team files
- licensed weather data
- personal local paths
- credentials

---

# 10. 最终论文数字台账

更新 `paper_support/PAPER_NUMBERS.csv`。

必须新增：

- production_score_formula_version
- score weights A/H/V/N
- independent metric Spearman
- independent metric Pearson
- independent metric MAE
- independent composite Spearman
- independent composite Top-3/5/10
- independent composite rank error
- rule_candidate_hb_fraction
- measured HB scene count
- operational scene count
- independent validation scene count
- HB workers
- CPU/RAM
- weight sensitivity v2 min rho
- weight sensitivity v2 min Top-10 overlap
- Monte Carlo stability summary

旧三项 weight sensitivity 数字：

必须标记：

`SUPERSEDED_NOT_FOR_PAPER`

---

# 11. Claims Ledger 最终化

新增或修订以下主张。

## 可以写

如果新结果支持：

> The defined universe of 630 two-building interventions was exhaustively screened by the low-cost 2.5D layer.

> Within a pre-frozen stratified sample of 20 previously unverified candidates, the 2.5D and Radiance-based low-sun-area changes showed strong agreement.

> The independent evaluation also assessed agreement between the production composite screening score and an HB-derived composite reference score using the same predeclared weighting scheme.

> The workflow uses selective higher-cost Radiance verification rather than exhaustive Radiance evaluation of all 630 candidates.

> Design translation can change candidate desirability, motivating a human-in-the-loop final review stage.

## 不能写

- 99.7% accuracy
- universal accuracy
- Radiance = ground truth
- all 630 were run in Radiance
- AI beats human
- learned AI/ML model
- globally optimal real-world design
- buildability proved
- legal compliance proved
- heritage compliance proved
- C9,C15 universally safe/optimal

---

# 12. SOICT 2026 官方投稿格式准备

> **Codex 只准备格式规范说明与 paper evidence package；最终论文由网页端 ChatGPT 写。**

本节信息来自 SOICT 2026 官方投稿页与 Springer Computer Science Proceedings/CCIS 作者规范，2026-09-10 核查。

## 12.1 Initial submission

SOICT 2026 当前官方要求：

- Language: English
- Venue: SOICT 2026
- Proceedings: Springer CCIS
- Submission system: EasyChair
- Format: official Springer CCIS/LNCS proceedings template
- Template options: LaTeX or Microsoft Word
- Submission PDF
- **No page numbers**
- **Single-blind review**
- **Author names and affiliations must be included**
- At least 3 independent reviewers
- Initial submission maximum: **12 pages excluding references**
- Full paper deadline: **2026-09-16**
- Notification: **2026-10-12**
- Camera-ready: **2026-10-23**

Official source:

- https://soict.org/submission/paper-submission/
- https://www.springer.com/gp/computer-science/lncs/forthcoming-proceedings

## 12.2 Camera-ready rule

SOICT 2026 camera-ready page currently says:

- full paper: **12–15 pages including figures, tables and references**
- short paper: 8–11 pages including figures, tables and references

Official source:

- https://soict.org/submission/camera-ready-submission/

因此 initial 与 camera-ready 的页数口径不同。

### 网页端最终写作目标

为了同时兼容两套规则：

> **目标正文（不含 references）约 10–11 页；加 references 后约 12–13 页。**

这样：

- initial submission < 12 pages excluding references
- camera-ready total falls in 12–15 pages

Codex 不负责压缩最终版，但要在 `SOICT_2026_PAPER_WRITING_BRIEF.md` 中提醒网页端。

## 12.3 Springer/CCIS 排版关键点

必须使用官方模板，不自行“模拟 Springer”。

已核对的 Springer CS Proceedings 规则：

- title centered, 14 pt bold（以模板为准）
- first-level heading 12 pt bold
- second-level heading 10 pt bold
- only first two heading levels numbered
- no section 0
- Word template uses Times-family template styling
- no page numbers / running heads
- figure captions below figures
- table captions above tables
- tables/equations editable，不能截图粘贴
- vector diagrams preferred
- line drawings >= 800 dpi，preferably 1200 dpi
- figure lettering >= 6 pt
- equations sequentially numbered `(1), (2), ...`
- numeric citations in square brackets，如 `[9]`, `[4–6, 9]`
- all cited references must appear in reference list and vice versa
- DOI strongly encouraged where available
- corresponding author must be clearly marked and email is mandatory
- ORCID encouraged

最终以**官方模板自身样式**为最高优先级，不能手动改字体/边距来塞页数。

---

# 13. SOICT 投稿 track 建议

SOICT 2026 官方列有：

> **Applied Operations Research and Optimization**

作为 special session / scope。

本论文优先按这一方向准备，因为本研究的计算前台是：

- combinatorial candidate search
- exhaustive low-cost screening
- selective high-cost simulation
- ranking/robustness
- human-in-the-loop decision support

不要硬包装成：

- machine learning
- generative AI
- foundation model

---

# 14. 给网页端的写作素材，而不是论文正文

Codex 最终新增：

`paper_support/SOICT_2026_PAPER_WRITING_BRIEF.md`

只包含：

1. final scientific question
2. final production score formula
3. exact methods pipeline
4. experiment inventory
5. all final paper numbers with source paths
6. final figures with source paths
7. final tables with source paths
8. supported contributions
9. limitations
10. forbidden claims
11. recommended SOICT track
12. official formatting checklist
13. any remaining blocker

**禁止在这个文件里生成整篇 polished paper。**

---

# 15. 推荐论文结构（供网页端后续使用）

Codex 在 writing brief 中只记录这个 skeleton：

```text
Title

Authors / Affiliations

Abstract
Keywords

1 Introduction

2 Related Work
  2.1 Low-Cost Solar-Access Screening
  2.2 Multi-Fidelity Simulation and Design-Space Search
  2.3 Decision Support in Urban Renewal

3 Method
  3.1 Problem Formulation and Candidate Universe
  3.2 Canonical Geometry and Analysis Protocol
  3.3 Precomputed 2.5D Occlusion Screening
  3.4 Composite Candidate Score
  3.5 Selective Radiance Verification
  3.6 Design Translation and Adverse-Effect Gate

4 Experimental Design
  4.1 Clean Reproduction
  4.2 Curated Reference Set
  4.3 Frozen Independent Validation
  4.4 Computational Cost Benchmark
  4.5 Weight Robustness

5 Results
  5.1 Exhaustive Screening Results
  5.2 Metric-Level Independent Validation
  5.3 Composite-Ranking Independent Validation
  5.4 Runtime
  5.5 Weight Sensitivity
  5.6 Design-Translation Cases

6 Discussion

7 Limitations

8 Conclusion

References
```

最终章节是否合并，由网页端按 12-page limit 决定。

---

# 16. 本轮明确不做

不做：

- 新 ML / LLM
- 全 630 HB
- 新 40/60 candidate validation
- 重新选择 20 个 independent candidates
- 为了“更漂亮”删除 negative result
- 人工 vs AI competition
- 新 web UI
- portfolio redesign
- 重新建模整套场地
- 2m/3m/6m 大规模实验（除非网页端后续明确要求）
- 最终英语论文正文

---

# 17. GitHub 最终交付

继续保留 `main` 不动。

建议在：

`research-repro-v1`

完成 patch；若 Codex 认为需要更清晰审计，可从当前 HEAD 建：

`soict-final-patch-v1`

二者选一，但必须清楚告诉网页端。

最终 tag：

`soict-2026-write-ready-v1`

最终 commit message 建议：

`release: freeze SOICT 2026 write-ready evidence package`

---

# 18. 最终 Handoff 文件

更新：

`HANDOFF_TO_CHATGPT.md`

必须写清：

```text
Repository:
Branch:
Final commit SHA:
Tag:
Run ID:

SOICT_WRITE_READY = TRUE/FALSE

Production score formula:
A/H/V/N weights:

630 reproduction:
PASS/FAIL

Historical diff:
PASS/FAIL

Independent HB sample:
N=20
frozen sample unchanged:
YES/NO

Metric-level validation:
Spearman:
Pearson:
MAE:
sign agreement:

Composite-ranking validation:
Spearman:
Top3:
Top5:
Top10:
rank error:

Runtime:
2.5D 630 median:
HB per-scene median:
HB workers:
rule candidate verification count:
operational HB scene count:
research-only validation scene count:
630 HB serial-equivalent extrapolation:

Weight sensitivity v2:
min Spearman:
min Top10 overlap:
Monte Carlo summary:

Design translation:
C9,C15:
C9,C24:
C9,C13:
C13,C24:
C6,C33:

Tests:
passed:
failed:
skipped:

Paper source-of-truth files:
...

Known blockers:
...

Files ChatGPT must inspect first:
1.
2.
3.
...
```

---

# 19. Final machine-readable summary

更新 `RESULTS_SUMMARY.json`，至少含：

```json
{
  "repo": "",
  "branch": "",
  "commit": "",
  "tag": "",
  "run_id": "",
  "soict_write_ready": false,
  "production_score": {
    "low_area_drop": 0.45,
    "avg_gain": 0.35,
    "volume_economy": 0.15,
    "new_low_avoidance": 0.05
  },
  "reproduction": {},
  "independent_metric_validation": {},
  "independent_composite_validation": {},
  "runtime": {},
  "weight_sensitivity_v2": {},
  "design_translation": {},
  "tests": {},
  "warnings": []
}
```

---

# 20. Final Stop Conditions

不得写 `SOICT_WRITE_READY = TRUE` 如果：

1. 630 ranking 在 config migration 后非预期改变；
2. production score 和 paper ledger 仍不一致；
3. independent 20 sample 被重新选过；
4. composite validation 代码使用 HB outcome 调过 weights；
5. runtime 仍把 extrapolated 630 HB 写成 measured；
6. tests fail；
7. PAPER_NUMBERS 仍包含 superseded 3-term sensitivity 作为 active result；
8. GitHub 没有最终 safe summary/results；
9. final commit/tag 未记录；
10. 存在已知 P0 blocker 未披露。

---

# 21. 最终 Codex 回复格式

任务完成后，不要长篇叙述。

只回复：

```text
STATUS:
SOICT_WRITE_READY = TRUE/FALSE

GITHUB:
repo =
branch =
commit =
tag =

RUN:
run_id =

PATCH:
scoring formula = PASS/FAIL
config migration = PASS/FAIL
630 regression = PASS/FAIL
sampling fallback = PASS/FAIL
independent composite validation = PASS/FAIL
weight sensitivity v2 = PASS/FAIL
runtime semantics = PASS/FAIL
tests = PASS/FAIL

KEY NEW RESULTS:
independent composite rho =
Top3 =
Top5 =
Top10 =
weight sensitivity min rho =
weight sensitivity min top10 overlap =

HANDOFF:
HANDOFF_TO_CHATGPT.md =
RESULTS_SUMMARY.json =
PAPER_NUMBERS.csv =
CLAIMS_LEDGER.csv =
SOICT_2026_PAPER_WRITING_BRIEF.md =

BLOCKERS:
...
```

完成并 push 后停止，等待网页端 ChatGPT 接管正式论文写作。
