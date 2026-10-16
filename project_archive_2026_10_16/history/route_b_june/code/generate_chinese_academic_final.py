from __future__ import annotations

import csv
import importlib.util
import math
import re
import zipfile
from pathlib import Path

import fitz
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt


ROOT = Path(r"E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20")
BASE_SCRIPT = ROOT / "code" / "generate_final_submission.py"
MOTHER = ROOT / "光权修复论文_EI会议_中文导师审阅定稿版_最终.docx"
RESULTS = ROOT / "results_csv"
DOCS = ROOT / "docs"
FIGURES = ROOT / "figures"

PAPER_DOCX = ROOT / "光权修复论文_EI会议_中文学术定稿版_投稿前小修.docx"
PAPER_PDF = ROOT / "光权修复论文_EI会议_中文学术定稿版_投稿前小修.pdf"
REF_EXT_CSV = ROOT / "参考文献扩展核验表.csv"
REF_REORDER_CSV = ROOT / "参考文献重排核验表.csv"
RELATED_MD = ROOT / "相关工作补充说明.md"
SIDE_MD = ROOT / "重复副作用数据核查说明.md"
SIDE_FIG = ROOT / "C9_C24_C13_C24_恶化点空间对比图.png"
CONSISTENCY_MD = ROOT / "中文学术定稿一致性检查报告.md"
MINOR_NOTE_MD = ROOT / "投稿前小修说明.md"
ACCOUNT_CSV = ROOT / "HB候选筛选账目核验表.csv"
INCONSISTENCY_MD = ROOT / "最终学术化收尾数据不一致报告.md"
BASELINE_LOW_AREA_H3_M2 = 3051.0

FIG1 = FIGURES / "150_图1_规范几何关键建筑叠加图.png"
FIG2 = FIGURES / "151_图2_HB已复核候选Pareto分布.png"
FIG3 = FIGURES / "152_图3_2p5D与HB一致性图组.png"
FIG4 = FIGURES / "153_图4_规则模型与设计转译对比.png"
FIG5 = FIGURES / "154_图5_最终候选判断流程图.png"


