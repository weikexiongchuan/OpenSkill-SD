# Model Family Comparison

## Scope
Use this table for first-pass comparison when users ask what differs between major SDXL branches.

## Family Matrix
| Family | Core Positioning | Prompt Style | Ecosystem Fit | Stability (Inference) | LoRA Portability |
|---|---|---|---|---|---|
| SDXL Base 1.0 | General-purpose base model | Natural language, moderate tags | Broadest tooling support | High | Highest within SDXL family |
| Illustrious XL | Anime-focused SDXL derivative with strong detail | Natural language plus tag-friendly prompting | Strong in anime workflows | Medium-High | Good inside Illustrious-like stacks |
| NoobAI XL | Illustrious-derived aesthetic tuning | Tag-heavy style control common | Popular for specific anime rendering styles | Medium | Best inside matching Noob/Illustrious downstream checkpoints; version matching matters |
| Animagine XL | Anime model family with mature tag conventions | Structured tags, order-sensitive prompts | Large anime user base and templates | Medium-High | Best inside Animagine line and close derivatives |
| Pony Diffusion XL | Niche style ecosystem with custom prompt conventions | Score/source tags and stricter conventions | Active but more specialized ecosystem | Medium | Lower cross-family portability |

## Practical Meaning of Stability
`High`: predictable prompt behavior, many known presets, fewer workflow surprises.
`Medium-High`: mostly stable with some family-specific conventions.
`Medium`: good outputs possible but more configuration sensitivity.

## Comparison Checklist
1. Check where inference will run in production.
2. Check whether prompt syntax must remain natural-language first.
3. Check whether LoRA must transfer across model families.
4. Check whether license restrictions affect commercial deployment.
5. Check whether team has existing presets for this family.


## NoobAI Version Note
- `NoobAI XL` should be selected with an explicit `version + branch`, not only by family name.
- Current workspace-selectable slots are `1.1 + epsilon`, `1.0 + epsilon`, `0.5 + epsilon`, and `0.5 + vpred`.
- If deployment is already fixed to one Noob slot, use the same slot for LoRA training first.
- If the user is a beginner and the Noob slot is still undecided, default workspace recommendation is `NoobAI XL 1.1` + `epsilon`.

## Recommendation Defaults
1. Choose `SDXL Base` when portability and neutral behavior matter most.
2. Choose `Illustrious` when anime direction is needed with moderate flexibility.
3. Choose `NoobAI` when target look is already Noob-like and deployment is fixed there; if slot is undecided, beginner default is `1.1 + epsilon`.
4. Choose `Animagine` when pipeline already relies on its tag conventions.
5. Choose `Pony` only when downstream inference is explicitly Pony-centric.
