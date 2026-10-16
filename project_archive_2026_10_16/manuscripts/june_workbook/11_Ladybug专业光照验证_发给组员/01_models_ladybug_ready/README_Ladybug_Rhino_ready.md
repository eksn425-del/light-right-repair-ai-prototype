# Ladybug/Rhino OBJ 转换报告

处理目标：把 SketchUp OBJ 转成 Rhino/Ladybug 更稳定的“米单位、Z 轴为高度”的 OBJ。

转换规则：`X = 原X / 1000`，`Y = -原Z / 1000`，`Z = 原Y / 1000`。

## baseline_original_full_site_ladybug_ready.obj
- 顶点数：9741
- 面数：9011
- 组数量：69
- X 范围：-0.733 到 675.781 m
- Y 范围：-0.828 到 467.533 m
- Z/高度范围：-0.022 到 21.000 m

## algorithm_after_full_site_only_C6_C33_changed_ladybug_ready.obj
- 顶点数：9741
- 面数：9011
- 组数量：69
- X 范围：-0.733 到 675.781 m
- Y 范围：-0.828 到 467.533 m
- Z/高度范围：-0.022 到 21.000 m

## 给组员的使用方式
1. 在 Rhino 里导入 `*_ladybug_ready.obj`，这两个文件已经是米单位、Z 轴朝上。
2. 如果 Ladybug 组件可以接 Mesh，直接使用导入对象即可。
3. 如果组件要求 Brep/Polysurface，运行 `Rhino_一键转多重曲面_命令脚本.txt` 里的命令，或手动执行 `MeshToNURB` 后 `Join`。
4. 前后模型必须使用同一 EPW、同一时段、同一 P01-P20 点位。

注意：OBJ 本质仍是网格文件。真正的 Rhino 多重曲面需要在 Rhino 内执行 MeshToNURB/Join 后保存为 3DM。