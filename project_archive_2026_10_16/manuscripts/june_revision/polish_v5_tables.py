from pathlib import Path

from docx import Document


FINAL_DIR = Path("paper_revision_work_2026_06_14/final_output")
DOCX = FINAL_DIR / "光权修复论文_EI会议中文投稿终稿_v5_规则启发式AI版.docx"
ASCII_COPY = FINAL_DIR / "paper_final_v5_validation_copy.docx"


def main() -> None:
    doc = Document(DOCX)
    changed = 0
    for table in doc.tables:
        if not table.rows:
            continue
        header = [cell.text.strip() for cell in table.rows[0].cells]
        if header[:2] == ["方案类型", "平均采光小时"]:
            replacements = {
                "保守型 AI": "保守型策略",
                "均衡型 AI": "均衡型策略",
                "采光优先型 AI": "采光优先型策略",
            }
            for row in table.rows:
                old = row.cells[0].text.strip()
                if old in replacements:
                    row.cells[0].text = replacements[old]
                    changed += 1
    doc.save(DOCX)
    doc.save(ASCII_COPY)
    print(f"table_labels_changed={changed}")


if __name__ == "__main__":
    main()
