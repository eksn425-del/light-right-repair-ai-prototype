# 中文产品定位说明｜Light Right Repair AI Prototype

## 推荐定位

推荐标题：

> AI 光权修复决策工具｜面向城市更新的空间诊断、候选生成与规则验证 Workflow

这个项目适合包装成 **AI-assisted spatial decision workflow**，而不是聊天机器人或强 Agent。

## 用户与场景

- 城市更新设计师：需要判断哪些区域光照不足、优先修复哪里。
- 规划研究者：需要把空间公平议题转化成可比较的指标。
- 设计团队：需要在早期阶段快速比较候选干预策略。

## 用户痛点

- 光照公平问题通常停留在后期渲染或主观判断。
- 设计团队很难快速比较多个微更新候选方案。
- 只看光照提升不够，还要考虑安全、可达性和规则冲突。
- 真实项目数据复杂，早期需要一个可复现的 toy workflow 先验证方法。

## Workflow

```text
toy block dataset / grouped OBJ massing
-> Algorithm A: sunlight diagnosis and dark-zone detection
-> Algorithm B: candidate intervention generation
-> Algorithm C: accessibility and safety validation
-> final recommendation and before/after metrics
-> human designer reviews caveats and reruns
```

## 当前已有证据

- `main.py` 可运行完整 A/B/C workflow。
- `data/sample_toy_street/` 提供公开 toy dataset。
- `outputs/demo_run/` 提供 demo 输出。
- `docs/PRD-lite.md` 提供轻量产品方案。
- `docs/EVALUATION_METRICS.md` 提供指标说明。
- `docs/AI_DECISION_PIPELINE.md` 描述三阶段决策流程。

## 已验证

公开 toy demo 可以运行，并生成：

- sunlight diagnosis
- dark zones
- candidate scores
- validation report
- final recommendation
- before/after metrics
- comparison chart

## 主要短板

- 没有真实用户访谈。
- 没有交互式 Web UI。
- AI 目前主要体现为决策工作流和算法辅助，不是 LLM Agent。
- 真实城市更新场景还需要人工校验数据、保护建筑、道路和规范限制。

## 最少补强

1. 补一页用户画像和使用场景。
2. 补一张产品流程截图或 demo GIF。
3. 补一个“为什么不用强 Agent”的说明。

## 项目叙述建议

这个项目解决的是城市更新中光照公平难以量化和迭代的问题。我把它做成一个可运行的 AI-assisted decision workflow：先诊断暗区，再生成微更新候选，最后用安全和可达性规则筛选推荐结果。它的价值不是自动设计，而是让设计团队在早期用指标比较方案，并保留人工复核。
