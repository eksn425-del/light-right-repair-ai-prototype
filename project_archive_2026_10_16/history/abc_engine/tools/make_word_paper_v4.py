from __future__ import annotations

import csv
import os
import re
from pathlib import Path

from PIL import Image
from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt


def east_asia(run, font_name: str = "宋体") -> None:
    run.font.name = font_name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font_name)


def set_style_font(doc: Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = "宋体"
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    normal.font.size = Pt(11)
    for style_name, size in [("Title", 18), ("Heading 1", 15), ("Heading 2", 13)]:
        style = doc.styles[style_name]
        style.font.name = "黑体"
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
        style.font.size = Pt(size)
        style.font.bold = True


def add_body_paragraph(doc: Document, text: str) -> None:
    p = doc.add_paragraph(style="Normal")
    p.paragraph_format.first_line_indent = Cm(0.74)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text)
    east_asia(r)


def add_caption(doc: Document, text: str, table: bool = False) -> None:
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(8)
    r = p.add_run(text)
    east_asia(r)
    r.font.size = Pt(10)
    r.bold = table


def add_image(doc: Document, path: Path, width_cm: float = 14.0) -> None:
    if not path.exists() or path.stat().st_size == 0:
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Cm(width_cm))


def set_cell_shading(cell, fill: str = "D9EAF7") -> None:
    props = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    props.append(shading)


def set_cell_text(cell, value: str, bold: bool = False) -> None:
    cell.text = ""
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(str(value))
    east_asia(r)
    r.font.size = Pt(9)
    r.bold = bold


def add_csv_table(
    doc: Document,
    caption: str,
    csv_path: Path,
    headers: list[str],
    keys: list[str],
    ratio_keys: set[str] | None = None,
) -> None:
    ratio_keys = ratio_keys or set()
    add_caption(doc, caption, table=True)
    rows = list(csv.DictReader(csv_path.open("r", encoding="utf-8")))
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    for i, header in enumerate(headers):
        set_cell_text(table.rows[0].cells[i], header, bold=True)
        set_cell_shading(table.rows[0].cells[i])
    for row in rows:
        cells = table.add_row().cells
        for i, key in enumerate(keys):
            value = row.get(key, "")
            if key in ratio_keys and value:
                value = f"{float(value) * 100:.2f}%"
            set_cell_text(cells[i], value)


def convert_first_bmp(src_dir: Path, out_path: Path) -> Path | None:
    files = sorted(src_dir.glob("*.bmp"))
    if not files:
        return None
    img = Image.open(files[0]).convert("RGB")
    img.save(out_path)
    return out_path


