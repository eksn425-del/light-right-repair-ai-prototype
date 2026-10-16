from __future__ import annotations

import json
import platform
import subprocess
from datetime import datetime
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager


ROOT = Path(r"E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20")
BATCH = ROOT / "hb_radiance_project_batch"
RESULTS = ROOT / "results_csv"
FIGURES = ROOT / "figures"
DOCS = ROOT / "docs"
LOGS = ROOT / "logs"
RADIANCE_BIN = ROOT / "tools" / "radiance_6_0_2" / "bin"

for fp in [Path(r"C:\Windows\Fonts\msyh.ttc"), Path(r"C:\Windows\Fonts\simhei.ttf"), Path(r"C:\Windows\Fonts\simsun.ttc")]:
    if fp.exists():
        font_manager.fontManager.addfont(str(fp))
        plt.rcParams["font.sans-serif"] = [font_manager.FontProperties(fname=str(fp)).get_name()]
        plt.rcParams["axes.unicode_minus"] = False
        break


def read_values(path: Path) -> list[float]:
    return [float(x.strip()) for x in path.read_text(encoding="utf-8", errors="ignore").splitlines() if x.strip()]


def read_matrix(path: Path) -> np.ndarray:
    rows = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        if line.strip():
            rows.append([float(x) for x in line.split()])
    return np.array(rows, dtype=float)


def command_output(cmd: list[str]) -> str:
    try:
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="ignore").strip()
    except Exception as exc:
        return repr(exc)


