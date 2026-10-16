from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle


BASE = Path(__file__).resolve().parent
FIG_DIR = BASE / "optimized_figures"
FIG_DIR.mkdir(exist_ok=True)
PROJECT = Path("light_equity_project")

BASELINE_CSV = PROJECT / "outputs" / "lakeside_leisure_final_6m" / "A_diagnosis" / "sunlight_hours.csv"
CONSERVATIVE_CSV = (
    PROJECT
    / "outputs"
    / "light_product_2026_06_02"
    / "strategy_comparison_postsim"
    / "conservative"
    / "post_simulation"
    / "algorithm_sunlight_hours.csv"
)
STRATEGY_CSV = (
    PROJECT
    / "outputs"
    / "light_product_2026_06_02"
    / "strategy_comparison_postsim"
    / "strategy_comparison_metrics.csv"
)
GRID_CSV = (
    PROJECT
    / "outputs"
    / "light_product_2026_06_03"
    / "grid_sensitivity"
    / "grid_sensitivity_metrics_partial.csv"
)
BUILDINGS_CSV = PROJECT / "data" / "real_guankou" / "lakeside_leisure_ready" / "buildings.csv"


def setup_font():
    font_paths = [
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\simsun.ttc",
    ]
    font_path = next((p for p in font_paths if Path(p).exists()), None)
    prop = font_manager.FontProperties(fname=font_path) if font_path else None
    if prop:
        mpl.rcParams["font.family"] = prop.get_name()
    mpl.rcParams["axes.unicode_minus"] = False
    mpl.rcParams["pdf.fonttype"] = 42
    mpl.rcParams["ps.fonttype"] = 42
    return prop


PROP = setup_font()
BLUE = "#2563eb"
TEAL = "#0f9f9a"
ORANGE = "#f59e0b"
RED = "#d94848"
GRAY = "#6b7280"
DARK = "#111827"
GREEN = "#22a06b"


def save_exact(fig, name, dpi=220):
    fig.savefig(FIG_DIR / name, dpi=dpi, facecolor="white")
    plt.close(fig)


def add_box(ax, xy, w, h, text, fc="white", ec=BLUE, fs=12):
    patch = FancyBboxPatch(
        xy,
        w,
        h,
        boxstyle="round,pad=0.015,rounding_size=0.025",
        fc=fc,
        ec=ec,
        lw=1.8,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + w / 2,
        xy[1] + h / 2,
        text,
        ha="center",
        va="center",
        fontsize=fs,
        color=DARK,
        fontproperties=PROP,
        linespacing=1.25,
    )


def add_arrow(ax, p1, p2, color=GRAY):
    ax.add_patch(
        FancyArrowPatch(
            p1,
            p2,
            arrowstyle="-|>",
            mutation_scale=14,
            lw=1.5,
            color=color,
            shrinkA=4,
            shrinkB=4,
        )
    )


def make_figure_1():
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(
        0.5,
        0.92,
        "CAD / SU / OBJ / CSV 数据转译接口",
        ha="center",
        va="center",
        fontsize=18,
        fontweight="bold",
        fontproperties=PROP,
        color=DARK,
    )
    items = [
        ("CAD/DXF\n编号、高度、道路图层", 0.05),
        ("SU / OBJ\n白模体块与空间位置", 0.25),
        ("CSV 属性表\n高度、可改性、保护约束", 0.45),
        ("对象一致性校核\nC1-C45 编号对齐", 0.65),
        ("算法入口\n热力图、候选策略、人工复核", 0.83),
    ]
    for text, x in items:
        add_box(ax, (x, 0.38), 0.13, 0.25, text, fc="#f8fafc", ec=BLUE, fs=10.5)
    for i in range(len(items) - 1):
        add_arrow(ax, (items[i][1] + 0.13, 0.505), (items[i + 1][1], 0.505), BLUE)
    ax.text(
        0.5,
        0.18,
        "核心要求：模型必须让建筑编号、空间边界、属性表和算法对象一一对应。",
        ha="center",
        fontsize=12,
        fontproperties=PROP,
        color=GRAY,
    )
    save_exact(fig, "image1.png", dpi=220)


