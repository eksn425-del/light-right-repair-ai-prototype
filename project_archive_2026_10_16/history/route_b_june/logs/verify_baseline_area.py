from pathlib import Path
root=Path(r'E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20')
res=root/'hb_radiance_project_batch'/'baseline'/'direct_sun_hours'/'results'/'cumulative'/'ground_3m_road_open_space.res'
vals=[float(x.strip()) for x in res.read_text().splitlines() if x.strip()]
low=sum(v<3.0 for v in vals)
print('count',len(vals))
print('low_h3_points',low)
print('low_h3_area_m2',low*9)
