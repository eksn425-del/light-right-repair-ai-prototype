# 72 复现说明 README

## 运行顺序

1. `python code/audit_docx_extract.py` 抽取 Word 母版。
2. `python code/audit_assets_environment.py` 生成资产与环境审计。
3. `python code/run_teacher_revision_experiments.py` 生成本轮新增 CSV、图表、日志和说明。

## 随机种子

- random baseline seed: 42

## 核心输入

- dataset: `E:\AI项目\light_equity_project\data\real_guankou\lakeside_leisure_ready`
- Ladybug-ready OBJ baseline: `E:\AI项目\ladybug_ready_models\baseline_original_full_site_ladybug_ready.obj`

## 图表脚本来源

本轮新增图 23、41、42、43、52、61、71 均由 `code/run_teacher_revision_experiments.py` 生成。

## 边界

当前独立参考为 trimesh 三维射线可见性，不是 Ladybug/Radiance。若导师要求投稿级环境模拟，应继续补 Rhino/Grasshopper/Ladybug/Honeybee/Radiance 链路。