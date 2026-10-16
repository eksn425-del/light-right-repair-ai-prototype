# 00 Project audit report

## 判断原则

本次补强只使用本地项目中已经存在的模型、CSV、图像和脚本。缺失项目直接标注，不补造文件或指标。

## 当前项目结构

- 项目根目录：`E:\AI项目`
- 算法工程目录：`E:\AI项目\light_equity_project`
- 论文工作包：`E:\AI项目\光权修复_论文工作包_2026-06-03`
- EI 补强输出目录：`E:\AI项目\光权修复_论文工作包_2026-06-03\09_EI补强图表`
- 真实沿湖休闲片区数据集：`E:\AI项目\light_equity_project\data\real_guankou\lakeside_leisure_ready`

## 关键文件检查

| item                                                                                          | exists | size   |
| --------------------------------------------------------------------------------------------- | ------ | ------ |
| E:\AI项目\light_equity_project\src\algorithm_a_diagnosis\run_diagnosis.py                       | yes    | 11667  |
| E:\AI项目\light_equity_project\src\algorithm_b_optimization\run_optimization.py                 | yes    | 9194   |
| E:\AI项目\light_equity_project\src\algorithm_b_optimization\intervention_generator.py           | yes    | 10145  |
| E:\AI项目\light_equity_project\src\algorithm_b_optimization\scoring.py                          | yes    | 1452   |
| E:\AI项目\light_equity_project\src\algorithm_c_validation\run_validation.py                     | yes    | 7827   |
| E:\AI项目\light_equity_project\data\real_guankou\lakeside_leisure_ready\buildings.csv           | yes    | 7054   |
| E:\AI项目\light_equity_project\data\real_guankou\lakeside_leisure_ready\site_model.obj          | yes    | 988268 |
| E:\AI项目\light_equity_project\data\real_guankou\lakeside_leisure_ready\protected_zones.csv     | yes    | 216    |
| E:\AI项目\light_equity_project\outputs\validation_lakeside_6m\A_diagnosis\sunlight_hours.csv    | yes    | 16314  |
| E:\AI项目\light_equity_project\outputs\validation_lakeside_6m\A_diagnosis\dark_zones.csv        | yes    | 5870   |
| E:\AI项目\light_equity_project\outputs\validation_lakeside_6m\A_diagnosis\gap_candidates.csv    | yes    | 1228   |
| E:\AI项目\light_equity_project\outputs\validation_lakeside_6m\B_candidates\candidate_scores.csv | yes    | 440    |
| E:\AI项目\light_equity_project\outputs\validation_lakeside_6m\B_candidates\interventions.csv    | yes    | 1422   |
| E:\AI项目\light_equity_project\outputs\validation_lakeside_6m\A_diagnosis\A_summary.json        | yes    | 1976   |
| E:\AI项目\light_equity_project\outputs\validation_lakeside_6m\B_candidates\B_summary.json       | yes    | 336    |
| E:\AI项目\光权修复_论文工作包_2026-06-03\03_核心数据表\strategy_comparison_metrics.csv                        | yes    | 906    |
| E:\AI项目\光权修复_论文工作包_2026-06-03\03_核心数据表\grid_sensitivity_metrics_partial.csv                   | yes    | 879    |


## 可直接复现或读取的内容

- 6m baseline 诊断输出可读取：`validation_lakeside_6m/A_diagnosis`。
- 三类策略 post-simulation 指标可读取：`strategy_comparison_metrics.csv`。
- 6m 与 3m 网格敏感性结果可读取：`grid_sensitivity_metrics_partial.csv`。
- C6/C33 高度变化表可读取：`candidate_01_height_changes.csv`。
- 保守型后完整场地 SKP 已存在，可供人工光照复核。

## 缺失或不宜硬造的内容

- 2m 全场网格测试未完成，不能作为正式结果写入。
- Algorithm B 的完整原始候选池未单独导出；本次候选排序基于已导出的 selected candidate interventions。
- 人工光照图是方向性复核，不是专业日照审查结果。
