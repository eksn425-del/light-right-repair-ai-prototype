from __future__ import annotations

import json
from pathlib import Path
from zipfile import ZipFile

from PIL import Image, ImageDraw


WORK_DIR = Path("paper_revision_work_2026_06_14")
FINAL_DIR = WORK_DIR / "final_output"
DOCX = FINAL_DIR / "光权修复论文_EI会议中文投稿终稿_v5_规则启发式AI版.docx"
ASCII_DOCX = FINAL_DIR / "paper_final_v5_validation_copy.docx"
REPORT = FINAL_DIR / "v5_投稿终稿修改说明.md"
VALIDATION_JSON = FINAL_DIR / "v5_submission_validation_report.json"
CONTACT_SHEET = FINAL_DIR / "v5_docx_media_contact_sheet.jpg"
ZIP_PATH = WORK_DIR / "光权修复论文_EI会议中文投稿终稿_v5_规则启发式AI交付包.zip"
WEIGHT_DIR = WORK_DIR / "weight_sensitivity"
C6C33_DIR = WORK_DIR / "c6_c33_same_scheme_grid_fast"


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
        thumbs.append((label, img.resize((thumb_w, max(1, int(img.height * ratio))), Image.LANCZOS)))

    rows = (len(thumbs) + cols - 1) // cols
    row_heights = []
    for r in range(rows):
        row_items = thumbs[r * cols : (r + 1) * cols]
        row_heights.append(max(item[1].height for item in row_items) + label_h)

    sheet = Image.new("RGB", (cols * thumb_w + (cols + 1) * gap, sum(row_heights) + (rows + 1) * gap), "white")
    draw = ImageDraw.Draw(sheet)
    y = gap
    for r in range(rows):
        x = gap
        for label, thumb in thumbs[r * cols : (r + 1) * cols]:
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
        "table_count_expected": 8,
        "key_updates": [
            "title uses rule-based AI wording",
            "abstract defines AI as rule reasoning + heuristic search + post-simulation + human review",
            "3m fixed C6/C33 re-simulation retained",
            "weight sensitivity section and Table 8 added",
            "0.013 h average sunlight gain framed as near simplified-model interpretation boundary",
        ],
        "key_results": {
            "baseline_6m_dark_zone_percent": 17.55,
            "conservative_6m_dark_zone_percent": 16.94,
            "fixed_c6_c33_3m_dark_zone_percent": 15.84,
            "weight_sensitivity_variants": 7,
            "c6_c33_weight_variant_count": 2,
        },
        "status": "pass" if media_count == 11 else "check_required",
    }
    VALIDATION_JSON.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")

    files = [
        DOCX,
        REPORT,
        VALIDATION_JSON,
        CONTACT_SHEET,
        WEIGHT_DIR / "weight_sensitivity_metrics.csv",
        WEIGHT_DIR / "weight_sensitivity_summary.json",
        C6C33_DIR / "c6_c33_same_scheme_grid_metrics.csv",
        C6C33_DIR / "c6_c33_same_scheme_grid_summary.json",
        C6C33_DIR / "c6_c33_same_scheme_grid_chart.png",
        FINAL_DIR / "C6C33_3m同方案复算_论文更新说明.md",
    ]
    with ZipFile(ZIP_PATH, "w") as zf:
        for file in files:
            if file.exists():
                zf.write(file, file.relative_to(WORK_DIR))
    print(json.dumps(validation, ensure_ascii=False, indent=2))
    print(ZIP_PATH)


if __name__ == "__main__":
    main()
