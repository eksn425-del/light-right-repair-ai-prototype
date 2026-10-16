from __future__ import annotations

import json
import shutil
from pathlib import Path

from docx import Document


WORK_DIR = Path("paper_revision_work_2026_06_14") / "v6_final_minor_fix"
INPUT_DOCX = WORK_DIR / "input.docx"
OUTPUT_DOCX = WORK_DIR / "光权修复论文_EI会议中文投稿终稿_v6_最终小修版.docx"
PROJECT_OUTPUT_DOCX = (
    Path("paper_revision_work_2026_06_14")
    / "final_output"
    / "光权修复论文_EI会议中文投稿终稿_v6_最终小修版.docx"
)
DESKTOP_OUTPUT_DOCX = Path(r"C:\Users\洪禄\Desktop\光权修复论文_EI会议中文投稿终稿_v6_最终小修版.docx")
REPORT_PATH = WORK_DIR / "v6_minor_fix_report.json"


def replace_paragraph(doc: Document, startswith: str, new_text: str) -> str:
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text.startswith(startswith):
            old = paragraph.text
            if paragraph.runs:
                paragraph.runs[0].text = new_text
                for run in paragraph.runs[1:]:
                    run.text = ""
            else:
                paragraph.add_run(new_text)
            return old
    raise ValueError(f"Paragraph not found: {startswith}")


