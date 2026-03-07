# Official Diagnosis Rubric

## Primary Sources
- Akegarasu `lora-scripts`: https://github.com/Akegarasu/lora-scripts
- kohya-ss `train_network_README.md`: https://github.com/kohya-ss/sd-scripts/blob/main/docs/train_network_README.md
- kohya-ss `config_README-en.md`: https://github.com/kohya-ss/sd-scripts/blob/main/docs/config_README-en.md
- kohya_ss LoRA parameter wiki: https://github.com/bmaltais/kohya_ss/wiki/LoRA-training-parameters
- Illustrious XL model card: https://huggingface.co/OnomaAIResearch/Illustrious-XL-v1.0
- NoobAI XL 1.1 model card: https://huggingface.co/Laxhar/noobai-XL-1.1
- diffusers DreamBooth docs: https://huggingface.co/docs/diffusers/training/dreambooth

## How To Judge
- 先分 `confirmed` 和 `inference`。
- `confirmed` 只来自：数据台账、配置文件、API 状态、日志错误、TensorBoard event 文件是否出现。
- `inference` 只来自：loss 走势、step 进度、模板与场景匹配度、域类型与 caption 风格匹配度、可观察性不足时的保守推断。
- 若没配置验证样张或验证集，不要把“训练 loss 下降”直接等同于“最终效果一定更好”。

## Dataset Signals
- 官方训练文档把 `repeats` 视为数据有效训练次数的一部分，因此分析时应同时看“原始图片数”和“图片数 × repeats”。来源：`train_network_README.md`。
- `keep_tokens` 用于在 `shuffle_caption` 开启时保留前 N 个 token，不被打乱；角色或服装触发词稳定性分析时要特别检查这两项是否冲突。来源：`config_README-en.md`。
- `bucket_no_upscale=true` 时，`min_bucket_reso` 与 `max_bucket_reso` 会被忽略，因此看到这组参数并不代表它们实际生效。来源：`train_network_README.md`。

## Domain Mismatch Signals
- `confirmed`：如果 caption 是句子，但配置仍 heavily 依赖 `shuffle_caption`、`keep_tokens`、`keep_tokens_separator` 之类 tag 控件，应判为 `confirmed weak-fit config choice`；因为 kohya 文档明确写了 `shuffle_caption` 对句子 caption 没意义，`keep_tokens` 也依赖 `shuffle_caption`。
- `confirmed`：如果用户把 `cache_text_encoder_outputs=true` 打开，同时又声称要靠 text encoder 训练提升真人脸或身份词稳定性，应判为 `confirmed config conflict`。
- `inference`：如果底模是 `NoobAI` / `Illustrious` 这类 tag-native 或 tag-friendly 体系，但 caption 被写成长篇自然语言，而且前景触发词不稳定，可判为 `inference domain-caption mismatch risk`。
- `inference`：如果底模是偏写实 photo 体系，但训练集塞入大量 Danbooru 质量 / 日期 / 站点风格 tag，且用户目标是写实真人风格，可判为 `inference domain-caption mismatch risk`。
- `inference`：如果任务是三次元真人脸或身份 LoRA，而配置始终只训 U-Net，可写成“可能限制身份词和脸部稳定性”的推断；官方 diffusers 文档明确说训练 text encoder 对 faces 更有帮助，但这不是所有场景都必须开启的硬规则。

## Config Interaction Signals
- `cache_text_encoder_outputs=true` 时：
  - text encoder 不会被训练；
  - `shuffle_caption`、`caption_dropout_rate`、`token_warmup_*`、tag dropout 之类依赖文本编码实时变化的增强项不会生效。
  来源：`config_README-en.md`。
- 诊断时如果用户以为“自己在训 text encoder”或“自己开了 caption 增强”，但同时启用了 `cache_text_encoder_outputs`，这应判为 `confirmed config conflict`。
- 训练配置必须是可执行数值，而不是字符串形式的伪数值；若学习率、epoch、batch 等字段仍是 `"1e-4"`、`"8"`、`"8~10"` 这类字符串，应先归一化再启动。这个结论来自运行器的实际类型要求与当前执行链路约束，属于工程约束，不是上游参数建议。

## Progress And Observability Signals
- `validation_prompt`、`validation_seed`、`validation_steps` 以及 `val_dataset_config` 用于生成验证样张和记录 `val_loss`；没有这些项时，分析者对“是否过拟合”的把握要降低。来源：`config_README-en.md`。
- 如果任务 API 显示 `RUNNING`，但新的 TensorBoard event 文件还没出现，不应过早判定“训练已正常开始”；应继续观察。这个结论属于执行链路判定规则，结合了上游 TensorBoard 输出行为与本工作区的启动闭环约束。

## Safe Diagnosis Patterns
- `log` 里出现明确 traceback、`OSError`、`ModuleNotFoundError`、`CUDA out of memory`、`No space left on device` 等，可直接归类为 `confirmed blocker`。
- `TensorBoard` 已出现 event 文件，且日志里已有 `steps:` 行持续推进，可归类为 `confirmed running`。
- 若只有 `train loss`，没有验证样张/验证集，则“可能过拟合/欠拟合”只能写成 `inference`，不要写成已确认结论。

## Output Contract
建议把结论分成四块：
1. 当前状态：是否已真正开始训练。
2. 已确认问题：只写确定问题。
3. 推断风险：明确标注“推断”。
4. 下一步动作：优先级从高到低。
