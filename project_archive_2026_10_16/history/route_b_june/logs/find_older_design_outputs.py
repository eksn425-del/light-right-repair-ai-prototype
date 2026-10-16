from pathlib import Path
root=Path(r'E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20')
for scen in ['C13_C24_design_stepback','C6_C33_design_stepback']:
    print('##', scen)
    for p in root.rglob('*'):
        if scen in p.name or scen in str(p):
            if p.is_file() and any(s in p.name.lower() for s in ['ill','res','json','csv','hbjson','hours']):
                print(p.relative_to(root), p.stat().st_size)
