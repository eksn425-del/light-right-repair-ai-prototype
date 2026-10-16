# Light Equity Dataset Contract

Use this checklist before trusting ABC outputs.

## Required Files

`site_model.obj`
: SketchUp or equivalent white-model OBJ. Units must be meters. Z is assumed vertical. Prefer one group/object per building.

`buildings.csv`
: Required columns: `building_id`, `name`, `x_min`, `x_max`, `y_min`, `y_max`, `height_m`, `floors`, `movable`, `protected`, `facade_type`, `notes`.

`streets.csv`
: Required columns: `street_id`, `start_x`, `start_y`, `end_x`, `end_y`, `width_m`, `main_direction`, `pedestrian_priority`, `notes`.

`nodes.csv`
: Required columns: `node_id`, `x`, `y`, `z`, `node_type`, `importance`, `notes`.

`protected_zones.csv`
: Required columns: `zone_id`, `x_min`, `x_max`, `y_min`, `y_max`, `z_min`, `z_max`, `reason`, `notes`.

## Usability Grades

Grade A: real OBJ grouped by building, manually checked `buildings.csv`, surveyed street centerlines, accessibility nodes, protected zones.

Grade B: real OBJ and building CSV checked, road/nodes partly inferred. Good for algorithm experiments, not final safety claims.

Grade C: standalone OBJ auto-converted to CSV. Good only for pipeline testing and early diagnosis.

Reject: OBJ has no vertices, coordinates are not meters, buildings are ungrouped and no CSV exists, or no street/path data is available.

## Reporting Caveats

Always state:

- grid size;
- winter-solstice sampling period;
- whether candidates were post-simulation verified;
- whether road/node data is surveyed or inferred;
- whether manual design values are placeholders or real.

