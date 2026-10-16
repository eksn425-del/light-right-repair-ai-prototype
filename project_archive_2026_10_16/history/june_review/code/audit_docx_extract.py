from __future__ import annotations

import json
import zipfile
from pathlib import Path

from docx import Document


def paragraph_text(paragraph) -> str:
    return "".join(run.text for run in paragraph.runs).strip()


def table_to_markdown(table) -> list[str]:
    lines: list[str] = []
    rows = []
    for row in table.rows:
        rows.append([" ".join(cell.text.split()) for cell in row.cells])
    if not rows:
        return lines
    col_count = max(len(row) for row in rows)
    normalized = [row + [""] * (col_count - len(row)) for row in rows]
    lines.append("| " + " | ".join(normalized[0]) + " |")
    lines.append("| " + " | ".join(["---"] * col_count) + " |")
    for row in normalized[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return lines


def main() -> None:
    work_root = Path(r"E:/AI项目/中文导师审阅定稿_工作包_2026_06_20")
    docx_path = work_root / "data_raw" / "光权修复论文_EI会议_最终排版版.docx"
    docs_dir = work_root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)

    document = Document(str(docx_path))
    lines: list[str] = [
        f"# Extracted text from {docx_path.name}",
        "",
    ]
    paragraph_count = 0
    for index, paragraph in enumerate(document.paragraphs, start=1):
        text = paragraph_text(paragraph)
        if not text:
            continue
        paragraph_count += 1
        style_name = paragraph.style.name if paragraph.style is not None else ""
        lines.append(f"## P{index:04d} [{style_name}]")
        lines.append(text)
        lines.append("")

    table_summaries = []
    for table_index, table in enumerate(document.tables, start=1):
        md = table_to_markdown(table)
        table_summaries.append(
            {
                "table_index": table_index,
                "row_count": len(table.rows),
                "column_count": max((len(row.cells) for row in table.rows), default=0),
            }
        )
        lines.append(f"## Table {table_index}")
        lines.extend(md)
        lines.append("")

    with zipfile.ZipFile(docx_path) as archive:
        names = archive.namelist()
        media = [name for name in names if name.startswith("word/media/")]
        xml_parts = [name for name in names if name.endswith(".xml")]

    sections = []
    for section_index, section in enumerate(document.sections, start=1):
        sections.append(
            {
                "section_index": section_index,
                "page_width_twips": section.page_width.twips if section.page_width else None,
                "page_height_twips": section.page_height.twips if section.page_height else None,
                "left_margin_twips": section.left_margin.twips if section.left_margin else None,
                "right_margin_twips": section.right_margin.twips if section.right_margin else None,
                "top_margin_twips": section.top_margin.twips if section.top_margin else None,
                "bottom_margin_twips": section.bottom_margin.twips if section.bottom_margin else None,
            }
        )

    inventory = {
        "source_docx": str(docx_path),
        "paragraph_count_nonempty": paragraph_count,
        "table_count": len(document.tables),
        "tables": table_summaries,
        "image_count": len(media),
        "media_files": media,
        "section_count": len(document.sections),
        "sections": sections,
        "xml_part_count": len(xml_parts),
    }

    (docs_dir / "mother_plaintext.md").write_text("\n".join(lines), encoding="utf-8")
    (docs_dir / "mother_docx_inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
