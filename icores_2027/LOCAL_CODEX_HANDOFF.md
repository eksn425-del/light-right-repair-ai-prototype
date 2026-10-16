# 给本机 Codex 的接续指令（可直接复制全文）

你现在作为实验执行助手，接续 ICORES 2027 第二轮 Regular Paper，Applications / Decision Support Systems，结合 Energy and Environment。会议已经确定，不再选会。请实际执行，不只给计划。

仓库：eksn425-del/light-right-repair-ai-prototype，必须保持 private。
唯一工作分支：icores-2027-sprint。
云端本轮交接性质：有真实运行证据的部分检查点，绝不是已经满足科学验收。最终定位 SHA 见本文件同目录 HANDOFF_TO_WEB.md 和 RESULTS_SUMMARY.json；开始前必须 fetch 并核对远端最新 HEAD，不把本文的旧提交当最新状态。

## 1. 先同步与检查，防止并行覆盖

1. 实际核查本机终端、GitHub认证/写权限、Python和Honeybee/Radiance。确认这是作者授权的本机环境。不得推断其他电脑或云端可读E盘。
2. 检查已有仓库与工作区；若有未提交修改，先报告并保留，不reset/clean覆盖。fetch远端后切到已有 icores-2027-sprint，核对HEAD、远端HEAD和工作区。遇不一致先查变更再合并正常快进，禁止force-push。
3. 云端已交接并停止对此分支写入后，你才成为唯一写入者；若发现其他执行仍在更新，先协调而不是同时提交。
4. 依次完整读 ICORES_START_HERE.md、icores_2027/DOT_EXECUTION.md、OFFICIAL_REQUIREMENTS.md、TASKS.md、STATUS.json、HANDOFF_TO_WEB.md、RESULTS_SUMMARY.json、configs/ICORES_PROTOCOL.json、audit/MISSING_INPUTS.md、audit/GEOMETRY_FINDINGS.md、audit/STATISTICS_FINDINGS.md 和 paper_support/METHOD_SPEC.md；若本机存在AGENTS.md也需遵守。
5. 不改变main、归档分支、旧tag、仓库可见性或历史输出；保留冻结20样本原始字节和原SHA。不要新增ML/LLM、默认全630HB、重做网站、购买算力、自动投稿/缴费/发邮件。

## 2. 在本机寻找最小真实输入，原始文件全程留本机

依据 project_archive_2026_10_16/indexes/EXCLUDED_SOURCE_FILES.csv、FILE_INVENTORY.csv、EXPERIMENT_REGISTER.csv及归档导航定位真实项目根目录。可在已授权的本机范围查找，不编造固定E盘路径，不仅凭相同文件名认定正确版本。

需要 clean run baseline_20260909_clean 的：
- canonical_site_v2/canonical_site_v2.geojson（索引41062字节）和与其一致的规范建筑属性；
- results_csv/100_HB_Radiance传感点.csv（索引47443字节），保持原2031点ID、坐标、顺序；
- baseline及五个既有退台配对 C9/C24、C9/C15、C9/C13、C13/C24、C6/C33 的实际模型/场景、recipe参数、WEA、有效太阳向量与时间列映射、逐点逐时.ill及累计.res。优先定位baseline和C9/C24恶化点证据。未运行/没有的原场景明确标记，不能假造；
- 来源、单位、北向、坐标框架与SHA256清单。

无需上传整套CAD/SKP，也不需要重新抽20个样本。建筑属性、630汇总和冻结20样本已有归档，先复用。全部坐标、geojson原几何、WEA、.res/.ill/.hbjson、CAD/OBJ等受限原始输入与完整逐点输出留本机私有目录，绝不git add。可提交去坐标的聚合结果、hash、代码和脱敏日志。

找不到材料时更新 audit/MISSING_INPUTS.md，一次列出仍缺的最小材料和受影响任务，继续不依赖它的工作。不能把toy/重建坐标替代真实场地。

## 3. 已有云端代码怎样使用，哪些还没有实现完成

云端确实执行了：生产源函数的合成反例、几何/夜间/映射测试、冻结表统计重算、实际Honeybee/Radiance单场景合成smoke、官方匿名模板编译。它们不是本机真实场地复算，不能算作本轮缺失的真实场景结果。

可用入口（先检查最新版--help并运行测试）：
- python icores_2027/scripts/geometry_audit.py --synthetic
  只复测合成反例；写专门合成证据，不代表实景。
- python icores_2027/scripts/matched_ablation.py --manifest <本机私有manifest.json> --check-only
  校验输入、hash、许可和协议；通过才允许benchmark。
- python icores_2027/scripts/geometry_audit.py --real-manifest <本机私有manifest.json> --output-dir <本机私有几何审计目录> --run-id <新的运行ID> --code-commit <当前40位代码SHA>
  已实现真实footprint分层/体积/包含性审计及whole-scene union；这是几何审计，不能自动解释原HB恶化射线。
- python icores_2027/scripts/matched_ablation.py --manifest <本机私有manifest.json> --output-dir <新的icores_2027/runs/运行ID目录> --run-id <新的运行ID> --code-commit <当前40位代码SHA>
  实现同一个求交原语的A逐候选重新求交与B预计算复用，包含阶段时间、匹配校验、pilot、固定嵌套集合和3次重复；禁止用合成输入写真实加速比。
- python -m pytest -q icores_2027/tests
  阅读每个测试适用范围；历史云端测试不能记成本机本轮执行。某些交付快照测试专门约束云端BLOCKED状态，完成本机真实任务后须更新契约测试并保留原日志，不要为了绿色覆盖真实失败。

