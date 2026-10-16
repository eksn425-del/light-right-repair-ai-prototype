# 光照复核模型说明

本文件夹用于算法前后 1:1 光照对照。

## 已有文件

1. `baseline_original_full_site.skp`

   组员原始 SketchUp 场地模型。用于算法前光照分析。

2. `baseline_original_full_site.obj`

   组员原始 OBJ 场地模型。用于算法前备份和跨软件导入。

3. `algorithm_after_full_site_only_C6_C33_changed.obj`

   算法后完整场地 OBJ。它保留原始 OBJ 的场地、道路、建筑和坐标关系，只修改：

   - C6：6.0m -> 4.5m；
   - C33：9.0m -> 6.75m。

   其余建筑和场地不动。

4. `algorithm_after_full_site_only_C6_C33_changed.skp`

   已经生成好的算法后完整场地 SKP。它从原始 SKP 复制并修改，只对 C6、C33 做保守型高度调整：

   - C6：6.0m -> 4.5m；
   - C33：9.0m -> 6.75m。

   推荐组员直接用这个文件做算法后光照复核。

5. `make_algorithm_after_skp_C6_C33.rb`

   SketchUp Ruby 脚本。用于在 SketchUp 中把原始 SKP 直接生成算法后 SKP。

## SKP 生成记录

已通过 SketchUp 2024 自动脚本生成：

`algorithm_after_full_site_only_C6_C33_changed.skp`

转换日志见：

`algorithm_after_skp_conversion_log.txt`

日志显示脚本命中的对象为：

- `C33: C33 9m`
- `C6: C6 6m`

## 给组员的光照复核要求

请做两组同参数光照分析：

1. 算法前：`baseline_original_full_site.skp`
2. 算法后：`algorithm_after_full_site_only_C6_C33_changed.skp`

必须保持：

- 同一城市/经纬度；
- 同一日期，建议冬至日；
- 同一时间段，建议 8:00-16:00；
- 同一视角或同一总平面图；
- 同一阴影显示参数；
- 只比较 C6、C33 修改带来的局部采光变化。

论文里不要写“完全验证算法正确”，应写：

> 通过同场地、同参数、同视角的人工光照复核，检查 AI 保守型候选方案在 C6、C33 周边是否产生与算法诊断方向一致的采光改善。
