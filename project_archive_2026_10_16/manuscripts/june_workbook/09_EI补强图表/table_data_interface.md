# Table: Data interface

| Data source  | Main content                                                       | Role in workflow                          | Human verification needed or not    |
| ------------ | ------------------------------------------------------------------ | ----------------------------------------- | ----------------------------------- |
| CAD/DXF      | building labels, road layer, height annotations                    | spatial reference and object identity     | needed                              |
| SKP          | complete site model and context                                    | manual review and sunlight re-check model | needed                              |
| OBJ          | white-model massing geometry                                       | algorithm-readable geometric input        | needed                              |
| CSV          | building_id, bounds, height, movable/protected status              | stable computation table                  | needed                              |
| manual notes | C42 fixed, C38/C39/C45 height clarification, duplicate-id handling | constraint correction and model audit     | source itself is human verification |
