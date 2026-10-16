from __future__ import annotations

from pathlib import Path

import pandas as pd
from docx import Document
from docx.shared import Pt


ROOT = Path(r"E:/AI项目/中文导师审阅定稿_工作包_2026_06_20")
DOCS = ROOT / "docs"
RESULTS = ROOT / "results_csv"


def set_font(document: Document) -> None:
    style = document.styles["Normal"]
    style.font.name = "Microsoft YaHei"
    style.font.size = Pt(10.5)


def add_heading(document: Document, text: str, level: int = 1) -> None:
    document.add_heading(text, level=level)


def add_kv(document: Document, rows: list[tuple[str, str]]) -> None:
    table = document.add_table(rows=1, cols=2)
    table.style = "Table Grid"
    hdr = table.rows[0].cells
    hdr[0].text = "问题"
    hdr[1].text = "回答"
    for key, value in rows:
        cells = table.add_row().cells
        cells[0].text = key
        cells[1].text = value


def main() -> None:
    ranking = pd.read_csv(RESULTS / "40_完整候选排名.csv")
    compare = pd.read_csv(RESULTS / "baseline_comparison_summary.csv")
    ref = pd.read_csv(RESULTS / "22_Python与参考模拟对比结果.csv")
    design = pd.read_csv(RESULTS / "60_规则模型与设计模型对比.csv")
    random_summary = pd.read_csv(RESULTS / "random_baseline_summary.csv").iloc[0].to_dict()

    first = ranking[ranking["candidate_id"] == "C13_C24"].iloc[0]
    c6 = ranking[ranking["candidate_id"] == "C6_C33"].iloc[0]
    final_supported = bool(ranking["final_retained"].fillna(False).any())

    self_check = [
        "# 投稿前自检报告",
        "",
        "## 总判断",
        "",
        "本轮已完成资产审计、30分钟算法A重跑、全候选双建筑枚举、Pareto与公平基线、网格尺度/原点/阈值敏感性、trimesh独立三维射线参考、规则模型与设计转译模型复算。但是，结果不满足用户设定的“中文导师审阅定稿版”验收门槛，因此不得输出或命名为定稿。",
        "",
        "## 未满足项",
        "",
        "| 门槛 | 状态 | 原因 |",
        "| --- | --- | --- |",
        "| 独立三维参考模拟没有推翻最终方案改善方向 | 未满足 | 2.5D 第一候选 C13/C24 在三维参考中有汇总改善，但三维参考下 C6/C33 的低直射日照面积下降为 54 m²，高于 C13/C24 的 18 m²，排序冲突。 |",
        "| 最终方案在公平预算约束下位于或接近 Pareto 前沿 | 部分满足 | C13/C24 位于 Pareto 前沿且优于随机基线，但独立参考不支持其作为唯一最终方案。 |",
        "| 3 m 网格重新优化无改善问题已解释 | 已满足 | 已用 3/4/5/6 m、四原点、2/3/4 h 阈值排查，旧 C6/C33 不再是唯一推荐。 |",
        "| 真实建筑设计转译版本已建模并复算 | 部分满足 | 已生成 C13/C24 规则模型与局部退台/转角切削 OBJ 并复算；但因未形成唯一最终方案，设计转译只能作为候选演示。 |",
        "| 所有参数、代码、输入输出、随机种子和图表来源可复现 | 基本满足 | 本工作包包含脚本、CSV、图、日志、requirements；Rhino/Ladybug/Radiance 链路仍不可用。 |",
        "| 图表、编号、引用和 Word/PDF 排版完成自检 | 未满足 | 未生成“中文导师审阅定稿版.docx/pdf”；参考文献尚未逐条完成投稿级核验。 |",
        "",
        "## 已完成部分",
        "",
        "- 01_项目资产清单.md、02_缺失文件与风险清单.md、03_运行环境清单.md。",
        "- 10-13：算法A参数、实现说明、运行日志、尺度阈值结果。",
        "- 30-44：候选规则、评分函数、候选日志、完整排名、Pareto、基线和随机分布。",
        "- 50-53：网格尺度、网格原点和3m异常诊断。",
        "- 20-24：独立三维参考设置、原始结果、对比结果和结论。",
        "- 60-63：规则模型与设计转译模型对比、人工复核协议和说明。",
        "- 70-73：效率对比、复现说明和 requirements。",
        "",
        "## 当前最诚实的论文定位",
        "",
        "低干预、局部改善、可进一步复核的旧街区早期直射日照候选筛查工作流。论文可以先给导师审阅方法链条、数据诚实度和后续补实验方向，但不适合作为投稿终稿。",
        "",
        "## 是否建议继续补实验",
        "",
        "建议继续。优先补 Rhino/Grasshopper/Ladybug/Honeybee/Radiance 或更严格三维参考链路，并围绕 C13/C24 与 C6/C33 候选区间做统一几何、统一掩膜和统一网格的复核。",
        "",
        "## 是否适合先给导师审阅",
        "",
        "适合先给导师看“审阅预整理版证据包”，不适合标注为“定稿版”。导师重点看：为何 C6/C33 降级、为何 C13/C24 不能直接成为唯一最终方案、以及后续投稿前还要补哪些验证。",
        "",
    ]
    (ROOT / "投稿前自检报告.md").write_text("\n".join(self_check), encoding="utf-8")

    summary_doc = Document()
    set_font(summary_doc)
    summary_doc.add_heading("导师阅读摘要（一页版，预审稿）", 0)
    add_kv(
        summary_doc,
        [
            ("这篇研究解决什么问题", "面向旧街区早期更新，建立直射日照可达性诊断、低干预候选生成、复算和设计师复核的工作流，用来缩小需要重点讨论的候选范围。"),
            ("原论文有哪些不足", "旧稿保留 C6/C33 的依据主要来自 6 m/3 m 2.5D 复算和人工同视角图，缺少独立三维数值验证、全候选 Pareto、4/5 m 与网格原点敏感性，也存在术语偏泛和设计转译未真实复算的问题。"),
            ("本次补了哪些实验", "完成 30 分钟太阳采样、3 m 主网格、2/3/4 h 阈值、3/4/5/6 m 与四原点敏感性、946 个合法双建筑候选枚举、Pareto、公平基线、1000 次随机基线、trimesh 三维参考、规则模型与局部退台模型复算。"),
            ("最终真实证明了什么", f"2.5D 规则模型中 C13/C24 位于 Pareto 前沿，低直射日照面积下降 {first['low_sun_area_drop_m2']:.0f} m²；C6/C33 在2.5D中仅下降 {c6['low_sun_area_drop_m2']:.0f} m²。但三维参考下 C6/C33 下降 54 m²，C13/C24 下降 18 m²，说明不能给出唯一最终方案。"),
            ("当前仍有哪些边界", "Rhino/Ladybug/Radiance 未接入；trimesh 参考与 2.5D 模型存在分类误差和排序冲突；设计转译只对 C13/C24 做了演示性复算；参考文献和 Word/PDF 定稿排版尚未完成。"),
            ("是否具备进一步投稿价值", "具备方法和诚实证据链价值，但当前应定位为早期筛查工作流。继续补专业参考模拟、统一几何掩膜和候选区间复核后，再判断投稿价值。"),
        ],
    )
    summary_doc.save(ROOT / "导师阅读摘要_一页版.docx")

    changes_doc = Document()
    set_font(changes_doc)
    changes_doc.add_heading("修改说明与新增实验清单（预审稿）", 0)
    add_heading(changes_doc, "一、核心修改", 1)
    for item in [
        "将研究定位从“采光可达性/光权修复”调整为“直射日照可达性早期候选筛查”。",
        "不再把 C6/C33 写作唯一推荐方案；改为候选区间中的旧稿重点对照。",
        "新增 30 分钟太阳采样、全候选枚举、Pareto、公平基线、随机基线、尺度和原点敏感性。",
        "新增独立 trimesh 三维射线参考，明确它不是 Ladybug/Radiance。",
        "新增规则模型与设计转译模型复算，避免把整体减高效果直接归因于退台/采光缝。",
    ]:
        changes_doc.add_paragraph(item, style=None)
    add_heading(changes_doc, "二、新增实验文件", 1)
    for item in [
        "10_算法A参数表.csv、11_算法A实现说明.md、12_算法A运行日志.txt、13_各尺度与阈值结果.csv",
        "30_候选规则与约束表.csv、31_评分函数与归一化说明.md、32_候选生成完整日志.csv、33_单元测试与异常检查报告.md",
        "40_完整候选排名.csv、41_Pareto前沿图.png、42_基线比较图.png、43_随机基线分布图.png、44_候选比较结论.md",
        "20_独立参考模拟设置说明.md、21_独立参考模拟原始结果.csv、22_Python与参考模拟对比结果.csv、23_误差地图与一致性图.png、24_独立验证结论.md",
        "50_网格尺度敏感性.csv、51_网格原点敏感性.csv、52_尺度稳定性图.png、53_3m异常诊断报告.md",
        "60_规则模型与设计模型对比.csv、61_设计转译前后模拟图.png、62_人工复核协议表.csv、63_建筑设计转译说明.md",
        "70_效率对比.csv、71_效率对比图.png、72_复现说明README.md、73_requirements.txt",
    ]:
        changes_doc.add_paragraph(item)
    add_heading(changes_doc, "三、结论状态", 1)
    changes_doc.add_paragraph(
        "本轮不满足“中文导师审阅定稿版”门槛，原因是独立三维参考没有支持 2.5D 第一候选作为唯一最终方案。建议以预审稿形式提交导师讨论。"
    )
    changes_doc.save(ROOT / "修改说明与新增实验清单.docx")

    # Minimal reference audit placeholder: honest, not a completed literature audit.
    ref_rows = []
    refs = [
        "SAMPSON T C, CHARO R A. Access to Sunlight...",
        "BRYAN H, STUEBING S. Natural Light as an Urban Amenity...",
        "CZACHURA A, KANTERS J, GENTILE N, WALL M. Solar Performance Metrics...",
        "COMPAGNON R. Solar and daylight availability in the urban fabric...",
        "SANAIEIAN H, et al. Review of the impact of urban block form...",
        "CURRELI A, et al. Solar Energy as a Form Giver for Future Cities...",
        "KONIS K, GAMAS A, KENSEK K. Passive performance and building form...",
        "WANG L, JANSSEN P, JI G. EvoMass...",
        "SADEGHIPOUR ROUDSARI M, PAK M, VIOLA A. Ladybug...",
        "DE LUCA F, DOGAN T, SEPULVEDA A. Reverse solar envelope method...",
        "THORING K, HUETTEMANN S, MUELLER R M. The augmented designer...",
        "JAKUBIK J, et al. Designing a human-in-the-loop system...",
        "RAFSANJANI H N, NABIZADEH A H. Towards human-centered AI...",
        "KANTERS J, WALL M. The impact of urban design decisions...",
        "WARD G J. The RADIANCE lighting simulation and rendering system...",
        "REINHART C F, WALKENHORST O. Validation of dynamic RADIANCE-based daylight simulations...",
        "NABIL A, MARDALJEVIC J. Useful daylight illuminances...",
        "REINHART C F, MARDALJEVIC J, ROGERS Z. Dynamic daylight performance metrics...",
        "MARDALJEVIC J. Simulation of annual daylighting profiles...",
        "ATTIA S, et al. Assessing gaps and needs...",
        "NGUYEN A T, REITER S, RIGO P. A review on simulation-based optimization...",
        "WORTMANN T. Opossum...",
        "BILAL M, et al. Big Data in the construction industry...",
        "SACKS R, EASTMAN C, LEE G, TEICHOLZ P. BIM Handbook...",
    ]
    for i, ref_text in enumerate(refs, start=1):
        ref_rows.append(
            {
                "index": i,
                "reference_short": ref_text,
                "body_citation_checked": "未完成",
                "bibliographic_verified": "未完成",
                "action": "定稿前需逐条联网核验；本轮因核心实验未达定稿门槛，未进入投稿级参考文献审计。",
            }
        )
    ref_rows[14]["bibliographic_verified"] = "部分核验"
    ref_rows[14]["action"] = "Ward 1994 页码需从旧稿 459-466 修正为 459-472 后再最终核验。"
    pd.DataFrame(ref_rows).to_csv(RESULTS / "80_参考文献核验表.csv", index=False, encoding="utf-8-sig")
    (DOCS / "81_参考文献修订说明.md").write_text(
        "# 81 参考文献修订说明\n\n本轮未形成可命名为定稿的论文，因此未执行完整投稿级参考文献审计。已记录待办：逐条核验正文引用与参考文献对应关系、DOI、卷期页码；Ward 1994 Radiance 文献页码需重点修正为 459-472 后再核验。\n",
        encoding="utf-8",
    )

    print("honest review docs written")


if __name__ == "__main__":
    main()
