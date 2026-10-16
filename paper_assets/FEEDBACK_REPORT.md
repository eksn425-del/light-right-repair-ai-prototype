# SOICT 2026 论文素材包反馈文档

**版本：** `soict-paper-assets-v1`  
**反馈日期：** 2026-09-10  
**用途：** 提供给网页端 ChatGPT，作为论文写作、图表排版和投稿检查的统一交接说明。

## 1. 本次完成内容

已基于冻结证据 `soict-2026-write-ready-v1` 制作最终论文素材包。此次工作是资料整理、格式转换和发布审计，不是重新实验，因此没有修改任何实验结果、候选排名、权重、采样方案或运行数据。

冻结证据身份如下：

- 研究分支：`research-repro-v1`
- 冻结源提交：`6b64fe43451e2e0330930a5677cbe3432307282b`
- 冻结标签：`soict-2026-write-ready-v1`
- 冻结运行 ID：`baseline_20260909_clean`
- 生产评分：`0.45 A_norm + 0.35 H_norm + 0.15 (1-V_norm) + 0.05 (1-N_norm)`

## 2. 素材包位置

### 完整私有素材包

- 仓库：`https://github.com/eksn425-del/soict-2026-paper-assets`
- 分支：`paper-assets-v1`
- 核心素材提交：`1f886551991d0e2a653de72981e084c6ecb89b6d`
- 标签：`soict-2026-paper-assets-v1`
- 素材路径：`paper_assets/`

完整包包含：

- Figures 1--9 的 PNG、PDF、SVG 容器版本；
- 11 份论文表格 CSV；
- `FIGURE_CAPTIONS.md`；
- `TABLE_CAPTIONS.md`；
- `PAPER_ASSET_MANIFEST.md`；
- `BIBLIOGRAPHY.bib`；
- `SOICT_SUBMISSION_CHECKLIST.md`；
- `ASSET_BUILD_METADATA.json` 和本反馈文档。

### 公开安全素材包

- 仓库：`https://github.com/eksn425-del/light-right-repair-ai-prototype`
- 分支：`research-repro-v1`
- 当前提交：`9e69613f351d13bba62b71b391ef235f31996bae`
- 路径：`research_reproducibility/paper_assets/`

公开包只包含经过筛选的图表、派生 CSV、题注、文献和投稿清单。完整私有包才是论文排版时的完整来源。

## 3. 公开与私有边界

以下内容保留在私有仓库，不应未经授权上传到公开仓库或发送给无权限人员：

- Figure 2：真实场地基线传感点场；
- Figure 5：真实场地点位变化图；
- Table 1：建筑几何一致性审计；
- Table 3：完整 630 候选体量筛选表；
- Table 4：场地特定的 HB-Radiance 复核结果。

这些内容可能通过点位分布、建筑编号、几何审计或候选组合暴露真实场地信息。公开仓库没有上传原始 CAD、DXF、DWG、SKP、OBJ、sensor coordinate table、Radiance `.ill/.res/.hbjson/.wea` 中间文件或未经授权的真实原始数据。

## 4. 图表使用说明

每张图和每份表都在题注文件中记录了：

- 来源 CSV 或 JSON；
- 来源脚本；
- 冻结运行 ID；
- 是否允许公开；
- 必要的解释边界。

论文写作时应优先读取：

1. `FIGURE_CAPTIONS.md`；
2. `TABLE_CAPTIONS.md`；
3. `PAPER_ASSET_MANIFEST.md`；
4. `tables/` 下的 CSV；
5. `BIBLIOGRAPHY.bib`；
6. `SOICT_SUBMISSION_CHECKLIST.md`。

PNG 检查结果：9 张图均为 320 dpi。PDF 和 SVG 已提供，但它们是把最终 PNG 像素嵌入出版容器，不应描述为重新绘制的纯矢量线稿。

## 5. 冻结结果与写作边界

论文中可以使用以下已冻结事实，但必须保持限定语：

- 45 栋建筑，36 栋进入候选资格；
- 完整 2.5D 候选宇宙为 630 个；
- 2,031 个分析传感点；
- 23 个规则候选经过 HB 复核；
- 33 个 operational HB 场景；
- 20 个 research-only 独立验证场景；
- 共 53 个已测 HB 场景；
- 独立复合排序验证为冻结 N=20 样本内的 agreement；
- 四项评分权重敏感性使用 1,000 次、固定种子的归一化扰动；
- 2.5D screening 的中位运行时间为 55.40 秒；
- 单个 HB 场景中位运行时间为 51.11 秒；
- 630 个 HB 场景的 32197.24 秒是 serial-equivalent extrapolation，不是实际完成的 630 场景批处理时间。