def make_figure_2():
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.axis("off")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(
        0.5,
        0.92,
        "AI 辅助采光修复工作流",
        ha="center",
        fontsize=18,
        fontweight="bold",
        fontproperties=PROP,
        color=DARK,
    )
    items = [
        ("输入\nCAD/SU/OBJ/CSV", 0.03, BLUE),
        ("A 诊断\n暗区识别 + 采光小时", 0.19, TEAL),
        ("B 决策\n保守 / 均衡 / 采光优先", 0.36, ORANGE),
        ("C 复核\n后模拟 + 网格敏感性", 0.54, GREEN),
        ("人工复核\n同视角光照 + 设计转译", 0.71, RED),
        ("输出\n图表、模型、论文证据链", 0.87, BLUE),
    ]
    for text, x, color in items:
        add_box(ax, (x, 0.38), 0.12, 0.25, text, fc="white", ec=color, fs=10.2)
    for i in range(len(items) - 1):
        add_arrow(ax, (items[i][1] + 0.12, 0.505), (items[i + 1][1], 0.505), items[i + 1][2])
    ax.text(
        0.5,
        0.18,
        "定位：早期设计决策支持，不替代专业日照审查；AI 输出必须回到模型和人工判断中复核。",
        ha="center",
        fontsize=12,
        fontproperties=PROP,
        color=GRAY,
    )
    save_exact(fig, "image2.png", dpi=220)


def make_heatmap(df, col, title, name, cmap="YlOrRd", vmin=0, vmax=9):
    fig, ax = plt.subplots(figsize=(8, 5.9))
    sc = ax.scatter(
        df["x"],
        df["y"],
        c=df[col],
        cmap=cmap,
        vmin=vmin,
        vmax=vmax,
        s=24,
        marker="s",
        edgecolors="none",
    )
    ax.set_title(title, fontsize=14, fontweight="bold", fontproperties=PROP, pad=10)
    ax.set_xlabel("x / m", fontproperties=PROP)
    ax.set_ylabel("y / m", fontproperties=PROP)
    ax.grid(True, color="#e5e7eb", lw=0.55)
    ax.set_aspect("equal", adjustable="box")
    cb = fig.colorbar(sc, ax=ax, fraction=0.035, pad=0.03)
    cb.set_label("采光小时 / h", fontproperties=PROP)
    ax.tick_params(labelsize=9)
    save_exact(fig, name, dpi=225)


