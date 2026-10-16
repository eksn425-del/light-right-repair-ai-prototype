# 光权修复论文中文定稿投稿前核查报告

核查对象：`C:/Users/洪禄/Desktop/光权修复论文_中文定稿_最终给老师版.docx`

核查副本：`E:/AI项目/paper_audit_2026_06_10/teacher_final_review_copy.docx`

## 总体判断

当前版本已经可以作为“给老师检查/内部评审”的稿件使用，但不建议直接作为 EI 会议正式投稿终稿上传。

原因不是研究方向错误，而是还存在几类投稿前小问题：

1. 引言有一处句子被空段打断，需要合并。
2. 参考文献基本可查，但少数条目需要补 DOI、页码或作者。
3. 正文引用位置大体合理，但数字编号不是严格按首次出现顺序排列，若目标会议要求顺序编码制，需要调整。
4. 还需要套目标会议模板，并检查图像分辨率、英文摘要、作者单位、关键词格式。

## Word 结构核查

- 段落数：139
- Word 表格数：7
- 嵌入媒体：11 张图片
- 图题：图1 至 图11，数量与嵌入图片基本匹配
- 表题：表1 至 表7，数量与 Word 表格匹配
- 参考文献：24 条
- 正文引用覆盖：1 至 24 均已被正文引用

## 明显排版/正文问题

### 1. 引言中存在断句空段

当前位置在引言 P14-P16 附近：

> 通过体量调整、退台、采光缝和公共空间优化，改善局部街巷与

下一段才接：

> 公共活动空间的日照可达性。

建议合并为同一段：

> 通过体量调整、退台、采光缝和公共空间优化，改善局部街巷与公共活动空间的日照可达性。

这是正式投稿前必须修的小问题。

### 2. 图表交叉引用

抽取得到的实际图表编号如下：

- 图1：CAD、SU/OBJ 与表格数据向算法输入的转译关系
- 图2：AI 辅助采光修复工作流
- 图3：6 m 网格下现状采光小时热力图
- 图4：保守型 AI 策略后采光小时热力图
- 图5：现状与保守型 AI 策略的采光小时差值图
- 图6：现状基准与三类 AI 策略指标对比
- 图7：C6、C33 周边局部采光变化示意
- 图8：6 m 与 3 m 网格敏感性测试结果
- 图9：6 m 与 3 m 网格敏感性测试三项指标对比
- 图10：人工光照复核图：算法前同视角结果
- 图11：人工光照复核图：算法后同视角结果

实际表编号：

- 表1：项目数据接口与论文表达作用
- 表2：简化光照诊断与候选生成的关键参数
- 表3：采光诊断与复核实验矩阵
- 表4：C6、C33 算法干预结果的设计语言转译
- 表5：baseline 与三类 AI 策略的指标对比
- 表6：6 m 与 3 m 网格敏感性测试结果
- 表7：C6/C33 周边 2 m 局部敏感性测试结果

正文中已检查到的显式引用包括：图3、图6、表5、表4、表6、图8、表7、图10、图11。当前这些引用与实际图表编号一致，未发现“图2/表2旧编号残留”的错误。

## 参考文献真实性与可检索性

总体结论：24 条参考文献没有发现明显虚构条目，大部分 DOI 或正式出版页面可检索。

需要小修的条目：

### [1] Sampson & Charo

可以查到。Columbia Journal of Environmental Law 官方页面显示 DOI、卷期与作者。当前条目基本正确，但建议补页码：

建议改为：

SAMPSON T C, CHARO R A. Access to Sunlight: Resolving Legal Issues to Encourage the Use of Solar Energy[J/OL]. Columbia Journal of Environmental Law, 1986, 11(2): 417-445. DOI: 10.7916/cjel.v11i2.5670.

### [9] Ladybug

可以查到。当前条目可检索，但不完整。IBPSA 页面显示 DOI；一些索引页显示页码为 3128-3135，并列出作者 Roudsari、Pak、Viola。

建议改为：

