# Model Family Starters

## How To Read
- `官方默认` 指上游 schema 默认值或官方示例命令中明确给出的值。
- `入门建议` 是基于官方默认、官方示例命令和 web 表单结构做的简化建议；这是推断，不是官方硬性规定。

## SD / SDXL LoRA
### `sd-lora`
- `官方默认`：共享优化器默认 `unet_lr=1e-4`、`text_encoder_lr=1e-5`、`optimizer_type=AdamW8bit`、`lr_scheduler=cosine_with_restarts`；web schema 默认 `network_dim=32`、`network_alpha=32`。
- `入门建议`：先用 `resolution=512,512`、`network_dim=32`、`network_alpha=16`、`batch=1`、`epoch=8~12`。
- `说明`：这是最稳的入门档，适合旧生态或显存较紧。

### `sdxl-lora`
- `官方默认`：仍走 LoRA 主模板；web schema 默认 `network_dim=32`、`network_alpha=32`，并明确写了“训练 SDXL LoRA 时推荐开启 `network_train_unet_only`”。
- `入门建议`：先用 `resolution=1024,1024`。`network_dim=32`、`network_alpha=16`、`network_train_unet_only=true`、`batch=1`、`epoch=8~12`。
- `说明`：如果是小白用户，`sdxl-lora` 往往比 `sd-lora` 更适合作为画风和角色训练的第一选择。若底模本身是 `Illustrious` / `NoobAI` 这类二次元标签型 SDXL 分支，再额外叠加 `domain-2d-vs-3d.md` 的二次元域规则，分辨率直接按 `1024` 面积处理。

## SD3 LoRA
### `sd3-lora`
- `官方默认`：web schema 默认使用中档分辨率、`network_dim=4`、`network_alpha=1`、`epoch=20`、`batch=1`、`gradient_checkpointing=true`、`network_train_unet_only=true`、`cache_text_encoder_outputs=true`。
- `官方示例`：官方文档示例命令给出 `network_dim=4`、`network_train_unet_only`、`learning_rate=1e-4`、`mixed_precision=bf16`、`max_train_epochs=4`。
- `入门建议`：先用 `resolution=1024,1024`、`network_dim=4`、`network_alpha=1`、`network_train_unet_only=true`、`learning_rate=1e-4`、`epoch=4~8`。
- `说明`：先按 U-Net only 起步，别一开始就把文本编码器也训上。

## FLUX LoRA
### `flux-lora`
- `官方默认`：web schema 默认使用中档分辨率、`network_dim=2`、`network_alpha=16`、`epoch=20`、`batch=1`、`gradient_checkpointing=true`、`network_train_unet_only=true`、`cache_text_encoder_outputs=true`。
- `官方示例`：官方文档示例命令给出 `network_dim=4`、`network_train_unet_only`、`learning_rate=1e-4`、`mixed_precision=bf16`、`max_train_epochs=4`，并推荐 `timestep_sampling=shift`、`discrete_flow_shift=3.1582`、`model_prediction_type=raw`、`guidance_scale=1.0`。
- `入门建议`：先用 `resolution=1024,1024`、`network_dim=4`、`network_alpha` 保持表单默认、`network_train_unet_only=true`、`learning_rate=1e-4`、`epoch=4~8`。
- `说明`：Flux 家族更吃显存，先别急着训练文本编码器。

## Lumina LoRA
### `lumina-lora`
- `官方默认`：web schema 默认 `resolution=1024,1024`、`network_dim=16`、`network_alpha=8`、`epoch=10`、`batch=2`、`gradient_checkpointing=true`、`network_train_unet_only=true`、`cache_text_encoder_outputs=true`。
- `入门建议`：如果以后补齐执行链路，可先从 `resolution=1024,1024`、`network_dim=16`、`network_alpha=8`、`batch=1~2`、`epoch=6~10` 起步。
- `说明`：当前 lora-scripts Web API 训练映射还没把 `lumina-lora` 接好，先把它当“表单可见、执行链路待补”的家族。
