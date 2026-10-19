# 最终英文稿与中文稿对应核验

中文忠实版对应最终整合英文论文 Solar-Access Intervention Screening and Preference-Sensitivity Decision Support for Urban Renewal。没有以旧中文稿直接代替最终译稿；保留的英文原段采用复核后的对应译文，修改和新增部分重新翻译，已删除的段落、表和图不沿用。

## 全文结构对应

| 英文最终部分 | 忠实中文版 | 核验 |
| --- | --- | --- |
| Title / Abstract / Keywords | 标题、摘要、关键词 | 完整 |
| 1 Introduction | 1 引言 | 全部5段 |
| 2 Related Work and Methodological Position | 2 相关研究与方法定位 | 2个小节 |
| 3 Finite Intervention Model and Performance Evidence | 3 有限干预模型与性能证据 | 3个小节 |
| 4 Preference-Sensitivity Methods | 4 偏好敏感性方法 | 5个小节 |
| 5 Broad and Local Preference Results | 5 广泛与局部偏好结果 | 5个小节 |
| 6 Solar-Priority Comparison and the Failed Replacement Test | 6 日照优先比较与未通过的替换检验 | 3个小节，新译 |
| 7 Integration with Simulation and Geometry Review | 7 与模拟及几何复核的整合 | 3个小节 |
| 8 Discussion, Limitations and Reproducibility | 8 讨论、局限与可复现性 | 3个小节 |
| 9 Conclusion | 9 结论 | 全部3段，新译 |
| AI Use Disclosure | AI使用披露 | 完整，包括匿名审稿位置待澄清条件 |
| References | 参考文献 | 同序13项，保留原题和出版信息以便检索 |

## 公式对应

编号与最终英文一致，共23个编号公式。

- 式1—2：恰选两组约束与固定减高规则
- 式3：有效太阳掩码下的直接日照时长
- 式4—7：A、H、V、N
- 式8—11：固定归一化、历史评分、三准则效用和有效中心
- 式12—14：完整、有序、局部偏好空间
- 式15：名次及前十可接受度
- 式16—18：最佳效用与遗憾、十候选选择目标、覆盖与恢复率
- 式19—20：固定集合线性规划与连续最坏遗憾恒等式
- 式21—22：Solar70/Solar80与期望恢复率
- 式23：可复用遮挡计数更新

式19在中文Word/PDF中分为目标与约束两行显示，共用编号19；全部约束完整保留。公式为可编辑Word数学对象，不是原始LaTeX代码。英文内联的筛选损失与总损失恒等式也在第6.3节保留。

## 表与图对应

| 最终表号 | 内容 | 数值核验 |
| --- | --- | --- |
| 1 | 全集归一化边界 | 完全一致 |
| 2 | 第二轮独立测试 | 完全一致 |
| 3 | 连续审计 | 完全一致 |
| 4 | 历史前十名 | 完全一致 |
| 5 | Robust10成员及证据状态 | 完全一致 |
| 6 | 第三轮主要情境 | 完全一致，包括最终修正末位数值 |
| 7 | 六情境替换门槛结果 | 完全一致 |
| 8 | 23项和20项专业复核队列 | 完全一致 |

程序逐表比较共307个数值标记，全部相同；此计数包含表中编号等数字，不等同于307个独立实验统计量。候选标识、证据标记、表题和单位另经正文与结构复核。

最终英文只有图1工作流程示意图，忠实中文版保留全部节点、顺序、箭头关系及图注，并翻译节点文字。Word和PDF嵌入完整图片；Markdown配套figures/workflow.png。没有沿用旧稿已删除的连续遗憾图或名次表。

## 文件与版式核验

- faithful.md、faithful.docx、faithful.pdf：同一忠实译文；Word渲染的PDF为20页
- plain.md、plain.docx、plain.pdf：新编通俗说明；Word渲染的PDF为8页
- 两份Word均重新打开，结构可读；全部最终PDF页面已渲染并逐页检查
- 8张忠实版表、4张通俗版表可读；公式不以损坏代码呈现；中文字体、图示、参考文献可读
- 首次转换发现的表格导入问题及式19多行渲染问题已修正后重新渲染
- PDF直接来自最终Word，因此两者内容与分页一致；不同Word版本仍可能重新分页
- 通俗版是解释文件，不冒充逐句全文翻译；完整正式内容以忠实版和英文稿对应

## 科学表述核验

两份中文均保留：45/35/15/5是研究偏好；N在630规则中恒为0；630不是完整Honeybee模拟数；23与20是不同的冻结同场地队列；六情境完整替换检验均未通过；完整单纯形改善是条件性诊断；历史前十为默认，额外候选为明确条件下的可选比较；最终设计选择属于建筑师；未新增科学实验或建筑师验证。