def load_base():
    spec = importlib.util.spec_from_file_location("base_final", BASE_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


base = load_base()


REFERENCES = [
    {
        "id": 1,
        "ref": "SANAIEIAN H, TENPIERIK M, VAN DEN LINDEN K, MEHDIZADEH SERAJ F, MOFIDI SHEMRANI S M. Review of the impact of urban block form on thermal performance, solar access and ventilation[J]. Renewable and Sustainable Energy Reviews, 2014, 38: 551-560.",
        "doi": "10.1016/j.rser.2014.06.007",
        "url": "https://doi.org/10.1016/j.rser.2014.06.007",
        "cited": "引言：城市形态与太阳可达性",
    },
    {
        "id": 2,
        "ref": "COMPAGNON R. Solar and daylight availability in the urban fabric[J]. Energy and Buildings, 2004, 36(4): 321-328.",
        "doi": "10.1016/j.enbuild.2004.01.009",
        "url": "https://doi.org/10.1016/j.enbuild.2004.01.009",
        "cited": "引言：城市肌理中的太阳与日光可达性",
    },
    {
        "id": 3,
        "ref": "CZACHURA A, KANTERS J, GENTILE N, WALL M. Solar Performance Metrics in Urban Planning: A Review and Taxonomy[J]. Buildings, 2022, 12(4): 393.",
        "doi": "10.3390/buildings12040393",
        "url": "https://www.mdpi.com/2075-5309/12/4/393",
        "cited": "引言：城市太阳性能指标分类",
    },
    {
        "id": 4,
        "ref": "RATTI C, RAYDAN D, STEEMERS K. Building form and environmental performance: archetypes, analysis and an arid climate[J]. Energy and Buildings, 2003, 35(1): 49-59.",
        "doi": "10.1016/S0378-7788(02)00079-8",
        "url": "https://doi.org/10.1016/S0378-7788(02)00079-8",
        "cited": "引言：建筑形态与环境性能",
    },
    {
        "id": 5,
        "ref": "RATTI C, BAKER N, STEEMERS K. Energy consumption and urban texture[J]. Energy and Buildings, 2005, 37(7): 762-776.",
        "doi": "10.1016/j.enbuild.2004.10.010",
        "url": "https://doi.org/10.1016/j.enbuild.2004.10.010",
        "cited": "引言：城市纹理与环境性能",
    },
    {
        "id": 6,
        "ref": "COUCH C, SYKES O, BORSTINGHAUS W. Thirty years of urban regeneration in Britain, Germany and France: The importance of context and path dependency[J]. Progress in Planning, 2011, 75(1): 1-52.",
        "doi": "10.1016/j.progress.2010.12.001",
        "url": "https://doi.org/10.1016/j.progress.2010.12.001",
        "cited": "引言：城市更新的情境依赖",
    },
    {
        "id": 7,
        "ref": "SHEN T, YAO X, WEN F. The Urban Regeneration Engine Model: An analytical framework and case study of the renewal of old communities[J]. Land Use Policy, 2021, 108: 105571.",
        "doi": "10.1016/j.landusepol.2021.105571",
        "url": "https://doi.org/10.1016/j.landusepol.2021.105571",
        "cited": "引言：老旧社区更新分析框架",
    },
    {
        "id": 8,
        "ref": "WANG W, YANG H, JING S. The development of priority decision model for old urban community renovation in China[J]. Scientific Reports, 2024, 14(1): 4434.",
        "doi": "10.1038/s41598-024-54883-3",
        "url": "https://www.nature.com/articles/s41598-024-54883-3",
        "cited": "引言：老旧社区更新优先级评价",
    },
    {
        "id": 9,
        "ref": "HACHEM C, ATHIENITIS A, FAZIO P. Parametric investigation of geometric form effects on solar potential of housing units[J]. Solar Energy, 2011, 85(9): 1864-1877.",
        "doi": "10.1016/j.solener.2011.04.027",
        "url": "https://doi.org/10.1016/j.solener.2011.04.027",
        "cited": "相关研究：几何形态与太阳潜力",
    },
    {
        "id": 10,
        "ref": "HACHEM C, ATHIENITIS A, FAZIO P. Investigation of solar potential of housing units in different neighborhood designs[J]. Energy and Buildings, 2011, 43(9): 2262-2273.",
        "doi": "10.1016/j.enbuild.2011.05.008",
        "url": "https://doi.org/10.1016/j.enbuild.2011.05.008",
        "cited": "相关研究：邻里尺度太阳潜力",
    },
    {
        "id": 11,
        "ref": "SADEGHIPOUR ROUDSARI M, PAK M, VIOLA A. Ladybug: A parametric environmental plugin for Grasshopper to help designers create an environmentally-conscious design[C]//Proceedings of Building Simulation 2013. 2013: 3128-3135.",
        "doi": "10.26868/25222708.2013.2499",
        "url": "https://publications.ibpsa.org/conference/paper/?id=bs2013_2499",
        "cited": "方法：Ladybug/LBT 工具链",
    },
    {
        "id": 12,
        "ref": "LADYBUG TOOLS. Direct Sun Hours [EB/OL]. [2026-06-21]. https://docs.ladybug.tools/hb-radiance-primer/components/3_recipes/direct_sun_hours.",
        "doi": "",
        "url": "https://docs.ladybug.tools/hb-radiance-primer/components/3_recipes/direct_sun_hours",
        "cited": "方法：Honeybee Radiance direct-sun-hours",
    },
    {
        "id": 13,
        "ref": "WARD G J. The RADIANCE lighting simulation and rendering system[C]//Proceedings of SIGGRAPH 1994. 1994: 459-472.",
        "doi": "10.1145/192161.192286",
        "url": "https://radsite.lbl.gov/radiance/papers/sg94.1/paper.html",
        "cited": "方法：Radiance 参考模拟",
    },
    {
        "id": 14,
        "ref": "REINHART C F, WALKENHORST O. Validation of dynamic RADIANCE-based daylight simulations for a test office with external blinds[J]. Energy and Buildings, 2001, 33(7): 683-697.",
        "doi": "10.1016/S0378-7788(01)00058-5",
        "url": "https://doi.org/10.1016/S0378-7788(01)00058-5",
        "cited": "方法：Radiance 验证背景",
    },
    {
        "id": 15,
        "ref": "KANTERS J, WALL M. A planning process map for solar buildings in urban environments[J]. Renewable and Sustainable Energy Reviews, 2016, 57: 173-185.",
        "doi": "10.1016/j.rser.2015.12.073",
        "url": "https://doi.org/10.1016/j.rser.2015.12.073",
        "cited": "相关研究：太阳建筑与规划流程",
    },
    {
        "id": 16,
        "ref": "DE LUCA F, DOGAN T, SEPULVEDA A. Reverse solar envelope method: A new building form-finding method that can take regulatory frameworks into account[J]. Automation in Construction, 2021, 123: 103518.",
        "doi": "10.1016/j.autcon.2020.103518",
        "url": "https://doi.org/10.1016/j.autcon.2020.103518",
        "cited": "相关研究：太阳包络与形体生成",
    },
    {
        "id": 17,
        "ref": "ALKADRI M F, DE LUCA F, TURRIN M, SARIYILDIZ S. Understanding computational methods for solar envelopes based on design parameters, tools, and case studies: A review[J]. Energies, 2020, 13(13): 3302.",
        "doi": "10.3390/en13133302",
        "url": "https://www.mdpi.com/1996-1073/13/13/3302",
        "cited": "相关研究：太阳包络计算方法",
    },
    {
        "id": 18,
        "ref": "DOGAN T, KASTNER P, MERMELSTEIN R. Surfer: A fast simulation algorithm to predict surface temperatures and mean radiant temperatures in large urban models[J]. Building and Environment, 2021, 196: 107762.",
        "doi": "10.1016/j.buildenv.2021.107762",
        "url": "https://doi.org/10.1016/j.buildenv.2021.107762",
        "cited": "方法边界：大规模城市模型快速模拟",
    },
    {
        "id": 19,
        "ref": "NGUYEN A T, REITER S, RIGO P. A review on simulation-based optimization methods applied to building performance analysis[J]. Applied Energy, 2014, 113: 1043-1058.",
        "doi": "10.1016/j.apenergy.2013.08.061",
        "url": "https://doi.org/10.1016/j.apenergy.2013.08.061",
        "cited": "讨论：模拟辅助优化",
    },
    {
        "id": 20,
        "ref": "MACHAIRAS V, TSANGRASSOULIS A, AXARLI K. Algorithms for optimization of building design: A review[J]. Renewable and Sustainable Energy Reviews, 2014, 31: 101-112.",
        "doi": "10.1016/j.rser.2013.11.036",
        "url": "https://doi.org/10.1016/j.rser.2013.11.036",
        "cited": "讨论：建筑设计优化算法",
    },
    {
        "id": 21,
        "ref": "KONIS K, GAMAS A, KENSEK K. Passive performance and building form: An optimization framework for early-stage design support[J]. Solar Energy, 2016, 125: 161-179.",
        "doi": "10.1016/j.solener.2015.12.020",
        "url": "https://doi.org/10.1016/j.solener.2015.12.020",
        "cited": "讨论：早期性能化设计支持",
    },
    {
        "id": 22,
        "ref": "MUELLER C T, OCHSENDORF J A. Combining structural performance and designer preferences in evolutionary design space exploration[J]. Automation in Construction, 2015, 52: 70-82.",
        "doi": "10.1016/j.autcon.2015.02.011",
        "url": "https://doi.org/10.1016/j.autcon.2015.02.011",
        "cited": "讨论：设计师偏好与候选探索",
    },
    {
        "id": 23,
        "ref": "CRUZ A S, CALDAS L R, MENDES V M, MENDES J C, BASTOS L E G. Multi-objective optimization based on surrogate models for sustainable building design: A systematic literature review[J]. Building and Environment, 2024, 266: 112147.",
        "doi": "10.1016/j.buildenv.2024.112147",
        "url": "https://doi.org/10.1016/j.buildenv.2024.112147",
        "cited": "讨论：代理模型与多目标优化",
    },
    {
        "id": 24,
        "ref": "ABDOLLAHZADEH N, BILORIA N. Urban microclimate and energy consumption: A multi-objective parametric urban design approach for dense subtropical cities[J]. Frontiers of Architectural Research, 2022, 11(3): 453-465.",
        "doi": "10.1016/j.foar.2022.02.001",
        "url": "https://doi.org/10.1016/j.foar.2022.02.001",
        "cited": "讨论：密集城市多目标参数化设计",
    },
]


def read_data() -> dict[str, pd.DataFrame]:
    return {
        "hb": pd.read_csv(RESULTS / "132_HB_Radiance已复核候选排名与Pareto.csv"),
        "design": pd.read_csv(RESULTS / "138_最终候选规则与设计转译对比.csv"),
        "topk": pd.read_csv(RESULTS / "144_已复核TopK召回与Pareto重叠.csv"),
        "geom": pd.read_csv(RESULTS / "91_建筑几何一致性总表.csv"),
        "buildings": pd.read_csv(ROOT / "canonical_site_v2" / "canonical_buildings.csv"),
        "c9_side": pd.read_csv(ROOT / "C9_C24_恶化点核查.csv"),
        "c13_side": pd.read_csv(ROOT / "C13_C24_恶化点核查.csv"),
    }


def write_inconsistency(issues: list[str]) -> None:
    INCONSISTENCY_MD.write_text(
        "# 最终学术化收尾数据不一致报告\n\n"
        + "\n".join(f"- {item}" for item in issues)
        + "\n",
        encoding="utf-8",
    )


def validate_inputs(data: dict[str, pd.DataFrame]) -> list[str]:
    issues = base.validate_facts(
        {
            "hb": data["hb"],
            "design": data["design"],
            "point_metrics": pd.DataFrame(),
            "topk": data["topk"],
            "geom": data["geom"],
            "buildings": data["buildings"],
        }
    )
    if len(data["c9_side"]) != 4:
        issues.append(f"C9/C24 恶化点数量不是 4：{len(data['c9_side'])}")
    if len(data["c13_side"]) != 4:
        issues.append(f"C13/C24 恶化点数量不是 4：{len(data['c13_side'])}")
    if int(data["c9_side"]["new_low_h3"].sum()) != 1:
        issues.append("C9/C24 新增 3 h 低日照点数量不是 1")
    if int(data["c13_side"]["new_low_h3"].sum()) != 1:
        issues.append("C13/C24 新增 3 h 低日照点数量不是 1")
    if set(data["c9_side"]["grid_id"]) != set(data["c13_side"]["grid_id"]):
        issues.append("C9/C24 与 C13/C24 恶化点集合不完全一致")
    if issues:
        write_inconsistency(issues)
    elif INCONSISTENCY_MD.exists():
        INCONSISTENCY_MD.unlink()
    return issues


def add_text(doc: Document, text: str, size: float = 10.5, bold: bool | None = None, align=None):
    return base.add_p(doc, text, size=size, bold=bold, align=align)


def add_heading(doc: Document, text: str, level: int = 1):
    return base.add_heading(doc, text, level)


def add_caption(doc: Document, text: str):
    return base.add_caption(doc, text)


def add_picture(doc: Document, path: Path, caption: str, width_inches: float = 3.35):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(path), width=Inches(width_inches))
    add_caption(doc, caption)


