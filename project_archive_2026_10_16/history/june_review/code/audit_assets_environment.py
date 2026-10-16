from __future__ import annotations

import csv
import hashlib
import importlib.metadata as metadata
import json
import os
import platform
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import pandas as pd


WORKSPACE = Path(r"E:/AI项目")
WORK_ROOT = WORKSPACE / "中文导师审阅定稿_工作包_2026_06_20"
PROJECT = WORKSPACE / "light_equity_project"
DATASET = PROJECT / "data" / "real_guankou" / "lakeside_leisure_ready"
DESKTOP_DOCX = Path(r"C:/Users/洪禄/Desktop/光权修复论文_EI会议_最终排版版.docx")


def sha256(path: Path, limit_mb: int = 80) -> str:
    if not path.exists() or not path.is_file():
        return ""
    if path.stat().st_size > limit_mb * 1024 * 1024:
        return f"SKIPPED_OVER_{limit_mb}MB"
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_row(path: Path, category: str, role: str, required: bool = False) -> dict:
    exists = path.exists()
    stat = path.stat() if exists else None
    return {
        "category": category,
        "role": role,
        "required": required,
        "exists": exists,
        "path": str(path),
        "extension": path.suffix.lower(),
        "size_bytes": stat.st_size if stat else "",
        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds") if stat else "",
        "sha256": sha256(path) if exists and path.is_file() else "",
    }


def read_csv_summary(path: Path, required_columns: list[str] | None = None) -> dict:
    required_columns = required_columns or []
    if not path.exists():
        return {
            "path": str(path),
            "exists": False,
            "row_count": "",
            "columns": "",
            "missing_required_columns": ",".join(required_columns),
        }
    df = pd.read_csv(path)
    missing = [col for col in required_columns if col not in df.columns]
    return {
        "path": str(path),
        "exists": True,
        "row_count": len(df),
        "columns": ",".join(df.columns),
        "missing_required_columns": ",".join(missing),
    }


def obj_stats(path: Path) -> dict:
    stats = {
        "path": str(path),
        "exists": path.exists(),
        "vertices": 0,
        "faces": 0,
        "groups": 0,
        "x_min": "",
        "x_max": "",
        "y_min": "",
        "y_max": "",
        "z_min": "",
        "z_max": "",
        "parse_error": "",
    }
    if not path.exists():
        return stats
    vertices: list[tuple[float, float, float]] = []
    groups = set()
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("v "):
                    parts = line.split()
                    if len(parts) >= 4:
                        vertices.append((float(parts[1]), float(parts[2]), float(parts[3])))
                elif line.startswith("f "):
                    stats["faces"] += 1
                elif line.startswith("g ") or line.startswith("o "):
                    name = line.strip().split(maxsplit=1)[1] if len(line.strip().split(maxsplit=1)) > 1 else ""
                    if name:
                        groups.add(name)
    except Exception as exc:  # noqa: BLE001
        stats["parse_error"] = repr(exc)
        return stats
    stats["vertices"] = len(vertices)
    stats["groups"] = len(groups)
    if vertices:
        xs, ys, zs = zip(*vertices)
        stats.update(
            {
                "x_min": round(min(xs), 3),
                "x_max": round(max(xs), 3),
                "y_min": round(min(ys), 3),
                "y_max": round(max(ys), 3),
                "z_min": round(min(zs), 3),
                "z_max": round(max(zs), 3),
            }
        )
    return stats


def command_version(command: str, args: list[str] | None = None) -> dict:
    args = args or ["--version"]
    path = shutil.which(command)
    result = {"command": command, "path": path or "", "available_in_path": bool(path), "version_output": ""}
    if not path:
        return result
    try:
        completed = subprocess.run(
            [path, *args],
            text=True,
            capture_output=True,
            timeout=20,
            encoding="utf-8",
            errors="replace",
        )
        result["version_output"] = (completed.stdout or completed.stderr).strip().splitlines()[0:3]
    except Exception as exc:  # noqa: BLE001
        result["version_output"] = [repr(exc)]
    return result


