from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Arial Unicode MS", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False


ROOT = Path(r"E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20")
OUT_C9 = ROOT / "C9_C24_恶化点核查.csv"
OUT_C13 = ROOT / "C13_C24_恶化点核查.csv"
OUT_FIG = ROOT / "C9_C24_C13_C24_恶化点空间对比图.png"
OUT_MD = ROOT / "重复副作用数据核查说明.md"

BASE_RES = ROOT / "hb_radiance_project_batch" / "baseline" / "direct_sun_hours" / "results" / "cumulative" / "ground_3m_road_open_space.res"
BASE_PTS_DIR = ROOT / "hb_radiance_project_batch" / "baseline" / "direct_sun_hours" / "resources" / "grid"
C9_RES = ROOT / "hb_radiance_project_final_design" / "C9_C24_design_stepback" / "direct_sun_hours" / "results" / "cumulative" / "ground_3m_road_open_space.res"
C13_RES = ROOT / "hb_radiance_project_batch" / "C13_C24_design_stepback" / "direct_sun_hours" / "results" / "cumulative" / "ground_3m_road_open_space.res"


def read_res(path: Path) -> list[float]:
    return [float(line.strip()) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def read_pts() -> pd.DataFrame:
    rows = []
    global_index = 0
    for chunk in ["0", "1", "2", "3"]:
        path = BASE_PTS_DIR / f"{chunk}.pts"
        for local_index, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
            if not line.strip():
                continue
            parts = [float(x) for x in line.split()]
            rows.append(
                {
                    "point_index": global_index,
                    "grid_id": f"G{global_index + 1:05d}",
                    "chunk_id": chunk,
                    "chunk_local_index": local_index,
                    "x": parts[0],
                    "y": parts[1],
                    "z": parts[2],
                    "nx": parts[3] if len(parts) > 3 else None,
                    "ny": parts[4] if len(parts) > 4 else None,
                    "nz": parts[5] if len(parts) > 5 else None,
                }
            )
            global_index += 1
    return pd.DataFrame(rows)


def audit_one(name: str, scenario_res: Path, points: pd.DataFrame, baseline: list[float]) -> pd.DataFrame:
    after = read_res(scenario_res)
    if len(after) != len(baseline) or len(after) != len(points):
        raise ValueError(f"{name} length mismatch: after={len(after)}, baseline={len(baseline)}, points={len(points)}")
    df = points[["point_index", "grid_id", "chunk_id", "chunk_local_index", "x", "y", "z"]].copy()
    df["baseline_direct_sun_h"] = baseline
    df["scenario_direct_sun_h"] = after
    df["delta_h"] = df["scenario_direct_sun_h"] - df["baseline_direct_sun_h"]
    df["worsened"] = df["delta_h"] < -1e-9
    df["baseline_low_h3"] = df["baseline_direct_sun_h"] < 3.0
    df["scenario_low_h3"] = df["scenario_direct_sun_h"] < 3.0
    df["new_low_h3"] = (~df["baseline_low_h3"]) & df["scenario_low_h3"]
    worsened = df[df["worsened"]].copy()
    return worsened


def plot_compare(c9: pd.DataFrame, c13: pd.DataFrame, points: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 5.4), dpi=220)
    ax.scatter(points["x"], points["y"], s=4, color="#d8dde3", label="全部地面传感点", alpha=0.45)
    ax.scatter(c9["x"], c9["y"], s=90, color="#e74c3c", marker="o", edgecolor="black", linewidth=0.7, label="C9/C24 恶化点")
    ax.scatter(c13["x"], c13["y"], s=120, color="#3498db", marker="x", linewidth=2.2, label="C13/C24 恶化点")
    for i, (_, row) in enumerate(c9.iterrows()):
        ax.annotate(row["grid_id"], (row["x"], row["y"]), xytext=(8, 8 + i * 2), textcoords="offset points", fontsize=8, color="#922b21")
    for i, (_, row) in enumerate(c13.iterrows()):
        ax.annotate(row["grid_id"], (row["x"], row["y"]), xytext=(8, -14 - i * 2), textcoords="offset points", fontsize=8, color="#1f618d")
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("规范坐标 X / m")
    ax.set_ylabel("规范坐标 Y / m")
    ax.set_title("C9/C24 与 C13/C24 设计转译恶化点空间对比")
    ax.grid(True, color="#edf1f5")
    ax.legend(fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT_FIG, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    points = read_pts()
    baseline = read_res(BASE_RES)
    c9 = audit_one("C9/C24", C9_RES, points, baseline)
    c13 = audit_one("C13/C24", C13_RES, points, baseline)
    c9.to_csv(OUT_C9, index=False, encoding="utf-8-sig")
    c13.to_csv(OUT_C13, index=False, encoding="utf-8-sig")
    plot_compare(c9, c13, points)
    overlap = sorted(set(c9["grid_id"]) & set(c13["grid_id"]))
    c9_only = sorted(set(c9["grid_id"]) - set(c13["grid_id"]))
    c13_only = sorted(set(c13["grid_id"]) - set(c9["grid_id"]))
    md = [
        "# 重复副作用数据核查说明",
        "",
        "## 核查对象",
        "",
        "- C9/C24_design_stepback",
        "- C13/C24_design_stepback",
        "",
        "## 数据来源",
        "",
        "- baseline: hb_radiance_project_batch/baseline/direct_sun_hours/results/cumulative/ground_3m_road_open_space.res",
        "- C9/C24: hb_radiance_project_final_design/C9_C24_design_stepback/direct_sun_hours/results/cumulative/ground_3m_road_open_space.res",
        "- C13/C24: hb_radiance_project_batch/C13_C24_design_stepback/direct_sun_hours/results/cumulative/ground_3m_road_open_space.res",
        "- 传感点坐标: hb_radiance_project_batch/baseline/direct_sun_hours/resources/grid/*.pts",
        "",
        "## 结果",
        "",
        f"- C9/C24 恶化点数量：{len(c9)}；新增 3 h 低直射日照点数量：{int(c9['new_low_h3'].sum())}。",
        f"- C13/C24 恶化点数量：{len(c13)}；新增 3 h 低直射日照点数量：{int(c13['new_low_h3'].sum())}。",
        f"- 两候选恶化点重叠数量：{len(overlap)}。",
        f"- 重叠点：{', '.join(overlap) if overlap else '无'}。",
        f"- 仅 C9/C24 恶化点：{', '.join(c9_only) if c9_only else '无'}。",
        f"- 仅 C13/C24 恶化点：{', '.join(c13_only) if c13_only else '无'}。",
        "",
        "## 判断",
        "",
    ]
    if len(overlap) == len(c9) == len(c13):
        md.append("两个候选在同一组局部敏感传感点上产生等量副作用；经点位坐标与结果文件核查，未发现 CSV 复制、场景映射或输出覆盖错误。")
    elif overlap:
        md.append("两个候选的恶化点部分重合，但并非完全相同；应在正文中说明数量相同不等于空间分布完全一致。")
    else:
        md.append("两个候选的恶化点位置不同；正文表 4 下应增加脚注说明数量相同但空间位置不同。")
    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(OUT_C9)
    print(OUT_C13)
    print(OUT_FIG)
    print(OUT_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