def make_spatial_figures():
    baseline = pd.read_csv(BASELINE_CSV)
    conservative = pd.read_csv(CONSERVATIVE_CSV)
    merged = baseline[["grid_id", "x", "y", "sunlight_hours"]].merge(
        conservative[["grid_id", "sunlight_hours"]],
        on="grid_id",
        suffixes=("_base", "_after"),
    )
    merged["diff"] = merged["sunlight_hours_after"] - merged["sunlight_hours_base"]
    buildings = pd.read_csv(BUILDINGS_CSV)

    make_heatmap(baseline, "sunlight_hours", "现状基准采光小时热力图（6 m 网格）", "image3.png")
    make_heatmap(conservative, "sunlight_hours", "保守型 AI 策略后采光小时热力图（6 m 网格）", "image4.png")

    lim = max(abs(merged["diff"]).max(), 0.25)
    fig, ax = plt.subplots(figsize=(8, 5.7))
    sc = ax.scatter(
        merged["x"],
        merged["y"],
        c=merged["diff"],
        cmap="RdBu_r",
        vmin=-lim,
        vmax=lim,
        s=24,
        marker="s",
        edgecolors="none",
    )
    for bid in ["C6", "C33"]:
        row = buildings[buildings.building_id == bid].iloc[0]
        ax.add_patch(
            Rectangle(
                (row.x_min, row.y_min),
                row.x_max - row.x_min,
                row.y_max - row.y_min,
                fill=False,
                ec=DARK,
                lw=1.3,
            )
        )
        ax.text(
            (row.x_min + row.x_max) / 2,
            (row.y_min + row.y_max) / 2,
            bid,
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            fontproperties=PROP,
            color=DARK,
        )
    ax.set_title("现状与保守型 AI 策略的采光小时差值", fontsize=14, fontweight="bold", fontproperties=PROP, pad=10)
    ax.set_xlabel("x / m", fontproperties=PROP)
    ax.set_ylabel("y / m", fontproperties=PROP)
    ax.grid(True, color="#e5e7eb", lw=0.55)
    ax.set_aspect("equal")
    cb = fig.colorbar(sc, ax=ax, fraction=0.035, pad=0.03)
    cb.set_label("采光小时变化 / h", fontproperties=PROP)
    save_exact(fig, "image5.png", dpi=225)

    c6 = buildings[buildings.building_id == "C6"].iloc[0]
    c33 = buildings[buildings.building_id == "C33"].iloc[0]
    xmin = min(c6.x_min, c33.x_min) - 35
    xmax = max(c6.x_max, c33.x_max) + 35
    ymin = min(c6.y_min, c33.y_min) - 35
    ymax = max(c6.y_max, c33.y_max) + 25
    local = merged[(merged.x >= xmin) & (merged.x <= xmax) & (merged.y >= ymin) & (merged.y <= ymax)]

    fig, ax = plt.subplots(figsize=(7.2, 7.6))
    sc = ax.scatter(
        local.x,
        local.y,
        c=local["diff"],
        cmap="RdBu_r",
        vmin=-lim,
        vmax=lim,
        s=36,
        marker="s",
        edgecolors="none",
    )
    for _, row in buildings[buildings.building_id.isin(["C6", "C33"])].iterrows():
        ax.add_patch(
            Rectangle(
                (row.x_min, row.y_min),
                row.x_max - row.x_min,
                row.y_max - row.y_min,
                fill=False,
                ec=DARK,
                lw=1.5,
            )
        )
        ax.text(
            (row.x_min + row.x_max) / 2,
            (row.y_min + row.y_max) / 2,
            row.building_id,
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            fontproperties=PROP,
            color=DARK,
        )
    ax.set_title("C6 / C33 周边局部采光变化", fontsize=14, fontweight="bold", fontproperties=PROP, pad=10)
    ax.set_xlabel("x / m", fontproperties=PROP)
    ax.set_ylabel("y / m", fontproperties=PROP)
    ax.grid(True, color="#e5e7eb", lw=0.55)
    ax.set_aspect("equal")
    cb = fig.colorbar(sc, ax=ax, fraction=0.04, pad=0.03)
    cb.set_label("采光小时变化 / h", fontproperties=PROP)
    ax.text(
        0.02,
        0.02,
        "黑框为 C6、C33 建筑边界；颜色表示干预前后采光小时差值",
        transform=ax.transAxes,
        fontsize=9,
        fontproperties=PROP,
        color=GRAY,
    )
    save_exact(fig, "image7.png", dpi=225)


def make_strategy_figure():
    strategy = pd.read_csv(STRATEGY_CSV)
    strategy["label"] = strategy["scheme_type"].map(
        {
            "baseline": "现状",
            "AI_conservative": "保守型",
            "AI_balanced": "均衡型",
            "AI_light_first": "采光优先型",
        }
    )
    fig, axs = plt.subplots(2, 2, figsize=(10.5, 5.0))
    metrics = [
        ("average_sunlight_hours", "平均采光小时 / h", BLUE),
        ("dark_zone_ratio", "暗区比例 / %", ORANGE),
        ("intervention_volume", "相对干预体量", GREEN),
        ("changed_building_count", "涉及建筑数量", RED),
    ]
    for ax, (col, ylabel, color) in zip(axs.ravel(), metrics):
        vals = strategy[col].copy()
        if col == "dark_zone_ratio":
            vals = vals * 100
        ax.bar(strategy["label"], vals, color=color, alpha=0.78, width=0.62)
        ax.set_ylabel(ylabel, fontproperties=PROP)
        ax.grid(axis="y", color="#e5e7eb", lw=0.55)
        ax.tick_params(axis="x", rotation=18, labelsize=9)
        ax.tick_params(axis="y", labelsize=9)
        top = max(vals) if max(vals) > 0 else 1
        for i, v in enumerate(vals):
            label = f"{v:.2f}" if col != "changed_building_count" else f"{int(v)}"
            ax.text(i, v + top * 0.025, label, ha="center", fontsize=8.5, fontproperties=PROP)
    fig.suptitle("现状基准与三类 AI 策略指标对比", fontsize=15, fontweight="bold", fontproperties=PROP)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    save_exact(fig, "image6.png", dpi=230)


