# 94_Ladybug_Honeybee_Radiance安装记录

记录时间：2026-06-20

## 可用性结论

- Rhino / Grasshopper：未在 PATH 或常见 Program Files 目录检出，本轮未伪造 Grasshopper 截图或 `.gh` 文件。
- Ladybug/Honeybee Python 包：已安装并可调用 `honeybee-radiance` 与 `lbt-recipes`。
- Radiance：已从 LBNL-ETA/Radiance GitHub Releases 下载 Windows ZIP，并在工作包内解压运行。
- Direct Sun Hours：`lbt-recipes run direct-sun-hours` 已成功运行 baseline、关键候选、2.5D Top/Pareto 追加候选和最终设计转译候选。

## 版本

- 操作系统：Windows 11
- Python：3.12.2
- ladybug-core：0.44.52
- ladybug-geometry：1.35.1
- honeybee-core：1.64.54
- honeybee-radiance：1.66.273
- honeybee-radiance-command：1.23.0
- lbt-recipes：0.28.2
- numpy：1.26.4
- pandas：2.3.3
- scipy：1.17.1
- matplotlib：3.10.8
- shapely：2.1.2
- pvlib：0.15.2
- Radiance：`RADIANCE 6.0.2 2026-02-02 LBNL (6.0.c1700d56cc)`

## 安装命令

```powershell
python -m pip install -U ladybug-core ladybug-geometry honeybee-core honeybee-radiance honeybee-radiance-command lbt-recipes
python -m pip install -U setuptools
honeybee-radiance set-config radiance-path E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20\tools\radiance_6_0_2
```

Radiance 裸命令版本检查需要显式设置 `RAYPATH`：

```powershell
$env:RAYPATH='.;E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20\tools\radiance_6_0_2\lib'
& 'E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20\tools\radiance_6_0_2\bin\rtrace.exe' -version
```

未设置 `RAYPATH` 时，`rtrace.exe -version` 会报告找不到 `rayinit.cal`。这不是 Radiance 缺失，而是裸命令环境变量未指定；`lbt-recipes` 批处理已成功调用 Radiance 并生成正式结果文件。

## 限制

本轮正式验证采用 Honeybee/LBT 官方 `direct-sun-hours` recipe 与 Radiance 命令行路径，不是 Rhino/Grasshopper GUI 路径。因此 `95/96/97` 中不得伪造 Grasshopper 版本截图或 `.gh` 文件。最终论文应写明本轮在本机完成的是 Honeybee-Radiance 命令行正式参考模拟，而非 Grasshopper 图形界面截图复现。
