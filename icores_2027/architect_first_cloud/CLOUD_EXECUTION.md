# dot Cloud-only 全链条执行任务书 — 建筑师决策主线 / ICORES 2027

日期：2026-10-18。**执行者：dot 云端工作环境（如实际具备计算机/命令行与GitHub写入能力）；不可假设其具备这些能力。**

## 0. 目标、质量门槛与真实限制

目标是让论文回归初衷：建筑师面对一个旧街区日照问题，系统先识别低直射日照区域，在36个研究规则允许的建筑组构成的630个无序双建筑减高组合中快速计算、排序、输出约10个值得下一阶段讨论的候选；对其中选中的候选再进行Honeybee/Radiance复核与几何转译的核查；最后**决策者仍是建筑师**。性能加速和纠错证明该筛选流程运行得高效、正确，不是论文唯一主题。

限定：真正的630是规则体量候选，**不是630张完整设计图，更不是630个获准实施的方案**；Top-10仅为“推荐进一步评估的规则候选”，不是10个保证可施工的设计方案。23个curated HB规则候选由Top10、Pareto和对照去重构成，20个另冻结的same-site覆盖样本不是总体随机抽样。实际更复杂的ABC旧计划不能用“已经实现”描述。

**一个重要事实：目前私有GitHub并没有上传原始DXF/CAD/SKP/OBJ、完整点位坐标、WEA/HBJSON/Radiance原始场景。云端可以对已归档的630候选汇总做真实重新分析，却不应宣称已经执行新的“真实场地3D物理模拟”。除非G0核查到合法、可用且完整的源输入，并且真的在云端运行并保留日志。** 用户明确不使用本地计算；不得转派本地Codex，也不得要求用户提供PC连接。

## 1. G0 云端能力审计（先做，必须真实）
- 报告当前是否有：云端终端、持久运行、Python/依赖安装、文件读写、LaTeX编译、GitHub分支写入、合法原始模型读权限；实测3个最小动作：`git read`、运行简单Python、写本分支测试文件并读取。失败如实记；不要以“DOT可操控电脑”视为事实。
- `audit/CLOUD_CAPABILITIES.json` 明确每项 VERIFIED/UNAVAILABLE/UNKNOWN；`audit/INPUT_MATRIX.csv` 记录每类所需数据、真实路径、SHA256、内容类型、是否可在云端重新计算、敏感级别。
- **若缺原始几何或Radiance运行数据**：只冻结 `NEW_HB_SITE_SIMULATION=NOT_RUN_MISSING_INPUTS`；继续从现有630输入跑可复算的排序、指标分析、Top-10和论文，不得以人工截图/OCR/程序造数充作结果。
- 若GitHub访问不可用：在可用云端空间创建输出包，明确GITHUB_WRITE_BLOCKED，不能声称上传成功；仅针对必要权限申请用户操作，不要求本地跑代码。
- 不得擅自把私有研究仓库改为公开，不得把真实场地源数据公开/复制进不受控第三方服务。任何需外部上传真实数据的路径须先征求用户与团队权限。

## 2. G1 科学版本锁定与“旧论文→新论文”对照
读取以下全部：
- `project_archive_2026_10_16/readable_manuscripts/context/source_documents/光权修复_终版执行大纲.md`
- `project_archive_2026_10_16/context/source_documents/光权修复AI项目完整介绍_给网页端AI_2026-06-05.txt`
- `project_archive_2026_10_16/readable_manuscripts/manuscripts/june_workbook/10_最终交付包_老师检查版/光权修复论文_初稿.md`
- `project_archive_2026_10_16/readable_manuscripts/history/route_b_june/光权修复论文_EI会议_中文学术定稿版_投稿前小修.md`
- `research_reproducibility/paper_support/PAPER_NUMBERS.csv`、`CLAIMS_LEDGER.csv`
- `icores_2027/paper_support/METHOD_SPEC.md`、`PAPER_NUMBERS_ICORES.csv`、`CLAIMS_LEDGER_ICORES.csv`、`CLAIM_CORRECTIONS.csv`
- `icores_2027/audit/LOCAL_FINAL_REPORT.md`、`icores_2027/runs/local_hb_20261016/translation_outcome_comparison.csv`、`icores_2027/runs/local_ablation_20261016/ablation_summary.csv`
- `icores_2027/manuscript_author_review/manuscript.tex`、`FULL_MANUSCRIPT_READABLE.txt`、`references.bib`、`qa/FINAL_QA.json`。