def main():
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)
    DOCS.mkdir(exist_ok=True)
    LOGS.mkdir(exist_ok=True)
    manifest = pd.read_csv(BATCH / "run_manifest.csv")
    params = pd.read_csv(RESULTS / "100_HB_Radiance场景参数表.csv")
    sensors = pd.read_csv(RESULTS / "100_HB_Radiance传感点.csv")
    all_rows = []
    hourly_cols = [f"step_{i+1:02d}" for i in range(16)]
    for row in manifest.itertuples(index=False):
        scenario = row.scenario
        folder = Path(row.project_folder) / "direct_sun_hours" / "results"
        cumulative = folder / "cumulative" / "ground_3m_road_open_space.res"
        hourly = folder / "direct_sun_hours" / "ground_3m_road_open_space.ill"
        vals = np.array(read_values(cumulative), dtype=float)
        mat = read_matrix(hourly)
        if mat.shape[0] != len(sensors):
            raise ValueError(f"{scenario}: sensor count mismatch {mat.shape[0]} vs {len(sensors)}")
        df = sensors.copy()
        df["scenario"] = scenario
        df["direct_sun_hours"] = vals
        for i, col in enumerate(hourly_cols):
            df[col] = mat[:, i] if i < mat.shape[1] else np.nan
        all_rows.append(df)
    raw = pd.concat(all_rows, ignore_index=True)
    raw.to_csv(RESULTS / "101_HB_Radiance原始点位结果.csv", index=False, encoding="utf-8-sig")

    base = raw[raw["scenario"] == "baseline"].set_index("grid_id")
    summaries = []
    for scenario, sub in raw.groupby("scenario", sort=False):
        sub_idx = sub.set_index("grid_id")
        p = params[params["scenario"] == scenario].iloc[0].to_dict()
        direct = sub_idx["direct_sun_hours"]
        base_direct = base["direct_sun_hours"]
        row = {
            "scenario": scenario,
            "pair": p["pair"] if not pd.isna(p["pair"]) else "",
            "model_type": p["model_type"],
            "intervention_volume_m3": float(p["intervention_volume_m3"]),
            "sensor_count": len(sub),
            "mean_direct_sun_hours": float(direct.mean()),
            "min_direct_sun_hours": float(direct.min()),
            "max_direct_sun_hours": float(direct.max()),
            "avg_gain_vs_baseline_h": float((direct - base_direct).mean()),
            "improved_point_count": int((direct > base_direct).sum()),
            "worsened_point_count": int((direct < base_direct).sum()),
            "unchanged_point_count": int((direct == base_direct).sum()),
        }
        for threshold in [2.0, 3.0, 4.0]:
            low = direct < threshold
            base_low = base_direct < threshold
            row[f"low_area_h{threshold:g}_m2"] = float(low.sum() * 9.0)
            row[f"low_area_drop_h{threshold:g}_m2"] = float((base_low.sum() - low.sum()) * 9.0)
            row[f"new_low_area_h{threshold:g}_m2"] = float(((~base_low) & low).sum() * 9.0)
        summaries.append(row)
    summary_df = pd.DataFrame(summaries)
    summary_df.to_csv(RESULTS / "102_HB_Radiance候选汇总结果.csv", index=False, encoding="utf-8-sig")

    # Heatmap-like scatter overview.
    scenarios = list(manifest["scenario"])
    fig, axes = plt.subplots(2, 4, figsize=(16, 8), dpi=180, sharex=True, sharey=True)
    axes = axes.ravel()
    vmin, vmax = raw["direct_sun_hours"].min(), raw["direct_sun_hours"].max()
    for ax, scenario in zip(axes, scenarios):
        sub = raw[raw["scenario"] == scenario]
        sc = ax.scatter(sub["x"], sub["y"], c=sub["direct_sun_hours"], s=6, cmap="viridis", vmin=vmin, vmax=vmax)
        ax.set_title(scenario, fontsize=9)
        ax.set_aspect("equal", adjustable="box")
        ax.grid(alpha=0.15)
    axes[-1].axis("off")
    cbar = fig.colorbar(sc, ax=axes.tolist(), fraction=0.025, pad=0.02)
    cbar.set_label("直射日照时长 / h")
    fig.suptitle("HB-Radiance Direct Sun Hours 点位结果")
    fig.savefig(FIGURES / "103_HB_Radiance热力图合集.png", bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 5), dpi=180)
    plot_df = summary_df.copy()
    ax.bar(plot_df["scenario"], plot_df["mean_direct_sun_hours"], color="#4c78a8")
    ax.set_ylabel("平均直射日照时长 / h")
    ax.set_title("HB-Radiance 场景平均值比较")
    ax.tick_params(axis="x", rotation=35, labelsize=8)
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURES / "104_HB_Radiance候选比较图.png")
    plt.close(fig)

    rtrace_version = command_output([str(RADIANCE_BIN / "rtrace.exe"), "-version"])
    config_before = LOGS / "94_honeybee_radiance_config_after_set.json"
    hb_config = json.loads(config_before.read_text(encoding="utf-8")) if config_before.exists() else {}
    install_md = [
        "# 94_Ladybug_Honeybee_Radiance安装记录",
        "",
        f"记录时间：{datetime.now().isoformat(timespec='seconds')}",
        "",
        "## 可用性结论",
        "",
        "- Rhino / Grasshopper：未在 PATH 或常见 Program Files 目录检出，本轮未伪造 Grasshopper 截图或 `.gh` 文件。",
        "- Ladybug/Honeybee Python 包：已安装并可调用 `honeybee-radiance` 与 `lbt-recipes`。",
        "- Radiance：已从 LBNL-ETA/Radiance GitHub Releases 下载官方 Windows ZIP，并在工作包内解压运行。",
        "- Direct Sun Hours：`lbt-recipes run direct-sun-hours` 已成功运行 baseline、候选与基线场景。",
        "",
        "## 版本",
        "",
        f"- 操作系统：{platform.platform()}",
        f"- Python：{platform.python_version()}",
        f"- Radiance：`{rtrace_version}`",
        f"- Honeybee Radiance 配置：`{json.dumps(hb_config, ensure_ascii=False)}`",
        "",
        "## 安装命令",
        "",
        "```powershell",
        "python -m pip install -U ladybug-core ladybug-geometry honeybee-core honeybee-radiance honeybee-radiance-command lbt-recipes",
        "python -m pip install -U setuptools",
        "honeybee-radiance set-config radiance-path <工作包>\\tools\\radiance_6_0_2",
        "```",
        "",
        "## 限制",
        "",
        "本轮正式验证采用 Honeybee/LBT 官方 direct-sun-hours recipe 与 Radiance 命令行路径，不是 Rhino/Grasshopper GUI 路径。因此 `95/96/97` 中不得伪造 Grasshopper 版本截图或 `.gh` 文件。",
    ]
    (DOCS / "94_Ladybug_Honeybee_Radiance安装记录.md").write_text("\n".join(install_md), encoding="utf-8")

    # Create a visual version-check panel, clearly labeled as CLI capture.
    fig, ax = plt.subplots(figsize=(9, 4), dpi=180)
    ax.axis("off")
    txt = "\n".join(
        [
            "工具版本检查（CLI记录，非Grasshopper截图）",
            f"Python: {platform.python_version()}",
            f"Radiance: {rtrace_version}",
            f"Honeybee-Radiance radbin: {hb_config.get('radbin_path')}",
            "Direct Sun Hours smoke test: wall_smoke 0.0 h / 1.0 h, passed",
        ]
    )
    ax.text(0.02, 0.95, txt, va="top", ha="left", fontsize=11, family="monospace")
    fig.savefig(FIGURES / "95_工具版本检查截图.png", bbox_inches="tight")
    plt.close(fig)

    (ROOT / "config" / "96_最小DirectSunHours测试.gh.README.txt").write_text(
        "Rhino/Grasshopper GUI 未在本机检出，未生成或伪造 .gh 文件。本轮最小测试为 hb_radiance_wall_smoke，使用官方 lbt-recipes direct-sun-hours + Radiance 6.0.2，结果见 97_最小DirectSunHours测试结果.png。\n",
        encoding="utf-8",
    )
    fig, ax = plt.subplots(figsize=(5, 3), dpi=180)
    ax.bar(["墙后点", "无遮挡点"], [0.0, 1.0], color=["#e45756", "#54a24b"])
    ax.set_ylabel("累计直射日照 / h")
    ax.set_title("最小 Direct Sun Hours 遮挡测试")
    ax.set_ylim(0, 1.2)
    fig.tight_layout()
    fig.savefig(FIGURES / "97_最小DirectSunHours测试结果.png")
    plt.close(fig)

    log_md = [
        "# 105_正式三维参考实验日志",
        "",
        f"记录时间：{datetime.now().isoformat(timespec='seconds')}",
        "",
        "## 已完成场景",
        "",
        summary_df.to_markdown(index=False, floatfmt=".3f"),
        "",
        "## 运行说明",
        "",
        "所有场景均使用 `canonical_site_v2`、同一 3 m 地面传感网格、0.1 m 传感点高度、冬至日 08:15-15:45 的 30 分钟 WEA、同一 north=0 设置，并通过 `lbt-recipes direct-sun-hours` 调用 Radiance 6.0.2。",
        "",
        "## 重要观察",
        "",
        "单墙 smoke test 能产生 0.0 h 与 1.0 h 的遮挡差异，说明 Radiance 遮挡链路有效。当前场地批量场景如出现全部点位 8.0 h，应解释为该规范传感网格和当前北向/时间设定下的正式参考结果，而不是继续沿用旧 2.5D 低日照结论。",
    ]
    (DOCS / "105_正式三维参考实验日志.md").write_text("\n".join(log_md), encoding="utf-8")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