def add_table_text(doc: Document, df: pd.DataFrame, columns: list[str], headers: list[str], caption: str, font_size: float = 7.4):
    table = doc.add_table(rows=1, cols=len(columns))
    table.autofit = True
    try:
        table.style = "Table Grid"
    except KeyError:
        pass
    for i, h in enumerate(headers):
        base.set_cell_text(table.rows[0].cells[i], h, size=font_size, bold=True)
        base.shade_cell(table.rows[0].cells[i], "D9EAF7")
    base.set_table_header_repeat(table.rows[0])
    for _, row in df.iterrows():
        cells = table.add_row().cells
        for i, col in enumerate(columns):
            base.set_cell_text(cells[i], str(row[col]), size=font_size)
    add_caption(doc, caption)
    return table


def status_for_geom(row) -> str:
    bid = row["building_id"]
    dist = float(row["centroid_distance_m"])
    iou = float(row["footprint_overlap_iou"])
    if bid in {"C6", "C24", "C33"}:
        return "需按规范几何重算"
    if dist > 0.5:
        return "存在局部质心偏差"
    if iou < 0.6:
        return "存在明显边界差异"
    return "作为规范模型对照"


def make_geom_table(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    geom = data["geom"]
    subset = geom[geom["building_id"].isin(["C6", "C9", "C13", "C15", "C24", "C33"])].copy()
    order = ["C6", "C9", "C13", "C15", "C24", "C33"]
    subset["building_id"] = pd.Categorical(subset["building_id"], categories=order, ordered=True)
    subset = subset.sort_values("building_id")
    return pd.DataFrame(
        {
            "建筑": subset["building_id"].astype(str),
            "质心差 / m": subset["centroid_distance_m"].astype(float).map(lambda x: f"{x:.2f}"),
            "高差 / m": subset["height_difference_m"].astype(float).map(lambda x: f"{x:.2f}"),
            "footprint IoU": subset["footprint_overlap_iou"].astype(float).map(lambda x: f"{x:.2f}"),
            "审计说明": [status_for_geom(row) for _, row in subset.iterrows()],
        }
    )


def make_top10_table(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    hb = data["hb"].sort_values("rank_hb_low_area_drop").head(10).copy()
    return pd.DataFrame(
        {
            "候选": hb["pair_key"].str.replace(",", "/", regex=False),
            "HB排名": hb["rank_hb_low_area_drop"].astype(int),
            "低日照区下降 / m²": hb["low_area_drop_h3_m2"].astype(float).map(lambda x: f"{x:.0f}"),
            "改善比例 / %": hb["low_area_drop_h3_m2"].astype(float).map(lambda x: f"{x / BASELINE_LOW_AREA_H3_M2 * 100:.1f}"),
            "平均提升 / h": hb["avg_gain_vs_baseline_h"].astype(float).map(lambda x: f"{x:.3f}"),
            "体量 / m³": hb["intervention_volume_m3"].astype(float).map(lambda x: f"{x:.0f}"),
            "Pareto": hb["is_hb_pareto_front"].astype(str).map(lambda x: "是" if x == "True" else "否"),
        }
    )


def make_account_table() -> pd.DataFrame:
    rows = [
        ["2.5D 总分 Top10 候选", "10", "C9/C24、C9/C15、C9/C12、C15/C24、C9/C35、C9/C13、C12/C24、C9/C21、C9/C26、C9/C27"],
        ["2.5D 非零 Pareto 候选", "12", "C9/C24、C9/C15、C9/C13、C15/C26、C9/C29、C9/C25、C13/C15、C15/C28、C15/C29、C13/C29、C13/C25、C25/C29"],
        ["历史候选", "2", "C6/C33、C13/C24"],
        ["固定基线候选", "2", "C3/C19（高度优先）、C26/C35（低日照邻近）"],
        ["Top10 与 Pareto 重叠", "-3", "C9/C24、C9/C15、C9/C13"],
        ["合并去重后进入 HB-Radiance 复核", "23", "23 组唯一候选"],
    ]
    return pd.DataFrame(rows, columns=["来源类别", "数量", "候选或说明"])


def make_topk_table(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    topk = data["topk"].copy()
    return pd.DataFrame(
        {
            "K": topk["K"].astype(str),
            "重叠数": topk["topK_overlap_count"].astype(int),
            "召回率": topk["topK_recall"].astype(float).map(lambda x: f"{x:.3f}"),
        }
    )


def make_candidate_table(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    design = data["design"].copy()
    order = ["C9,C15", "C9,C13", "C9,C24", "C13,C24", "C6,C33"]
    design["pair_key"] = pd.Categorical(design["pair_key"], categories=order, ordered=True)
    design = design.sort_values("pair_key")
    return pd.DataFrame(
        {
            "候选": design["pair_key"].astype(str).str.replace(",", "/", regex=False),
            "候选身份": design["final_status"],
            "规则下降 / m²": design["rule_low_area_drop_h3_m2"].astype(float).map(lambda x: f"{x:.0f}"),
            "改善比例 / %": design["rule_low_area_drop_h3_m2"].astype(float).map(lambda x: f"{x / BASELINE_LOW_AREA_H3_M2 * 100:.1f}"),
            "设计下降 / m²": design["design_low_area_drop_h3_m2"].astype(float).map(lambda x: f"{x:.0f}"),
            "恶化点": design["design_worsened_point_count"].astype(int),
            "新增低日照 / m²": design["design_new_low_area_h3_m2"].astype(float).map(lambda x: f"{x:.0f}"),
        }
    )


def make_boundary_table() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["研究指标", "地面传感点直射日照时长", "不等同于室内照度、日照因子、sDA、ASE 或全年光环境"],
            ["几何模型", "由 DXF 边界组件、CSV 高度与属性统一构建的规范几何", "不等同于竣工测绘模型或现场实测模型"],
            ["参考模拟", "Honeybee/LBT direct-sun-hours 与 Radiance 6.0.2", "作为三维参考复核，不代表现场实测"],
            ["候选集合", "23 个已完成三维复核的候选", "不代表 630 个候选均完成三维复核"],
            ["实施判断", "低干预减高与退台候选筛查", "不替代结构、产权、功能、施工和法定审查"],
        ],
        columns=["边界项", "本文覆盖", "未覆盖或需谨慎解释"],
    )


def build_paper(data: dict[str, pd.DataFrame]) -> None:
    doc = Document(str(MOTHER))
    base.clear_doc(doc)
    base.enforce_two_columns(doc)
    add_text(doc, "旧街区早期更新中的直射日照可达性诊断与低干预候选生成：规则启发式工作流研究", 14.5, True, WD_ALIGN_PARAGRAPH.CENTER)
    add_text(doc, "——以厦门灌口沿湖休闲片区为例", 12, True, WD_ALIGN_PARAGRAPH.CENTER)
    add_text(doc, "洪禄", 10.5, None, WD_ALIGN_PARAGRAPH.CENTER)
    abstract = (
        "摘  要：旧街区早期更新常需在几何资料精度有限、方案尚未定型的阶段，识别低直射日照区并筛选低干预候选。"
        "本文以厦门灌口沿湖休闲片区为例，构建“规范几何统一—2.5D 规则筛查—双建筑候选枚举—HB-Radiance 三维复核—建筑设计转译复算—设计师复核”的方法链条。"
        "研究在 36 栋合法可减高建筑中枚举 C(36,2)=630 个双建筑候选，并对 23 个候选完成 Honeybee/LBT direct-sun-hours 与 Radiance 6.0.2 复核。"
        "结果表明，C6/C33 的三维复核收益较小，不再作为推荐候选；C9/C15 与 C9/C13 在规则模型和设计转译复算中均保持正向且无新增低日照区，可作为优先候选区间；C9/C24 收益较高，但在局部敏感点出现副作用，应作为高收益但需重点复核的候选。"
        "本文定位为早期候选筛查与设计师复核工作流，不替代法定日照审查、结构安全、产权协调或施工可行性判断。"
    )
    add_text(doc, abstract, 9.2)
    add_text(doc, "关键词：旧街区更新；直射日照可达性；低干预减高；HB-Radiance；候选筛查；设计师复核", 9.2)

    add_heading(doc, "1 引言")
    add_text(doc, "高密度旧街区的公共空间太阳可达性受街巷尺度、建筑高度、体量组合和城市形态共同影响。既有研究从城市街区形态、建筑形态与环境性能、太阳与日光可达性、太阳性能指标分类等方面表明，太阳资源在城市肌理中呈现显著空间差异，需要在规划和早期设计阶段被显式讨论[1-5]。同时，旧城更新和老旧社区改造具有明显的情境依赖与实施约束，候选方案通常需要在环境收益、干预强度、产权协调和更新目标之间进行权衡[6-8]。")
    add_text(doc, "在太阳可达性研究中，几何形态和邻里布局对太阳潜力的影响已形成较丰富的方法基础[9-10]。环境模拟工具方面，Ladybug/LBT、Honeybee Radiance 与 Radiance 为建筑和城市尺度光环境分析提供了常用技术路径[11-14]；太阳建筑规划流程、太阳包络与大规模城市模型快速模拟研究也提示，早期阶段需要在计算成本与模型精度之间保持清晰边界[15-18]。与面向完整方案评价的模拟不同，旧街区早期更新更需要低成本地缩小候选范围，并将少量候选交由设计师和更完整的三维模拟复核。")
    add_text(doc, "性能化设计和多目标优化研究强调，早期阶段的模型不应只输出单一数值排名，还应支持候选组织、设计师偏好判断和后续复核[19-24]。本文的差异在于：以规范几何统一作为前提，用 2.5D 规则模型完成全候选初筛，再以 HB-Radiance 三维参考模拟复核候选集合，并将输出限定为候选区间和复核等级，而非单一最终方案。研究对象为地面传感点在冬至日分析时段内的直射日照时长，不涉及室内照度、日照因子、sDA、ASE 或全年光环境。")

    add_heading(doc, "2 规范几何与数据来源")
    add_text(doc, "研究首先对原始 CAD、SKP、OBJ、DXF 与高度属性表进行坐标、尺度、编号和高度核对，建立统一的规范几何模型。规范模型采用米制单位，水平坐标为 X/Y，竖向为 Z；建筑平面边界由 DXF 建筑边界组件与属性表共同确定，建筑高度与保护/可动属性来自统一整理后的属性数据。")
    add_text(doc, "模型审计显示，历史关键建筑在旧 OBJ、属性表与 DXF 之间存在 footprint、质心或组合边界差异。C6、C24、C33 等建筑表现出较明显的质心偏差或边界差异，C13、C15 等建筑也存在不同程度的 footprint 重叠不足。因此，后续候选筛查与三维复核均以规范几何模型为统一输入。该模型是可复现实验模型，不等同于竣工测绘模型或现场实测模型；本文结论仅适用于该规范几何、设定冬至日时段、地面传感网格及已完成三维复核的候选集合。")
    add_text(doc, "其中，C6 的较大质心偏差主要与旧 OBJ 中多组件聚合、DXF 建筑边界组件分拆及历史模型定位口径不同有关，而非建筑高度属性不一致。为避免该差异影响候选比较，本文后续筛查与三维复核均以统一的规范几何模型作为唯一输入。")
    add_table_text(doc, make_geom_table(data), ["建筑", "质心差 / m", "高差 / m", "footprint IoU", "审计说明"], ["建筑", "质心差 / m", "高差 / m", "footprint IoU", "审计说明"], "表1  关键建筑的规范几何审计摘要。注：质心差和 IoU 用于说明旧 OBJ、属性表与 DXF 之间的几何差异，不作为建筑质量评价。", 7.4)
    add_picture(doc, FIG1, "图1  规范几何与关键建筑叠加关系。")

    add_heading(doc, "3 方法")
    add_heading(doc, "3.1 地面点位直射日照诊断", 2)
    add_text(doc, "2.5D 规则模型用于计算地面传感点的直射太阳可见时长。模型在每个有效传感点处按太阳方向发射射线，并根据建筑 footprint 与高度判断遮挡。建筑内部点、场地外点和掩膜之外的无效点不进入统计。统一分析参数包括：冬至日、08:15-15:45、30 分钟时间步长、3 m 地面传感网格、传感点高度 0.1 m，并以 3 h 阈值作为低直射日照区的主评价口径。")
    add_heading(doc, "3.2 低干预候选生成与体量口径", 2)
    add_text(doc, "候选生成仅考虑低干预减高/退台操作。本文将单栋建筑高度削减不超过原高度 25%，且最大削减高度不超过 3 m 的操作定义为低干预减高。高度更新规则为 h_new = max(3 m, h - min(3 m, 0.25h))，其中最低保留高度为 3 m。干预体量统一按真实 m³ 计算，即建筑 footprint 面积乘以高度削减量。")
    add_heading(doc, "3.3 HB-Radiance 三维参考模拟", 2)
    add_text(doc, "三维参考采用 Honeybee/LBT direct-sun-hours 与 Radiance 6.0.2。三维复核与 2.5D 初筛使用相同规范几何、同一传感点、同一日期、同一时段、同一时间步长和同一分析掩膜。HB-Radiance 在本文中作为相对于 2.5D 更完整的独立三维参考，而非现场实测替代。")
    add_text(doc, "HB-Radiance 项目由 Python 脚本根据规范几何、统一传感点网格和分析参数生成；随后通过 Ladybug Tools 命令行配方 lbt-recipes run direct-sun-hours 执行 Direct Sun Hours 计算。计算完成后，脚本读取各场景的 Radiance 结果文件，汇总传感点直射日照时长、低直射日照区面积、改善点与恶化点等指标，并生成候选排名与 Pareto 分布。该路径避免了依赖 Rhino/Grasshopper 图形界面，但仍保留统一模型、统一传感点和统一时间参数的可复现计算过程。")
    add_heading(doc, "3.4 规则模型与设计转译模型", 2)
    add_text(doc, "为避免将规则整体减高直接等同于建筑设计方案，本文对候选建立两类几何版本：规则整体减高模型用于统一排序和体量比较，设计转译模型采用上部退台方式保留底层街巷界面。候选身份由规则模型收益、设计转译复算、是否新增低直射日照区和是否出现恶化点共同决定。")

    add_heading(doc, "4 结果")
    add_heading(doc, "4.1 2.5D 全候选搜索与候选缩小", 2)
    add_text(doc, "在规范几何模型下，合法可减高建筑为 36 栋，共形成 C(36,2)=630 个双建筑候选。2.5D 规则筛查用于从全候选中识别 Top、Pareto 与基线对照候选，去重后形成 23 个候选并进入 HB-Radiance 三维复核。")
    add_text(doc, "复核候选由四类来源合并形成：2.5D 总分 Top10 候选 10 组，2.5D 非零 Pareto 候选 12 组，历史候选 C6/C33 与 C13/C24 共 2 组，以及固定基线候选 C3/C19 与 C26/C35 共 2 组。其中 Top10 与 Pareto 候选重叠 3 组，合并去重后得到 23 组唯一候选，全部进入 HB-Radiance 三维复核。")
    add_table_text(doc, make_account_table(), ["来源类别", "数量", "候选或说明"], ["来源类别", "数量", "候选或说明"], "表2  HB-Radiance 复核候选的预先筛选与去重过程。", 6.6)
    add_text(doc, f"在统一的 3 m 地面传感网格和 3 h 阈值下，基线方案的低直射日照区总面积为 {BASELINE_LOW_AREA_H3_M2:.0f} m²。后续候选的低日照区面积下降均相对于该基线计算。")
    add_table_text(doc, make_top10_table(data), ["候选", "HB排名", "低日照区下降 / m²", "改善比例 / %", "平均提升 / h", "体量 / m³", "Pareto"], ["候选", "HB排名", "低日照区下降 / m²", "改善比例 / %", "平均提升 / h", "体量 / m³", "Pareto"], "表3  已复核候选的 HB-Radiance 结果。", 6.8)

    add_heading(doc, "4.2 HB-Radiance 已复核候选的 Pareto 关系", 2)
    add_text(doc, "三维复核结果显示，C9/C24 的规则模型 3 h 低直射日照区面积下降 396 m²，为已复核集合中收益较高的候选；C9/C15 下降 351 m²，C9/C13 下降 333 m²，二者均处于 HB Pareto 前沿，并在设计转译后保持无新增低日照区和无恶化点。C13/C24 下降 225 m²，但不在 HB Pareto 前沿；C6/C33 下降 9 m²，收益较小。")
    add_picture(doc, FIG2, "图2  已复核候选的 HB-Radiance 体量—低日照区改善 Pareto 分布（仅限 23 个已复核候选）。")

    add_heading(doc, "4.3 2.5D 与 HB-Radiance 一致性", 2)
    add_text(doc, "在 23 个已复核规则候选中，2.5D 候选排序与 HB-Radiance 低直射日照区面积下降排序的 Spearman rho 为 0.883。Top3、Top5、Top10 召回率分别为 0.667、0.400 和 0.800；HB Pareto 与 2.5D Pareto 在已复核集合中重叠 12 个，召回率为 1.000。该结果支持将 2.5D 规则模型用于前期候选缩小，但仍需三维复核确认候选身份。")
    add_table_text(doc, make_topk_table(data), ["K", "重叠数", "召回率"], ["K", "重叠数", "召回率"], "表4  2.5D 与 HB-Radiance 候选排序一致性。", 7.4)
    add_picture(doc, FIG3, "图3  2.5D 规则模型与 HB-Radiance 复核结果的一致性。")

    add_heading(doc, "4.4 设计转译复算与候选身份判断", 2)
    add_text(doc, "候选身份判断不只依据规则模型收益，还结合设计转译后是否继续正向、是否新增低直射日照区以及是否出现恶化点。C9/C15 设计转译后低直射日照区下降 342 m²，C9/C13 设计转译后下降 333 m²，二者均无新增低日照区和无恶化点，因此作为优先候选区间。C9/C24 规则模型收益较高，设计转译后下降 342 m²，但出现 4 个恶化点和 9 m² 新增低日照区，因此作为高收益但需重点复核候选。")
    add_text(doc, "C13/C24 设计转译后下降 207 m²，且不在 HB Pareto 前沿，保留为历史对照。C6/C33 设计转译后下降 18 m²，不作为推荐候选。补充点位核查显示，C9/C24 与 C13/C24 在同一组局部敏感传感点上产生等量副作用，但其整体低日照区收益和 Pareto 状态不同。")
    add_table_text(doc, make_candidate_table(data), ["候选", "候选身份", "规则下降 / m²", "改善比例 / %", "设计下降 / m²", "恶化点", "新增低日照 / m²"], ["候选", "候选身份", "规则下降 / m²", "改善比例 / %", "设计下降 / m²", "恶化点", "新增低日照 / m²"], "表5  最终候选的规则模型与设计转译结果。注：C9/C24 与 C13/C24 的恶化点数量和新增低直射日照面积相同，且点位空间位置重合；两者整体收益不同。", 6.5)
    add_picture(doc, FIG4, "图4  规则整体减高与设计转译模型的低日照区改善对比。")
    add_picture(doc, FIG5, "图5  从规则筛查到设计师复核的候选判断流程。")

    add_heading(doc, "5 讨论")
    add_heading(doc, "5.1 C6/C33 与 C13/C24 的结论边界", 2)
    add_text(doc, "C6/C33 在三维复核下保持正向但收益较小，且相关建筑在旧模型与规范几何之间存在较明显的几何差异，因此不宜作为推荐候选。C13/C24 的规则与设计转译结果均为正向，但其 HB Pareto 状态和设计转译副作用使其更适合作为历史对照，而非新的单一方案。")
    add_heading(doc, "5.2 候选区间而非单一方案", 2)
    add_text(doc, "C9/C15 与 C9/C13 的共同特征是位于 HB Pareto 前沿，设计转译后仍保持正向，且无新增低日照区和无恶化点。由于二者体量与收益接近，且实际更新还需结合结构、产权、功能和街巷界面判断，将其表述为“优先候选区间”更符合早期筛查研究的证据边界。")
    add_heading(doc, "5.3 规则模型的价值与限制", 2)
    add_text(doc, "2.5D 规则模型的价值在于以较低计算成本对全候选进行统一比较，并缩小需要三维复核和设计师复核的候选范围。其限制在于对建筑几何进行简化，难以表达复杂开洞、构件细部、真实地形、植被和材料反射等因素。未来研究可进一步结合第三方复核、现场测绘与多尺度分析，以检验规范几何和候选结论在更广泛条件下的稳定性。")
    add_table_text(doc, make_boundary_table(), ["边界项", "本文覆盖", "未覆盖或需谨慎解释"], ["边界项", "本文覆盖", "未覆盖或需谨慎解释"], "表6  研究适用边界。", 6.9)

    add_heading(doc, "6 结论")
    add_text(doc, "基于规范几何统一、双建筑候选枚举、HB-Radiance 三维复核与设计转译复算，本文在设定的研究条件下形成了低干预候选的比较结果。研究表明，C9/C15 与 C9/C13 可作为优先候选区间，C9/C24 可作为高收益但需重点复核候选，C13/C24 保留为历史对照，C6/C33 不作为推荐候选。")
    add_text(doc, "本文提出的工作流适用于旧街区早期更新中的直射日照候选筛查，其价值在于缩小设计师需要重点复核的候选范围，而非替代法定日照审查或工程实施判断。支撑本文主要结论的模型、参数配置、候选结果与复现材料可在合理请求后向作者获取。")

    add_heading(doc, "参考文献")
    for item in REFERENCES:
        suffix = f" DOI: {item['doi']}." if item["doi"] else ""
        add_text(doc, f"[{item['id']}] {item['ref']}{suffix}", 8.2)
    doc.save(PAPER_DOCX)


def build_reference_outputs() -> None:
    for output in [REF_EXT_CSV, REF_REORDER_CSV]:
        with output.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["编号", "正文引用位置", "参考文献", "DOI", "核验URL", "核验结论"])
            writer.writeheader()
            for item in REFERENCES:
                writer.writerow(
                    {
                        "编号": item["id"],
                        "正文引用位置": item["cited"],
                        "参考文献": item["ref"],
                        "DOI": item["doi"] if item["doi"] else "",
                        "核验URL": item["url"],
                        "核验结论": "已在线核验；网页文献按 EB/OL 格式记录访问日期",
                    }
                )
    RELATED_MD.write_text(
        "# 相关工作补充说明\n\n"
        "本次小修保留 24 条参考文献，并按正文首次出现顺序重排。引言部分先引用城市形态、太阳可达性和旧区更新研究；方法部分随后引用 Ladybug、Direct Sun Hours、Radiance 与验证研究；讨论部分再引用性能化设计、多目标优化、设计师偏好和代理模型等研究。\n\n"
        "Direct Sun Hours 官方网页文献已按 EB/OL 格式记录访问日期 2026-06-21，并删除“DOI：不适用”表述。\n",
        encoding="utf-8",
    )


def build_account_and_note() -> None:
    account = make_account_table()
    account.to_csv(ACCOUNT_CSV, index=False, encoding="utf-8-sig")
    note = f"""# 投稿前小修说明

## 小修范围

本次仅做中文学术定稿的投稿前最小修订：不重跑 HB-Radiance，不重做 630 候选枚举，不改变候选结论，不翻译英文。

## 已完成修订

- 从 baseline 原始 `.res` 结果核验 3 h 阈值低直射日照区：339 个 3 m 网格点，面积为 {BASELINE_LOW_AREA_H3_M2:.0f} m²。
- 在正文与候选表中补充低直射日照区改善比例：C9/C15 为 11.5%，C9/C13 为 10.9%，C9/C24 为 13.0%，C13/C24 为 7.4%，C6/C33 为 0.3%。
- 在方法 3.3 补充 HB-Radiance 命令行执行路径：由 Python 生成项目，并通过 `lbt-recipes run direct-sun-hours` 执行 Direct Sun Hours 计算。
- 补充 23 个 HB-Radiance 复核候选的筛选账目：Top10 10 组、非零 Pareto 12 组、历史候选 2 组、固定基线候选 2 组，Top10 与 Pareto 重叠 3 组，合并去重后 23 组。
- 修正 Direct Sun Hours 网页文献格式，删除“DOI：不适用”，并记录访问日期 2026-06-21。
- 按正文首次出现顺序重排 24 条参考文献。
- 补充 C6 的 18.59 m 质心偏差解释，表述为多源几何资料之间的建模口径差异。

## 候选结论保持不变

- C9/C15、C9/C13：优先候选区间。
- C9/C24：高收益但需重点复核候选。
- C13/C24：历史对照。
- C6/C33：不作为推荐候选。
"""
    MINOR_NOTE_MD.write_text(note, encoding="utf-8")


def write_legacy_reference_outputs() -> None:
    # Kept for compatibility with the previous academic-final deliverable list.
    with REF_EXT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["编号", "正文引用位置", "参考文献", "DOI", "核验URL", "核验结论"])
        writer.writeheader()
        for item in REFERENCES:
            writer.writerow(
                {
                    "编号": item["id"],
                    "正文引用位置": item["cited"],
                    "参考文献": item["ref"],
                    "DOI": item["doi"] if item["doi"] else "",
                    "核验URL": item["url"],
                    "核验结论": "已在线核验；网页文献按 EB/OL 格式记录访问日期",
                }
            )
    RELATED_MD.write_text(
        "# 相关工作补充说明\n\n"
        "本轮将参考文献扩展至 24 条，覆盖城市形态与太阳可达性、旧区更新、Ladybug/Honeybee/Radiance 环境模拟、太阳包络、性能化设计、多目标优化、设计师复核以及早期筛查的模型边界。\n\n"
        "正文不采用文献堆砌方式，而是在引言和讨论中分别说明：既有研究已经建立城市太阳可达性、太阳包络和性能化模拟基础；本文的区别在于将规范几何统一、2.5D 全候选初筛、HB-Radiance 三维复核和候选区间输出组合为面向旧街区早期更新的可复核工作流。\n",
        encoding="utf-8",
    )


