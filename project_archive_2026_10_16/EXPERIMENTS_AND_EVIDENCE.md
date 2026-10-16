# 全部实验与证据导航

整理日期：2026-10-16。这里只登记和解释已有实验，不生成新实验结果。

## 如何区分三层材料

| 层次 | 目录 | 可用于什么 |
|---|---|---|
| 早期 ABC 与三策略 | `history/abc_engine/`、`history/may_25_delivery/`、`history/may_29_validation/` | 工程过程、敏感性问题、历史局限；不能混用为冻结论文主数据 |
| 六月研究与修订 | `history/route_b_june/`、`history/june_review/`、`manuscripts/` | 论文演变、几何审计、专业复核、规则和设计转译对比 |
| 九月冻结研究 | `research/experiments/baseline_20260909_clean/`、根部 `research_reproducibility/` | 当前论文数字、主张、排序、独立验证、敏感性与 runtime 的证据来源 |

完整实验目录登记在 [EXPERIMENT_REGISTER.csv](indexes/EXPERIMENT_REGISTER.csv)。登记 30 个运行或阶段输出目录，包含 smoke test、配置目录及 A/B/C 阶段目录；这个数量不是“30 个成功的独立实验”。完整历史文件登记在 [FILE_INVENTORY.csv](indexes/FILE_INVENTORY.csv)，其中 `duplicate_reference` 表示源文件与已存副本逐字节一致。

## 实验家族

| 实验或检查 | 来源 | 当前解释 |
|---|---|---|
| Toy street ABC 全流程 | `history/abc_engine/outputs/validation_toy_verified` 等 | 合成数据管线测试 |
| 单独 OBJ / 自动建表 | `validation_auto_obj_toy`、`validation_script_auto_obj` 等 | 有限输入处理测试；不能外推任意真实 OBJ |
| 沿湖真实场地早期试跑 | `lakeside_leisure_test`、`lakeside_leisure_ready_fulltest` 等 | 早期转换、对齐与计算历史 |
| 6 m 现实化重算 | `lakeside_leisure_realistic_6m`、`lakeside_leisure_final_6m` | 保留旧口径；不是冻结 Route B 基线 |
| 三策略共享基线 | `product_strategy_lakeside_2026_06_02_sharedA` 等 | 保守/均衡/日照优先的产品策略实验 |
| 6 m / 3 m 网格检查 | `light_product_2026_06_03/grid_sensitivity`、相关 docs | 候选与收益对网格敏感的历史证据 |
| 局部 2 m 检查 | `reviews/submission_june_09`、六月工作包 `12_reviewer_audit_and_local_2m` | 限定局部范围；不写成全场 2 m 已完成 |
| 人工前后光照图 | `validation/human_sunlight` 与团队图片 | 视觉方向校核；独立数值验证应读取 HB/匹配点位结果 |
| 统一几何和候选枚举 | 六月 Route B 与九月 clean run | 真实几何审计、限定双建筑减高宇宙 |
| Curated HB 验证 | `132_HB_Radiance已复核候选排名与Pareto.csv` | 选择性 23 规则候选检查 |
| 设计转译后再计算 | `138_最终候选规则与设计转译对比.csv`、`design_translation_summary.csv` | 区分规则候选和建筑设计转译的影响 |
| 冻结独立 N=20 低日照区验证 | `results/independent_validation_*` | 预先冻结样本内单项指标一致性 |
| 同一 N=20 四项复合排序验证 | `results/independent_composite_*` | 固定 630 候选归一化范围下的样本内排序一致性 |
| 四项权重敏感性 | `results/weight_sensitivity_*_v2.csv`、`candidate_rank_stability_v2.csv` | 6 场景、1,000 次固定种子扰动 |
| 配置迁移回归 | `SCORING_FORMULA_MIGRATION_AUDIT.csv` | 630 候选分数、次序、Top10 和 Pareto 未变 |
| Runtime 复核 | `runtime_benchmark_v2.csv`、`runtime_summary_v2.json` | measured / extrapolated / operational / research-only 分开 |

## 冻结协议

