from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd
from docx import Document
from docx.shared import Inches, Pt
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


ROOT = Path(r"E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20")
MOTHER = Path(r"C:\Users\洪禄\Desktop\光权修复论文_EI会议_最终排版版.docx")
RESULTS = ROOT / "results_csv"
FIGURES = ROOT / "figures"
DOCS = ROOT / "docs"

PAPER_DOCX = ROOT / "光权修复论文_EI会议_中文导师审阅定稿版.docx"
PAPER_PDF = ROOT / "光权修复论文_EI会议_中文导师审阅定稿版.pdf"
SUMMARY_DOCX = ROOT / "导师阅读摘要_一页版_定稿.docx"
CHANGE_DOCX = ROOT / "修改说明与新增实验清单_定稿.docx"
GEOM_DOCX = ROOT / "模型几何一致性审计报告.docx"
HB_DOCX = ROOT / "HB-Radiance正式验证报告.docx"
FINAL_DOCX = ROOT / "最终候选判断说明.docx"
SELFCHECK = ROOT / "投稿前自检报告_定稿.md"
README = ROOT / "README.md"
REQ = ROOT / "requirements.txt"


def clear_doc(doc: Document):
    body = doc._body._element
    for child in list(body):
        if child.tag.endswith("sectPr"):
            continue
        body.remove(child)


def set_font(paragraph, size=10.5, bold=None):
    for run in paragraph.runs:
        run.font.name = "SimSun"
        run.font.size = Pt(size)
        if bold is not None:
            run.bold = bold


def add_p(doc: Document, text: str, size=10.5, style=None):
    p = doc.add_paragraph(style=style)
    p.add_run(text)
    set_font(p, size=size)
    return p


def add_h(doc: Document, text: str, level=1):
    p = doc.add_paragraph()
    p.add_run(text)
    set_font(p, size=12 if level == 1 else 11, bold=True)
    return p


def add_table_docx(doc: Document, df: pd.DataFrame, columns: list[str], headers: list[str]):
    table = doc.add_table(rows=1, cols=len(columns))
    try:
        table.style = "Table Grid"
    except KeyError:
        pass
    for i, h in enumerate(headers):
        table.rows[0].cells[i].text = h
    for _, row in df.iterrows():
        cells = table.add_row().cells
        for i, col in enumerate(columns):
            value = row[col]
            if isinstance(value, float):
                cells[i].text = f"{value:.3f}"
            else:
                cells[i].text = str(value)
    return table


def add_picture_if_exists(doc: Document, path: Path, caption: str):
    if path.exists():
        doc.add_picture(str(path), width=Inches(3.35))
        add_p(doc, caption, size=9)