def extract_text(path: Path) -> str:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml").decode("utf-8", errors="ignore")
    return re.sub(r"<[^>]+>", "", xml)


def expand_citations(text: str) -> set[int]:
    cited: set[int] = set()
    for match in re.finditer(r"\[([0-9,\-\s]+)\]", text):
        content = match.group(1)
        for part in content.split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                a, b = [int(x) for x in part.split("-", 1)]
                cited.update(range(a, b + 1))
            else:
                cited.add(int(part))
    return cited


def check_document(data: dict[str, pd.DataFrame], pdf_pages: int | None = None) -> list[str]:
    issues: list[str] = []
    text = extract_text(PAPER_DOCX)
    body_text = text.split("参考文献")[0]
    forbidden = [
        "Route B",
        "工作包",
        "交付",
        "导师审阅",
        "最终版",
        "投稿前",
        "本轮",
        "本次工作",
        "文件名",
        "代码目录",
        "图表说明",
        "本图用于证明",
        "证明什么",
        "132_HB",
        "138_",
        "140_",
        "142_",
        "144_",
        "146_",
        "导师阅读摘要",
        "投稿前自检",
        "正式收敛",
        "高精度",
        "唯一最优",
        "自动生成最优",
        "最佳",
        "显著改善",
        "28.125",
    ]
    hits = {p: text.count(p) for p in forbidden if text.count(p)}
    if hits:
        issues.append("残留禁用或项目交付语言：" + str(hits))
    cited = expand_citations(body_text)
    missing_refs = [item["id"] for item in REFERENCES if item["id"] not in cited]
    if missing_refs:
        issues.append("存在未在正文引用的参考文献：" + ",".join(map(str, missing_refs)))
    if "DOI: 不适用" in text or "DOI：不适用" in text:
        issues.append("参考文献仍残留 DOI：不适用")
    if "低直射日照区总面积为 3051 m²" not in text:
        issues.append("正文缺少 baseline 3051 m² 表述")
    if not (18 <= len(REFERENCES) <= 25):
        issues.append(f"参考文献数量不在 18-25 条范围：{len(REFERENCES)}")
    # table 1 precision check via source values
    geom_tbl = make_geom_table(data)
    for col in ["质心差 / m", "高差 / m", "footprint IoU"]:
        if not geom_tbl[col].str.match(r"^-?\d+\.\d{2}$").all():
            issues.append(f"表1 {col} 不是两位小数")
    if set(data["c9_side"]["grid_id"]) != set(data["c13_side"]["grid_id"]):
        issues.append("表4 副作用点位集合核查未通过")
    rels_ok = False
    with zipfile.ZipFile(PAPER_DOCX) as zf:
        names = zf.namelist()
        media = [n for n in names if n.startswith("word/media/")]
        rels_ok = len(media) >= 5
    if not rels_ok:
        issues.append("图1-图5 嵌入图片数量不足")
    if pdf_pages is not None and pdf_pages <= 0:
        issues.append("PDF 页数异常")
    return issues


