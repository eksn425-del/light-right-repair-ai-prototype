# 灌口真实数据提交说明

你们不是随便建模，而是要让模型和 CSV 能被算法读取。  
这个文件夹里的文件名和字段名请不要改，后续算法会直接读取这些固定文件。

## 2025-2026 新任务书范围

本次真实数据不再只按“灌口老街一条直街”理解，而要覆盖：

- 大井脚里 1 号片区：村前球场、主要道路、停车场地、房前屋后、旧公社周边。
- 沿湖休闲片区：旧菜市场、闲置空地、镇属闲置公房、停车与慢行系统。
- 关联要素：风景湖、榕树广场中心、灌口老街、凤山庙片区、道路交通系统。

所以模型和表格要能表达“片区 + 节点 + 慢行系统”，不能只表达一条街道剖面。

## 1. `site_model.obj`

从 SketchUp 导出的极简白模，只保留建筑体量。

要求：

- 单位统一为米。
- 坐标原点尽量放在场地西南角，或一个明确、可复述的基准点。
- 只保留建筑外轮廓体块，不要材质、门窗、家具、栏杆、树、人、复杂构件。
- 每栋建筑可以是一个简单盒子或少量盒子组合。
- 不需要精模，重点是轮廓、位置、高度大致可信。

## 2. `buildings.csv`

每一行是一栋建筑或一个可分析体块。

字段必须包括：

| 字段 | 说明 |
| --- | --- |
| `building_id` | 建筑唯一编号，例如 B001 |
| `name` | 建筑名称或现场称呼 |
| `x_min` | 建筑包围盒最小 x 坐标 |
| `x_max` | 建筑包围盒最大 x 坐标 |
| `y_min` | 建筑包围盒最小 y 坐标 |
| `y_max` | 建筑包围盒最大 y 坐标 |
| `height_m` | 建筑高度，单位米 |
| `floors` | 层数，可估算 |
| `movable` | 是否允许小范围干预，填 `true` 或 `false` |
| `protected` | 是否保护/不可动，填 `true` 或 `false` |
| `facade_type` | 立面类型，例如 old_shopfront、residential、historic |
| `notes` | 现场备注 |

## 3. `streets.csv`

每一行是一条街道中心线或主要通行段。

字段必须包括：

| 字段 | 说明 |
| --- | --- |
| `street_id` | 街道编号，例如 S001 |
| `start_x` | 起点 x 坐标 |
| `start_y` | 起点 y 坐标 |
| `end_x` | 终点 x 坐标 |
| `end_y` | 终点 y 坐标 |
| `width_m` | 街道净宽，单位米 |
| `main_direction` | 主要方向，例如 east-west 或 north-south |
| `pedestrian_priority` | 是否以步行为主，填 `true` 或 `false` |
| `notes` | 现场备注 |

## 4. `nodes.csv`

每一行是一个重要节点，例如入口、广场、店铺密集段、老人活动点、阴暗点。

字段必须包括：

| 字段 | 说明 |
| --- | --- |
| `node_id` | 节点编号，例如 N001 |
| `x` | 节点 x 坐标 |
| `y` | 节点 y 坐标 |
| `z` | 节点高度，一般地面填 0 |
| `node_type` | 节点类型，例如 entrance、shop_cluster、elder_activity |
| `importance` | 重要性，建议 1-5 |
| `notes` | 现场备注 |

## 5. `protected_zones.csv`

每一行是不能切除、不能占用或需要谨慎处理的区域。

字段必须包括：

| 字段 | 说明 |
| --- | --- |
| `zone_id` | 保护区编号，例如 PZ001 |
| `x_min` | 包围盒最小 x 坐标 |
| `x_max` | 包围盒最大 x 坐标 |
| `y_min` | 包围盒最小 y 坐标 |
| `y_max` | 包围盒最大 y 坐标 |
| `z_min` | 包围盒最小 z 坐标 |
| `z_max` | 包围盒最大 z 坐标 |
| `reason` | 保护原因，例如 historic_facade、structure、resident_use |
| `notes` | 现场备注 |

## 提交前自查

- OBJ 和 CSV 使用同一个坐标系。
- 所有长度单位都是米。
- CSV 表头没有改名，没有多余空格。
- `movable` 和 `protected` 不要同时填 true；如果冲突，以 protected 为准。
- 真实数据可以粗糙，但必须完整、统一、可读取。

## 6. `site_zones.csv`（新增，建议提交）

每一行是一个任务书里的片区、节点或问题区域。算法 A 会按这些区域汇总采光和暗区比例，算法 B 会优先在这些区域生成公共空间/慢行/停车重组类候选操作。

字段必须包括：

| 字段 | 说明 |
| --- | --- |
| `zone_id` | 分区编号，例如 Z001 |
| `name` | 分区名称，例如 村前球场、旧菜市场、沿湖闲置空地 |
| `zone_type` | 类型，例如 ball_court、old_market、vacant_land、parking、waterfront、lakeside_leisure、vacant_public_building、road_edge |
| `x_min` | 分区包围盒最小 x 坐标 |
| `x_max` | 分区包围盒最大 x 坐标 |
| `y_min` | 分区包围盒最小 y 坐标 |
| `y_max` | 分区包围盒最大 y 坐标 |
| `priority` | 改造优先级，建议 1-5 |
| `needs_light_improvement` | 是否需要采光/开敞度改善，填 `true` 或 `false` |
| `needs_accessibility_improvement` | 是否需要慢行/无障碍改善，填 `true` 或 `false` |
| `protected` | 是否不可动，填 `true` 或 `false` |
| `notes` | 现场备注 |

## CAD / DWG 使用说明

当前收到的 `CAD地形文件_t3(3).dwg` 是 AutoCAD R2004 / `AC1018` 格式。Python 当前环境可以识别它是 DWG，但不能直接可靠读取 DWG 几何。

建筑组或 CAD 负责人需要做一步转换：

1. 用 AutoCAD、浩辰 CAD、天正或 ODA File Converter 打开 DWG。
2. 另存为 DXF，建议 DXF R2004 或 DXF R2010。
3. 根据图层把内容整理成这些 CSV：
   - 建筑轮廓和高度：`buildings.csv`
   - 道路/慢行中心线：`streets.csv`
   - 重要节点：`nodes.csv`
   - 保护区：`protected_zones.csv`
   - 球场、菜市场、闲置空地、停车、滨湖界面等：`site_zones.csv`

也就是说，CAD 不是直接拿来“看图”的，而是要转成算法能读的边界、坐标和属性表。
