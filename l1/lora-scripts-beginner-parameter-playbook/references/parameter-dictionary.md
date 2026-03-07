# Parameter Dictionary

## Scope
This dictionary only keeps the core fields a beginner usually needs to touch first.

## Read Rule
- If the user is a beginner, start from this file before showing the full schema.
- Prefer keeping other fields at their default values unless there is a clear reason to change them.
- If the user already knows the training scene but not whether the base model is `二次元` or `三次元`, route to `domain-2d-vs-3d.md` next.

## Core Parameters
| param | 作用 | 小白起手怎么填 | 什么时候再动它 |
|---|---|---|---|
| `model_train_type` | 训练家族 | 先选 `sdxl-lora`、`sd-lora`、`sd3-lora`、`flux-lora` 之一 | 只有换底模家族时才改 |
| `pretrained_model_name_or_path` | 底模路径 | 填你要挂载的底模 | 底模换了才改 |
| `train_data_dir` | 训练集目录 | 填数据集文件夹 | 数据集换了才改 |
| `resolution` | 训练分辨率 | 先按模型家族起手值填 | 画质/显存不平衡时再改 |
| `enable_bucket` | 允许不同宽高比 | 默认开 | 只有你明确要固定尺寸时才关 |
| `network_module` | LoRA 网络类型 | 默认用 LoRA，不先碰 OFT / LyCORIS | 想练特殊网络再改 |
| `network_dim` | LoRA 容量 | 先按家族或场景起手值填 | 模型学不住或过拟合时再调 |
| `network_alpha` | LoRA 缩放 | 先填 `dim` 的一半，或直接用家族默认 | 只有在 rank 很小或想更稳时再调 |
| `network_train_unet_only` | 是否只训 U-Net | Flux / SD3 / Lumina 先开；SDXL 也常可先开 | 角色触发词学不住时再考虑关掉 |
| `unet_lr` / `learning_rate` | 主学习率 | 默认先 `1e-4` | loss 不稳或过拟合时再降 |
| `text_encoder_lr` | 文本编码器学习率 | SD/SDXL 先 `1e-5`；不训文本编码器就不用管 | 角色词不稳时再微调 |
| `optimizer_type` | 优化器 | 默认 `AdamW8bit` | 显存非常紧或有明确经验时再换 |
| `lr_scheduler` | 学习率策略 | 默认 `cosine_with_restarts` | 想极简时可换 `constant` |
| `train_batch_size` | 单步批量 | 先 `1`，Lumina 可 `2` | 显存足够时再加 |
| `max_train_epochs` | 总训练轮数 | 先按模型家族和场景起手值填 | 看样张不够或过拟合再调 |
| `mixed_precision` | 训练精度 | RTX30 及以后优先 `bf16`；不稳就 `fp16` | 遇兼容性问题时再改 |
| `cache_latents` | 缓存 latent | 默认开 | 磁盘太紧张时再关 |
| `cache_text_encoder_outputs` | 缓存文本编码器输出 | Flux / SD3 / Lumina 默认开；开时不要再乱用 `shuffle_caption` | 只有要训文本编码器时再重看 |
| `shuffle_caption` | 打乱标签 | 画风训练常开；角色/服装要保留触发词时谨慎 | 开了缓存文本编码器时通常别乱开 |
| `keep_tokens` | 保留前几个 token | 角色/服装常从 `1` 起；画风常 `0` | 触发词丢失时再加 |
| `save_every_n_epochs` | 每几轮保存 | 默认 `1` 或 `2` | 只影响中间检查点密度 |
| `sample_every_n_epochs` | 每几轮出预览 | 默认 `2` | 想更频繁看图时再改 |

## Domain-Sensitive Parameters
| param | 二次元 / 标签型底模 | 三次元 / 写实自然语言型底模 |
|---|---|---|
| `resolution` | `Illustrious` / `NoobAI` 直接优先 `1024` 面积 | 写实高质量也直接优先 `1024` 面积 |
| `shuffle_caption` | 常开；对逗号分隔 tag 更有意义 | 句子 caption 默认关；caption 真是 tag 时才再考虑开 |
| `keep_tokens` | 角色 / 服装常 `1`，必要时 `2` | 默认 `0`；更依赖稳定 caption 写法，不靠 token 保护 |
| `keep_tokens_separator` / `secondary_separator` | 只在要保护固定 tag 前缀时使用 | 多数不需要 |
| `network_train_unet_only` | 画风 / 服装多从 `true` 起，角色按触发词稳定性决定 | 真人脸 / 身份任务更值得从 `false` 起 |
| `text_encoder_lr` | 只在真的训练 text encoder 时才重要 | 若训真人脸或身份词，`1e-5` 的价值更高 |
| `sample prompts` | 更适合 tag 或短 tag+自然语言混合提示词 | 更适合自然语言 photo prompt |

## Small-Beginner Rule
- 先只动 `model_train_type`、底模、数据集、分辨率、rank/alpha、学习率、epoch。
- 如果已经知道自己是 `二次元` 还是 `三次元`，再补看 `domain-2d-vs-3d.md` 里那几项域敏感参数。
- 其他参数能不动就不动。