SADEGHIPOUR ROUDSARI M, PAK M, VIOLA A. Ladybug: A parametric environmental plugin for Grasshopper to help designers create an environmentally-conscious design[C]//Proceedings of BS2013: 13th Conference of International Building Performance Simulation Association. 2013: 3128-3135. DOI: 10.26868/25222708.2013.2499.

### [22] Opossum

可以查到。CUMINCAD、ICD Stuttgart 与 ResearchGate 均可定位到 CAADRIA 2017 论文。当前条目可以保留，但建议补完整会议书名和 DOI：

建议改为：

WORTMANN T. Opossum: Introducing and evaluating a model-based optimization tool for Grasshopper[C]//Janssen P, Loh P, Raonic A, Schnabel M A, eds. Protocols, Flows and Glitches: Proceedings of the 22nd International Conference of the Association for Computer-Aided Architectural Design Research in Asia. Hong Kong: CAADRIA, 2017: 283-292. DOI: 10.52842/conf.caadria.2017.283.

### [24] BIM Handbook

可以查到。Wiley Online Books 页面显示第三版、出版时间、ISBN 和 DOI。当前条目没有 DOI，建议补上：

SACKS R, EASTMAN C, LEE G, TEICHOLZ P. BIM Handbook: A Guide to Building Information Modeling for Owners, Designers, Engineers, Contractors, and Facility Managers[M]. 3rd ed. Hoboken: Wiley, 2018. DOI: 10.1002/9781119287568.

## 引注位置判断

总体上，引用位置是合理的：

- [1-2] 用于支撑太阳可达性、法规、产权和邻里协调，位置合适。
- [3-6,10,14] 用于支撑城市形态、太阳可达性、太阳包络和城市设计影响，位置合适。
- [7-9,15-22] 用于支撑性能化设计、参数化环境分析、Radiance/动态采光指标、性能优化工具，位置基本合适。
- [11-13] 用于支撑生成式 AI、人机协同和 human-in-the-loop，位置合适。
- [23-24] 用于支撑 AEC 数据化、BIM/对象属性和建模数据一致性，位置合适。

但存在一个格式风险：如果目标会议采用“顺序编码制”，参考文献编号应尽量按照正文首次出现顺序排列。当前首次出现顺序为：

1, 2, 4, 5, 3, 6, 10, 14, 7, 8, 9, 15-22, 11, 13, 12, 23, 24

这说明文献列表是按主题组织的，不是严格按首次引用顺序。正式投稿前建议二选一：

1. 调整正文，使 [3] 先于 [4][5] 出现，并尽量让 [7-14] 按编号顺序出现。
2. 重新排序参考文献编号，使其符合首次引用顺序。

如果会议模板不严格要求顺序编码，这个问题影响较小；如果是 EI 会议常见模板，则建议修。

## 是否可以投稿

结论：还差一轮“小修+模板化”，不建议现在直接投稿。

可以认为当前稿件已经完成：

- 研究主线明确：不是比较 AI 与人工谁更强，而是构建 AI 辅助空间决策工作流。
- 实验结构完整：baseline、保守型、均衡型、采光优先型、3 m 敏感性、2 m 局部复核、人工同视角复核。
- 核心数据保持一致：6.422 h、17.55%、6.435 h、16.94%、3.48%、28.125 等关键值均在正文和表格中出现。
- 文献体系基本真实：太阳可达性、性能化设计、人机协同、AEC 数据工作流都有对应文献支撑。

正式投稿前建议完成：

1. 合并引言断句空段。
2. 补全 [1] 页码、[9] 作者/页码/DOI、[22] DOI、[24] DOI。
3. 检查参考文献编号是否要按首次引用顺序重排。
4. 套目标会议 Word/LaTeX 模板。
5. 导出 PDF 后检查所有图片是否清晰，图题是否紧跟图片，表格是否跨页。
6. 根据会议要求补英文摘要、作者单位、通信作者、基金/致谢等信息。

## 核查用到的本地文件

- `E:/AI项目/paper_audit_2026_06_10/extracted_paragraphs.txt`
- `E:/AI项目/paper_audit_2026_06_10/audit_extract.json`
- `E:/AI项目/paper_audit_2026_06_10/teacher_final_review_copy.docx`

