# Rhino + Grasshopper + Ladybug 光照验证包

这个包只做一件事：用真实 Rhino/Ladybug 对 AI 的“算法前/算法后”结果做外部复核。

## 你需要导入的模型

在 `01_models/` 里有两组 OBJ：

1. `baseline_original_full_site.obj`
   - 原始完整场地。

2. `algorithm_after_full_site_only_C6_C33_changed.obj`
   - 算法后完整场地。
   - 只修改 C6、C33。
   - 其他建筑、道路、位置都不变。

请注意：两个模型都要保持原坐标，不要移动，不要缩放，不要旋转。

## 你要怎么做

### 第一次：算法前

1. 打开 Rhino。
2. 导入 `baseline_original_full_site.obj`。
3. 单位设为“米”。
4. 用 Grasshopper + Ladybug 做光照分析。
5. 地点设为厦门 Xiamen。
6. 日期设为冬至日：12 月 21 日或 12 月 22 日。
7. 时间设为 8:00-16:00。
8. 把 `02_validation_template/P01_P20_sampling_points.csv` 里的点放到 Rhino 里。
9. 记录每个点的光照小时数，填到 `software_baseline_h`。
10. 导出一张热力图截图，命名为 `baseline_ladybug_heatmap.png`。

### 第二次：算法后

1. 新开 Rhino 文件。
2. 导入 `algorithm_after_full_site_only_C6_C33_changed.obj`。
3. 用完全一样的 Ladybug 设置再跑一次。
4. 还是同一批 P01-P20 点。
5. 记录每个点的光照小时数，填到 `software_after_h`。
6. 导出一张热力图截图，命名为 `algorithm_after_ladybug_heatmap.png`。

一句话：除了模型不同，其他设置全部一样。

## 你最后交回什么

请把下面文件发回来：

1. 填好的 `professional_light_validation_template.xlsx`
2. `baseline_ladybug_heatmap.png`
3. `algorithm_after_ladybug_heatmap.png`
4. 如果可以，再附一张 Grasshopper/Ladybug 参数截图

## 如果不会导出小时数

如果 Ladybug 不能直接导出每个点的小时数，就先填等级：

- `low`：采光差 / 暗区
- `medium`：一般
- `high`：采光较好

填到：

- `software_baseline_level`
- `software_after_level`

## 本包采样点数量

本次先给 20 个点。点位包括：

- C6 / C33 周边重点点；
- 可能暗区或候选建筑周边点；
- 普通对照区点。

