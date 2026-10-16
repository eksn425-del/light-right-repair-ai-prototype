from pathlib import Path
import pandas as pd
root=Path(r'E:\AI项目\路线B_中文导师审阅定稿_工作包_2026_06_20')
for fn in ['121_canonical_2p5D_Top10候选.csv','122_canonical_2p5D_非零Pareto候选.csv','123_需追加HB_Radiance复核候选清单.csv','120_canonical_2p5D完整双建筑候选排名.csv']:
    p=root/'results_csv'/fn
    df=pd.read_csv(p)
    print('\n##',fn)
    print(df.columns.tolist())
    print(df.head(12).to_string())
