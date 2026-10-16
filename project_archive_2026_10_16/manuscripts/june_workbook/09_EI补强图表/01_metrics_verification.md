# 01 Metrics verification

## 6m strategy metrics

| scheme_type     | average_sunlight_hours | dark_zone_ratio | intervention_volume | source                                                                 |
| --------------- | ---------------------- | --------------- | ------------------- | ---------------------------------------------------------------------- |
| baseline        | 6.422                  | 17.55%          | 0.000               | E:\AI项目\光权修复_论文工作包_2026-06-03\03_核心数据表\strategy_comparison_metrics.csv |
| AI_conservative | 6.435                  | 16.94%          | 28.125              | E:\AI项目\光权修复_论文工作包_2026-06-03\03_核心数据表\strategy_comparison_metrics.csv |
| AI_balanced     | 6.435                  | 16.94%          | 45.000              | E:\AI项目\光权修复_论文工作包_2026-06-03\03_核心数据表\strategy_comparison_metrics.csv |
| AI_light_first  | 6.435                  | 16.94%          | 46.095              | E:\AI项目\光权修复_论文工作包_2026-06-03\03_核心数据表\strategy_comparison_metrics.csv |


## Grid sensitivity metrics

| grid  | baseline_avg | baseline_dark_ratio | post_dark_ratio | changed_buildings | source                                                                      |
| ----- | ------------ | ------------------- | --------------- | ----------------- | --------------------------------------------------------------------------- |
| 6.0 m | 6.422        | 17.55%              | 16.94%          | C33;C6            | E:\AI项目\光权修复_论文工作包_2026-06-03\03_核心数据表\grid_sensitivity_metrics_partial.csv |
| 3.0 m | 6.509        | 16.09%              | 16.09%          | C28;C34;C38;C9    | E:\AI项目\光权修复_论文工作包_2026-06-03\03_核心数据表\grid_sensitivity_metrics_partial.csv |


## 核查结论

- 6m baseline 的平均采光小时、暗区比例与论文当前数值一致。
- 保守型、均衡型、采光优先型三类策略的 post-simulation 后平均采光小时和暗区比例相同或接近，因此推荐保守型的理由应写成“相近采光收益下干预体量最小”。
- 3m 网格下候选建筑排序发生变化，说明当前简化模型存在尺度依赖，不能表述为唯一最优。
