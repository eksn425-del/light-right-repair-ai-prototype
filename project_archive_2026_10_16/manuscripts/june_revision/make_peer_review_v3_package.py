import json
import shutil
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

from PIL import Image, ImageDraw


WORK_DIR = Path("paper_revision_work_2026_06_14")
FINAL_DIR = WORK_DIR / "final_output"
DOCX = FINAL_DIR / "光权修复论文_EI会议中文最终审阅版_v3_同行评审增强版.docx"
ASCII_DOCX = FINAL_DIR / "peer_review_v3_validation_copy.docx"
REPORT_MD = FINAL_DIR / "同行评审回应_v3_最终说明.md"
VALIDATION_JSON = FINAL_DIR / "peer_review_v3_validation_report.json"
CONTACT_SHEET = FINAL_DIR / "v3_docx_media_contact_sheet.jpg"
ZIP_PATH = WORK_DIR / "光权修复论文_EI会议中文最终审阅版_v3_同行评审回应交付包.zip"
BASELINE_DIR = WORK_DIR / "non_ai_baseline_comparison"
FIG6 = WORK_DIR / "optimized_figures" / "image6.png"


def extract_paragraphs(docx_path: Path) -> list[str]:
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with ZipFile(docx_path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    paragraphs: list[str] = []
    for para in root.findall(".//w:p", ns):
        text = "".join(t.text or "" for t in para.findall(".//w:t", ns)).strip()
        if text:
            paragraphs.append(text)
    return paragraphs


def make_contact_sheet(docx_path: Path, output_path: Path) -> int:
    with ZipFile(docx_path) as zf:
        image_names = [
            name
            for name in zf.namelist()
            if name.startswith("word/media/")
            and name.lower().endswith((".png", ".jpg", ".jpeg"))
        ]
        images = []
        for name in image_names:
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
        thumb = img.resize((thumb_w, thumb_h), Image.LANCZOS)
        thumbs.append((label, thumb))

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
    if not ASCII_DOCX.exists():
        shutil.copy2(DOCX, ASCII_DOCX)

    paragraphs = extract_paragraphs(ASCII_DOCX)
    media_count = make_contact_sheet(ASCII_DOCX, CONTACT_SHEET)

    required_markers = {
        "v3_title": "5.2  AI 策略与非 AI 基线对比",
        "table5_caption": "表5  baseline、AI 策略与非 AI 基线的指标对比",
        "dark_nearest_volume": "33.75",
        "random_mean_volume": "31.04",
        "height_priority": "高度优先基线",
        "dark_nearest": "暗区邻近基线",
        "random_mean": "随机基线均值",
        "scale_sensitivity": "网格尺度存在敏感性",
        "human_review": "人工同视角光照复核",
    }
    marker_hits = {
        key: any(marker in para for para in paragraphs)
        for key, marker in required_markers.items()
    }

    validation = {
        "docx": str(DOCX),
        "paragraph_count": len(paragraphs),
        "media_count": media_count,
        "marker_hits": marker_hits,
        "status": "pass" if all(marker_hits.values()) and media_count == 11 else "check_required",
    }
    VALIDATION_JSON.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    REPORT_MD.write_text(
        """# 同行评审回应 v3 最终说明

## 本轮审核暴露的核心问题

1. 三类 AI 策略的后模拟指标过于接近，容易被审稿人质疑策略区分度不足。
2. 3 m 网格敏感性测试改变了推荐建筑，说明当前简化算法对网格尺度敏感，不能宣称找到唯一最优解。
3. 原稿缺少非 AI 基线，无法说明 AI 策略相对朴素规则的价值。

## 本轮已完成的补强

- 在 5.2 节将标题调整为“AI 策略与非 AI 基线对比”。
- 补充三类非 AI 基线：高度优先基线、暗区邻近基线、随机 10 次均值基线。
- 重绘图 6，改为“现状、AI 保守型与非 AI 基线策略指标对比”。
- 更新表 5，加入高度优先、暗区邻近和随机基线三行。
- 在正文和结论中补齐 33.75、31.04 等干预体量数据，避免只在图中表达。

## 新增对照实验结果

| 策略 | 平均采光小时 | 暗区比例 | 干预体量 | 涉及建筑 |
|---|---:|---:|---:|---|
| 现状基准 | 6.422 h | 17.55% | 0.0 | — |
| AI 保守型 | 6.435 h | 16.94% | 28.125 | C6、C33 |
| 高度优先基线 | 6.424 h | 17.55% | 45.0 | C19、C3 |
| 暗区邻近基线 | 6.439 h | 17.35% | 33.75 | C27、C6 |
| 随机基线均值 | 6.435 h | 17.26% | 31.04 | 10 次随机均值 |

## 现在应该如何解释“改善幅度小”的问题

本轮没有把 3.48% 暗区改善夸大成十几或二十个百分点。更稳妥的论文表述是：在当前 6 m 网格和 2.5D 简化遮挡模型下，AI 保守型并未显著抬升全场平均采光小时，但它以更小干预体量取得了比高度优先、暗区邻近和随机基线更低的暗区比例。因此，论文贡献应定位为“早期设计阶段的可复核决策工作流”，而不是“高精度日照优化算法”。

## 仍需保留的边界

- 当前模型仍是 2.5D 简化遮挡判断，不能替代 Ladybug、Radiance 或法定日照审查软件。
- 3 m 网格敏感性显示推荐对象会变化，必须保留“候选策略生成”而非“唯一最优解”的表述。
- 单案例研究仍需后续多街区、多软件复核。

## 交付文件

- `光权修复论文_EI会议中文最终审阅版_v3_同行评审增强版.docx`
- `peer_review_v3_validation_report.json`
- `v3_docx_media_contact_sheet.jpg`
- `non_ai_baseline_comparison_fast.csv`
- `random_baseline_trials_fast.csv`
- `non_ai_baseline_summary_fast.json`
""",
        encoding="utf-8",
    )

    files_to_zip = [
        DOCX,
        REPORT_MD,
        VALIDATION_JSON,
        CONTACT_SHEET,
        FIG6,
        BASELINE_DIR / "non_ai_baseline_comparison_fast.csv",
        BASELINE_DIR / "random_baseline_trials_fast.csv",
        BASELINE_DIR / "non_ai_baseline_summary_fast.json",
    ]
    with ZipFile(ZIP_PATH, "w") as zf:
        for file in files_to_zip:
            if file.exists():
                zf.write(file, file.relative_to(WORK_DIR))

    print(json.dumps(validation, ensure_ascii=False, indent=2))
    print(ZIP_PATH)


if __name__ == "__main__":
    main()