对旧稿和新稿建立 `audit/NARRATIVE_DELTA.md`：
- 旧：旧街区日照诊断 → 630候选 → Top10/Pareto →23复核 →人工判断。
- 新：算法遮挡复用速度+几何退台错误纠错。
- 目标：**不抹除真实新实验**，改为“建筑师可复核候选决策”的证据链；强技术实验放在支持该工作流准确、高效的章节。
- 明确先前4月构想（任意OBJ、加减重组、模拟退火、安全路径、跨城市通用、实地已验证）未得到本轮冻结证据充分证明，不能暗示已实现。
- 校对“v3上传PDF”与GitHub实际 `manuscript.tex` 是否同版：如果只有本对话附件而云端Dot拿不到，记录未取得原件，先用GitHub受控版本，出稿前提示用户提供v3的GitHub/Library版本；不得假装精确逐字对比v3。

## 3. G2 630候选重新分析与Top-10真实性核查（本轮最关键新增输出）
使用GitHub上真实 `aggregate_B_m630_r1_run.csv`，以及同工作流的重复样本和已冻结paper-ledger，运行代码在云端重新**读取、校验和推导**：
- 行数630、pair唯一、建筑ID合法、排序逻辑、A/H/V/N含义及单位、nominal volume vs实际场景并集体积、N全为0、固定分数权重0.45/0.35/0.15/0.05、ties/稳定排序政策；数值与已冻结Top10逐项回归比对。
- 若数据字段与旧文或另一脚本不一致，先审计根因、报告差异；**不根据想要的Top10修改权重或结果**。
- 输出 `analysis/top10_rule_candidates.csv`：rank、building_pair、rule_height_change(仅有证据时)、low_sun_area_reduction_m2、mean_DSH_gain_h、nominal_volume_proxy_m3、weighted_score、Pareto_membership、HB_review_status、design_translation_status、scientific_caveat、source_file、run_id。
- 输出 `analysis/pareto_rule_candidates.csv` 和 `analysis/selected_23_provenance.csv`（验证Top10 10 + nonzero Pareto 12 + historical 2 + baseline 2 − overlap 3 =23在历史选择约定下成立；若重新计算真实列表不同，以CSV为准且解释）。
- 输出 `analysis/architect_decision_cards.md`：每个Top10用两三句**通俗中文**解释“改哪两栋、能改善什么、预计代价、是否经过HB复核、哪些还需人工检查”；不伪造建筑使用功能/法规可改性/施工建议/图像。
- **最关键：明确谁有HB结果，谁仅有2.5D结果**。不能把Top10全部变成“已通过专业验证”；已检查的rule候选也未必已有合格的设计转译。
- 以保留历史排序、不对结果调参为前提，附一个非支配候选/效益-体积选择视图；输出 `analysis/selection_policy_frozen.md`，说明Top10是按原生产分数，Pareto按A/V；注意A改善/体积的权衡，不能用一个新阈值“优化结果”后回填。
- 把含敏感坐标/建筑详细场地几何的可视化保持私有；出图不引入仿真不存在的图形。

## 4. G3 新分析与现有实验的三重验证（不隐瞒老结果）
A. **计算效率**：保留 `icores_2027/runs/local_ablation_20261016/` 的5、20、60、630真实匹配A/B对照（同原语单线程、每组3次，630 11,608.183秒 vs 24.037秒，约482.927倍）；云端可重新计算这些已测日志的统计、图表，但禁止称为新的云端重跑。计算复用是“让建筑师快速看候选”的能力证据，不是对所有HB或空间索引实现的领先。
B. **验证可信**：按相同指标重算旧23 curated与冻结20 same-site覆盖样本对应的Spearman、MAE、tie sensitivity、score/area区别；说明23复核并非随机、20不是独立地点；N常数0，V共同输入，不能写“100% accuracy”。只能用现有表。
C. **设计转译**：引用 `translation_outcome_comparison.csv` 的旧几何越界和contained-v2四个实际修正版，C9/C13已有contained直接复用。旧C9/C24副作用被查明是**生成几何越界的错误**，不是减高正常导致的真实权衡；不能保留旧“C9/C24高收益但正常产生副作用”的表述。所有候选最终状态需根据新证据再审，禁止硬编码原先C9/C15、C9/C13的唯一最终优先身份。
D. 若云端有实际输入与环境，可另建明确标注的实验run，只做预先冻结的最小必要核对；**优先复用已真实重跑的10场景，不重复做大HB**。任何新实验必须有完整真实输入/运行日志，先登记实验协议与出处。不允许旧数据当新实验。
E. 输出 `audit/RESULT_RECONCILIATION.csv`、`analysis/decision_evidence_matrix.csv`、`analysis/figure_provenance.json`、`analysis/CLOUD_RUN_LOG.md`：事实区分 RAW_MEASURED_HISTORICAL、CLOUD_RECOMPUTED_FROM_ARCHIVE、NEW_REAL_SIMULATION（若真的做了）、NOT_RUN。

