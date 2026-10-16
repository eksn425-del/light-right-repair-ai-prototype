from __future__ import annotations

import json
import shutil
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from docx import Document


WORK_DIR = Path("paper_revision_work_2026_06_14")
FINAL_DIR = WORK_DIR / "final_output"
SRC = FINAL_DIR / "光权修复论文_EI会议中文最终审阅版_v3_同行评审增强版.docx"
DST = FINAL_DIR / "光权修复论文_EI会议中文终稿_v4_C6C33三米复算版.docx"
ASCII_COPY = FINAL_DIR / "paper_final_v4_validation_copy.docx"
CHART = WORK_DIR / "c6_c33_same_scheme_grid_fast" / "c6_c33_same_scheme_grid_chart.png"
METRICS = WORK_DIR / "c6_c33_same_scheme_grid_fast" / "c6_c33_same_scheme_grid_metrics.csv"
SUMMARY = WORK_DIR / "c6_c33_same_scheme_grid_fast" / "c6_c33_same_scheme_grid_summary.json"
REPORT = FINAL_DIR / "C6C33_3m同方案复算_论文更新说明.md"


def set_paragraph_text(paragraph, text: str) -> None:
    """Replace text while preserving the original paragraph style."""
    for run in paragraph.runs:
        run.text = ""
    if paragraph.runs:
        paragraph.runs[0].text = text
    else:
        paragraph.add_run(text)


