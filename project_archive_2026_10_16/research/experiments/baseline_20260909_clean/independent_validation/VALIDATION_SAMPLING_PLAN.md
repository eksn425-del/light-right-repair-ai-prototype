# Independent HB validation sampling plan

This sample was frozen before any independent-validation HB output was read.

- Seed: 20260909
- Requested sample size: 20
- Candidate universe: 607 after excluding 23 historical rule pairs
- Stratification: five 2.5D-score quintiles, equal allocation
- Within-stratum tie breaking: deterministic intervention-volume spread and building-ID diversity
- Frozen CSV SHA256: ad4abb9b89a263edaecc2cb3553f7832ce0ccb460521ba218e0083e05bcb46b2

The sample is a within-independent-sample validation set. It must not be described as global 630-candidate recall.

|   sample_order | candidate_id   | pair_key   | stratum   |    score |   intervention_volume_m3 |
|---------------:|:---------------|:-----------|:----------|---------:|-------------------------:|
|              1 | P259           | C11,C19    | Q1        | 0.187359 |                  1747.62 |
|              2 | P173           | C8,C17     | Q1        | 0.187841 |                  2853.8  |
|              3 | P125           | C6,C31     | Q1        | 0.165306 |                  4811.86 |
|              4 | P031           | C3,C37     | Q1        | 0.121107 |                  5912.05 |
|              5 | P237           | C10,C25    | Q2        | 0.205917 |                  1018.03 |
|              6 | P375           | C16,C39    | Q2        | 0.209442 |                  1246.13 |
|              7 | P413           | C18,C33    | Q2        | 0.240865 |                  1661.86 |
|              8 | P601           | C32,C40    | Q2        | 0.215248 |                  2410.72 |
|              9 | P442           | C20,C22    | Q3        | 0.330948 |                  1250.9  |
|             10 | P561           | C28,C38    | Q3        | 0.309396 |                  1817.5  |
|             11 | P044           | C4,C13     | Q3        | 0.3138   |                  4753.85 |
|             12 | P547           | C27,C36    | Q3        | 0.333255 |                  6000.25 |
|             13 | P528           | C26,C29    | Q4        | 0.385915 |                  1793.8  |
|             14 | P467           | C21,C30    | Q4        | 0.405876 |                  2485.97 |
|             15 | P076           | C5,C12     | Q4        | 0.386485 |                  2645.26 |
|             16 | P615           | C35,C44    | Q4        | 0.396501 |                  7307.56 |
|             17 | P141           | C7,C15     | Q5        | 0.52784  |                  6207.92 |
|             18 | P216           | C9,C32     | Q5        | 0.558978 |                  3238.46 |
|             19 | P508           | C24,C39    | Q5        | 0.499784 |                  3868.09 |
|             20 | P305           | C12,C44    | Q5        | 0.418121 |                  6034.78 |
