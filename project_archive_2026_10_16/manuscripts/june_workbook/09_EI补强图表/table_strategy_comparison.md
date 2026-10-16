# Table: Strategy comparison

| scheme_type     | average_sunlight_hours | dark_zone_ratio | intervention_volume | changed_building_ids | notes                                                                   |
| --------------- | ---------------------- | --------------- | ------------------- | -------------------- | ----------------------------------------------------------------------- |
| baseline        | 6.422                  | 17.55%          | 0.000               | nan                  | Existing condition from Algorithm A; no manual-design placeholder.      |
| AI_conservative | 6.435                  | 16.94%          | 28.125              | C33;C6               | 保守型 AI selected candidate; post-simulated with simplified 2.5D model.   |
| AI_balanced     | 6.435                  | 16.94%          | 45.000              | C33;C6               | 均衡型 AI selected candidate; post-simulated with simplified 2.5D model.   |
| AI_light_first  | 6.435                  | 16.94%          | 46.095              | C33;C6;C9            | 采光优先型 AI selected candidate; post-simulated with simplified 2.5D model. |
