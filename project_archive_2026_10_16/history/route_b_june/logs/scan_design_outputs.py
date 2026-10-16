from pathlib import Path
root=Path(r'E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20\hb_radiance_project_final_design')
for scen in ['C9_C24_design_stepback','C13_C24_design_stepback','C9_C13_design_stepback','C9_C15_design_stepback','C6_C33_design_stepback']:
    d=root/scen
    print('\n##', scen)
    for p in d.rglob('*'):
        if p.is_file() and any(s in p.name.lower() for s in ['sun','result','grid','sensor','hours','ill','res','npy','csv','json']):
            print(p.relative_to(d), p.stat().st_size)
