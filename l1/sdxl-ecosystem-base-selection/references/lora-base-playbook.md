# LoRA Base Playbook

## Decision Flow
1. Lock deployment checkpoint first.
2. Lock checkpoint family and version together whenever the target stack is already known.
3. Train LoRA on the same checkpoint family whenever possible.
4. Use cross-family transfer only as fallback and warn about drift risk.

## Base Selection by Goal
| Goal | Preferred Base Family | Why |
|---|---|---|
| Maximum reuse across unknown SDXL checkpoints | SDXL Base | Lowest coupling to branch-specific prompt conventions |
| Anime character LoRA for Illustrious-like pipeline | Illustrious or direct target checkpoint | Better style alignment and lower inference mismatch |
| Noob-centric final rendering | NoobAI matching target inference version | Minimizes trigger-word and style drift |
| Animagine-centric production | Animagine matching major version | Preserves expected tag semantics |
| Pony-centric production | Pony matching runtime stack | Avoids prompt-contract mismatch |


## NoobAI Version Rule
- Treat `NoobAI` as a version- and branch-sensitive family; do not only record `noobai` without `family_version` and `family_branch`.
- Current workspace-selectable Noob slots:
  - `NoobAI XL 1.1` + `epsilon` → `Laxhar/noobai-XL-1.1` → beginner default.
  - `NoobAI XL 1.0` + `epsilon` → `Laxhar/noobai-XL-1.0` → compatibility fallback.
  - `NoobAI XL 0.5` + `epsilon` → `Laxhar/noobai-XL-0.5` → legacy fallback.
  - `NoobAI XL 0.5` + `vpred` → `Laxhar/noobai-XL-Vpred-0.5` → only for old v-pred stacks.
- If downstream inference is already fixed to one Noob slot, train on the same slot first.
- If the user is a beginner and the Noob slot is still undecided, default to `NoobAI XL 1.1` + `epsilon`.
- Keep `NoobAI XL 1.0` + `epsilon` as the main compatibility fallback.
- Use `vpred` only when the downstream stack is already confirmed to be v-pred.

## Risk Flags
- Training on one family and deploying on another.
- Using mixed caption styles without normalization.
- Ignoring license terms of the target base.
- Changing VAE or text encoder assumptions between train and inference.

## Handoff Template
Return this block when finishing a recommendation:

```
base_model: <exact checkpoint or repo id>
family: <sdxl-base|illustrious|noobai|animagine|pony>
family_version: <exact version or empty>
family_branch: <epsilon|vpred|empty>
reason: <one sentence>
expected_prompt_style: <natural|tag-heavy|pony-score-tags>
license_review_required: <yes|no>
fallback_base_model: <exact checkpoint or repo id>
```