def build_paper():
    rule = pd.read_csv(RESULTS / "132_HB_Radiance已复核候选排名与Pareto.csv")
    final = pd.read_csv(RESULTS / "138_最终候选规则与设计转译对比.csv")
    metrics = pd.read_csv(RESULTS / "144_已复核TopK召回与Pareto重叠.csv")

    doc = Document(str(MOTHER))
    clear_doc(doc)
    add_p(doc, "旧街区早期更新中的直射日照可达性诊断与低干预候选生成：规则启发式工作流研究", size=15)
    add_p(doc, "——以厦门灌口沿湖休闲片区为例", size=13)
    add_p(doc, "作者姓名：洪禄", size=10.5)
    add_p(
        doc,
        "摘  要：本文针对旧街区早期更新中低直射日照区定位、低干预候选筛选和结果复核困难的问题，构建了“规范几何统一—2.5D 规则诊断—候选枚举—HB-Radiance 正式三维复核—设计师复核”的工作流。研究以厦门灌口沿湖休闲片区 C1—C45 建筑数据为对象，先对 CSV、DXF、OBJ 与旧 Ladybug-ready 模型进行坐标、尺度、编号和高度审计，建立 canonical_site_v2；再在统一冬至日、3 m 地面传感点、30 分钟时间步长和相同掩膜条件下枚举双建筑低干预减高候选。结果表明，旧 C6/C33 方案在正式三维复核下收益较小，不能作为唯一最终方案；C13/C24 虽为正向候选，但在追加复核集合中不处于 HB-Radiance Pareto 前沿。最终建议将 C9/C15 与 C9/C13 作为经正式三维复核和设计转译复算后较稳健的优先候选区间，C9/C24 作为高收益但需重点复核的候选。本研究输出的是早期候选筛查与设计师复核依据，不替代专业日照审查、室内照度模拟或法定合规报告。",
        size=9.5,
    )
    add_p(doc, "关键词：旧街区更新；直射日照可达性；规则启发式；候选生成；HB-Radiance；设计师复核", size=9.5)

    add_h(doc, "1 引言")
    add_p(doc, "旧街区更新中的公共空间环境品质往往受高密度建筑、狭窄街巷和多层级体量遮挡影响。早期方案阶段需要快速判断低直射日照区在哪里、哪些建筑局部调整可能有效、以及候选是否值得设计师继续复核。过早进入专业日照审查或室内照度模拟会增加建模成本，而仅凭经验又难以比较不同候选。本文将原项目内部简称“光权修复”降级为背景性称呼，并明确其不等同于法律意义上的日照权裁定。")
    add_p(doc, "本文研究问题收敛为三点：第一，如何把 CAD/SKP/OBJ/DXF/CSV 调研资料统一成可计算的规范几何；第二，如何在低干预约束下生成可比较的直射日照候选；第三，如何用正式三维参考模拟和设计师复核避免把规则模型输出误读为唯一最优方案。")

    add_h(doc, "2 规范几何与数据来源")
    add_p(doc, "本轮以原始 SKP/DXF 与 buildings.csv 为优先依据，建立 canonical_site_v2。DXF 到规范坐标采用 x=dxf_x_mm/1000-317.890127、y=dxf_y_mm/1000-2426.142342；OBJ 检查采用 x=obj_x_mm/1000-191.792、y=-obj_z_mm/1000-95.982、z=obj_y_mm/1000。审计显示 C6、C33、C13、C24 在旧 OBJ/CSV/DXF 间存在 footprint 或质心差异，因此旧 Ladybug-ready OBJ 不再作为正式验证输入。")
    add_picture_if_exists(doc, FIGURES / "93_全场几何叠加核对图.png", "图1  全场规范几何叠加核对。图表说明：本图用于证明旧模型与规范模型之间存在需要说明的几何差异。")

    add_h(doc, "3 方法")
    add_h(doc, "3.1 直射日照诊断", 2)
    add_p(doc, "算法 A 计算地面传感点在冬至日指定时段内获得的直射日照时长。统一参数为厦门灌口近似经纬度 24.55°N、118.03°E，Asia/Shanghai 时区，冬至日 08:15—15:45，30 分钟步长，3 m 地面网格，传感点高度 0.1 m，低直射日照阈值 2 h、3 h 和 4 h，其中 3 h 作为主结果。")
    add_h(doc, "3.2 候选生成与体量口径", 2)
    add_p(doc, "算法 B 仅保留低干预减高/退台候选，不再把 add、reorganize 写作主实验操作。规则高度为 h_new=max(3 m, h-min(3 m,0.25h))。所有干预体量统一为真实 m³，即 footprint 面积乘以高度削减量。旧稿中的 28.125 不再作为真实体量使用。")
    add_h(doc, "3.3 正式三维参考模拟", 2)
    add_p(doc, "正式参考采用 Honeybee/LBT direct-sun-hours recipe 与 Radiance 6.0.2 命令行路径。Rhino/Grasshopper GUI 本机未检出，未伪造截图或 .gh 文件。HB-Radiance 与 Python 2.5D 使用同一规范几何、同一传感点、同一时段、同一时间步长和同一掩膜。")

    add_h(doc, "4 结果")
    add_h(doc, "4.1 全候选枚举与追加复核", 2)
    add_p(doc, "在 canonical_site_v2 下，合法可减高建筑为 36 栋，共生成 C(36,2)=630 个双建筑候选。根据 2.5D Top10、非零 Pareto、C6/C33、C13/C24、高度优先基线和低日照邻近基线形成 23 个去重规则候选，并全部完成 HB-Radiance 追加复核。")
    add_picture_if_exists(doc, FIGURES / "133_HB_Radiance_Top候选Pareto图.png", "图2  HB-Radiance 已复核候选 Pareto 分布。图表说明：本图证明最终判断应基于三维复核后的体量—收益关系。")
    add_table_docx(
        doc,
        rule.head(10),
        ["pair_key", "rank_hb_low_area_drop", "low_area_drop_h3_m2", "avg_gain_vs_baseline_h", "intervention_volume_m3", "is_hb_pareto_front"],
        ["候选", "HB排名", "低日照下降/m²", "均值提升/h", "体量/m³", "HB Pareto"],
    )
    add_p(doc, "表1  HB-Radiance 已复核规则候选 Top10。图表说明：本表用于证明 C9 相关候选在正式三维复核中整体优于旧 C6/C33 与 C13/C24。", size=9)

    add_h(doc, "4.2 2.5D 与 HB-Radiance 一致性", 2)
    add_p(doc, "在 23 个已复核规则候选中，2.5D 排名与 HB-Radiance 低日照面积下降排名 Spearman rho 为 0.883，p=2.35e-08。Top3 召回为 0.667，Top5 召回为 0.4，Top10 召回为 0.8；HB Pareto 与 2.5D Pareto 在已复核集合中重叠数为 12。该结果说明规则模型可用于早期缩小候选范围，但不能自动给出唯一最优方案。")
    add_table_docx(doc, metrics, ["K", "topK_overlap_count", "topK_recall"], ["K", "重叠数", "召回率"])
    add_picture_if_exists(doc, FIGURES / "145_已复核模型分歧图组.png", "图3  已复核候选的模型分歧图组。图表说明：本图证明统一几何后总体趋势一致，但低体量候选排序仍需三维复核。")

    add_h(doc, "4.3 规则模型与设计转译复算", 2)
    add_p(doc, "对最终候选建立两类几何：A 为规则整体减高模型；B 为保留底层街巷界面的上部退台设计转译模型。C9/C15 与 C9/C13 在设计转译后仍保持正向改善，且没有新增低日照区或恶化点；C9/C24 在规则模型中收益最高，但设计转译后出现 4 个恶化点和 9 m² 新增低日照区，因此降级为高收益但需重点复核候选。")
    add_table_docx(
        doc,
        final,
        ["pair_key", "final_status", "rule_low_area_drop_h3_m2", "design_low_area_drop_h3_m2", "design_worsened_point_count", "design_new_low_area_h3_m2"],
        ["候选", "判断", "规则下降/m²", "设计下降/m²", "设计恶化点", "新增低日照/m²"],
    )
    add_picture_if_exists(doc, FIGURES / "139_最终候选规则与设计转译对比图.png", "图4  最终候选规则模型与设计转译模型对比。图表说明：本图证明规则模型效果不能直接等同于建筑设计转译效果。")

    add_h(doc, "5 讨论")
    add_p(doc, "本轮结果推翻了旧稿中把 C6/C33 作为唯一保守型推荐的写法。C6/C33 在 HB-Radiance 下 3 h 低直射日照区面积仅下降 9 m²，设计转译后下降 18 m²，属于正向但收益较小的历史对照。C13/C24 也不应被规则模型结果直接替换为新唯一方案；它在正式三维复核中正向，但追加复核后不在 HB Pareto 前沿。")
    add_p(doc, "最终更诚实的论文定位是：该工作流在统一输入条件下提供可复核的低直射日照候选筛查能力，其价值在于缩小设计师需要重点复核的候选范围，而非替代专业环境模拟或自动给出唯一最优方案。结构、产权、功能置换、施工可行性和法定日照审查仍需后续专业流程处理。")

    add_h(doc, "6 结论")
    add_p(doc, "本文完成了从几何审计、规则模型重跑、正式 HB-Radiance 复核到设计转译复算的中文收敛。结果支持将 C9/C15 与 C9/C13 写为优先候选区间，将 C9/C24 写为高收益但需重点复核候选；C13/C24 与 C6/C33 保留为方法演进中的对照。该结论仅适用于本轮 canonical_site_v2、冬至日、3 m 地面传感网格和已完成三维复核的候选集合。")
    add_h(doc, "参考文献")
    refs = [
        "[1] CZACHURA A, KANTERS J, GENTILE N, WALL M. Solar Performance Metrics in Urban Planning: A Review and Taxonomy[J]. Buildings, 2022, 12(4): 393.",
        "[2] COMPAGNON R. Solar and daylight availability in the urban fabric[J]. Energy and Buildings, 2004, 36(4): 321-328.",
        "[3] SADEGHIPOUR ROUDSARI M, PAK M, VIOLA A. Ladybug: A parametric environmental plugin for Grasshopper[C]//BS2013. 2013: 3128-3135.",
        "[4] WARD G J. The RADIANCE lighting simulation and rendering system[C]//SIGGRAPH 1994: 459-472.",
        "[5] REINHART C F, WALKENHORST O. Validation of dynamic RADIANCE-based daylight simulations[J]. Energy and Buildings, 2001, 33(7): 683-697.",
        "[6] NGUYEN A T, REITER S, RIGO P. A review on simulation-based optimization methods applied to building performance analysis[J]. Applied Energy, 2014, 113: 1043-1058.",
    ]
    for ref in refs:
        add_p(doc, ref, size=9)
    doc.save(PAPER_DOCX)


