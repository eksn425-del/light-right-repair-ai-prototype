# Standalone OBJ Validation Guide

## What This Mode Is For

Standalone OBJ mode lets you test whether a single exported massing model can enter the workflow. It is useful for early feasibility checks and portfolio demos.

It should not be used as a final design judgment unless the generated dataset is manually corrected.

## Command

```bash
python main.py --obj examples/single_mass_block.obj --overwrite-obj-dataset --diagnosis-only --output-dir outputs/single_mass_check
```

For your own model:

```bash
python main.py --obj path/to/your_model.obj --overwrite-obj-dataset --diagnosis-only --output-dir outputs/your_model_check
```

## Expected OBJ Format

Best input:

- Wavefront OBJ file.
- Z-up massing model.
- One object or group per building or massing block.
- Realistic model units in meters.
- Simple white-model geometry.

Acceptable for early testing:

- One single massing block.

Less reliable:

- One merged site mesh with no object/group separation.
- Decorative high-poly model.
- Terrain-only OBJ.
- Model with unknown scale or wrong vertical axis.

## What the System Auto-generates

When only an OBJ is provided, the system creates a rough dataset under `data/auto_obj/`:

- `site_model.obj`
- `buildings.csv`
- `streets.csv`
- `nodes.csv`
- `protected_zones.csv`
- `site_zones.csv`
- `auto_obj_summary.json`

The auto-generated street and nodes are fallback placeholders. Replace them before making serious spatial claims.

## How to Interpret a Single Block Result

If there is only one massing block, use `--diagnosis-only`. The result mainly checks:

- whether the geometry can be parsed
- whether bounding boxes and height are readable
- whether the sunlight grid can be generated
- whether the report pipeline works

It cannot reliably prove a real light-right repair strategy because a single block lacks the surrounding urban context that creates meaningful shadow and intervention trade-offs. Full A/B/C mode is better for a multi-building grouped OBJ or a manually prepared dataset.

## Recommended Validation Ladder

1. Start with one simple block to confirm OBJ import.
2. Add neighboring blocks to create real shadow context.
3. Group each building separately in the OBJ.
4. Replace fallback `streets.csv` with actual road centerlines.
5. Add protected buildings and public-space zones.
6. Rerun without `--diagnosis-only`.
7. Add `--verify-candidates` for a slower but stronger candidate ranking.
8. Review candidate recommendations manually.

## Product-manager Conclusion

For an interview or portfolio review, standalone OBJ mode is valuable as a demo of system extensibility. For real design claims, use a manually prepared dataset with verified street, building, and accessibility data.