## 5. G4 写作：恢复建筑师主线，并保留真实技术贡献
**英文论文目标ICORES Regular Paper—Applications/Decision Support Systems，非建筑艺术论文。**

建议工作标题（可以有更精确的优化，但不得与内容脱离）：
`Efficient Solar-Access Intervention Screening for Early Urban Renewal: An Auditable Decision-Support Workflow`
中文对应：
`面向旧街区日照改善的高效候选方案筛选与可审计辅助决策`

研究故事顺序：
1. 建筑师面对几十栋可研究建筑和大量可选干预组合，早期不宜逐个建模/高成本模拟。
2. 将已有规范模型、可动性研究约束、固定冬至日/网格/指标明确成有限的630候选空间。
3. 2.5D筛选所有候选并给出Top10+Pareto的可解释候选清单；这些是**规则层候选**不是完整建筑设计。
4. 选择性高成本复核23规则候选 + 先行冻结20个额外覆盖候选，为筛选提供限定范围的一致性证据。
5. 支持快速筛选的实现：预计算遮挡贡献，保留真实同条件性能对照、误差和局限。
6. 从推荐候选到三维建筑表达时必须检验几何包含；10月真实纠错说明未受控设计转译可以违背原意。
7. 输出给建筑师的应是优先核查清单/候选范围以及数据和限制，由人决定产权、用途、结构、风貌、实施。

推荐章节：Abstract / 1 Introduction / 2 Related work / 3 Case, decision universe and solar setup / 4 Screening and decision workflow / 5 Validation and experimental setup / 6 Results: Top10/Pareto + selected-23 / solver agreement + runtime + design translation / 7 Discussion for architect use + validity limits / 8 Conclusion / AI disclosure / references。

正文须**明确出现“从630→Top10/Pareto→23 reviewed→建筑师进一步选择”的真实表格或图**，至少一张Top10表可在正文，附表可以扩展完整候选；不能只拿图表show speedup。
不写“AI自动生成了十套最终设计”；不写全球泛化、法定合规或现场改善。别采用过度夸大的主题宣言。保留事实限制：DXF组件bounding-box/shared footprints、真实OBJ差异、single site、固定3m grid、0.1m点高、3h阈值、16×0.5h、north 0假设、WEA常数辐照数据非实测天气、pvlib/HB solar vectors非完全同一、原20样本局限、N项无排序贡献、volume proxy并非真正拆除工程量。
论文语言：严谨但便于建筑本科生理解；短句；陈述问题/方法/结果/限制；不堆叠没有帮助的Jargon。

## 6. G5 中文逐段理解稿（必须，与英文双轨一致）
生成 `paper/CHINESE_READER_VERSION.md` 与建议 `paper/CHINESE_FAITHFUL_TRANSLATION.md`：
- 第一份为**通俗阅读版**，每章: 为什么做、怎么做、得到了什么、对建筑师有何价值；每段附英文section/ref编号与数据出处；术语第一次出现用简单中文+英文括号。
- 第二份为**逐段忠实译稿**，保留英文论文公式、图号、表号、参考文献号，便于用户逐句核对。
- 用户必须看得懂Top10如何产生，23去重如何成立，为什么旧几何出错被纠正，483倍仅针对哪两种实现。
- 不能把通俗版理解性解释当成英文真实实验结果；保留旧结果和新结果出处。
- 优先提供中文通俗内容和中英摘要给用户审核。

## 7. G6 严格遵守2027年ICORES官方要求
官方链接:
- https://icores.scitevents.org/ImportantDates.aspx
- https://icores.scitevents.org/Guidelines.aspx
- https://icores.scitevents.org/Templates.aspx
- https://icores.scitevents.org/AiTools.aspx
- https://icores.scitevents.org/CallForPapers.aspx

官网截至2026-10-18显示第二轮Regular Paper截止2026-10-22 AoE；2026-12-04通知；12-18 camera ready/registration。初稿英文、PDF、双盲、10,000—50,000个非空白字符（包括参考文献、表、图、附录），按照Springer会议作者模板，不是SOICT12页规定。系统PRIMORIS。需重新联网核查，记录取证时间、URL、页面变化。
- 双盲PDF不得包含作者名、单位、机构致谢、GitHub实名地址、敏感提交SHA或可识别项目文件位置。作者真实身份由作者在PRIMORIS填。
- AI披露遵守ICORES Guidelines与AI Tools专页：透明注明AI生成文字/图/代码等用途和位置，不删除披露伪装人工；因双盲与acknowledgments有表面冲突，采用不含身份信息的合规文本，**若不能确定，记录作者需向组委会询问**，不得擅自宣称官方已认可具体放置形式。
- 检查原稿v3更新与新稿重叠/原创性，避免同时投稿；文献查实DOI/作者/年份，严禁编造来源。
- 官方模板排版，含真实vector图、可编辑表格、标题、参考文献。编译PDF后逐页渲染QA（裁切、溢出、符号、脚注、图题、匿名、字体、PDF元数据）；字符数和页数记录，并附source ZIP。
- **禁止在取得最终作者信息/集体确认前提交、支付、签署声明、发送对外邮件。**