def simple_docx(path: Path, title: str, paragraphs: list[str], tables: list[tuple[pd.DataFrame, list[str], list[str], str]] | None = None):
    doc = Document()
    add_p(doc, title, size=15)
    for text in paragraphs:
        if text.startswith("# "):
            add_h(doc, text[2:], 1)
        elif text.startswith("## "):
            add_h(doc, text[3:], 2)
        else:
            add_p(doc, text)
    if tables:
        for df, cols, headers, caption in tables:
            add_table_docx(doc, df, cols, headers)
            add_p(doc, caption, size=9)
    doc.save(path)


def build_aux_docs():
    final = pd.read_csv(RESULTS / "138_最终候选规则与设计转译对比.csv")
    rule = pd.read_csv(RESULTS / "132_HB_Radiance已复核候选排名与Pareto.csv")
    geom = pd.read_csv(RESULTS / "91_建筑几何一致性总表.csv")

    simple_docx(
        SUMMARY_DOCX,
        "导师阅读摘要_一页版_定稿",
        [
            "这篇研究解决的问题：在旧街区早期更新中，如何把分散的 CAD/SKP/OBJ/DXF/CSV 资料转成可复核的直射日照诊断输入，并筛出值得设计师重点复核的低干预候选。",
            "原论文不足：旧稿把 C6/C33 写得过于接近最终推荐，体量口径混用，缺少正式三维参考模拟，也没有充分说明旧 OBJ、CSV、DXF 之间的几何差异。",
            "本次补充：建立 canonical_site_v2；完成 630 个双建筑候选 2.5D 枚举；完成 23 个 Top/Pareto/基线候选 HB-Radiance 复核；对 C9/C15、C9/C13、C9/C24 做设计转译复算；统一体量为 m³。",
            "最终真实证明：C9/C15 与 C9/C13 是更稳健的优先候选区间；C9/C24 收益高但设计转译后需复核；C13/C24 和 C6/C33 不应作为最终唯一方案。",
            "当前边界：不替代法定日照审查；没有完成全部 630 个候选的 HB 复核；Rhino/Grasshopper GUI 未运行；结构、产权、功能和施工可行性尚未纳入。",
            "投稿价值：具备进一步投稿潜力，但建议在导师审阅后补齐 GUI 或第三方复核、网格原点/尺度扩展图表和参考文献逐条 DOI 核验。",
        ],
    )
    simple_docx(
        CHANGE_DOCX,
        "修改说明与新增实验清单_定稿",
        [
            "本轮将论文定位从“光权修复/采光优化”改为“旧街区早期更新中的直射日照可达性诊断与低干预候选筛查”。",
            "新增实验包括：几何一致性审计、canonical_site_v2 规范模型、2.5D 全候选枚举、HB-Radiance 关键场景与追加 Top/Pareto 场景、最终设计转译场景、2.5D 与 HB 排名一致性分析。",
            "删除或降级旧表述：不再宣称 C6/C33 为唯一最终方案；不再使用 28.125 作为真实体量；不再把人工同视角光照图写作独立数值验证。",
        ],
        tables=[(final, ["pair_key", "final_status", "rule_low_area_drop_h3_m2", "design_low_area_drop_h3_m2"], ["候选", "判断", "规则下降/m²", "设计下降/m²"], "表1  最终候选判断摘要。")],
    )
    simple_docx(
        GEOM_DOCX,
        "模型几何一致性审计报告",
        [
            "几何审计发现，旧 OBJ、CSV、DXF 在关键建筑上存在 footprint 与质心差异。旧 Ladybug-ready OBJ 不再作为正式验证输入。",
            "本轮采用 DXF component bbox union 与 CSV 高度/属性建立 canonical_site_v2，统一单位为米，统一 Z 为竖向。",
            "该处理仍有边界：DXF 线框并非完整闭合真实建筑轮廓，因此 canonical_site_v2 是本轮可复现规范模型，不等同于现场测绘模型。",
        ],
        tables=[
            (
                geom[geom["building_id"].isin(["C6", "C33", "C13", "C24"])],
                ["building_id", "centroid_distance_m", "height_difference_m", "footprint_overlap_iou"],
                ["建筑", "质心差/m", "高差/m", "IoU"],
                "表1  关键建筑几何一致性审计。",
            )
        ],
    )
    simple_docx(
        HB_DOCX,
        "HB-Radiance正式验证报告",
        [
            "正式参考模拟采用 Honeybee/LBT direct-sun-hours recipe 与 Radiance 6.0.2，统一 3 m 地面传感点、冬至日 08:15—15:45、30 分钟步长和 sensor height 0.1 m。",
            "23 个已复核规则候选中，C9/C24、C9/C15、C9/C13 等 C9 相关候选表现较好；2.5D 与 HB-Radiance 排名 Spearman rho 为 0.883。",
            "C6/C33 在正式三维复核下收益较小；C13/C24 正向但不在 HB Pareto 前沿。",
        ],
        tables=[(rule.head(12), ["pair_key", "rank_hb_low_area_drop", "low_area_drop_h3_m2", "intervention_volume_m3", "is_hb_pareto_front"], ["候选", "排名", "下降/m²", "体量/m³", "Pareto"], "表1  HB-Radiance 已复核候选排名。")],
    )
    simple_docx(
        FINAL_DOCX,
        "最终候选判断说明",
        [
            "最终不输出唯一最优方案，而输出经正式三维复核的候选区间。",
            "优先候选区间：C9/C15 与 C9/C13。两者均在 HB Pareto 前沿，设计转译后仍正向，且无新增低日照区和无恶化点。",
            "高收益复核候选：C9/C24。规则模型收益最高，但设计转译后出现少量恶化点和新增低日照区。",
            "历史对照：C13/C24 与 C6/C33。它们可用于说明方法演进，但不作为最终优先候选。",
        ],
        tables=[(final, ["pair_key", "final_status", "reason"], ["候选", "最终状态", "理由"], "表1  最终候选取舍。")],
    )


