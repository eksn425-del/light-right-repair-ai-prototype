# 光权修复：AI辅助空间决策系统

这是一个建筑学 + AI 辅助空间决策项目的工程骨架版。当前目标不是马上得出真实论文结论，而是先搭好一套稳定、可替换真实数据的 Python 流程，让后续灌口真实 SketchUp 白模、CAD/DXF 坐标和现场 CSV 数据可以直接接入。

项目核心原则是：最小干预、光权修复、安全验证。系统不做大拆大建，也不依赖 Rhino、Grasshopper、Ladybug、Unity 或商业插件。

## 三段算法流程

算法 A：诊断层  
读取 `site_model.obj`、建筑表、街道表和可选的片区分区表，建立简化地面网格，模拟厦门冬至日 8:00-16:00 太阳路径，输出采光小时数、暗区、可改善缝隙和热力图。若提交 `site_zones.csv`，还会输出 `zone_diagnosis.csv`，按球场、旧菜市场、闲置空地、停车、滨湖界面等分区汇总问题。

算法 B：决策层  
读取算法 A 的暗区、缝隙列表和分区诊断，在“最小干预”原则下生成 2-3 组候选方案。当前支持三类操作：`subtract` 局部削减，`add` 小型采光/灰空间/记忆装置体块，`reorganize` 底层灰空间、停车慢行或闲置空间重组。

算法 C：验证层  
读取候选方案，按老人、儿童、残障人士通行安全规则检查坡度、净宽、台阶、护栏、滨水安全和人车分流等约束，输出安全报告、可达路线和最终推荐方案。

## 25-26 新任务书定位

项目对象已从“灌口老街直街”升级为“灌口沿湖片区”，重点包含两组：

- 大井脚里 1 号社区组：村前球场、主要道路、停车场地、房前屋后、旧公社周边。
- 沿湖休闲片区组：旧菜市场、闲置空地、镇属闲置公房、滨湖界面、停车与慢行系统。

原 ABC 框架保留，但新增 `site_zones.csv` 作为片区/节点/问题区域接口。

## 安装依赖

建议使用 Python 3.10+。

```bash
pip install -r requirements.txt
```

说明：代码对 `pyyaml` 和 `trimesh` 做了轻量兜底，未安装时 toy demo 也能运行；但正式协作建议按 `requirements.txt` 安装完整依赖。

## 运行 Toy Demo

在项目根目录运行：

```bash
python main.py --dataset sample_toy_street
```

如果想重新生成 toy 数据：

```bash
python main.py --dataset sample_toy_street --regenerate-toy
```

## 运行真实数据

建筑组把真实文件放入：

```text
data/real_guankou/
```

然后运行：

```bash
python main.py --dataset real_guankou
```

如果 `site_model.obj` 还是占位文件，程序会提示 OBJ 没有顶点，需要替换为 SketchUp 导出的真实白模。

## CAD/DXF 参考提取

当前 `NEW-CAD地形文件_.dxf` 已可读取。已提取结果在：

```text
data/cad_reference/
```

包括：

- `dxf_summary.json`
- `dxf_layers.csv`
- `dxf_entity_types.csv`
- `dxf_texts.csv`
- `dxf_closed_polylines.csv`

重要：这个 DXF 大部分实体都在 `地形图` 一个图层里，所以这些表只能作为坐标和轮廓参考，不能自动替代建筑组判断。组员仍需要人工核对建筑、道路、水体、停车、片区边界，并整理成 CSV。

如需重新提取：

```bash
python tools/analyze_dxf_reference.py ../NEW-CAD地形文件_.dxf
```

## 建筑组必须提交的文件

详见 `data/real_guankou/README_FOR_ARCHITECTURE_TEAM.md`。核心文件包括：

- `site_model.obj`：SU 导出的极简白模，只保留建筑体量，单位米。
- `buildings.csv`：建筑包围盒、高度、层数、可动/保护状态。
- `streets.csv`：街道中心线、宽度、方向、步行优先信息。
- `nodes.csv`：入口、节点、阴暗段、活动点、停车冲突点、滨湖停留点等重要位置。
- `protected_zones.csv`：历史立面、结构、居民使用、老树、滨水危险边界等不可动或需谨慎区域。
- `site_zones.csv`：球场、旧菜市场、闲置空地、停车场、滨湖界面、社区节点等新任务书分区。

重点：OBJ 和 CSV 必须使用同一坐标系。CSV 字段名不要改。

## 两组协作模板

- `data/real_guankou/GROUP_WORK_GUIDE.md`
- `data/real_guankou/group_templates/dajingjiaoli_1/`
- `data/real_guankou/group_templates/lakeside_leisure/`
- `组员任务说明_大井脚里1号与沿湖休闲片区.txt`

## 输出文件说明

`outputs/A_diagnosis/`

- `sunlight_hours.csv`：每个地面网格点的采光小时数、阴影小时数、是否暗区。
- `dark_zones.csv`：暗区坐标、严重程度、最近建筑。
- `gap_candidates.csv`：可能改善采光的缝隙或暗区周边候选点。
- `zone_diagnosis.csv`：按任务书分区统计的平均采光、暗区比例和诊断标签。
- `heatmap.png`：采光热力图，适合论文和汇报。
- `A_summary.json`：诊断层摘要指标。

`outputs/B_candidates/`

- `candidate_01.obj` 等：候选改造参考体块，可拖回 SU 对照。
- `candidate_scores.csv`：候选方案得分表。
- `interventions.csv`：每个干预操作的类型、坐标、尺寸、体积变化。
- `B_summary.json`：决策层摘要。

`outputs/C_validation/`

- `safety_report.csv`：候选方案安全评分和违规统计。
- `safe_routes.csv`：节点间可达路线表。
- `final_recommendation.json`：最终推荐方案。
- `C_summary.json`：验证层摘要。

`outputs/final_report/`

- `before_after_metrics.csv`：baseline、manual_design、algorithm_design 三组对比接口。
- `comparison_chart.png`：平均采光小时数、暗区比例、干预体积、安全可达覆盖率对比图。
- `final_summary.json`：最终汇总摘要。

## 当前简化假设

- 建筑用轴对齐盒子和 CSV 包围盒表达。
- 算法 A 使用 2.5D 简化遮挡判断，不是专业光环境软件。
- 算法 B 输出的是建议体块/参考框体，不做真实几何布尔。
- 算法 C 的路线是节点间简化路线，不是完整道路网络。
- `manual_design` 当前是占位对照值，等建筑组人工方案提交后替换。

## 后续可升级方向

- 用 `trimesh` 或更专业的射线追踪替换当前 2.5D 阴影判断。
- 将真实 SU 白模分栋导出，减少 CSV 与 OBJ 的人工对应成本。
- 将现场测绘路线整理成真实路径网络，替换节点间直连路线。
- 引入人工方案 CSV，让 `manual_design` 对照从占位变为真实实验数据。
- 将候选 OBJ 的参考框体进一步转译为建筑语言：退台、采光井、灰空间、连续步行界面、滨湖慢行节点。

