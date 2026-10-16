from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager


WORK = Path(__file__).resolve().parent
FIG_DIR = WORK / "optimized_figures"
FIG_DIR.mkdir(exist_ok=True)
BASELINE_COMPARE = WORK / "non_ai_baseline_comparison" / "non_ai_baseline_comparison_fast.csv"


def setup_font():
    for path in [r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\simsun.ttc"]:
        if Path(path).exists():
            prop = font_manager.FontProperties(fname=path)
            mpl.rcParams["font.family"] = prop.get_name()
            mpl.rcParams["axes.unicode_minus"] = False
            return prop
    return None


PROP = setup_font()
BLUE = "#2563eb"
ORANGE = "#f59e0b"
GREEN = "#22a06b"
RED = "#d94848"
GRAY = "#6b7280"


def make_baseline_comparison_figure():
    df = pd.read_csv(BASELINE_COMPARE)
    labels = {
        "baseline": "现状",
        "ai_conservative": "AI保守型",
        "height_priority": "高度优先\n基线",
        "dark_nearest": "暗区邻近\n基线",
        "random_10_mean": "随机基线\n均值",
    }
    df["label"] = df["case_id"].map(labels)
    df = df[df["case_id"].isin(labels.keys())].copy()

    fig, axs = plt.subplots(1, 3, figsize=(12.2, 4.4))
    panels = [
        ("average_sunlight_hours", "平均采光小时 / h", BLUE, "{:.3f}"),
        ("dark_zone_ratio_percent", "暗区比例 / %", ORANGE, "{:.2f}%"),
        ("intervention_volume", "相对干预体量", GREEN, "{:.2f}"),
    ]
    colors = [GRAY, BLUE, RED, ORANGE, GREEN]
    for ax, (col, title, default_color, fmt) in zip(axs, panels):
        values = df[col].astype(float)
        ax.bar(df["label"], values, color=colors, alpha=0.82, width=0.62)
        ax.set_title(title, fontsize=11.5, fontweight="bold", fontproperties=PROP)
        ax.grid(axis="y", color="#e5e7eb", lw=0.55)
        ax.tick_params(axis="x", labelsize=8)
        ax.tick_params(axis="y", labelsize=8)
        top = max(values) if max(values) > 0 else 1
        for i, v in enumerate(values):
            ax.text(i, v + top * 0.025, fmt.format(v), ha="center", va="bottom", fontsize=8, fontproperties=PROP)
        if col == "dark_zone_ratio_percent":
            ax.axhline(17.55, color="#9ca3af", lw=0.8, ls="--")

    fig.suptitle(
        "现状、AI保守型与非 AI 基线策略对比",
        fontsize=15,
        fontweight="bold",
        fontproperties=PROP,
    )
    fig.text(
        0.5,
        0.01,
        "非 AI 基线使用同一简化 2.5D 后模拟口径；AI保守型在暗区比例下降与干预体量控制之间取得更稳妥平衡。",
        ha="center",
        fontsize=9.5,
        color="#4b5563",
        fontproperties=PROP,
    )
    fig.tight_layout(rect=(0, 0.05, 1, 0.9))
    fig.savefig(FIG_DIR / "image6.png", dpi=235, facecolor="white")
    plt.close(fig)


if __name__ == "__main__":
    make_baseline_comparison_figure()
    print(FIG_DIR / "image6.png")
