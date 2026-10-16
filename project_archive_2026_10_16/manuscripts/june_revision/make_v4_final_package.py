from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw


WORK_DIR = Path("paper_revision_work_2026_06_14")
FINAL_DIR = WORK_DIR / "final_output"
DOCX = FINAL_DIR / "光权修复论文_EI会议中文终稿_v4_C6C33三米复算版.docx"
ASCII_DOCX = FINAL_DIR / "paper_final_v4_validation_copy.docx"
REPORT = FINAL_DIR / "C6C33_3m同方案复算_论文更新说明.md"
VALIDATION_JSON = FINAL_DIR / "v4_final_validation_report.json"
CONTACT_SHEET = FINAL_DIR / "v4_docx_media_contact_sheet.jpg"
ZIP_PATH = WORK_DIR / "光权修复论文_EI会议中文终稿_v4_C6C33三米复算交付包.zip"
RESULT_DIR = WORK_DIR / "c6_c33_same_scheme_grid_fast"


def make_contact_sheet(docx_path: Path, output_path: Path) -> int:
    with ZipFile(docx_path) as zf:
        names = [
            name
            for name in zf.namelist()
            if name.startswith("word/media/") and name.lower().endswith((".png", ".jpg", ".jpeg"))
        ]
        images = []
        for name in names:
            with zf.open(name) as fp:
                img = Image.open(fp).convert("RGB")
                images.append((Path(name).name, img.copy()))

    thumb_w = 520
    label_h = 28
    gap = 28
    cols = 2
    thumbs = []
    for label, img in images:
        ratio = thumb_w / img.width
        thumb_h = max(1, int(img.height * ratio))
        thumbs.append((label, img.resize((thumb_w, thumb_h), Image.LANCZOS)))

    rows = (len(thumbs) + cols - 1) // cols
    row_heights = []
    for r in range(rows):
        row_items = thumbs[r * cols : (r + 1) * cols]
        row_heights.append(max(item[1].height for item in row_items) + label_h)

    sheet_w = cols * thumb_w + (cols + 1) * gap
    sheet_h = sum(row_heights) + (rows + 1) * gap
    sheet = Image.new("RGB", (sheet_w, sheet_h), "white")
    draw = ImageDraw.Draw(sheet)
    y = gap
    for r in range(rows):
        x = gap
        row_items = thumbs[r * cols : (r + 1) * cols]
        for label, thumb in row_items:
            draw.text((x, y), label, fill="black")
            sheet.paste(thumb, (x, y + label_h))
            x += thumb_w + gap
        y += row_heights[r] + gap
    sheet.save(output_path, quality=92)
    return len(images)


def main() -> None:
    media_count = make_contact_sheet(ASCII_DOCX, CONTACT_SHEET)
    validation = {
        "docx": str(DOCX),
        "media_count": media_count,
        "required_results": {
            "metrics_csv": str(RESULT_DIR / "c6_c33_same_scheme_grid_metrics.csv"),
            "summary_json": str(RESULT_DIR / "c6_c33_same_scheme_grid_summary.json"),
            "chart_png": str(RESULT_DIR / "c6_c33_same_scheme_grid_chart.png"),
        },
        "key_result": {
            "grid_3m_baseline_dark_zone_percent": 16.09,
            "grid_3m_fixed_c6_c33_post_dark_zone_percent": 15.84,
            "grid_3m_dark_grid_count_before": 314,
            "grid_3m_dark_grid_count_after": 309,
            "grid_3m_average_sunlight_before_h": 6.509,
            "grid_3m_average_sunlight_after_h": 6.519,
        },
        "status": "pass" if media_count == 11 else "check_required",
    }
    VALIDATION_JSON.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")

    files = [
        DOCX,
        REPORT,
        VALIDATION_JSON,
        CONTACT_SHEET,
        RESULT_DIR / "c6_c33_same_scheme_grid_metrics.csv",
        RESULT_DIR / "c6_c33_same_scheme_grid_summary.json",
        RESULT_DIR / "c6_c33_same_scheme_grid_chart.png",
        RESULT_DIR / "grid_3m_fixed_c6_c33" / "c6_c33_fixed_grid_diff.csv",
        RESULT_DIR / "grid_6m_fixed_c6_c33" / "c6_c33_fixed_grid_diff.csv",
    ]
    with ZipFile(ZIP_PATH, "w") as zf:
        for file in files:
            if file.exists():
                zf.write(file, file.relative_to(WORK_DIR))
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    print(ZIP_PATH)


if __name__ == "__main__":
    main()
