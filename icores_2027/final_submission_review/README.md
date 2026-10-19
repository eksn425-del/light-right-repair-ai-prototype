# ICORES 2027 最终作者审阅稿

本目录只提供一套正式英文整合稿，题目：
**Solar-Access Intervention Screening and Preference-Sensitivity Decision Support for Urban Renewal**

中文题目：《面向旧街区日照改善的候选方案筛选与偏好敏感性决策支持》

## 阅读顺序
1. `paper/manuscript.pdf`：正式英文匿名稿。
2. `chinese/faithful.pdf` 或 `chinese/faithful.docx`：对应最终英文的完整忠实翻译；Markdown同名。
3. `chinese/plain.pdf` 或 `chinese/plain.docx`：通俗解释版；Markdown同名。
4. `qa/INDEPENDENT_FINAL_NUMERIC_REVIEW.md`、`qa/data_claim_check.csv`：数字与归档来源核查。
5. `handoff/AUTHOR_CONFIRMATIONS.md`：投稿前仍须作者处理的事项。

## 文件与重编译
`paper/final_latex_source.zip` 为自包含LaTeX编译包；解压后按 `paper/SOURCE_README.md` 执行。PDF和LaTeX只对应一个整合版本，不存在多个竞争投稿稿。
`figures/` 提供论文实际使用的矢量流程图及PNG；原始绘制和全部表格公式包含在LaTeX。图是提出的流程，不是实测用户行为。

## 科学结论
日照改善优先、干预代价次之。原45/35/15/5是研究者声明偏好，不能当作已经验证的建筑师偏好。原Top-10保留为透明起点，再根据明确偏好考察敏感性与补充候选。
有序日照优先和历史局部偏好下，旧清单已经保存最佳选择，零遗憾不等于全部候选排序相同。70%/80%日照总权重支持允许更偏重时长的选择，新清单可改善最佳机会覆盖，但Top-10恢复率增益、日照收益或其他预注册保护条件不足。第三轮六个情景全部未通过完整替换门槛。
算法给出可解释候选，不批准施工方案。部分补充候选缺少规则HB复核，更多候选缺少设计转译复核。最终建筑师仍需判断空间、产权、结构、成本和法规。

## 历史证据与本轮边界
本分支继承原有三个阶段的历史目录，保留其名称和内容。
- `../architect_first_cloud/`：建筑师辅助决策、630候选、既有物理复核与几何/计算证据。
- `../preference_robust/`：原21页正式稿和偏好稳健实验。
- `../solar_priority_final/`：六情景冻结实验与15页补充报告、原始结果。
本轮仅取回/核对已有文件、整合稿件及图表排版，未运行新物理模拟、重新抽样、改变权重或设计第四套算法。
本次数值文件恢复为备份提取和哈希核对。备份本身记录了上一轮曾按冻结脚本恢复并得到原文件一致哈希的过程，见恢复审计；不将该既往恢复描述为新的物理模拟。

## 验收状态
技术检查与作者学术审查分开。技术检查详见 `qa/`；作者尚需审阅内容、实际作者贡献、重复投稿、数据权利和AI披露位置。私有仓库归档不等于公开可复现，也不等于会议录用保证。
未登录PRIMORIS投稿、付款、填写作者身份或代签声明。交付后停止，等待作者和网页版ChatGPT审阅。