def replace_docx_media(docx_path: Path, media_name: str, image_path: Path) -> None:
    """Replace one image inside a docx zip archive."""
    tmp_path = docx_path.with_suffix(".tmp.docx")
    with ZipFile(docx_path, "r") as zin, ZipFile(tmp_path, "w", ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == f"word/media/{media_name}":
                data = image_path.read_bytes()
            zout.writestr(item, data)
    tmp_path.replace(docx_path)


def update_table_6(doc: Document) -> None:
    for table in doc.tables:
        if not table.rows:
            continue
        header = [cell.text.strip() for cell in table.rows[0].cells]
        if header[:2] == ["网格尺寸", "现状平均采光/h"]:
            desired_rows = [
                ["网格尺寸", "现状平均采光/h", "现状暗区比例", "方案后平均采光/h", "方案后暗区比例", "改善比例", "候选建筑"],
                ["6 m 网格", "6.422", "17.55%", "6.435", "16.94%", "3.48%", "C6、C33"],
                ["3 m 网格（重新优化）", "6.509", "16.09%", "6.509", "16.09%", "0.00%", "C28、C34、C38、C9"],
                ["3 m 网格（固定 C6/C33）", "6.509", "16.09%", "6.519", "15.84%", "1.59%", "C6、C33"],
            ]
            while len(table.rows) < len(desired_rows):
                table.add_row()
            for r_idx, values in enumerate(desired_rows):
                for c_idx, value in enumerate(values):
                    table.cell(r_idx, c_idx).text = value
            for r_idx in range(len(desired_rows), len(table.rows)):
                for c_idx in range(len(table.columns)):
                    table.cell(r_idx, c_idx).text = ""
            return
    raise RuntimeError("未找到表6。")


def update_paragraphs(doc: Document) -> list[str]:
    changes: list[str] = []
    replacements = {
        "在方法上，算法 A 基于冬至日 8:00 至 16:00 的简化太阳路径和 2.5D 遮挡判断，生成采光热力图、平均采光小时和暗区比例；算法 B 在最小干预原则下生成保守型、均衡型和采光优先型三类候选策略，通过光照增益、干预体量、新增阴影惩罚和保护冲突惩罚进行启发式评分；算法 C 对候选策略进行方案后复算。结果显示，在 6 m 基准网格下，现状平均采光小时为 6.422 h，暗区比例为 17.55%；保守型 AI 方案将暗区比例相对改善约 3.48%，主要干预建筑为 C6 和 C33。3 m 网格敏感性测试揭示当前简化模型的尺度依赖性，说明该方法适合早期问题诊断与候选生成，而非替代专业日照软件。":
        "在方法上，算法 A 基于冬至日 8:00 至 16:00 的简化太阳路径和 2.5D 遮挡判断，生成采光热力图、平均采光小时和暗区比例；算法 B 在最小干预原则下生成保守型、均衡型和采光优先型三类候选策略，通过光照增益、干预体量、新增阴影惩罚和保护冲突惩罚进行启发式评分；算法 C 对候选策略进行方案后复算。结果显示，在 6 m 基准网格下，现状平均采光小时为 6.422 h，暗区比例为 17.55%；保守型 AI 方案将暗区比例相对改善约 3.48%，主要干预建筑为 C6 和 C33。进一步固定 C6/C33 方案并在 3 m 网格下复算，暗区比例由 16.09% 降至 15.84%，说明同一干预在更密网格下仍具有方向性改善，但改善幅度有限。3 m 网格敏感性测试揭示当前简化模型的尺度依赖性，说明该方法适合早期问题诊断与候选生成，而非替代专业日照软件。",

        "为检查算法稳定性，本文采用多尺度复核：原始计算采用 6 m 基准网格，随后补做 3 m 全场网格敏感性测试，并在 C6/C33 周边 18 m 影响区补做 2 m 局部网格复核。3 m 网格用于观察暗区比例和候选建筑排序是否随采样尺度变化；2 m 局部网格用于判断保守型策略在关键干预区是否产生可解释的点位改善。":
        "为检查算法稳定性，本文采用多尺度复核：原始计算采用 6 m 基准网格，随后补做 3 m 全场网格敏感性测试，并在 C6/C33 周边 18 m 影响区补做 2 m 局部网格复核。3 m 网格首先用于观察暗区比例和候选建筑排序是否随采样尺度变化；随后进一步固定 6 m 保守型方案中的 C6/C33 干预，在 3 m 网格下进行同方案复算，以区分“重新优化导致候选变化”和“同一方案跨尺度表现”两个问题。2 m 局部网格用于判断保守型策略在关键干预区是否产生可解释的点位改善。",

        "3 m 网格敏感性测试显示，现状基准平均采光小时为 6.509 h，暗区比例为 16.09%。与 6 m 网格相比，3 m 网格下候选建筑排序发生变化，推荐对象转为 C28、C34、C38 和 C9，且方案后复算后暗区比例没有进一步下降。表6 对两种网格设置的结果进行了汇总，图8 直观展示了网格尺度对候选结果的影响。":
        "3 m 网格敏感性测试显示，现状基准平均采光小时为 6.509 h，暗区比例为 16.09%。与 6 m 网格相比，3 m 网格下重新优化时候选建筑排序发生变化，推荐对象转为 C28、C34、C38 和 C9，且方案后复算后暗区比例没有进一步下降。为避免将“重新优化候选变化”误读为 C6/C33 方案失效，本文进一步固定 6 m 保守型方案中的 C6/C33 干预，并在 3 m 网格下进行同方案复算。结果显示，固定 C6/C33 后 3 m 网格平均采光小时由 6.509 h 提升至 6.519 h，暗区比例由 16.09% 降至 15.84%，暗区网格数由 314 降至 309，且未新增暗区。表6 对结果进行了汇总，图8 展示重新优化下的尺度敏感性，图9 展示固定 C6/C33 同方案复算结果。",

        "图9  6 m 与 3 m 网格敏感性测试三项指标对比":
        "图9  C6/C33 同一保守型方案在 6 m 与 3 m 网格下的复算结果",

        "表6  6 m 与 3 m 网格敏感性测试结果":
        "表6  6 m 与 3 m 网格敏感性及固定 C6/C33 同方案复算结果",

        "该结果说明，当前简化算法对网格尺度存在敏感性，不能被表述为精确找到唯一最优建筑。更稳妥的表述是：该算法适用于早期问题定位和候选策略生成，最终方案仍需通过人工判断和专业光照工具复核。":
        "该结果说明，当前简化算法对网格尺度存在敏感性，不能被表述为精确找到唯一最优建筑；但固定 C6/C33 同方案复算表明，保守型方案在 3 m 网格下仍能产生小幅方向性改善。更稳妥的表述是：该算法适用于早期问题定位和候选策略生成，最终方案仍需通过人工判断和专业光照工具复核。",

        "本研究的主要贡献不在于提出高精度日照模拟算法，而在于建立一个可复核、可替换数据、可嵌入设计流程的早期 AI 决策工作流。该流程将 CAD/SU/OBJ/CSV 与人工可改性判断转译为算法输入，并通过全场 6 m 诊断、全场 3 m 敏感性测试、C6/C33 局部 2 m 复核和人工同视角图像校核形成证据链。当前模型采用 2.5D 简化遮挡判断，适合早期趋势判断和候选生成，但不能替代 Ladybug、Radiance 或法定日照审查软件。未来研究应进一步接入专业环境模拟工具，并在多个旧街区案例中验证方法稳定性。":
        "本研究的主要贡献不在于提出高精度日照模拟算法，而在于建立一个可复核、可替换数据、可嵌入设计流程的早期 AI 决策工作流。该流程将 CAD/SU/OBJ/CSV 与人工可改性判断转译为算法输入，并通过全场 6 m 诊断、全场 3 m 敏感性测试、固定 C6/C33 的 3 m 同方案复算、C6/C33 局部 2 m 复核和人工同视角图像校核形成证据链。当前模型采用 2.5D 简化遮挡判断，适合早期趋势判断和候选生成，但不能替代 Ladybug、Radiance 或法定日照审查软件。未来研究应进一步接入专业环境模拟工具，并在多个旧街区案例中验证方法稳定性。",

        "在 6 m 基准网格下，保守型 AI 策略使暗区比例从 17.55% 降至 16.94%，平均采光小时从 6.422 h 提升至 6.435 h。虽然全场提升幅度有限，但该策略干预体量较小，主要涉及 C6 与 C33，适合转译为局部退台、屋顶平台和采光缝等建筑策略。补充非 AI 基线对照显示，高度优先基线在 45.0 的干预体量下未降低暗区比例，暗区邻近基线在 33.75 的干预体量下暗区比例为 17.35%，随机基线均值在 31.04 的干预体量下暗区比例为 17.26%，其暗区比例下降均弱于 AI 保守型。这说明本文算法的价值不是制造大幅全场提升，而是在有限干预条件下形成比朴素规则更可解释、更可复核的候选策略。C6/C33 周边 2 m 局部网格进一步显示，局部平均采光小时由 5.555 h 提升至 5.801 h，最大单点提升达到 4.0 h。3 m 网格敏感性测试显示，当前简化模型对采样尺度存在敏感性，因此算法输出应被定位为候选决策支持，而不是唯一最优方案或专业日照审查结论。":
        "在 6 m 基准网格下，保守型 AI 策略使暗区比例从 17.55% 降至 16.94%，平均采光小时从 6.422 h 提升至 6.435 h。虽然全场提升幅度有限，但该策略干预体量较小，主要涉及 C6 与 C33，适合转译为局部退台、屋顶平台和采光缝等建筑策略。补充非 AI 基线对照显示，高度优先基线在 45.0 的干预体量下未降低暗区比例，暗区邻近基线在 33.75 的干预体量下暗区比例为 17.35%，随机基线均值在 31.04 的干预体量下暗区比例为 17.26%，其暗区比例下降均弱于 AI 保守型。这说明本文算法的价值不是制造大幅全场提升，而是在有限干预条件下形成比朴素规则更可解释、更可复核的候选策略。进一步固定 C6/C33 干预并在 3 m 网格下复算，暗区比例由 16.09% 降至 15.84%，暗区网格数由 314 降至 309，说明同一方案在更密网格下仍具有小幅方向性改善。C6/C33 周边 2 m 局部网格进一步显示，局部平均采光小时由 5.555 h 提升至 5.801 h，最大单点提升达到 4.0 h。3 m 网格敏感性测试显示，当前简化模型对采样尺度存在敏感性，因此算法输出应被定位为候选决策支持，而不是唯一最优方案或专业日照审查结论。",
    }

    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text in replacements:
            set_paragraph_text(paragraph, replacements[text])
            changes.append(text[:28])
    return changes


def main() -> None:
    if not CHART.exists():
        raise FileNotFoundError(CHART)
    doc = Document(SRC)
    changes = update_paragraphs(doc)
    update_table_6(doc)
    doc.save(DST)
    replace_docx_media(DST, "image9.png", CHART)
    shutil.copy2(DST, ASCII_COPY)

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    REPORT.write_text(
        "# C6/C33 3m 同方案复算与论文更新说明\n\n"
        "## 新增计算\n\n"
        "- 固定 6m 保守型方案中的 C6/C33 干预，不重新选择建筑。\n"
        "- 在 3m 网格下复算，区分“重新优化导致候选变化”和“同一方案跨尺度表现”。\n"
        "- 计算口径：向量化复现项目简化 2.5D 有效高度削减逻辑，与非 AI 基线补强口径一致。\n\n"
        "## 核心结果\n\n"
        "- 6m 固定 C6/C33：暗区比例 17.55% -> 16.94%，暗区网格数 86 -> 83。\n"
        "- 3m 固定 C6/C33：暗区比例 16.09% -> 15.84%，暗区网格数 314 -> 309，平均采光小时 6.509 h -> 6.519 h，未新增暗区。\n\n"
        "## 写入论文的位置\n\n"
        "- 摘要补充 3m 固定 C6/C33 复算结果。\n"
        "- 3.4 多尺度复核说明加入“同方案复算”。\n"
        "- 5.4 网格敏感性测试重写解释，并替换图9。\n"
        "- 表6 增加“3m 网格（固定 C6/C33）”行。\n"
        "- 6.5 与结论补充同方案复算结论。\n\n"
        "## 边界\n\n"
        "新增结果不改变论文的谨慎定位：3m 重新优化仍说明模型存在尺度敏感性；固定 C6/C33 复算只证明该保守型方案在更密网格下仍有小幅方向性改善，不能解释为专业日照审查结论。\n\n"
        f"## 数据文件\n\n- `{METRICS}`\n- `{SUMMARY}`\n- `{CHART}`\n\n"
        f"## 复算摘要 JSON\n\n```json\n{json.dumps(summary, ensure_ascii=False, indent=2)}\n```\n",
        encoding="utf-8",
    )
    print(DST)
    print(REPORT)


if __name__ == "__main__":
    main()
