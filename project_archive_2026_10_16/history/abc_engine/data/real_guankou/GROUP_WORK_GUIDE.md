# 两组协作说明：大井脚里1号社区组 / 沿湖休闲片区组

本次任务书的范围已经从“单条灌口老街”转为“灌口沿湖片区”的两个重点板块。算法仍然是 A/B/C 三层，但数据需要两组分别整理，最后合并到 `data/real_guankou/`。

## 共同规则

两组都要使用同一个 CAD/SU 坐标系，单位统一为米。不要只画漂亮图，要把场地变成算法能读的表格。

每组至少提交：

- 片区边界截图或 CAD 标注图一张。
- `site_zones.csv` 分区表。
- 与本组相关的 `buildings.csv` 建筑行。
- 与本组相关的 `streets.csv` 路径行。
- 与本组相关的 `nodes.csv` 节点行。
- 需要保护或不能动的区域，填入 `protected_zones.csv`。

## 大井脚里1号社区组

重点对象：

- 村前球场。
- 主要道路。
- 停车场地。
- 房前屋后。
- 旧公社周边。
- 居民日常活动和通行空间。

算法关注：

- 哪些居住边界和道路边侧采光差。
- 哪些停车/道路空间影响老人儿童通行。
- 球场和旧公社周边是否适合形成社区公共节点。
- 是否可以用小尺度灰空间、口袋广场、退让或打通来修复光照和通行。

模板位置：

`data/real_guankou/group_templates/dajingjiaoli_1/`

## 沿湖休闲片区组

重点对象：

- 旧菜市场。
- 大面积闲置空地。
- 镇属闲置公房。
- 滨湖界面。
- 停车与慢行系统。

算法关注：

- 闲置空间是否具备改造成公共活动节点的潜力。
- 沿湖慢行是否连续、安全、可达。
- 临水空间是否需要护栏和净宽控制。
- 停车是否挤压步行与公共活动。
- 旧菜市场和闲置公房是否适合功能活化。

模板位置：

`data/real_guankou/group_templates/lakeside_leisure/`

## 合并方式

每组先填自己的模板。最后由统筹同学把两组数据合并进：

- `data/real_guankou/site_zones.csv`
- `data/real_guankou/buildings.csv`
- `data/real_guankou/streets.csv`
- `data/real_guankou/nodes.csv`
- `data/real_guankou/protected_zones.csv`

合并后再运行：

```bash
python main.py --dataset real_guankou
```

如果真实 SU 白模还没完成，可以先只用 CSV 检查字段和坐标逻辑；但最终算法 A 仍需要 `site_model.obj` 有真实体量顶点。

