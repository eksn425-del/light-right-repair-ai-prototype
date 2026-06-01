# AI Product Flow Diagram

This diagram explains Light Right Repair as an AI-assisted decision product, not as a pure modeling script.

```mermaid
flowchart LR
    A["User / Design Team Need<br/>Which blocks should be repaired first?"] --> B["Input Data<br/>street massing OBJ<br/>building heights<br/>road nodes<br/>protected zones"]
    B --> C["Algorithm A<br/>sunlight diagnosis<br/>dark-zone detection<br/>heatmap generation"]
    C --> D["Algorithm B<br/>candidate intervention generation<br/>minimal-change strategy<br/>candidate scoring"]
    D --> E["Algorithm C<br/>accessibility and safety validation<br/>rule conflict screening"]
    E --> F["Output<br/>priority repair blocks<br/>candidate OBJ<br/>before-after metrics<br/>recommendation report"]
    F --> G["Human Validation<br/>designer checks geometry, rules, and caveats"]
    G --> H["Feedback Loop<br/>adjust constraints<br/>rerun diagnosis<br/>compare next candidate"]
    H --> C
```

## Product Manager Reading

- **User problem:** Designers need an explainable way to identify priority light-equity repair targets.
- **AI / algorithm role:** Convert spatial data into diagnosis, candidates, validation, and recommendations.
- **Output value:** Produce reviewable evidence instead of a black-box design result.
- **Validation:** Human designers remain responsible for checking geometry accuracy and planning feasibility.
