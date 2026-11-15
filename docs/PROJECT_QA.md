# Interview Talking Points

## 30-second Version

Light Right Repair is an AI-assisted spatial decision prototype for urban light equity. I converted a design problem into a repeatable workflow: the system reads a simplified block model, diagnoses low-light zones, generates minimal repair candidates, validates them against accessibility and safety constraints, and outputs a recommendation for designer review.

## 60-second Version

This project is not about using AI to make a rendering. I treated light equity as a product problem: what does the user input, what does the system process, what does it output, and how do we verify the result? The workflow has three stages. Algorithm A estimates sunlight exposure and identifies dark zones. Algorithm B generates small intervention candidates and scores them by light gain, intervention volume, shadow risk, and protected-zone conflict. Algorithm C checks accessibility and safety before producing a final recommendation. The current release is a public-safe prototype with a toy dataset and a standalone OBJ import mode.

## How to Answer "Is This Really AI?"

I would describe it as AI-assisted spatial decision workflow rather than a black-box AI model. The value is in structuring the spatial task into an input-process-output-validation loop. In future versions, an LLM or agent layer could help explain candidate trade-offs, but even v0.1 already shows how spatial decisions can become repeatable, measurable, and reviewable.

## What Not to Overclaim

- Do not claim professional daylight certification.
- Do not claim fully autonomous design.
- Do not claim the toy dataset represents a real site.
- Do not claim every candidate improves sunlight.
- Do not claim safety without manual site verification.

## Best Resume Bullet

Designed a Python-based AI-assisted spatial decision prototype that diagnoses low-light public spaces, generates minimal repair candidates, validates accessibility and safety constraints, and outputs explainable metrics for human design review.

## Portfolio Caption

From spatial justice issue to product workflow: site model input, sunlight diagnosis, candidate generation, rule validation, and final recommendation.