def package_rows() -> list[dict]:
    packages = [
        "numpy",
        "pandas",
        "scipy",
        "matplotlib",
        "shapely",
        "geopandas",
        "trimesh",
        "pyvista",
        "open3d",
        "pvlib",
        "python-docx",
        "ezdxf",
        "ladybug-core",
        "ladybug-rhino",
        "honeybee-core",
        "honeybee-radiance",
    ]
    rows = []
    for package in packages:
        try:
            version = metadata.version(package)
            installed = True
        except metadata.PackageNotFoundError:
            version = ""
            installed = False
        rows.append({"package": package, "installed": installed, "version": version})
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[dict], columns: list[str]) -> str:
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(col, "")).replace("\n", " ") for col in columns) + " |")
    return "\n".join(lines)


def main() -> None:
    docs = WORK_ROOT / "docs"
    results = WORK_ROOT / "results_csv"
    logs = WORK_ROOT / "logs"
    docs.mkdir(parents=True, exist_ok=True)
    results.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)

    core_assets = [
        file_row(DESKTOP_DOCX, "Word母版", "本轮唯一正文、图表、编号和排版母版", True),
        file_row(WORK_ROOT / "data_raw" / DESKTOP_DOCX.name, "Word母版副本", "本轮只读母版副本", True),
        file_row(DATASET / "site_model.obj", "OBJ模型", "沿湖休闲片区算法输入白模", True),
        file_row(DATASET / "buildings.csv", "CSV原始数据", "建筑编号、矩形边界、高度、可动与保护属性", True),
        file_row(DATASET / "streets.csv", "CSV原始数据", "道路中心线与宽度", True),
        file_row(DATASET / "nodes.csv", "CSV原始数据", "节点/可达性输入", True),
        file_row(DATASET / "protected_zones.csv", "CSV原始数据", "保护区与不可干预约束", True),
        file_row(DATASET / "site_zones.csv", "CSV原始数据", "场地区域分区", False),
        file_row(DATASET / "road_segments.csv", "CSV原始数据", "道路分段补充", False),
        file_row(WORKSPACE / "谢研组" / "沿湖休闲片区场地.skp", "SKP原始模型", "原始 SketchUp 场地模型", True),
        file_row(WORKSPACE / "谢研组" / "沿湖休闲片区场地.obj", "OBJ原始模型", "原始导出 OBJ 场地模型", False),
        file_row(WORKSPACE / "谢研组" / "沿湖休闲片区标号(新）.dxf", "DXF原始数据", "建筑标号与场地标注", True),
        file_row(WORKSPACE / "谢研组" / "沿湖休闲片区场地说明.dxf", "DXF原始数据", "场地说明与道路/边界信息", True),
        file_row(WORKSPACE / "谢研组" / "沿湖休闲片区标号.dwg", "DWG原始数据", "CAD 标号源文件", False),
        file_row(WORKSPACE / "方案后体块.skp", "SKP方案模型", "既有方案后体块模型", False),
        file_row(WORKSPACE / "candidate_01_modified_full_site.skp", "SKP方案模型", "既有候选完整场地模型", False),
        file_row(WORKSPACE / "ladybug_ready_models" / "baseline_original_full_site_ladybug_ready.obj", "独立模拟准备模型", "既有 Ladybug/Rhino ready baseline OBJ", False),
        file_row(WORKSPACE / "ladybug_ready_models" / "algorithm_after_full_site_only_C6_C33_changed_ladybug_ready.obj", "独立模拟准备模型", "既有 Ladybug/Rhino ready C6/C33 OBJ", False),
        file_row(PROJECT / "main.py", "Python代码", "ABC主流程入口", True),
        file_row(PROJECT / "src" / "solar" / "sunlight_simulator.py", "Python代码", "算法 A 2.5D遮挡实现", True),
        file_row(PROJECT / "src" / "solar" / "sun_path.py", "Python代码", "简化太阳路径实现", True),
        file_row(PROJECT / "src" / "algorithm_b_optimization" / "run_optimization.py", "Python代码", "算法 B 候选搜索入口", True),
        file_row(PROJECT / "src" / "algorithm_b_optimization" / "scoring.py", "Python代码", "算法 B 评分函数", True),
        file_row(PROJECT / "src" / "algorithm_b_optimization" / "post_simulation_ranker.py", "Python代码", "算法 C 后复算", True),
        file_row(PROJECT / "outputs" / "lakeside_leisure_final_6m" / "final_report" / "before_after_metrics.csv", "历史实验输出", "6m最终包 before/after 指标", False),
        file_row(PROJECT / "outputs" / "lakeside_leisure_final_6m" / "B_candidates" / "interventions.csv", "历史实验输出", "6m候选干预表", False),
        file_row(WORKSPACE / "paper_revision_work_2026_06_14" / "c6_c33_same_scheme_3m" / "fixed_c6_c33_candidate_input" / "candidate_01.obj", "历史实验输出", "C6/C33 3m固定方案候选OBJ", False),
        file_row(WORKSPACE / "figure9_C6_C33_resimulation_revised.png", "历史图表", "C6/C33 复算图", False),
    ]
    write_csv(results / "asset_inventory_core.csv", core_assets)

    required_columns = {
        "buildings.csv": [
            "building_id",
            "name",
            "x_min",
            "x_max",
            "y_min",
            "y_max",
            "height_m",
            "floors",
            "movable",
            "protected",
            "facade_type",
            "notes",
        ],
        "streets.csv": [
            "street_id",
            "start_x",
            "start_y",
            "end_x",
            "end_y",
            "width_m",
            "main_direction",
            "pedestrian_priority",
            "notes",
        ],
        "nodes.csv": ["node_id", "x", "y", "z", "node_type", "importance", "notes"],
        "protected_zones.csv": ["zone_id", "x_min", "x_max", "y_min", "y_max", "z_min", "z_max", "reason", "notes"],
    }
    csv_summaries = []
    for name, columns in required_columns.items():
        csv_summaries.append(read_csv_summary(DATASET / name, columns))
    for name in ["site_zones.csv", "road_segments.csv", "buildings_with_audit_columns.csv", "intervention_levels_checked.csv"]:
        csv_summaries.append(read_csv_summary(DATASET / name))
    write_csv(results / "data_contract_csv_summary.csv", csv_summaries)

    buildings = pd.read_csv(DATASET / "buildings.csv")
    building_focus = buildings[buildings["building_id"].astype(str).isin(["C6", "C33", "C42"])].copy()
    building_focus["width_x_m"] = building_focus["x_max"].astype(float) - building_focus["x_min"].astype(float)
    building_focus["depth_y_m"] = building_focus["y_max"].astype(float) - building_focus["y_min"].astype(float)
    building_focus["footprint_area_m2_rect"] = building_focus["width_x_m"] * building_focus["depth_y_m"]
    write_csv(results / "C6_C33_C42_geometry_attributes.csv", building_focus.to_dict("records"))

    duplicate_ids = buildings["building_id"][buildings["building_id"].duplicated()].astype(str).tolist()
    invalid_heights = buildings[buildings["height_m"].astype(float) <= 0]["building_id"].astype(str).tolist()
    protected = buildings[buildings["protected"].astype(str).str.lower().isin(["true", "1", "yes"])]

    obj_rows = [
        obj_stats(DATASET / "site_model.obj"),
        obj_stats(WORKSPACE / "谢研组" / "沿湖休闲片区场地.obj"),
        obj_stats(WORKSPACE / "ladybug_ready_models" / "baseline_original_full_site_ladybug_ready.obj"),
        obj_stats(WORKSPACE / "ladybug_ready_models" / "algorithm_after_full_site_only_C6_C33_changed_ladybug_ready.obj"),
    ]
    write_csv(results / "obj_model_stats.csv", obj_rows)

    env_commands = [
        command_version("python", ["--version"]),
        command_version("pip", ["--version"]),
        command_version("pandoc", ["--version"]),
        command_version("soffice", ["--version"]),
        command_version("rhino", ["--version"]),
        command_version("rtrace", ["-version"]),
        command_version("oconv", ["-version"]),
    ]
    write_csv(results / "environment_commands.csv", env_commands)
    write_csv(results / "environment_python_packages.csv", package_rows())

    env_info = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "workspace": str(WORKSPACE),
        "work_root": str(WORK_ROOT),
        "platform": platform.platform(),
        "python": platform.python_version(),
        "python_executable": os.environ.get("PYTHONHOME", "") or shutil.which("python") or "",
        "processor": platform.processor(),
        "machine": platform.machine(),
    }
    (logs / "environment_base.json").write_text(json.dumps(env_info, ensure_ascii=False, indent=2), encoding="utf-8")

    command_map = {row["command"]: row for row in env_commands}
    package_map = {row["package"]: row for row in package_rows()}
    all_required_assets_exist = all(row["exists"] for row in core_assets if row["required"])
    data_contract_ok = all(not row["missing_required_columns"] and row["exists"] for row in csv_summaries[:4])

    asset_md = [
        "# 01 项目资产清单",
        "",
        f"审计时间：{datetime.now().isoformat(timespec='seconds')}",
        "",
        "## 核心判断",
        "",
        f"- 当前 Word 母版：{'具备' if DESKTOP_DOCX.exists() else '缺失'}。",
        f"- 原始 Python 代码：{'具备' if (PROJECT / 'main.py').exists() else '缺失'}。",
        f"- OBJ / SKP / DXF：{'具备核心文件' if all([ (DATASET / 'site_model.obj').exists(), (WORKSPACE / '谢研组' / '沿湖休闲片区场地.skp').exists(), (WORKSPACE / '谢研组' / '沿湖休闲片区标号(新）.dxf').exists() ]) else '不完整'}。",
        f"- 建筑编号与高度 CSV：{'具备' if (DATASET / 'buildings.csv').exists() else '缺失'}。",
        f"- 道路、场地边界、保护建筑数据：{'具备主要CSV' if data_contract_ok else '不完整'}。",
        f"- C6、C33、C42 真实几何与属性：{'可在 buildings.csv 中定位' if len(building_focus) == 3 else '不完整'}。",
        f"- 原始/历史实验输出：{'具备若干历史输出' if any(row['exists'] and row['category'] == '历史实验输出' for row in core_assets) else '未定位'}。",
        f"- Rhino、Grasshopper、Ladybug、Honeybee、Radiance：{'可直接调用' if command_map['rhino']['available_in_path'] and command_map['rtrace']['available_in_path'] else '未在 PATH 中发现完整可用链路'}。",
        "",
        "## 核心资产表",
        "",
        markdown_table(
            [
                {
                    "类别": row["category"],
                    "状态": "存在" if row["exists"] else "缺失",
                    "必要": "是" if row["required"] else "否",
                    "用途": row["role"],
                    "路径": row["path"],
                }
                for row in core_assets
            ],
            ["类别", "状态", "必要", "用途", "路径"],
        ),
        "",
        "## 数据契约摘要",
        "",
        markdown_table(
            [
                {
                    "文件": Path(row["path"]).name,
                    "状态": "存在" if row["exists"] else "缺失",
                    "行数": row["row_count"],
                    "缺失字段": row["missing_required_columns"] or "无",
                }
                for row in csv_summaries
            ],
            ["文件", "状态", "行数", "缺失字段"],
        ),
        "",
        "## C6 / C33 / C42 属性核对",
        "",
        markdown_table(
            [
                {
                    "建筑": row["building_id"],
                    "高度m": row["height_m"],
                    "x范围": f"{row['x_min']}–{row['x_max']}",
                    "y范围": f"{row['y_min']}–{row['y_max']}",
                    "可动": row["movable"],
                    "保护": row["protected"],
                    "备注": row["notes"],
                }
                for row in building_focus.to_dict("records")
            ],
            ["建筑", "高度m", "x范围", "y范围", "可动", "保护", "备注"],
        ),
        "",
        "## OBJ 模型读取摘要",
        "",
        markdown_table(
            [
                {
                    "文件": Path(row["path"]).name,
                    "状态": "存在" if row["exists"] else "缺失",
                    "顶点": row["vertices"],
                    "面": row["faces"],
                    "组": row["groups"],
                    "边界": f"x {row['x_min']}–{row['x_max']}, y {row['y_min']}–{row['y_max']}, z {row['z_min']}–{row['z_max']}",
                }
                for row in obj_rows
            ],
            ["文件", "状态", "顶点", "面", "组", "边界"],
        ),
        "",
        "完整 CSV 清单见 `results_csv/asset_inventory_core.csv`、`results_csv/data_contract_csv_summary.csv`、`results_csv/obj_model_stats.csv`。",
        "",
    ]
    (docs / "01_项目资产清单.md").write_text("\n".join(asset_md), encoding="utf-8")

    risks = [
        {
            "风险项": "Ladybug/Radiance独立参考模拟环境不可直接调用",
            "状态": "未满足" if not command_map["rtrace"]["available_in_path"] else "可调用",
            "影响": "不能把当前流程声称为已通过 Ladybug/Radiance 投稿级验证；可改用真正独立的三维射线追踪并透明标注。",
            "最小补充": "安装/确认 Rhino+Grasshopper+Ladybug+Honeybee+Radiance，或批准采用 trimesh 三维射线追踪作为独立参考引擎。",
        },
        {
            "风险项": "现有太阳采样仍为1小时时步",
            "状态": "未满足",
            "影响": "不满足 15/30 分钟升级要求，现有表格中的数值不能直接作为本轮定稿结论。",
            "最小补充": "新增 30 分钟或 15 分钟配置并重跑 baseline、候选、敏感性和参考模拟。",
        },
        {
            "风险项": "4m/5m网格、网格原点四偏移、2h/3h/4h阈值尚未形成完整输出",
            "状态": "未满足",
            "影响": "无法证明 C6/C33 跨尺度与原点稳定性。",
            "最小补充": "运行 3m/4m/5m/6m × 4原点 × 3阈值的敏感性测试。",
        },
        {
            "风险项": "算法B现有实现不是全候选枚举和Pareto分析",
            "状态": "未满足",
            "影响": "不能直接声明最终方案位于或接近 Pareto 前沿。",
            "最小补充": "新增全候选枚举、归一化评分、Pareto 和公平基线脚本。",
        },
        {
            "风险项": "add/reorganize含占位几何，subtract后复算为有效高度削减近似",
            "状态": "已确认",
            "影响": "论文需弱化 add/reorganize 主张，并将结果定位为低干预减高/退台候选筛查。",
            "最小补充": "候选规则表中透明写出真实执行操作与占位操作的边界。",
        },
        {
            "风险项": "建筑设计转译尚未证明为真实几何复算",
            "状态": "未满足",
            "影响": "不能把整体降低高度的规则模型效果直接归因于退台/采光缝设计。",
            "最小补充": "建立设计转译几何版本并分别进行独立参考模拟。",
        },
        {
            "风险项": "OBJ坐标/轴向存在版本差异",
            "状态": "已确认",
            "影响": "数据集 site_model.obj 顶点边界出现毫米级/轴向未转换特征；ladybug_ready_models 下 OBJ 才表现为米制且 z 约 0-21 m。独立三维验证若混用模型会产生错误。",
            "最小补充": "明确采用同一转换后的 Ladybug-ready OBJ，或记录转换脚本、比例和轴向规则后再模拟。",
        },
        {
            "风险项": "PDF导出工具未在PATH中发现",
            "状态": "未满足" if not command_map["soffice"]["available_in_path"] else "可调用",
            "影响": "最终 PDF 可能无法在本机自动导出。",
            "最小补充": "安装 LibreOffice/WPS命令行导出，或手动使用 Word/WPS 导出并记录。",
        },
        {
            "风险项": "参考文献尚未逐条联网核验",
            "状态": "未满足",
            "影响": "不能完成参考文献审计表与 DOI/页码修正。",
            "最小补充": "联网核验 24 条参考文献，重点检查 Ward 1994 SIGGRAPH页码。",
        },
    ]
    write_csv(results / "missing_and_risk_register.csv", risks)
    risk_md = [
        "# 02 缺失文件与风险清单",
        "",
        "## 结论",
        "",
        "核心母版、算法代码、OBJ/SKP/DXF 和主要 CSV 已定位；但独立参考模拟环境、15/30 分钟重跑、全候选 Pareto、网格原点敏感性和真实设计转译复算尚未满足。按用户验收门槛，目前不能输出“中文导师审阅定稿版”，只能继续补实验或形成透明降级的导师审阅预整理版。",
        "",
        "## 风险表",
        "",
        markdown_table(risks, ["风险项", "状态", "影响", "最小补充"]),
        "",
        "## 已发现的数据问题",
        "",
        f"- buildings.csv 行数：{len(buildings)}；重复 building_id：{duplicate_ids or '无'}。",
        f"- 非正高度建筑：{invalid_heights or '无'}。",
        f"- protected=True 建筑：{protected['building_id'].astype(str).tolist() if not protected.empty else '无'}。",
        "- `site_model.obj` 与 `ladybug_ready_models` 中的 OBJ 边界尺度/轴向不同；三维参考模拟前必须统一坐标、单位、北向和 z 轴。",
        "- 现有论文表述中仍有“采光可达性、采光小时、暗区、人机协同”等术语，需要统一替换为本轮指定术语。",
        "- 现有母版明确承认尚未通过 Ladybug/Radiance 或实测校准；本轮若不补独立验证，不能删除这一边界。",
        "",
    ]
    (docs / "02_缺失文件与风险清单.md").write_text("\n".join(risk_md), encoding="utf-8")

    env_md = [
        "# 03 运行环境清单",
        "",
        f"审计时间：{datetime.now().isoformat(timespec='seconds')}",
        "",
        "## 系统与硬件",
        "",
        f"- 操作系统：{platform.platform()}",
        f"- Python：{platform.python_version()}",
        f"- Python 可执行文件：{shutil.which('python') or '未找到'}",
        f"- CPU/机器：{platform.processor()} / {platform.machine()}",
        "",
        "## 命令行工具",
        "",
        markdown_table(
            [
                {
                    "工具": row["command"],
                    "PATH状态": "可用" if row["available_in_path"] else "未发现",
                    "路径": row["path"],
                    "版本输出": " / ".join(row["version_output"]) if isinstance(row["version_output"], list) else row["version_output"],
                }
                for row in env_commands
            ],
            ["工具", "PATH状态", "路径", "版本输出"],
        ),
        "",
        "## Python关键库",
        "",
        markdown_table(
            [
                {
                    "库": row["package"],
                    "状态": "已安装" if row["installed"] else "未安装",
                    "版本": row["version"],
                }
                for row in package_map.values()
            ],
            ["库", "状态", "版本"],
        ),
        "",
        "## 环境说明",
        "",
        "- 本机已具备 numpy、pandas、scipy、matplotlib、shapely、trimesh、pvlib、python-docx、ezdxf，可运行现有 Python 数据管线、太阳位置计算和三维网格/OBJ解析。",
        "- geopandas、pyvista、open3d、Ladybug、Honeybee 未安装。",
        "- Rhino、Grasshopper、Radiance 未在 PATH 中发现，不能直接执行用户优先指定的独立参考模拟链路。",
        "",
    ]
    (docs / "03_运行环境清单.md").write_text("\n".join(env_md), encoding="utf-8")


if __name__ == "__main__":
    main()
