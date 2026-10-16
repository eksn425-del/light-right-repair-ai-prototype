from pathlib import Path

from docx import Document


WORK_DIR = Path("paper_revision_work_2026_06_14")
FINAL_DIR = WORK_DIR / "final_output"
SRC = FINAL_DIR / "光权修复论文_EI会议中文最终审阅版_v2_同行评审回应版.docx"
DST = FINAL_DIR / "光权修复论文_EI会议中文最终审阅版_v3_同行评审增强版.docx"
ASCII_COPY = FINAL_DIR / "peer_review_v3_validation_copy.docx"


def set_paragraph_text(paragraph, new_text: str) -> None:
    """Replace paragraph text while keeping the paragraph style."""
    for run in paragraph.runs:
        run.text = ""
    if paragraph.runs:
        paragraph.runs[0].text = new_text
    else:
        paragraph.add_run(new_text)


def update_paragraphs(doc: Document) -> list[str]:
    changes: list[str] = []
    old_result = (
        "结果显示，高度优先基线在 45.0 的干预体量下暗区比例仍为 17.55%，"
        "暗区邻近基线为 17.35%，随机基线均值为 17.26%；"
        "AI 保守型以较小的 28.125 干预体量将暗区比例降至 16.94%。"
    )
    new_result = (
        "结果显示，高度优先基线在 45.0 的干预体量下暗区比例仍为 17.55%，"
        "暗区邻近基线在 33.75 的干预体量下暗区比例为 17.35%，"
        "随机基线均值在 31.04 的干预体量下暗区比例为 17.26%；"
        "AI 保守型以较小的 28.125 干预体量将暗区比例降至 16.94%。"
    )
    old_conclusion = (
        "补充非 AI 基线对照显示，高度优先基线在更大体量下未降低暗区比例，"
        "暗区邻近基线和随机基线的暗区比例下降也弱于 AI 保守型。"
    )
    new_conclusion = (
        "补充非 AI 基线对照显示，高度优先基线在 45.0 的干预体量下未降低暗区比例，"
        "暗区邻近基线在 33.75 的干预体量下暗区比例为 17.35%，"
        "随机基线均值在 31.04 的干预体量下暗区比例为 17.26%，"
        "其暗区比例下降均弱于 AI 保守型。"
    )

    for para in doc.paragraphs:
        text = para.text
        if text.strip() == "5.2  三类 AI 策略对比":
            set_paragraph_text(para, "5.2  AI 策略与非 AI 基线对比")
            changes.append("更新 5.2 标题，纳入非 AI 基线对照。")
        elif text.strip() == "表5  baseline 与三类 AI 策略的指标对比":
            set_paragraph_text(para, "表5  baseline、AI 策略与非 AI 基线的指标对比")
            changes.append("更新表 5 题名。")
        elif old_result in text:
            set_paragraph_text(para, text.replace(old_result, new_result))
            changes.append("5.2 正文补齐暗区邻近基线与随机基线的干预体量。")
        elif old_conclusion in text:
            set_paragraph_text(para, text.replace(old_conclusion, new_conclusion))
            changes.append("结论补齐非 AI 基线体量和暗区比例。")
    return changes


def update_table_5(doc: Document) -> str:
    """Update the existing metrics table so it matches the revised Figure 6."""
    rows = [
        ["方案类型", "平均采光小时", "暗区比例", "相对干预体量", "涉及建筑", "冲突"],
        ["现状基准（Baseline）", "6.422 h", "17.55%", "0.0", "—", "0"],
        ["保守型 AI", "6.435 h", "16.94%", "28.125", "C6、C33", "0"],
        ["均衡型 AI", "6.435 h", "16.94%", "45.0", "C6、C33", "0"],
        ["采光优先型 AI", "6.435 h", "16.94%", "46.095", "C6、C33、C9", "0"],
        ["高度优先基线", "6.424 h", "17.55%", "45.0", "C19、C3", "0"],
        ["暗区邻近基线", "6.439 h", "17.35%", "33.75", "C27、C6", "0"],
        ["随机基线均值", "6.435 h", "17.26%", "31.04", "10 次随机均值", "—"],
    ]

    for table in doc.tables:
        if len(table.rows) >= 2 and len(table.columns) >= 6:
            first = table.cell(0, 0).text.strip()
            second = table.cell(0, 1).text.strip()
            if first == "方案类型" and "采光小时" in second:
                while len(table.rows) < len(rows):
                    table.add_row()
                # Keep any extra rows if Word has hidden structure, but clear visible cells beyond target.
                for r_idx, values in enumerate(rows):
                    for c_idx, value in enumerate(values):
                        table.cell(r_idx, c_idx).text = value
                for r_idx in range(len(rows), len(table.rows)):
                    for c_idx in range(len(table.columns)):
                        table.cell(r_idx, c_idx).text = ""
                return "表 5 已加入高度优先、暗区邻近和随机基线三行。"
    raise RuntimeError("未找到表 5 指标表。")


def main() -> None:
    doc = Document(SRC)
    changes = update_paragraphs(doc)
    changes.append(update_table_5(doc))
    doc.save(DST)
    doc.save(ASCII_COPY)
    report = FINAL_DIR / "peer_review_v3_update_report.md"
    report.write_text(
        "# 同行评审回应 v3 更新说明\n\n"
        + "\n".join(f"- {item}" for item in changes)
        + "\n\n核心判断：本次不夸大 3.48% 暗区改善，而是用非 AI 基线说明 AI 保守型在暗区比例下降与干预体量控制之间具有更好的折中表现。\n",
        encoding="utf-8",
    )
    print(DST)
    print(report)


if __name__ == "__main__":
    main()