def build_pdf():
    pdfmetrics.registerFont(TTFont("SimHei", r"C:\Windows\Fonts\simhei.ttf"))
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="CN", fontName="SimHei", fontSize=9, leading=13))
    styles.add(ParagraphStyle(name="CNTitle", fontName="SimHei", fontSize=15, leading=20, spaceAfter=8))
    story = [
        Paragraph("旧街区早期更新中的直射日照可达性诊断与低干预候选生成", styles["CNTitle"]),
        Paragraph("中文导师审阅定稿版 PDF（由 Python/reportlab 生成，非 Word 原生导出）", styles["CN"]),
        Spacer(1, 5 * mm),
    ]
    final = pd.read_csv(RESULTS / "138_最终候选规则与设计转译对比.csv")
    paras = [
        "摘要：本文建立 canonical_site_v2，完成 630 个 2.5D 候选枚举、23 个 HB-Radiance 规则候选复核和 3 个最终候选设计转译复算。结果支持 C9/C15 与 C9/C13 作为优先候选区间，C9/C24 作为高收益但需重点复核候选。",
        "方法边界：本研究是早期候选筛查与设计师复核依据，不替代专业日照审查、室内照度模拟或法定合规报告。",
    ]
    for para in paras:
        story.append(Paragraph(para, styles["CN"]))
        story.append(Spacer(1, 3 * mm))
    table_data = [["候选", "状态", "规则下降", "设计下降", "恶化点", "新增低日照"]]
    for _, r in final.iterrows():
        table_data.append([
            r["pair_key"],
            r["final_status"],
            f"{r['rule_low_area_drop_h3_m2']:.0f}",
            f"{r['design_low_area_drop_h3_m2']:.0f}",
            f"{r['design_worsened_point_count']:.0f}",
            f"{r['design_new_low_area_h3_m2']:.0f}",
        ])
    tbl = Table(table_data, repeatRows=1)
    tbl.setStyle(TableStyle([("FONTNAME", (0, 0), (-1, -1), "SimHei"), ("GRID", (0, 0), (-1, -1), 0.25, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey)]))
    story.append(tbl)
    SimpleDocTemplate(str(PAPER_PDF), pagesize=A4, rightMargin=18 * mm, leftMargin=18 * mm, topMargin=18 * mm, bottomMargin=18 * mm).build(story)