## 8. G7 交付文件与完成标准
目录建议：
`icores_2027/architect_first_cloud/audit/`
`icores_2027/architect_first_cloud/analysis/`
`icores_2027/architect_first_cloud/paper/`
`icores_2027/architect_first_cloud/handoff/`

最低文件：
1. `audit/CLOUD_CAPABILITIES.json`、`INPUT_MATRIX.csv`、`NARRATIVE_DELTA.md`、`RESULT_RECONCILIATION.csv`
2. `analysis/recompute_candidates.py`与依赖/运行命令、`top10_rule_candidates.csv`、`pareto_rule_candidates.csv`、`selected_23_provenance.csv`、`architect_decision_cards.md`、`selection_policy_frozen.md`、`decision_evidence_matrix.csv`、`CLOUD_RUN_LOG.md`
3. `paper/manuscript.tex`、`paper/anonymous_regular_submission.pdf`、`paper/references.bib`、`paper/source_bundle.zip`（若连接器无法上传binary，写出准确的云端下载文件链接和hash，并不要假称GitHub已有PDF）
4. `paper/CHINESE_READER_VERSION.md`、`paper/CHINESE_FAITHFUL_TRANSLATION.md`、`paper/FIGURE_TABLE_MANIFEST.md`、`paper/QA_REPORT.md`
5. `handoff/WEB_AUTHOR_HANDOFF.md`、`handoff/SUBMISSION_STEPS.md`、`handoff/OPEN_ITEMS.md`、`handoff/FINAL_STATUS.json`

评价标准（全部有证据后才能填true）：
- `CLOUD_RECOMPUTATION_DONE`：真实读取630数据、脚本重算排序Top10/Pareto、输出hash与脚本/日志；
- `SCIENTIFIC_CLAIMS_AUDITED`：旧/新结果与所有引用逐项核对；
- `FULL_MANUSCRIPT_READY_FOR_AUTHOR_REVIEW`：匿名完整论文确实已经保存、编译、逐页QA并具真实hash；
- `CHINESE_EXPLANATION_COMPLETE`：通俗版+对应章节译稿齐全；
- `UPLOAD_READY`：通过所有自动化门槛，但作者审批、会务披露冲突和PrimoRIS个人操作仍属人工责任；
- `SUBMITTED` 必须为false，除非用户在日后提供真实系统确认回执并授权变更（本轮不允许dot自己提交）。

**时效：2026-10-18启动，优先在10-20完成证据+初稿；10-21完成编译、匿名、中文审阅与交付；10-22 AoE为官网deadline。若赶不上，不得为按时宣称模拟成功或少做匿名检查；提交不是质量责任的替代。**

## 9. 不要犯的错误
- 不得主动等本地Codex、Windows权限或下载E盘，也不得暗中使用远程本地计算；本轮cloud-only。
- 不得直接修改原冻结tag或此前12/15页论文，必须在新分支另存版本。
- 不得把6月旧C6/C33数值和9月630基线混为同一场景。
- 不得把旧的C9/C24新增阴影写成有物理必然性的设计trade-off；10月定位到错误几何外扩，修复后须以新版证据叙述。
- 不得把Top10写成十张建筑设计或十个已完成施工审查的方案。
- 不得继续主要写一个“483x程序性能+Bug修复”论文；它们支持**建筑师的早期决策候选筛查**。
- 不得捏造新HB输出/完整630高保真模拟/现场实测、跨案例准确率、产权/结构/施工许可。
- 不得隐藏缺输入、缺源码、云计算权限、GitHub写入或编译失败。
- 不得持续在背景运行/承诺通知，除非dot本身真正具备对应持续执行能力且实际接管。

## 10. 结束时必须向用户报告
`STATUS, repo, branch, final_commit, exact paper_source_path, exact pdf_path/link and sha256, bilingual files, cloud actual re-runs vs archived recomputation, numeric check result, official rules checked date, missing pieces, earliest submit-ready date`。
并在WEB_AUTHOR_HANDOFF用**通俗中文**回答：
“这篇论文究竟解决了什么建筑师问题？系统如何从630里选10？如何进一步审核？算法没做什么？为什么这一篇仍适合ICORES？”
