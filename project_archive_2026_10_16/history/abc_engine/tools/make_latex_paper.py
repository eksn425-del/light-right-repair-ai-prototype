from __future__ import annotations

import csv
import os
import re
import shutil
from pathlib import Path

from PIL import Image


def tex_escape(text: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(ch, ch) for ch in text)


def md_to_tex_body(markdown: str) -> str:
    markdown = re.sub(r"## 8 图表建议[\s\S]*?## 参考文献", "## 8 图表与表格\n", markdown)
    markdown = re.sub(r"## 参考文献[\s\S]*$", "", markdown).strip()
    lines: list[str] = []
    for raw in markdown.splitlines():
        line = raw.strip()
        if not line:
            continue
        line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
        if line.startswith("# "):
            continue
        if line.startswith("## "):
            title = line[3:].strip()
            if title == "8 图表与表格":
                continue
            lines.append(rf"\section{{{tex_escape(title)}}}")
        elif line.startswith("### "):
            lines.append(rf"\subsection{{{tex_escape(line[4:].strip())}}}")
        else:
            lines.append(tex_escape(line))
            lines.append("")
    return "\n".join(lines)


def csv_table(path: Path, headers: list[str], keys: list[str], ratio_keys: set[str] | None = None) -> str:
    ratio_keys = ratio_keys or set()
    with path.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    col_spec = "p{0.13\\textwidth}" + "p{0.13\\textwidth}" * (len(headers) - 1)
    out = [rf"\begin{{tabular}}{{{col_spec}}}", r"\toprule"]
    out.append(" & ".join(tex_escape(h) for h in headers) + r" \\")
    out.append(r"\midrule")
    for row in rows:
        vals = []
        for key in keys:
            val = row.get(key, "")
            if key in ratio_keys and val:
                val = f"{float(val) * 100:.2f}\\%"
            vals.append(tex_escape(str(val)))
        out.append(" & ".join(vals) + r" \\")
    out.append(r"\bottomrule")
    out.append(r"\end{tabular}")
    return "\n".join(out)


