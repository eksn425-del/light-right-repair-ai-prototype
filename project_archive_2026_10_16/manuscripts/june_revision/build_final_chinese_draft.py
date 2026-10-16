from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET
import json
import shutil
import zipfile


WORK = Path(__file__).resolve().parent
SRC = WORK / "draft_input.docx"
FIG_DIR = WORK / "optimized_figures"
OUT_DIR = WORK / "final_output"
OUT_DIR.mkdir(exist_ok=True)

FINAL_DOCX = OUT_DIR / "光权修复论文_EI会议中文最终审阅版.docx"
BACKUP_DOCX = OUT_DIR / "光权修复论文_中文初稿_原始备份.docx"

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
    return "".join(parts)


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


def insert_after(body, paragraphs, after_index, text):
    """Insert a normal paragraph after a 0-based paragraph index using nearby style."""
    new_p = deepcopy(paragraphs[after_index])
    set_para_text(new_p, text)
    body.insert(list(body).index(paragraphs[after_index]) + 1, new_p)


def update_document_xml(xml_bytes):
    root = ET.fromstring(xml_bytes)
    body = root.find("w:body", NS)
    paragraphs = list(body.findall("w:p", NS))
    inserted_repro = False
    changes = []

    for p in paragraphs:
        text = para_text(p).strip()
        if text.startswith("城市形态会直接改变太阳可达性。Compagnon [4]") and "Czachura 等 [3]" in text:
            set_para_text(
                p,
                "城市形态会直接改变太阳可达性。Czachura 等 [3] 对城市规划中的太阳性能指标进行了综述，强调太阳可达性指标适合在早期规划设计中提供反馈，但指标复杂度需要与设计阶段相匹配。"
                "Compagnon [4] 对城市肌理中的太阳与自然光可达性进行了研究，指出城市尺度下的光环境评价应把建筑群体、街巷形态和开放空间作为整体考虑。"
                "Sanaieian 等 [5] 从热性能、太阳可达性和通风等角度梳理了城市街区形态的环境影响，说明采光问题不应只在单体建筑层面处理。"
                "对于本研究而言，平均采光小时、暗区比例和采样网格诊断属于低复杂度早期指标，适合用于问题定位和候选策略比较，但不能直接等同于专业日照审查结论。"
            )
            changes.append("调整文献综述中 [3]-[5] 的局部引文顺序。")

        if text.startswith("在人机协同方面，Thoring 等 [11]") and "Jakubik 等 [12]" in text:
            set_para_text(
                p,
                "在人机协同方面，Thoring 等 [11] 提出生成式 AI 应当增强设计师能力而不是替代设计师。"
                "Jakubik 等 [12] 在 AEC 平面图对象识别中采用 human-in-the-loop 机制，说明 AI 输出与人工复核结合可以提升系统可信度。"
                "Nabizadeh Rafsanjani 与 Nabizadeh [13] 从 AEC 行业角度讨论以人为中心的 AI，强调 AI 系统需要保留人的判断、反馈和控制权。"
                "本文据此将人工复核纳入方法本身：建筑可改性判断、模型同一性确认、空间转译和最终方案取舍均由人工参与完成。"
            )
            changes.append("调整 Human-in-the-loop 段落中 [11]-[13] 的局部引文顺序。")

        if text.startswith("保守型 AI 方案后，平均采光小时提高至 6.435 h"):
            set_para_text(
                p,
                "保守型 AI 方案后，平均采光小时提高至 6.435 h，暗区比例降低至 16.94%，暗区比例相对改善约为 3.48%，主要涉及 C6 和 C33 两栋建筑，简化干预体量为 28.125。"
                "均衡型和采光优先型在方案后复算中同样得到 6.435 h 和 16.94% 的结果，但其干预体量分别增加至 45.0 和 46.095，涉及建筑数量也增加。"
                "这一结果说明，在当前 6 m 网格和 2.5D 简化遮挡模型下，三类权重策略最终触发了相近的关键遮挡关系，后模拟指标区分度有限；因此本文不把三类策略解释为三种明确优劣不同的最终设计，而是把它们作为同一规则系统下的干预强度对比。"
                "在相同采光收益下，保守型方案具有更小干预体量和更少涉及建筑，更符合旧街区有机更新和微更新逻辑。图6 和表5 对四种方案的核心指标进行了对比。"
            )
            changes.append("补强三类 AI 策略结果趋同的原因解释。")

        if text.startswith("从证据链看，本文已形成较完整的工作流"):
            set_para_text(
                p,
                "从证据链看，本文已形成较完整的工作流：CAD/SU/OBJ 与建筑表构成数据底座，算法 A 提供暗区诊断，算法 B 提供候选策略，算法 C 提供方案后复算，网格敏感性测试揭示模型局限，人工同视角光照分析提供外部复核，C6 和 C33 的设计转译把算法输出转化为空间语言。"
                "这条链条能够支撑论文的主论点：本文贡献不是证明某个自动生成方案绝对最优，而是展示如何把旧街区采光问题组织成可计算、可复核、可由设计团队持续迭代的工作流。"
                "后续研究仍需结合更高精度的日照模拟、专业软件复核和多案例验证进一步校准。"
            )
            changes.append("强化论文贡献边界与证据链表述。")

    # Refresh paragraph list before insertion.
    paragraphs = list(body.findall("w:p", NS))
    for i, p in enumerate(paragraphs):
        text = para_text(p).strip()
        if text.startswith("为检查算法结果能否回到建筑模型中被复核"):
            insert_after(
                body,
                paragraphs,
                i,
                "为提高可复现性，本文保留了输入数据、建筑属性表、候选方案、后模拟结果、网格敏感性结果和论文图表输出。论文中的数值均来自同一套 Python 数据管线与 CSV/JSON 输出，人工光照图仅作为方向性复核证据，不用于替代算法指标或法定日照审查结论。",
            )
            inserted_repro = True
            changes.append("新增可复现性说明段落。")
            break

    return ET.tostring(root, encoding="utf-8", xml_declaration=True), changes, inserted_repro


def main():
    shutil.copy2(SRC, BACKUP_DOCX)
    with zipfile.ZipFile(SRC, "r") as zin:
        files = {name: zin.read(name) for name in zin.namelist()}

    files["word/document.xml"], changes, inserted_repro = update_document_xml(files["word/document.xml"])

    replaced_images = []
    for i in range(1, 10):
        source = FIG_DIR / f"image{i}.png"
        target = f"word/media/image{i}.png"
        if source.exists() and target in files:
            files[target] = source.read_bytes()
            replaced_images.append(target)

    with zipfile.ZipFile(FINAL_DOCX, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for name, content in files.items():
            zout.writestr(name, content)

    report = {
        "final_docx": str(FINAL_DOCX),
        "backup_docx": str(BACKUP_DOCX),
        "text_changes": changes,
        "inserted_reproducibility_paragraph": inserted_repro,
        "replaced_images": replaced_images,
    }
    (OUT_DIR / "revision_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
