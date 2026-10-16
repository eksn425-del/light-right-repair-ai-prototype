# Table: Algorithm parameters

| Parameter      | Value                                                  | Used in                        | Explanation                                  | Limitation                                                      |
| -------------- | ------------------------------------------------------ | ------------------------------ | -------------------------------------------- | --------------------------------------------------------------- |
| location       | Xiamen / Guankou                                       | Algorithm A                    | site latitude/longitude context              | not a certified daylight compliance setup                       |
| date           | winter solstice                                        | Algorithm A/C                  | low-sun seasonal diagnostic condition        | single-day simplified diagnosis                                 |
| time range     | 8:00-16:00                                             | Algorithm A/C                  | hourly sunlight-hour accumulation            | does not model all-year radiation                               |
| grid size      | 6 m baseline; 3 m sensitivity                          | diagnosis and sensitivity test | ground sample spacing                        | candidate ranking changes with grid scale                       |
| model type     | simplified 2.5D obstruction model                      | Algorithm A/C                  | building masses approximated by height boxes | not professional daylight simulation                            |
| movable rule   | C42 kindergarten fixed; others candidates only         | Algorithm B                    | human-confirmed intervention constraint      | real feasibility still needs structure/property/function review |
| output metrics | average sunlight hours; dark-zone ratio                | results                        | early-stage comparison metrics               | not legal sunshine-right judgement                              |
| strategy types | baseline, conservative, balanced, daylight-prioritized | strategy comparison            | controlled AI strategy comparison            | not AI-vs-human comparison                                      |
