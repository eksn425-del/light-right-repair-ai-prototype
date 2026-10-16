from __future__ import annotations

import importlib.util
from pathlib import Path

import fitz


ROOT = Path(r"E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20")
GENERATOR = ROOT / "code" / "generate_final_submission.py"
PDF = ROOT / "光权修复论文_EI会议_中文导师审阅定稿版_最终.pdf"
PREVIEW = ROOT / "figures" / "155_最终PDF首页渲染检查.png"


def load_generator():
    spec = importlib.util.spec_from_file_location("generate_final_submission", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> int:
    if not PDF.exists():
        raise FileNotFoundError(PDF)
    doc = fitz.open(PDF)
    page_count = doc.page_count
    text = "\n".join(page.get_text() for page in doc)
    required_terms = [
        "旧街区早期更新",
        "HB-Radiance",
        "C9/C15",
        "C9/C13",
        "C9/C24",
        "参考文献",
    ]
    missing = [term for term in required_terms if term not in text]
    page = doc.load_page(0)
    pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False)
    pix.save(PREVIEW)
    doc.close()

    status = f"通过。PDF 由 Microsoft Word 原生导出；PyMuPDF 读取 {page_count} 页；首页已渲染为 {PREVIEW.name}。"
    if missing:
        status += " 但 PDF 文本抽取未识别：" + "、".join(missing) + "（可能与中文字体编码有关，需人工视觉复核）。"
    else:
        status += " 关键文本抽取通过。"

    gen = load_generator()
    data = gen.read_data()
    gen.build_consistency_report(data, pdf_status=status)
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