def make_manual_validation_figure(before_dir: Path, after_dir: Path, out_path: Path) -> None:
    before = sorted(before_dir.glob("*.bmp"))
    after = sorted(after_dir.glob("*.bmp"))
    if not before or not after:
        return
    b = Image.open(before[0]).convert("RGB")
    a = Image.open(after[0]).convert("RGB")
    thumb_w, thumb_h = 900, 650

    def fit(img: Image.Image) -> Image.Image:
        img = img.copy()
        img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
        frame = Image.new("RGB", (thumb_w, thumb_h), "white")
        frame.paste(img, ((thumb_w - img.width) // 2, (thumb_h - img.height) // 2))
        return frame

    canvas = Image.new("RGB", (thumb_w * 2 + 60, thumb_h + 80), "white")
    canvas.paste(fit(b), (20, 60))
    canvas.paste(fit(a), (thumb_w + 40, 60))
    canvas.save(out_path)


def main() -> None:
    root = Path(os.environ.get("WORKPKG", r"E:\AI项目\光权修复_论文工作包_2026-06-03"))
    draft = root / "01_论文初稿" / "论文初稿_v3_科研写作skills版_2026-06-03.md"
    latex_dir = root / "08_LaTeX排版稿"
    fig_out = latex_dir / "figures"
    latex_dir.mkdir(parents=True, exist_ok=True)
    fig_out.mkdir(parents=True, exist_ok=True)

    figure_sources = {
        "algorithm_heatmap.png": root / "04_图表与光照复核" / "algorithm_heatmap.png",
        "strategy_comparison_chart.png": root / "04_图表与光照复核" / "strategy_comparison_chart.png",
        "grid_sensitivity_chart_partial.png": root
        / "04_图表与光照复核"
        / "grid_sensitivity_chart_partial.png",
    }
    for name, src in figure_sources.items():
        if src.exists():
            shutil.copy2(src, fig_out / name)
    make_manual_validation_figure(
        root / "04_图表与光照复核" / "同视角人工光照复核_2026-06-03" / "算法前",
        root / "04_图表与光照复核" / "同视角人工光照复核_2026-06-03" / "算法后",
        fig_out / "manual_validation_before_after.png",
    )

    body = md_to_tex_body(draft.read_text(encoding="utf-8"))
    table_dir = root / "03_核心数据表"
    table1 = csv_table(
        table_dir / "strategy_comparison_metrics.csv",
        ["方案类型", "平均采光小时", "暗区比例", "干预体量", "涉及建筑", "保护冲突"],
        [
            "scheme_type",
            "average_sunlight_hours",
            "dark_zone_ratio",
            "intervention_volume",
            "changed_building_ids",
            "protected_conflict_count",
        ],
        {"dark_zone_ratio"},
    )
    table2 = csv_table(
        table_dir / "grid_sensitivity_metrics_partial.csv",
        ["网格尺寸", "现状平均采光小时", "现状暗区比例", "方案后平均采光小时", "方案后暗区比例", "改善比例", "候选建筑"],
        [
            "grid_size_m",
            "baseline_average_sunlight_hours",
            "baseline_dark_zone_ratio",
            "post_average_sunlight_hours",
            "post_dark_zone_ratio",
            "dark_zone_improvement_ratio",
            "changed_building_ids",
        ],
        {"baseline_dark_zone_ratio", "post_dark_zone_ratio", "dark_zone_improvement_ratio"},
    )
    table3 = r"""\begin{tabular}{p{0.12\textwidth}p{0.12\textwidth}p{0.14\textwidth}p{0.14\textwidth}p{0.34\textwidth}}
\toprule
建筑编号 & 原高度/m & 算法后高度/m & 削减高度/m & 设计转译 \\
\midrule
C6 & 6.0 & 4.5 & 1.5 & 屋顶边缘退台、屋顶平台、采光缝。\\
C33 & 9.0 & 6.75 & 2.25 & 二层以上局部退台、转角采光缝、口袋灰空间。\\
\bottomrule
\end{tabular}"""

    tex = rf"""\documentclass[UTF8,zihao=-4,a4paper]{{ctexart}}
\usepackage{{geometry}}
\usepackage{{graphicx}}
\usepackage{{booktabs}}
\usepackage{{tabularx}}
\usepackage{{array}}
\usepackage{{caption}}
\usepackage{{float}}
\usepackage{{hyperref}}
\usepackage{{setspace}}
\usepackage{{titlesec}}
\usepackage{{fancyhdr}}

\geometry{{left=2.8cm,right=2.8cm,top=2.5cm,bottom=2.5cm}}
\setstretch{{1.35}}
\captionsetup[figure]{{name=图,labelsep=quad,font=small}}
\captionsetup[table]{{name=表,labelsep=quad,font=small,position=top}}
\titleformat{{\section}}{{\heiti\zihao{{4}}}}{{\thesection}}{{0.8em}}{{}}
\titleformat{{\subsection}}{{\heiti\zihao{{-4}}}}{{\thesubsection}}{{0.8em}}{{}}
\pagestyle{{fancy}}
\fancyhf{{}}
\fancyhead[C]{{光权修复 AI 辅助空间决策工作流研究}}
\fancyfoot[C]{{\thepage}}

\title{{\heiti\zihao{{2}} 光权修复：面向旧街区采光修复的 AI 辅助空间决策工作流研究}}
\author{{}}
\date{{2026年6月3日}}

\begin{{document}}
\maketitle

{body}

\section{{图表与表格}}

\begin{{figure}}[H]
\centering
\includegraphics[width=0.88\textwidth]{{figures/algorithm_heatmap.png}}
\caption{{现状采光热力图。该图展示 baseline 状态下场地冬至日简化采光诊断结果，用于定位整体暗区分布。}}
\end{{figure}}

\begin{{figure}}[H]
\centering
\includegraphics[width=0.88\textwidth]{{figures/strategy_comparison_chart.png}}
\caption{{三类 AI 策略指标对比。该图比较 baseline、保守型、均衡型与采光优先型策略的核心指标。}}
\end{{figure}}

\begin{{figure}}[H]
\centering
\includegraphics[width=0.88\textwidth]{{figures/grid_sensitivity_chart_partial.png}}
\caption{{网格敏感性测试结果。该图比较 6m 与 3m 网格下采光诊断与候选结果的变化。}}
\end{{figure}}

\begin{{figure}}[H]
\centering
\includegraphics[width=0.96\textwidth]{{figures/manual_validation_before_after.png}}
\caption{{算法前后同视角人工光照复核。算法后模型保留完整场地，仅调整 C6 与 C33，用于方向性复核。}}
\end{{figure}}

\begin{{table}}[H]
\centering
\caption{{baseline 与三类 AI 策略对比指标}}
\small
{table1}
\end{{table}}

\begin{{table}}[H]
\centering
\caption{{6m 与 3m 网格敏感性测试结果}}
\small
{table2}
\end{{table}}

\begin{{table}}[H]
\centering
\caption{{保守型方案中 C6、C33 的高度变化与设计转译}}
\small
{table3}
\end{{table}}

\section{{参考文献}}
\begin{{enumerate}}
\item CZACHURA A, KANTERS J, GENTILE N, 等. Solar performance metrics in urban planning: a review and taxonomy[J]. Buildings, 2022, 12(4): 393. DOI: 10.3390/buildings12040393.
\item COMPAGNON R. Solar and daylight availability in the urban fabric[J]. Energy and Buildings, 2004, 36(4): 321-328. DOI: 10.1016/j.enbuild.2004.01.009.
\item ALLEGRINI J, DORER V, CARMELIET J. Review of the impact of urban block form on thermal performance, solar access and ventilation[J]. Renewable and Sustainable Energy Reviews, 2015, 38: 551-560. DOI: 10.1016/j.rser.2014.06.007.
\item CURRELI A, SERRA-COCH G, ISALGUE A, 等. Solar energy as a form giver for future cities[J]. Energies, 2016, 9(7): 544. DOI: 10.3390/en9070544.
\item KONIS K, GAMAS A, KENSEK K. Passive performance and building form: an optimization framework for early-stage design support[J]. Solar Energy, 2016, 125: 161-179. DOI: 10.1016/j.solener.2015.12.020.
\item WANG L, 等. Optimization-based design exploration of building massing typologies: EvoMass and a typology-oriented computational design optimization method for early-stage performance-based building massing design[J]. Frontiers of Architectural Research, 2024, 13(6): 1400-1422. DOI: 10.1016/j.foar.2024.06.001.
\item SADEGHIPOUR ROUDSARI M, PAK M. Ladybug: a parametric environmental plugin for Grasshopper to help designers create an environmentally-conscious design[C]//Proceedings of BS2013. 2013.
\item DE LUCA F, 等. Reverse solar envelope method: a new building form-finding method that can take regulatory frameworks into account[J]. Automation in Construction, 2021, 123: 103518. DOI: 10.1016/j.autcon.2020.103518.
\item THORING K, HUETTEMANN S, MUELLER R M. The augmented designer: a research agenda for generative AI-enabled design[C]//Proceedings of the Design Society. 2023, 3: 3345-3354. DOI: 10.1017/pds.2023.335.
\item JAKUBIK J, HEMMER P, VÖSSING M, 等. Designing a human-in-the-loop system for object detection in floor plans[J]. Proceedings of the AAAI Conference on Artificial Intelligence, 2022, 36(11): 12524-12530. DOI: 10.1609/aaai.v36i11.21522.
\item RAFSANJANI H N, NABIZADEH A H. Towards human-centered artificial intelligence (AI) in architecture, engineering, and construction (AEC) industry[J]. Computers in Human Behavior Reports, 2023, 11: 100319. DOI: 10.1016/j.chbr.2023.100319.
\end{{enumerate}}

\end{{document}}
"""

    (latex_dir / "main.tex").write_text(tex, encoding="utf-8")
    (latex_dir / "README_编译说明.md").write_text(
        "使用 XeLaTeX 编译：\n\n```bash\nxelatex main.tex\nxelatex main.tex\n```\n\n也可以上传整个 `08_LaTeX排版稿` 文件夹到 Overleaf，编译器选择 XeLaTeX。\n",
        encoding="utf-8",
    )
    print(latex_dir / "main.tex")


if __name__ == "__main__":
    main()