def main() -> None:
    if not INPUT_DOCX.exists():
        raise FileNotFoundError(INPUT_DOCX)
    doc = Document(str(INPUT_DOCX))
    changes: list[dict[str, str]] = []

    changes.append(
        {
            "section": "摘要",
            "old": replace_paragraph(
                doc,
                "在方法上，算法 A 基于冬至日",
                "在方法上，算法 A 基于冬至日 8:00 至 16:00 的简化太阳路径和 2.5D 遮挡判断，生成采光热力图、平均采光小时和暗区比例；算法 B 在最小干预原则下生成保守型、均衡型和采光优先型三类候选策略，通过光照增益、干预体量、新增阴影惩罚和保护冲突惩罚进行启发式评分；算法 C 对候选策略进行方案后复算。结果显示，在 6 m 基准网格下，现状平均采光小时为 6.422 h，暗区比例为 17.55%；保守型方案将暗区比例相对改善约 3.48%，主要干预建筑为 C6 和 C33。进一步固定 C6/C33 方案并在 3 m 网格下复算，暗区比例由 16.09% 降至 15.84%，说明同一干预在更密网格下仍具有方向性改善，但改善幅度有限。原始权重敏感性测试显示，C6/C33 仅在 7 种权重配置中的 2 种保持稳定；进一步加入同一候选方案内建筑编号不重复的工程约束后，C6/C33 在 5/7 配置中保持，说明重复建筑退化可由组合约束缓解，但该方法仍应定位为候选策略生成与复核工具，而不是唯一最优解搜索器。",
            ),
            "new": "摘要补充了 2/7 与去重约束 5/7 的量化说明。",
        }
    )

    changes.append(
        {
            "section": "4.2",
            "old": replace_paragraph(
                doc,
                "算法 B 以算法 A 的暗区识别结果",
                "算法 B 以算法 A 的暗区识别结果、gap candidates、建筑属性表和保护约束为输入，在最小干预原则下生成候选方案。候选操作包括 subtract、add 和 reorganize；本文推荐方案主要采用 subtract 的建筑高度削减操作。启发式评分综合光照收益、干预体量、新增阴影惩罚和保护冲突惩罚四项指标，在保守型、均衡型和采光优先型三种权重配置下分别排序候选建筑。需要说明的是，权重并非经机器学习训练得到，而是用于早期设计阶段的可解释规则参数，最终方案必须通过后复算和人工复核筛选。原始实现未把“同一候选方案内建筑编号不重复”作为硬约束，因此在极端权重扰动下可能出现同一建筑被重复选择的退化候选；本文在敏感性分析中保留该现象并补做去重约束复算，用于区分评分权重不稳定与组合约束不足两类问题。",
            ),
            "new": "4.2 补充算法 B 重复建筑退化的原因和处理方式。",
        }
    )

    changes.append(
        {
            "section": "5.7",
            "old": replace_paragraph(
                doc,
                "为回应启发式评分权重可能影响候选排序的问题",
                "为回应启发式评分权重可能影响候选排序的问题，本文以 6 m 保守型权重为基准，对光照收益、干预体量惩罚和新增阴影惩罚分别进行 ±50% 的单因素扰动，并重新运行算法 B。原始结果显示，C6/C33 组合只在基准权重和体量惩罚降低两种情况下保持，即 7 种权重配置中有 2 种维持该组合；当光照收益、体量惩罚或阴影惩罚发生较大扰动时，候选可能转向 C6 重复干预或其他组合，且后复算暗区比例未产生改善（见表8）。为进一步判断重复建筑是否来自评分权重本身，本文补做“同一候选方案内建筑编号不重复”的工程约束复算。结果显示，去重约束下不再出现 C6/C6 退化候选，C6/C33 在 7 种配置中的 5 种保持，最优暗区比例仍为 16.94%。这一补充说明，原始表8暴露的是启发式搜索中的组合约束不足和参数敏感性，而不是 C6/C33 方案本身完全失效。总体而言，算法 B 不能被解释为稳定求得唯一最优解，但后复算与去重约束可以共同筛除退化候选，强化其作为早期候选策略生成工具的使用边界。",
            ),
            "new": "5.7 增加去重约束复算实验结果：重复目标 0，C6/C33 为 5/7，最佳暗区比例 16.94%。",
        }
    )

    changes.append(
        {
            "section": "6.2",
            "old": replace_paragraph(
                doc,
                "简化模型的价值在于轻量化",
                "简化模型的价值在于轻量化、可解释和易复核。成熟工具如 Ladybug/Honeybee 或专业日照软件更适合高精度模拟和合规审查，而本文工作流的重点在于早期阶段的数据转译、候选生成、指标对比和人工复核。当前流程使用 Python、CSV、OBJ 和 SketchUp 模型，不依赖复杂商业插件，降低了早期设计团队的数据整理和协作门槛。与此同时，模型局限也很明确：2.5D 遮挡判断无法达到专业日照软件精度，网格尺度、权重设置和 OBJ 白模几何质量都会影响结果。尤其是全场平均采光小时提升仅约 0.013 h，已接近简化模型可解释边界；由于本文尚未通过 Ladybug、Radiance 或实测数据建立模型误差量级，该数值不能被表述为显著采光性能提升。因此，论文必须保留“早期决策支持”的定位，而不宣称系统已完成专业日照审查。",
            ),
            "new": "6.2 补充未建立专业误差边界，因此不夸大 0.013 h。",
        }
    )

    changes.append(
        {
            "section": "6.5",
            "old": replace_paragraph(
                doc,
                "本研究的主要贡献不在于提出高精度日照模拟算法",
                "本研究的主要贡献不在于提出高精度日照模拟算法，而在于建立一个可复核、可替换数据、可嵌入设计流程的早期规则启发式 AI 决策工作流。该流程将 CAD/SU/OBJ/CSV 与人工可改性判断转译为算法输入，并通过全场 6 m 诊断、全场 3 m 敏感性测试、固定 C6/C33 的 3 m 同方案复算、C6/C33 局部 2 m 复核、权重敏感性测试、去重约束复算和人工同视角图像校核形成证据链。当前模型采用 2.5D 简化遮挡判断，适合旧街区早期趋势判断和候选生成，尤其适用于已有白模、建筑编号和高度表但尚未进入专业环境模拟阶段的课程设计或前期研究场景。需要强调的是，网格尺度变化和权重扰动都会改变部分候选建筑，这种双重敏感性恰恰说明早期阶段不宜把算法输出理解为唯一答案，而应把它用作“候选区间生成—方案后复算—人工复核”的人机协同流程；对于法定日照审查、高层复杂遮挡、多气候区泛化或精细构件级设计，仍需接入 Ladybug、Radiance 或其他专业工具，并在多个旧街区案例中验证方法稳定性。",
            ),
            "new": "6.5 正面回应网格和权重的双重敏感性。",
        }
    )

    changes.append(
        {
            "section": "结论",
            "old": replace_paragraph(
                doc,
                "在 6 m 基准网格下，保守型策略使暗区比例",
                "在 6 m 基准网格下，保守型策略使暗区比例从 17.55% 降至 16.94%，平均采光小时从 6.422 h 提升至 6.435 h。由于平均采光小时绝对提升较小，且尚未建立专业软件或实测数据的误差边界，本文不将其表述为显著性能提升，而是将重点放在暗区比例、干预体量和候选策略可复核性上。补充非 AI 基线对照显示，高度优先基线在 45.0 的干预体量下未降低暗区比例，暗区邻近基线在 33.75 的干预体量下暗区比例为 17.35%，随机基线均值在 31.04 的干预体量下暗区比例为 17.26%，其暗区比例下降均弱于保守型策略。进一步固定 C6/C33 干预并在 3 m 网格下复算，暗区比例由 16.09% 降至 15.84%，暗区网格数由 314 降至 309，说明同一方案在更密网格下仍具有小幅方向性改善。权重敏感性测试表明，C6/C33 不是所有权重扰动下的稳定唯一解；去重约束复算进一步说明，加入基本组合约束后可消除重复建筑退化，并使 C6/C33 在多数扰动配置中保持。因此，算法输出应被定位为可复核的候选决策支持，而不是唯一最优方案或专业日照审查结论。C6/C33 周边 2 m 局部网格进一步显示，局部平均采光小时由 5.555 h 提升至 5.801 h，最大单点提升达到 4.0 h。",
            ),
            "new": "结论同步补充误差边界、去重约束和候选决策支持定位。",
        }
    )

    OUTPUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
    PROJECT_OUTPUT_DOCX.parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(OUTPUT_DOCX))
    shutil.copy2(OUTPUT_DOCX, PROJECT_OUTPUT_DOCX)
    shutil.copy2(OUTPUT_DOCX, DESKTOP_OUTPUT_DOCX)
    REPORT_PATH.write_text(
        json.dumps(
            {
                "input": str(INPUT_DOCX),
                "output": str(OUTPUT_DOCX),
                "project_output": str(PROJECT_OUTPUT_DOCX),
                "desktop_output": str(DESKTOP_OUTPUT_DOCX),
                "changes": changes,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"output": str(OUTPUT_DOCX), "desktop_output": str(DESKTOP_OUTPUT_DOCX), "report": str(REPORT_PATH)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