def build_readme_and_selfcheck():
    REQ.write_text(
        "\n".join(
            [
                "numpy==1.26.4",
                "pandas==2.3.3",
                "scipy==1.17.1",
                "matplotlib==3.10.8",
                "shapely==2.1.2",
                "pvlib==0.15.2",
                "python-docx==1.2.0",
                "reportlab==4.4.10",
                "ladybug-core==0.44.52",
                "ladybug-geometry==1.35.1",
                "honeybee-core==1.64.54",
                "honeybee-radiance==1.66.273",
                "honeybee-radiance-command==1.23.0",
                "lbt-recipes==0.28.2",
            ]
        ),
        encoding="utf-8",
    )
    README.write_text(
        "\n".join(
            [
                "# 路线B中文导师审阅定稿工作包",
                "",
                "运行顺序：",
                "1. `code/route_b_geometry_audit.py`",
                "2. `code/route_b_prepare_hb_batch.py` 后运行 `lbt-recipes run direct-sun-hours`",
                "3. `code/route_b_enumerate_2p5d_candidates.py`",
                "4. `code/route_b_prepare_hb_extra_candidates.py` 后运行追加 HB 批处理",
                "5. `code/route_b_prepare_hb_final_design_candidates.py` 后运行设计转译 HB 批处理",
                "6. `code/route_b_collect_hb_merged_results.py`",
                "7. `code/route_b_final_candidate_judgement.py`",
                "8. `code/generate_route_b_deliverables.py`",
                "",
                "随机种子：20260620。正式候选判断以 `results_csv/138_最终候选规则与设计转译对比.csv` 为准。",
            ]
        ),
        encoding="utf-8",
    )
    SELFCHECK.write_text(
        "\n".join(
            [
                "# 投稿前自检报告_定稿",
                "",
                "## 已满足",
                "",
                "- 已建立 canonical_site_v2，并记录 DXF/OBJ 到规范坐标的转换。",
                "- 已完成 Honeybee/LBT direct-sun-hours + Radiance 6.0.2 正式命令行模拟。",
                "- 已完成 23 个 2.5D Top/Pareto/基线候选的 HB-Radiance 追加复核。",
                "- 已完成 C9/C15、C9/C13、C9/C24 的设计转译复算。",
                "- 结论已从唯一方案改为经正式三维复核的候选区间。",
                "",
                "## 未完全满足或需导师知情",
                "",
                "- Rhino/Grasshopper GUI 未在本机检出，未生成真实 .gh 文件或 GUI 截图。",
                "- PDF 由 reportlab 生成，不是 Word/LibreOffice 对主 Word 的原生排版导出。",
                "- 未对全部 630 个双建筑候选运行 HB-Radiance，仅对预注册 Top10、非零 Pareto、旧候选和基线共 23 个规则候选复核。",
                "- 结构、产权、功能置换、施工可行性和法定日照审查未纳入。",
                "- 参考文献尚建议导师审阅后逐条补 DOI/页码核验；Ward 1994 页码已改为 459-472。",
                "",
                "## 当前最诚实论文定位",
                "",
                "适合作为中文导师审阅定稿版，用于说明研究主线、真实数据、正式复核结果和方法边界；不建议未经进一步排版、参考文献和第三方复核直接投稿。",
            ]
        ),
        encoding="utf-8",
    )


def main():
    build_paper()
    build_aux_docs()
    build_pdf()
    build_readme_and_selfcheck()
    print(PAPER_DOCX)
    print(PAPER_PDF)


if __name__ == "__main__":
    main()
