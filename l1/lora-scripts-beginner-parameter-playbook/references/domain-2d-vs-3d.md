# 2D / 3D Domain Overlay

## Scope
- This file is a domain overlay on top of `model-family-starters.md` and `scenario-recipes.md`.
- `二次元` here means illustration / anime / tag-native bases such as `Illustrious` and `NoobAI`.
- `三次元` here means photo / real-person / photoreal bases, usually `SDXL base` or photo-oriented SDXL merges.
- Keep `direct facts` and `beginner overlay` separate.

## Direct Facts From Official Sources
- `Illustrious-XL-v1.0` says it supports both natural language prompts and Danbooru tags, and its native resolution support goes from `512x512` to `1536x1536`.
- `NoobAI XL 1.1` says it uses `native tags caption`, recommends total area around `1024x1024`, and gives a preferred caption order `<1girl/1boy/...>, <character>, <series>, <artists>, <special tags>, <general tags>, <other tags>`.
- kohya config docs say `shuffle_caption` only makes sense for comma-separated captions and has no meaning for sentence captions.
- kohya config docs say `keep_tokens` only works when `shuffle_caption` is enabled.
- kohya config docs expose `caption_prefix` / `caption_suffix` / `keep_tokens_separator` / `secondary_separator` for keeping parts of captions fixed against shuffling or dropout.
- Hugging Face diffusers DreamBooth docs say training the text encoder improves quality, especially faces, but needs about `24GB` VRAM.

## Beginner Overlay
These are inferred starter rules built from the direct facts above.

### 1. 二次元 / 标签型底模
#### Caption Style
- Prefer stable tag captions over long prose.
- If the base is `NoobAI`, keep the subject / character / series / artist / tag structure stable instead of rewriting every caption into free-form sentences.
- If the base is `Illustrious`, hybrid prompting is possible, but small beginner datasets still work more predictably when the caption style is consistent.

#### Parameter Bias
- `shuffle_caption=true` is usually the better default.
- `keep_tokens=1` for character / outfit is the normal start; `0` for pure style training.
- Raise `keep_tokens` to `2` only when the front trigger block really needs to stay fixed.
- `keep_tokens_separator` or `secondary_separator` are optional advanced tools only when a fixed front tag block must not be shuffled.
- `resolution` should start near `1024` area when quality is the target.
- `network_train_unet_only=true` stays fine for style or outfit; for character identity stability, `false` is still worth trying.

#### Prompt And Sample Style
- Use tag prompts or short tag-first prompts.
- Do not default to long photographic prose.

### 2. 三次元 / 写实自然语言型底模
#### Caption Style
- Prefer short natural-language captions or subject-first descriptive phrases.
- Do not copy Danbooru quality/date tag stacks into a photo dataset by habit.
- If the captions are sentences instead of tag lists, do not rely on tag-shuffling controls as the main identity tool.

#### Parameter Bias
- `shuffle_caption=false` is the safer default unless the captions are actually comma-separated tags.
- `keep_tokens=0` is the safer default.
- If a trigger phrase matters, keep the phrase literally stable in the captions instead of depending on `keep_tokens`.
- `keep_tokens_separator` / `secondary_separator` / `caption_prefix` are usually unnecessary.
- `resolution` should stay on the `1024` line when face and skin detail matter.
- For real-person face or identity LoRA, `network_train_unet_only=false` is more worth trying than in pure 2D style training.
- If VRAM is enough and the task is face-heavy, keeping text encoder training in play is more valuable here.

#### Prompt And Sample Style
- Use natural-language photo prompts.
- Do not evaluate a photo LoRA only with Danbooru-tag style sample prompts.

## Quick Choice Rule
- If the base model is `Illustrious` / `NoobAI`, or the dataset captions are tag-native, start from the `二次元` branch.
- If the base model is a photo-real SDXL line and the captions are sentence-like, start from the `三次元` branch.
- If the dataset mixes both styles, first make the caption style consistent before tuning advanced parameters.

## Source Anchors
- Illustrious XL model card: `https://huggingface.co/OnomaAIResearch/Illustrious-XL-v1.0`
- NoobAI XL 1.1 model card: `https://huggingface.co/Laxhar/noobai-XL-1.1`
- kohya_ss LoRA parameter wiki: `https://github.com/bmaltais/kohya_ss/wiki/LoRA-training-parameters`
- diffusers DreamBooth docs: `https://huggingface.co/docs/diffusers/training/dreambooth`
