from pathlib import Path

from docx import Document


DOCX = Path(r"C:\Users\洪禄\Desktop\光权修复论文_EI会议_最终排版版.docx")
OUT = Path(r"E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20\logs\mother_docx_outline.txt")


def main():
    doc = Document(str(DOCX))
    lines = [f"paragraph_count={len(doc.paragraphs)}", f"table_count={len(doc.tables)}", ""]
    for i, p in enumerate(doc.paragraphs):
        text = p.text.strip()
        if not text:
            continue
        style = p.style.name if p.style is not None else ""
        if i < 80 or text.startswith(("图", "表", "摘要", "关键词", "参考文献")) or any(ch.isdigit() for ch in text[:4]):
            lines.append(f"[{i:03d}] {style}: {text}")
    for ti, table in enumerate(doc.tables):
        rows = []
        for row in table.rows[:3]:
            rows.append(" | ".join(cell.text.strip().replace("\n", " / ") for cell in row.cells[:6]))
        lines.append("")
        lines.append(f"TABLE {ti+1}:")
        lines.extend(rows)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    main()
