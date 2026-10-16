# 路线B中文导师审阅定稿工作包

运行顺序：
1. `code/route_b_geometry_audit.py`
2. `code/route_b_prepare_hb_batch.py` 后运行 `lbt-recipes run direct-sun-hours`
3. `code/route_b_enumerate_2p5d_candidates.py`
4. `code/route_b_prepare_hb_extra_candidates.py` 后运行追加 HB 批处理
5. `code/route_b_prepare_hb_final_design_candidates.py` 后运行设计转译 HB 批处理
6. `code/route_b_collect_hb_merged_results.py`
7. `code/route_b_final_candidate_judgement.py`
8. `code/generate_route_b_deliverables.py`

随机种子：20260620。正式候选判断以 `results_csv/138_最终候选规则与设计转译对比.csv` 为准。