def main() -> None:
    root = Path(os.environ["WORKPKG"])
    draft = root / "01_论文初稿" / "论文初稿_v3_科研写作skills版_2026-06-03.md"
    out = root / "01_论文初稿" / "论文初稿_v4_Word排版版_含图表参考文献_2026-06-03.docx"
    fig_dir = root / "04_图表与光照复核"
    table_dir = root / "03_核心数据表"
    asset_dir = fig_dir / "论文插图_排版用"
    asset_dir.mkdir(exist_ok=True)

    before_png = convert_first_bmp(fig_dir / "同视角人工光照复核_2026-06-03" / "算法前", asset_dir / "manual_validation_before_view1.png")
    after_png = convert_first_bmp(fig_dir / "同视角人工光照复核_2026-06-03" / "算法后", asset_dir / "manual_validation_after_view1.png")

    text = draft.read_text(encoding="utf-8")
    text = re.sub(r"## 8 图表建议[\s\S]*?## 参考文献", "", text)
    text = re.sub(r"## 参考文献[\s\S]*$", "", text).strip()

    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.8)
    section.right_margin = Cm(2.8)
    set_style_font(doc)

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
        if line.startswith("# "):
            p = doc.add_paragraph(line[2:].strip(), style="Title")
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif line.startswith("## "):
            title = line[3:].strip()
            p = doc.add_paragraph(title, style="Heading 1")
            p.paragraph_format.space_before = Pt(12)
        elif line.startswith("### "):
            p = doc.add_paragraph(line[4:].strip(), style="Heading 2")
            p.paragraph_format.space_before = Pt(10)
        else:
            add_body_paragraph(doc, line)

    doc.add_paragraph("8 图表与表格", style="Heading 1")
    add_image(doc, fig_dir / "algorithm_heatmap.png")
    add_caption(doc, "图 1 现状采光热力图。该图展示 baseline 状态下场地冬至日简化采光诊断结果，用于定位整体暗区分布。")
    add_image(doc, fig_dir / "strategy_comparison_chart.png")
    add_caption(doc, "图 2 三类 AI 策略指标对比。该图比较 baseline、保守型、均衡型与采光优先型策略的核心指标。")
    add_image(doc, fig_dir / "grid_sensitivity_chart_partial.png")
    add_caption(doc, "图 3 网格敏感性测试结果。该图比较 6m 与 3m 网格下采光诊断与候选结果的变化。")
    if before_png:
        add_image(doc, before_png)
        add_caption(doc, "图 4 算法前同视角人工光照分析图。")
    if after_png:
        add_image(doc, after_png)
        add_caption(doc, "图 5 算法后同视角人工光照复核图。算法后模型保留完整场地，仅调整 C6 与 C33。")

    add_csv_table(
        doc,
        "表 1 baseline 与三类 AI 策略对比指标",
        table_dir / "strategy_comparison_metrics.csv",
        ["方案类型", "平均采光小时", "暗区比例", "干预体量", "涉及建筑", "保护冲突"],
        ["scheme_type", "average_sunlight_hours", "dark_zone_ratio", "intervention_volume", "changed_building_ids", "protected_conflict_count"],
        {"dark_zone_ratio"},
    )
    add_csv_table(
        doc,
        "表 2 6m 与 3m 网格敏感性测试结果",
        table_dir / "grid_sensitivity_metrics_partial.csv",
        ["网格尺寸", "现状平均采光小时", "现状暗区比例", "方案后平均采光小时", "方案后暗区比例", "改善比例", "候选建筑"],
        ["grid_size_m", "baseline_average_sunlight_hours", "baseline_dark_zone_ratio", "post_average_sunlight_hours", "post_dark_zone_ratio", "dark_zone_improvement_ratio", "changed_building_ids"],
        {"baseline_dark_zone_ratio", "post_dark_zone_ratio", "dark_zone_improvement_ratio"},
    )

    add_caption(doc, "表 3 保守型方案中 C6、C33 的高度变化与设计转译", table=True)
    table = doc.add_table(rows=1, cols=5)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    for i, header in enumerate(["建筑编号", "原高度/m", "算法后高度/m", "削减高度/m", "设计转译"]):
        set_cell_text(table.rows[0].cells[i], header, True)
        set_cell_shading(table.rows[0].cells[i])
    for row in [
        ["C6", "6.0", "4.5", "1.5", "屋顶边缘退台、屋顶平台、采光缝。"],
        ["C33", "9.0", "6.75", "2.25", "二层以上局部退台、转角采光缝、口袋灰空间。"],
    ]:
        cells = table.add_row().cells
        for i, value in enumerate(row):
            set_cell_text(cells[i], value)

    doc.add_paragraph("9 参考文献", style="Heading 1")
    refs = [
        "[1] CZACHURA A, KANTERS J, GENTILE N, 等. Solar performance metrics in urban planning: a review and taxonomy[J]. Buildings, 2022, 12(4): 393. DOI: 10.3390/buildings12040393.",
        "[2] COMPAGNON R. Solar and daylight availability in the urban fabric[J]. Energy and Buildings, 2004, 36(4): 321-328. DOI: 10.1016/j.enbuild.2004.01.009.",
        "[3] ALLEGRINI J, DORER V, CARMELIET J. Review of the impact of urban block form on thermal performance, solar access and ventilation[J]. Renewable and Sustainable Energy Reviews, 2015, 38: 551-560. DOI: 10.1016/j.rser.2014.06.007.",
        "[4] CURRELI A, SERRA-COCH G, ISALGUE A, 等. Solar energy as a form giver for future cities[J]. Energies, 2016, 9(7): 544. DOI: 10.3390/en9070544.",
        "[5] KONIS K, GAMAS A, KENSEK K. Passive performance and building form: an optimization framework for early-stage design support[J]. Solar Energy, 2016, 125: 161-179. DOI: 10.1016/j.solener.2015.12.020.",
        "[6] WANG L, 等. Optimization-based design exploration of building massing typologies: EvoMass and a typology-oriented computational design optimization method for early-stage performance-based building massing design[J]. Frontiers of Architectural Research, 2024, 13(6): 1400-1422. DOI: 10.1016/j.foar.2024.06.001.",
        "[7] SADEGHIPOUR ROUDSARI M, PAK M. Ladybug: a parametric environmental plugin for Grasshopper to help designers create an environmentally-conscious design[C]//Proceedings of BS2013. 2013.",
        "[8] DE LUCA F, 等. Reverse solar envelope method: a new building form-finding method that can take regulatory frameworks into account[J]. Automation in Construction, 2021, 123: 103518. DOI: 10.1016/j.autcon.2020.103518.",
        "[9] THORING K, HUETTEMANN S, MUELLER R M. The augmented designer: a research agenda for generative AI-enabled design[C]//Proceedings of the Design Society. 2023, 3: 3345-3354. DOI: 10.1017/pds.2023.335.",
        "[10] JAKUBIK J, HEMMER P, VÖSSING M, 等. Designing a human-in-the-loop system for object detection in floor plans[J]. Proceedings of the AAAI Conference on Artificial Intelligence, 2022, 36(11): 12524-12530. DOI: 10.1609/aaai.v36i11.21522.",
        "[11] RAFSANJANI H N, NABIZADEH A H. Towards human-centered artificial intelligence (AI) in architecture, engineering, and construction (AEC) industry[J]. Computers in Human Behavior Reports, 2023, 11: 100319. DOI: 10.1016/j.chbr.2023.100319.",
    ]
    for ref in refs:
        p = doc.add_paragraph(style="Normal")
        p.paragraph_format.left_indent = Cm(0.74)
        p.paragraph_format.first_line_indent = Cm(-0.74)
        p.paragraph_format.line_spacing = 1.25
        r = p.add_run(ref)
        east_asia(r)
        r.font.size = Pt(10)

    doc.save(out)
    print(out)


if __name__ == "__main__":
    main()