必须避免下列表述：

- 不要把 `rho=1.0` 写成“100%准确率”；
- 不要把 Radiance 写成绝对 ground truth；
- 不要声称已经完成全部 630 个 HB 高精度场景；
- 不要声称算法在所有街区、所有模型上都有效；
- 不要声称 AI 击败人工方案；
- 不要声称方案已经具备施工、法律、产权或历史保护合规性；
- 不要把研究-only 验证场景写成 operational production result；
- 不要把 serial-equivalent 时间写成直接测得的批处理时间。

推荐使用的表达是：

> within-independent-sample composite-ranking agreement

> selective HB-Radiance verification

> human-in-the-loop design translation

> site-specific computational screening and decision support

## 6. 已完成的核验

### 代码与回归

- 私有研究仓库：`19 passed`；
- 公开镜像：`17 passed, 2 skipped`；
- 公开跳过项属于需要私有几何输入的测试，不是失败；
- 630 candidate clean ranking 的迁移回归审计已通过；
- 生产评分公式已由配置文件作为 single source of truth。

### 资产与数值

- PNG 数量：9；
- PDF 数量：9；
- SVG 数量：9；
- 论文表格 CSV 数量：11；
- 私有素材 manifest 哈希检查通过；
- 派生表格的数值与冻结来源通过容差审计；
- runtime 表中的关键数值与冻结 JSON 一致；
- PDF 和 SVG 文件可读取；
- 私有包和公开 paper-assets 目录均未发现禁传格式或传感点坐标文件；
- BibTeX 共 13 条文献，其中 12 条含 DOI，1 条为 BS2013 会议文献并使用官方 IBPSA 记录。

### 文献

文献条目使用 DOI、出版社/会议页面和项目中保存的来源记录进行核对。需要特别保留的透明说明是：Sampson 与 Charo 的 Columbia 数字化落地页显示的是数字化发布日期，而期刊卷期引用年份按 1986 保留，具体说明已经写入 `BIBLIOGRAPHY.bib`。

## 7. 网页端 ChatGPT 的推荐工作顺序

网页端继续写论文时，不要重新读取旧的 demo 输出或旧版本图表。建议按以下顺序读取：

1. 读取公开仓库的 `research_reproducibility/HANDOFF_TO_CHATGPT.md`；
2. 读取 `SOICT_2026_PAPER_WRITING_BRIEF.md`；
3. 读取 `PAPER_NUMBERS.csv` 和 `CLAIMS_LEDGER.csv`；
4. 读取 `paper_assets/FIGURE_CAPTIONS.md` 与 `TABLE_CAPTIONS.md`；
5. 根据目标是否需要真实场地图，向私有仓库申请 Figure 2、Figure 5、Table 1、Table 3、Table 4；
6. 只从 `paper_assets/tables/` 复制论文表格数字；
7. 用 `BIBLIOGRAPHY.bib` 统一生成参考文献；
8. 最后依据当前官方 SOICT 模板进行排版和 PDF 检查。

## 8. 投稿前仍需人工完成的工作

这部分不是算法问题，而是论文和投稿责任：

1. 核对当前 SOICT 2026 官方模板、篇幅、匿名要求、文件格式和投稿系统规则；
2. 将 Figures 1--9 插入最终论文，并检查正文交叉引用；
3. 将表格 CSV 导入排版模板后重新检查小数位、单位、列宽和脚注；
4. 由项目成员确认真实场地图是否可以公开，不能默认公开 Figure 2 和 Figure 5；
5. 检查正文每一个主张是否能回溯到 figure、table、ledger 或参考文献；
6. 补充作者、单位、基金、数据可用性、软件和利益冲突声明；
7. 完成最终 PDF 渲染检查和人工通读；
8. 归档投稿版本的 PDF、源文件和 SHA256。

## 9. 最终判断

当前素材包已经达到“可交给网页端 ChatGPT 继续写作和排版”的工程交付状态。它不是新的实验版本，也不应被描述成新的实验结果。后续工作的重点应转为：

- 用冻结数据写出方法、实验、局限性和讨论；
- 用题注和 manifest 保证每张图表可追溯；
- 用 claims ledger 控制论文措辞；
- 根据官方 SOICT 要求完成最终排版和投稿检查；
- 维持人工复核和建筑学解释，不把算法排序等同于自动设计结论。

**结论：** 素材包可用于论文初稿和网页端协作；投稿前仍必须完成人工排版、官方格式核对、公开范围确认和最终作者审阅。
