# 02 Algorithm B explanation

## 代码位置

- `src/algorithm_b_optimization/run_optimization.py`
- `src/algorithm_b_optimization/intervention_generator.py`
- `src/algorithm_b_optimization/scoring.py`
- `src/algorithm_b_optimization/intervention_constraints.py`

## 输入

- `dark_zones.csv`：Algorithm A 输出的暗区点。
- `gap_candidates.csv`：Algorithm A 输出的潜在缝隙或可改善位置。
- `buildings.csv`：建筑边界、高度、可动性和保护属性。
- `protected_zones.csv`：保护区或不可触碰空间。
- `intervention_levels_checked.csv`：如存在，则作为人工干预等级约束。

## 候选生成逻辑

Algorithm B 先根据暗区点寻找最近或相关的可编辑建筑，生成 `subtract` 操作；再根据 gap candidates 生成 `add` 和 `reorganize` 操作。对于本论文主线，最终采用保守型 `subtract` 结果作为主要解释对象，因为它最容易被转译为退台、屋顶平台和采光缝，并且与“最小干预”原则一致。

## 评分公式

当前代码中的稳定评分公式为：

`score = light_gain * w1 - intervention_volume * w2 - new_shadow_penalty * w3 - protected_zone_penalty * w4`

权重来自 `scoring.py` 与配置文件，默认值为：

- `light_gain`: 1.0
- `intervention_volume`: 0.08
- `new_shadow_penalty`: 0.6
- `protected_zone_penalty`: 1.0

保守型输出中的 B_summary：

```json
{
  "candidate_count": 3,
  "best_candidate_id": "candidate_01",
  "score_weights": {
    "light_gain": 1.0,
    "intervention_volume": 0.16,
    "new_shadow_penalty": 0.9,
    "protected_zone_penalty": 2.0
  },
  "search_iterations": 220,
  "intervention_level_table": "E:\\AI项目\\light_equity_project\\data\\real_guankou\\lakeside_leisure_ready\\intervention_levels_checked.csv",
  "intervention_constraints": {
    "enabled": true,
    "input_count": 25,
    "filtered_count": 0,
    "remaining_count": 25,
    "blocked_examples": []
  },
  "notes": "Framework version: boolean geometry is represented by reference boxes."
}
```

## 约束处理

- C42 幼儿园被设为不可动建筑，因此 Algorithm B 不应对其生成削减操作。
- 如存在人工干预等级表，`intervention_constraints.py` 会过滤不允许的操作。
- `protected_conflict` 会进入评分惩罚。

## 论文中应采用的保守表述

Algorithm B 当前是启发式候选生成与评分排序框架，而不是严格全局最优求解器。论文应强调其价值在于把暗区诊断结果转译为可比较的体块干预候选，并为人工复核提供排序依据。

## 候选排序表

见 `candidate_ranking_for_paper.csv` 与 `table_candidate_ranking.md`。注意：该表基于已经导出的候选 interventions，而不是完整原始候选池。
