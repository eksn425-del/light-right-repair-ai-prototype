from __future__ import annotations

from pathlib import Path
from xml.etree import ElementTree as ET
import json
import shutil
import zipfile


WORK = Path(__file__).resolve().parent
OUT_DIR = WORK / "final_output"
SOURCE_DOCX = OUT_DIR / "光权修复论文_EI会议中文最终审阅版.docx"
UPDATED_DOCX = OUT_DIR / "光权修复论文_EI会议中文最终审阅版_v2_同行评审回应版.docx"
BACKUP_DOCX = OUT_DIR / "光权修复论文_EI会议中文最终审阅版_v1备份.docx"
NEW_IMAGE6 = WORK / "optimized_figures" / "image6.png"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W}
ET.register_namespace("w", W)


def para_text(p):
    parts = []
    for node in p.iter():
        if node.tag == f"{{{W}}}t":
            parts.append(node.text or "")
        elif node.tag == f"{{{W}}}tab":
            parts.append("\t")
        elif node.tag == f"{{{W}}}br":
            parts.append("\n")
    return "".join(parts).strip()


def set_para_text(p, text):
    text_nodes = [node for node in p.iter() if node.tag == f"{{{W}}}t"]
    if not text_nodes:
        r = p.find("w:r", NS)
        if r is None:
            r = ET.SubElement(p, f"{{{W}}}r")
        t = ET.SubElement(r, f"{{{W}}}t")
        t.text = text
        t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
        return
    text_nodes[0].text = text
    text_nodes[0].set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    for node in text_nodes[1:]:
        node.text = ""


def main():
    shutil.copy2(SOURCE_DOCX, BACKUP_DOCX)
    shutil.copy2(SOURCE_DOCX, UPDATED_DOCX)
    with zipfile.ZipFile(UPDATED_DOCX, "r") as zin:
        files = {name: zin.read(name) for name in zin.namelist()}

    root = ET.fromstring(files["word/document.xml"])
    body = root.find("w:body", NS)
    changes = []
    for p in body.findall("w:p", NS):
        text = para_text(p)
        if text.startswith("保守型 AI 方案后，平均采光小时提高至 6.435 h"):
            set_para_text(
                p,
                "保守型 AI 方案后，平均采光小时提高至 6.435 h，暗区比例降低至 16.94%，暗区比例相对改善约为 3.48%，主要涉及 C6 和 C33 两栋建筑，简化干预体量为 28.125。"
                "均衡型和采光优先型在方案后复算中同样得到 6.435 h 和 16.94% 的结果，但其干预体量分别增加至 45.0 和 46.095，涉及建筑数量也增加。"
                "这一结果说明，在当前 6 m 网格和 2.5D 简化遮挡模型下，三类权重策略最终触发了相近的关键遮挡关系，后模拟指标区分度有限；因此本文不把三类策略解释为三种明确优劣不同的最终设计，而是把它们作为同一规则系统下的干预强度对比。"
                "为回应 AI 策略是否优于朴素规则的问题，本文补充了三类非 AI 基线：高度优先基线选取 C19、C3，暗区邻近基线选取 C27、C6，随机基线为 10 次随机选择两栋可干预建筑的均值。"
                "结果显示，高度优先基线在 45.0 的干预体量下暗区比例仍为 17.55%，暗区邻近基线为 17.35%，随机基线均值为 17.26%；AI 保守型以较小的 28.125 干预体量将暗区比例降至 16.94%。"
                "因此，AI 保守型的优势不在于显著抬升全场平均采光小时，而在于暗区比例下降与干预体量控制之间取得更稳妥的平衡。图6 和表5 对核心指标进行了对比。"
            )
            changes.append("5.2 增加非 AI 基线对照解释。")
        elif text == "图6  现状基准与三类 AI 策略指标对比":
            set_para_text(p, "图6  现状、AI保守型与非 AI 基线策略指标对比")
            changes.append("更新图6题名。")
        elif text.startswith("本文较关键的方法调整，是将研究从"):
            set_para_text(
                p,
                "本文较关键的方法调整，是将研究从\"AI 与人工方案谁更好\"转向\"AI 如何辅助空间决策\"。这一转向使变量更可控，也更符合建筑设计研究的逻辑。人工方案包含审美、功能、课程表达和教师反馈等多重因素，若直接与 AI 方案比较，容易把研究问题混杂化。"
                "本文首先在同一套模型和规则下比较现状基准、保守型 AI、均衡型 AI 和采光优先型 AI，并进一步补充高度优先、暗区邻近和随机选择三类非 AI 基线。"
                "这种比较并不证明 AI 具有普遍最优性，而是说明在当前数据和最小干预约束下，AI 保守型相较朴素规则能更好地控制干预体量，并获得更稳定的暗区比例下降。"
            )
            changes.append("6.1 加入非 AI 基线讨论。")
        elif text.startswith("在 6 m 基准网格下，保守型 AI 策略使暗区比例从 17.55%"):
            set_para_text(
                p,
                "在 6 m 基准网格下，保守型 AI 策略使暗区比例从 17.55% 降至 16.94%，平均采光小时从 6.422 h 提升至 6.435 h。虽然全场提升幅度有限，但该策略干预体量较小，主要涉及 C6 与 C33，适合转译为局部退台、屋顶平台和采光缝等建筑策略。"
                "补充非 AI 基线对照显示，高度优先基线在更大体量下未降低暗区比例，暗区邻近基线和随机基线的暗区比例下降也弱于 AI 保守型。"
                "这说明本文算法的价值不是制造大幅全场提升，而是在有限干预条件下形成比朴素规则更可解释、更可复核的候选策略。"
                "C6/C33 周边 2 m 局部网格进一步显示，局部平均采光小时由 5.555 h 提升至 5.801 h，最大单点提升达到 4.0 h。3 m 网格敏感性测试显示，当前简化模型对采样尺度存在敏感性，因此算法输出应被定位为候选决策支持，而不是唯一最优方案或专业日照审查结论。"
            )
            changes.append("结论加入非 AI 基线对照结论。")

    files["word/document.xml"] = ET.tostring(root, encoding="utf-8", xml_declaration=True)
    if NEW_IMAGE6.exists():
        files["word/media/image6.png"] = NEW_IMAGE6.read_bytes()
        changes.append("替换图6为非 AI 基线对照图。")

    with zipfile.ZipFile(UPDATED_DOCX, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, content in files.items():
            zout.writestr(name, content)

    report = {
        "source": str(SOURCE_DOCX),
        "updated": str(UPDATED_DOCX),
        "backup": str(BACKUP_DOCX),
        "changes": changes,
    }
    (OUT_DIR / "peer_review_response_revision_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