def make_grid_figures():
    grid = pd.read_csv(GRID_CSV)
    grid["grid_label"] = grid["grid_size_m"].astype(str).str.replace(".0", "", regex=False) + " m"
    fig, ax = plt.subplots(figsize=(9.2, 5.8))
    x = np.arange(len(grid))
    width = 0.34
    ax.bar(x - width / 2, grid["baseline_dark_zone_ratio"] * 100, width, label="现状", color=BLUE, alpha=0.78)
    ax.bar(x + width / 2, grid["post_dark_zone_ratio"] * 100, width, label="策略后", color=ORANGE, alpha=0.78)
    for i, row in grid.iterrows():
        ax.text(i - width / 2, row["baseline_dark_zone_ratio"] * 100 + 0.25, f"{row['baseline_dark_zone_ratio'] * 100:.2f}%", ha="center", fontsize=9, fontproperties=PROP)
        ax.text(i + width / 2, row["post_dark_zone_ratio"] * 100 + 0.25, f"{row['post_dark_zone_ratio'] * 100:.2f}%", ha="center", fontsize=9, fontproperties=PROP)
        ax.text(i, max(row["baseline_dark_zone_ratio"], row["post_dark_zone_ratio"]) * 100 + 1.5, str(row["changed_building_ids"]), ha="center", fontsize=8.5, fontproperties=PROP, color=GRAY)
    ax.set_xticks(x)
    ax.set_xticklabels(grid["grid_label"], fontproperties=PROP)
    ax.set_ylabel("暗区比例 / %", fontproperties=PROP)
    ax.set_title("6 m 与 3 m 网格敏感性测试：暗区比例对比", fontsize=14, fontweight="bold", fontproperties=PROP)
    ax.grid(axis="y", color="#e5e7eb", lw=0.55)
    ax.legend(prop=PROP, frameon=False)
    save_exact(fig, "image8.png", dpi=225)

    fig, axs = plt.subplots(1, 3, figsize=(11.5, 4.6))
    metric_defs = [
        ("baseline_average_sunlight_hours", "post_average_sunlight_hours", "平均采光小时 / h", BLUE),
        ("baseline_dark_zone_ratio", "post_dark_zone_ratio", "暗区比例 / %", ORANGE),
        ("baseline_dark_grid_count", "post_dark_grid_count", "暗区网格数", GREEN),
    ]
    for ax, (bcol, pcol, title, color) in zip(axs, metric_defs):
        baseline = grid[bcol].copy()
        post = grid[pcol].copy()
        if "ratio" in bcol:
            baseline = baseline * 100
            post = post * 100
        x = np.arange(len(grid))
        w = 0.34
        ax.bar(x - w / 2, baseline, w, label="现状", color=color, alpha=0.45)
        ax.bar(x + w / 2, post, w, label="策略后", color=color, alpha=0.9)
        ax.set_title(title, fontproperties=PROP, fontsize=11, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(grid["grid_label"], fontproperties=PROP)
        ax.grid(axis="y", color="#e5e7eb", lw=0.55)
        top = max(max(baseline), max(post)) if max(max(baseline), max(post)) > 0 else 1
        for i, v in enumerate(baseline):
            ax.text(i - w / 2, v + top * 0.02, f"{v:.2f}" if top < 100 else f"{int(v)}", ha="center", fontsize=8, fontproperties=PROP)
        for i, v in enumerate(post):
            ax.text(i + w / 2, v + top * 0.02, f"{v:.2f}" if top < 100 else f"{int(v)}", ha="center", fontsize=8, fontproperties=PROP)
    axs[0].legend(prop=PROP, frameon=False, loc="upper left")
    fig.suptitle("6 m 与 3 m 网格敏感性测试三项指标对比", fontsize=14, fontweight="bold", fontproperties=PROP)
    fig.tight_layout(rect=(0, 0, 1, 0.9))
    save_exact(fig, "image9.png", dpi=230)


if __name__ == "__main__":
    make_figure_1()
    make_figure_2()
    make_spatial_figures()
    make_strategy_figure()
    make_grid_figures()
    print(f"Generated figures in {FIG_DIR}")