尚需本机实际完成/必要开发的部分：真实历史HB模型和结果的ID+坐标+逐时双重映射；原恶化点遮挡面/射线追踪；baseline及五原转译案例的受控HB运行编排；若缺陷适用，则修正版的必要重算；真实结果到最终台账与报告的整合。geometry_audit.py不包含完整历史HB重放器；smoke_hb_runtime.py只是云端合成能力检查且有云端默认路径，不能直接当实景批处理脚本。可复用 research_reproducibility 的既有批处理/解析代码，但先审计并显式传入私有目录与本轮新run，禁止覆盖历史freeze。

本机若为Windows：先核查导入、路径、shell和计时/内存统计兼容性，云端未验证Windows执行。记录安装版本差异；优先使用可复现现有Honeybee/Radiance环境。云端Radiance6.0.2、lbt-recipes0.29.1；云端只修了lbt-recipes驱动UTC duration记录的时区bug，补丁在 audit/lbt_recipes_timestamp_fix.patch，不能未经核对套用到其他版本，也不能因此改动求解参数。

## 4. 私有manifest必须真实填写

matched_ablation.py开头docstring给出JSON字段契约。各文件path留私有manifest，不提交；sha256必须现算。source_run为baseline_20260909_clean，site、单位、north与冻结协议一致。private_runtime_authorized和sensor_order_preserved只能在实际确认后填true。historical_verified要求真正核查历史太阳序列；不能为了通过校验直接写solar_verified=true。

若使用新pvlib序列，显式注册new_pvlib_protocol与solar_version，单列新输入hash，不声称与历史HB射线相同。历史太阳表列名与当前代码不同，转换须记录实际逐列关系、时间偏移和向量norm，不能只改列名假装一致。得到真实输入hash后另交输入manifest摘要，不静默改已冻结协议目标、容差、20样本或候选顺序。

## 5. 必须解决的科学问题

G2：云端证明生产函数对合成凹形可能越界、对courtyard遗漏洞边界且roof填洞、face异常被吞；还证明一个低高度参数边界的目标/实际移除体积不一致。但这不能证明真实C9/C24原因。对原五配对检查多部件/holes/union、z范围、实际输出面、solid子集、目标与实际体积，再定位旧4恶化点/9m²的逐时原因。contained_stepback_v2只是待验证修正，不能未经复算宣称可交付。保持原负结果和原代码证据。共享baseline/时间/解析出错则扩大影响范围并报告，不继续使用受污染结论。

先重放baseline+必要原方案；修正后才追加受影响方案，通常6–11个场景是规划范围，非已完成数量。不要默认全630HB或重跑冻结20HB。

G3：用已冻结候选自然顺序的m=5/20/60/630，至少3次；A和B同场地、同点位太阳、同求交原语/容差、同线程；B总计必须包含precompute。先匹配逐点DSH及A/H/V/N、分数、排序，不等价不给speedup。pilot只据时间决定范围；若完整A三次预计12小时内则完成630匹配，否则最大可完成固定子集真实对照并把630A外推单列。53旧HB、55.40秒、8.94小时不能冒充本机新测量。

G4：已有正确的冻结表结论保留，接着核对真实recipe/WEA/二进制时间列。16*0.5h=8h，端点跨度7.5h；N常量，TopK tie敏感，rho1非100%准确率，MAE.45非空间分辨率。太阳算法差异与夜间latent bug的本次实际影响要靠输入证据，不靠推测。

## 6. GitHub收敛与终止条件

每完成一个阶段更新TASKS/STATUS并单独提交到icores-2027-sprint。提交前检查diff和敏感文件清单，只添加允许的派生汇总/代码/日志/模板骨架，不上传受限原始输入。保留历史freeze、20样本和旧证据；更正用新run和差异表。

产出真实测试日志、图表来源/矢量属性、PAPER_NUMBERS_ICORES.csv、CLAIMS_LEDGER_ICORES.csv、CLAIM_CORRECTIONS.csv、RESULT_DIFF_ICORES.csv、METHOD_SPEC更新、HANDOFF_TO_WEB.md和RESULTS_SUMMARY.json。每个新CSV保留run_id/config_hash/code_commit/input_hash/measurement_class；旧值REUSED_FROZEN，新统计RECOMPUTED，新实验MEASURED，外推EXTRAPOLATED。

只有缺失输入、真实几何与恶化点原因、必要同solver复算、匹配benchmark、实际时间语义和测试等P0真正解决才可置EVIDENCE_READY_FOR_WEB_REVIEW=true；结果不好看不是失败，未解释物理矛盾必须阻断。稿件、作者批准、提交三个标志不得由执行助手擅自置true。

最后先提交证据得到E，再提交引用E的交接元数据得到M，避免自引用SHA。若本机git已认证且有权限，先查远端icores-2027-evidence-v1是否不存在，再创建新annotated tag指向最终E并只push该tag、核对远端。已有同名tag则停下报告，不移动或覆盖。云端没有创建远端tag，切勿把预定名称当作已存在。若仍有关键阻断，只交部分证据检查点，明确ready=false，不用tag名称暗示已通过科学验收。

最终返回repo/branch、evidence_commit、handoff_commit、实际已创建tag或精确阻断、完成/阻断任务、实景几何结论、真实A/B规模/重复/等价性/加速比、新旧证据区别、缺失材料/作者决定。完成交接后停止。正式英文论文由网页端ChatGPT读取冻结结果后审核修改；最终投稿由作者确认。
