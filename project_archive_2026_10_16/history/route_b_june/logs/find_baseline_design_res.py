from pathlib import Path
import json
root=Path(r'E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20')
for scen in ['baseline_original','baseline','C9_C24_design_stepback','C13_C24_design_stepback']:
    print('---',scen)
    for p in root.rglob('*'):
        if scen.lower() in str(p).lower() and p.is_file() and p.name in ['ground_3m_road_open_space.res','grids_info.json','_info.json']:
            print(p.relative_to(root), p.stat().st_size)
