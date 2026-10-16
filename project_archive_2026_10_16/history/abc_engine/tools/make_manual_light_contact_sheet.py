from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def main() -> None:
    root = (
        Path.cwd().parent
        / "光权修复_论文工作包_2026-06-03"
        / "04_图表与光照复核"
        / "同视角人工光照复核_2026-06-03"
    )
    before = sorted((root / "算法前").glob("*.bmp"))
    after = sorted((root / "算法后").glob("*.bmp"))
    pairs = list(zip(before, after))

    thumb_w, thumb_h = 520, 390
    pad, label_h, header_h = 28, 52, 80
    canvas_w = pad * 3 + thumb_w * 2
    canvas_h = header_h + len(pairs) * (thumb_h + label_h + pad) + pad
    canvas = Image.new("RGB", (canvas_w, canvas_h), "white")
    draw = ImageDraw.Draw(canvas)

    try:
        font_title = ImageFont.truetype("arial.ttf", 28)
        font = ImageFont.truetype("arial.ttf", 20)
        font_small = ImageFont.truetype("arial.ttf", 15)
    except Exception:
        font_title = font = font_small = None

    draw.text((pad, 18), "Manual sunlight validation: before / after", fill=(25, 25, 25), font=font_title)
    draw.text(
        (pad, 56),
        "Same-view comparison for validating the conservative AI candidate.",
        fill=(90, 90, 90),
        font=font_small,
    )

    for idx, (b_path, a_path) in enumerate(pairs, start=1):
        y = header_h + (idx - 1) * (thumb_h + label_h + pad)
        for col, (img_path, title) in enumerate(
            [(b_path, f"Before view {idx}"), (a_path, f"After view {idx}")]
        ):
            x = pad + col * (thumb_w + pad)
            img = Image.open(img_path).convert("RGB")
            img.thumbnail((thumb_w, thumb_h), Image.Resampling.LANCZOS)
            frame = Image.new("RGB", (thumb_w, thumb_h), (245, 245, 245))
            frame.paste(img, ((thumb_w - img.width) // 2, (thumb_h - img.height) // 2))
            canvas.paste(frame, (x, y + label_h))
            draw.rectangle(
                [x, y + label_h, x + thumb_w, y + label_h + thumb_h],
                outline=(210, 210, 210),
                width=2,
            )
            draw.text((x, y + 12), title, fill=(30, 30, 30), font=font)
            draw.text((x + 150, y + 17), img_path.name, fill=(120, 120, 120), font=font_small)

    out = root / "manual_light_validation_before_after_contact_sheet.png"
    canvas.save(out)
    print(out)


if __name__ == "__main__":
    main()