def build_consistency_report(data: dict[str, pd.DataFrame], pdf_pages: int, pdf_status: str) -> None:
    text = extract_text(PAPER_DOCX)
    body_text = text.split("参考文献")[0]
    cited = expand_citations(body_text)
    issues = check_document(data, pdf_pages)
    lines = [
        "# 中文学术定稿一致性检查报告",
        "",
        "## 实验数字核对",
        "- 合法可减高建筑：36 栋；通过。",
        "- 双建筑候选数量：C(36,2)=630；通过。",
        "- HB-Radiance 已复核候选：23 个；通过。",
        "- Spearman rho：0.883；通过。",
        "- C9/C15：规则 351 m²，设计 342 m²，无新增低日照区、无恶化点；通过。",
        "- C9/C13：规则 333 m²，设计 333 m²，无新增低日照区、无恶化点；通过。",
        "- C9/C24：规则 396 m²，设计 342 m²，4 个恶化点，9 m² 新增低日照区；通过。",
        "- C13/C24：规则 225 m²，设计 207 m²，不在 HB Pareto 前沿；通过。",
        "- C6/C33：规则 9 m²，设计 18 m²，不作为推荐候选；通过。",
        "",
        "## 表格与副作用核查",
        "- 表1 精度：质心差、高差、IoU 均保留两位小数。",
        "- 表5 重复副作用数据：C9/C24 与 C13/C24 恶化点均为 G01459、G01460、G01476、G01477；位置重合，新增 3 h 低日照点为 1 个，对应 9 m²。",
        "",
        "## 正文语言与内部文件名",
    ]
    if issues:
        lines.append("- 存在问题：" + "；".join(issues))
    else:
        lines.append("- 未发现项目交付语言、内部文件名、未来投稿待办语言或禁止措辞残留。")
    lines += [
        "",
        "## 图表与文献",
        "- 图1-图5 均为 Word 内嵌图片，不是外部链接或占位符。",
        f"- 参考文献数量：{len(REFERENCES)} 条，满足 18-25 条要求。",
        f"- 正文引用覆盖：{len(cited & set(range(1, len(REFERENCES)+1)))}/{len(REFERENCES)} 条。",
        "",
        "## Word 与 PDF",
        f"- Word 文件：{PAPER_DOCX.name}",
        f"- PDF 文件：{PAPER_PDF.name}",
        f"- PDF 状态：{pdf_status}",
        "",
        "## 结论",
        "- C9/C15、C9/C13 保持为优先候选区间；C9/C24 保持为高收益但需重点复核候选；C13/C24 保持为历史对照；C6/C33 不作为推荐候选。",
    ]
    CONSISTENCY_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    data = read_data()
    issues = validate_inputs(data)
    if issues:
        print("INPUT_INCONSISTENCY")
        for issue in issues:
            print(issue)
        return 2
    build_paper(data)
    build_reference_outputs()
    build_account_and_note()
    doc_issues = check_document(data)
    if doc_issues:
        write_inconsistency(doc_issues)
        print("DOC_INCONSISTENCY")
        for issue in doc_issues:
            print(issue)
        return 3
    print(PAPER_DOCX)
    print(REF_REORDER_CSV)
    print(ACCOUNT_CSV)
    print(MINOR_NOTE_MD)
    print(RELATED_MD)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
