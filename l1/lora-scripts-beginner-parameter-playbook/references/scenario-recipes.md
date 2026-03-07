# Scenario Recipes

## Read Rule
- These are beginner starter recipes for three user-facing scenes.
- They are simplified recommendations inferred from official defaults, official example commands, and web-form defaults, not upstream hard rules.
- Start from the matching model-family starter first, then apply the domain overlay in `domain-2d-vs-3d.md`, then apply the scene delta below.

## Domain Overlay First
- `二次元 / 标签型底模`：先看 `domain-2d-vs-3d.md` 的 2D 分支。
- `三次元 / 写实自然语言型底模`：先看 `domain-2d-vs-3d.md` 的 3D 分支。
- 如果 caption 风格混杂，先统一数据，再谈高级参数。

## 1. 画风训练
### 适合谁
- 主要想学“整体风格、笔触、色调、构图倾向”。

### 首选家族
- 首选 `sdxl-lora`
- 旧生态或显存更紧时用 `sd-lora`

### 起手参数
- `network_dim=16~32`
- `network_alpha=8~16` 或直接取 `dim` 的一半
- `network_train_unet_only=true` 可先开
- `keep_tokens=0`
- `shuffle_caption=true`
- `epoch=6~10`

### 域差异提醒
- `二次元`：tag caption 常更稳，`shuffle_caption=true` 的价值更高。
- `三次元`：如果 caption 是句子，`shuffle_caption` 可以直接当作默认关闭项。

### 调参方向
- 风格不明显：先把 `epoch` 提到 `10~12`，再考虑把 `dim` 提到 `32`
- 过拟合、样张开始死板：先降 `epoch`，再降 `dim`

## 2. 角色训练
### 适合谁
- 主要想学“同一个角色的脸、发型、气质、标志特征和触发词”。

### 首选家族
- 首选 `sdxl-lora`
- 已经绑定旧底模生态时用 `sd-lora`

### 起手参数
- `network_dim=32~64`
- `network_alpha=16~32`
- `network_train_unet_only=false` 更容易学到触发词；如果显存不够，先开 `true` 再看结果
- `text_encoder_lr=1e-5` 起步
- `keep_tokens=1`，必要时 `2`
- `shuffle_caption=true`，但要保证触发词在前面
- `epoch=8~14`

### 域差异提醒
- `二次元`：角色 tag 常放前面，`keep_tokens=1~2` 更常用。
- `三次元`：如果是自然语言 caption，优先保持固定主语写法，而不是依赖 `keep_tokens`。
- `三次元` 真人脸：`network_train_unet_only=false` 和 text encoder 训练价值更高。

### 调参方向
- 触发词不稳：先把 `keep_tokens` 从 `1` 加到 `2`
- 角色脸不像：先补数据一致性，再把 `epoch` 小幅加到 `12~16`
- 过拟合：先降 `epoch`，再把 `dim` 从 `64` 降回 `32`

## 3. 服装 / 配饰训练
### 适合谁
- 主要想学“某件衣服、帽子、眼镜、武器、发饰、包”等局部概念。

### 首选家族
- 首选 `sdxl-lora`
- 兼容旧生态时用 `sd-lora`

### 起手参数
- `network_dim=8~16`
- `network_alpha=4~8`
- `network_train_unet_only=true`
- `keep_tokens=1`（如果有固定触发词）
- `shuffle_caption=true`，但别把触发词打散掉
- `epoch=6~10`

### 域差异提醒
- `二次元`：tag 型服装词和配饰词更适合 `keep_tokens=1` 起步。
- `三次元`：若 caption 是句子，先保证局部概念写法稳定，再考虑要不要保留 token。

### 调参方向
- 配饰细节学不住：先把 `dim` 提到 `16~32`
- 学到人物本体太多：先降 `epoch`，再减少数据中的人物变化干扰
- 只想学某个部件：先优先整理裁切和标注，而不是盲目加大 `dim`

## Beginner Decision Shortcut
- 不确定选什么：先 `sdxl-lora`
- 不确定是 `二次元` 还是 `三次元`：先看底模和 caption 风格，再套 `domain-2d-vs-3d.md`
- 先只练整体风格：先 `画风训练`
- 先让名字/触发词稳定：走 `角色训练`
- 只学局部物件：走 `服装/配饰训练`