- Run ID：`baseline_20260909_clean`。
- 固定场地：沿湖休闲片区，45 栋，36 栋符合当前规则资格。
- 630 个无序双建筑候选，2,031 个固定接收点。
- 2026-12-21，Asia/Shanghai，08:15–15:45，30 min。
- 网格 3 m，接收点 0.1 m，低日照阈值 3 h。
- 高度规则：`max(3 m, h-min(3 m,0.25h))`。
- 分数：`0.45 A_norm+0.35 H_norm+0.15(1-V_norm)+0.05(1-N_norm)`。

最终数字一律通过根目录下 `research_reproducibility/paper_support/PAPER_NUMBERS.csv` 找到其 source_file、source_field_or_rule、run_id、status 和 notes，再决定如何引用。不要从本文四舍五入值反向覆盖原始 CSV。

## 当前主要发现

| 项目 | 已有冻结值 | 限定 |
|---|---:|---|
| HB 基线平均直射时长 | 5.957163958641064 h | 来自冻结 paper ledger；不等同于早期 6.422 h |
| 规范化 2.5D 基线低日照区 | 3,051 m² | 3 h 阈值、固定 3 m 网格 |
| Curated 排名 Spearman | 0.8833992094861661 | 23 个选择性规则候选；与独立样本值不同 |
| 独立单项指标 Spearman | 0.997668088547906 | 冻结 N=20 |
| 独立单项指标 MAE | 0.45 m² | 低日照区减少量的误差 |
| 独立单项 Top5 recall | 0.8 | 不要与复合排序 Top5 recall=1.0 混用 |
| 独立复合排序 Spearman | 1.0 | 同一冻结 N=20；不是“100% 准确率” |
| 复合排序 Top3/5/10 recall | 1.0/1.0/1.0 | 仅样本内部名次 |
| 四项确定性敏感性最小 Spearman | 0.9759413903909104 | 声明的 6 种权重场景 |
| 确定性 Top10 最低重合 | 6/10 | 不能只写“排名完全稳定” |
| 2.5D 全筛选中位时间 | 55.39783389999866 s | 3 次完整筛选重复实测 |
| HB 每场景中位时间 | 51.106736 s | 53 个已有场景计时 |
| 630 HB 串行等效时间 | 32197.24368 s | 外推，未直接运行完整 630 场景批次 |

53 个 HB 场景由 33 operational 场景与 20 research-only 独立验证场景组成。23 表示经特定候选筛选流程复核的规则候选，不是全部场景数。

冻结 `independent_composite_metadata.json` 还记录：完整 630 规则候选的 `new_low_area_h3_m2` 最小与最大值均为 0。生产代码保留四项公式，但该项在这个限定减高宇宙中没有候选间变化；不能因此宣称已经充分检验“新增阴影惩罚”在非单调加法/重组方案中的区分能力。权重场景结果应连同这个适用边界一起报告。

## 设计转译的结果不能被排序覆盖

`design_translation_summary.csv` 保存以下已存在记录：

| 候选 | 规则减少低日照区 | 设计转译后减少 | 恶化点 | 新增低日照区 | 解释 |
|---|---:|---:|---:|---:|---|
| C9/C24 | 396 m² | 342 m² | 4 | 9 m² | 收益高但要人工复核副作用 |
| C9/C15 | 351 m² | 342 m² | 0 | 0 m² | 这次转译复算中的优先候选区间 |
| C9/C13 | 333 m² | 333 m² | 0 | 0 m² | 同上，干预体积与收益权衡不同 |

CSV 还保存未完成设计转译复算的组合；这些空值应保留为空值，不能写成无副作用。C6/C33 是重要历史对照，但不是冻结研究唯一推荐。

## 本次没有重跑

原先的冻结 sample SHA256、选样、HB 数值、630 clean ranking 和论文 ledger 均保留。本轮只做归档、哈希核验、Word 文本提取和阅读导航。之前 `19 passed`、公开脱敏包 `17 passed, 2 skipped` 属于九月记录；本轮验证通过与否应看 `ARCHIVE_REPORT.md` 的归档审计，不把旧测试伪装成本轮全实验重跑。

## 复现边界

实验代码、配置和汇总输出已归档；CAD/OBJ 和接收点坐标等原始输入在本地。网页端可以阅读和讨论证据，不能仅凭仓库声称独立重跑了真实场地。需要重跑时，应在获授权的本地环境使用保留的输入，写入新 run 目录并产生新的差异审计。
