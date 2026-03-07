# AutoDL Storage And Asset Flow

## Scope
- 这份参考只服务 `AutoDL` 场景。
- 其他服务器厂商后续再补各自的 provider reference，不把规则提前写死到通用层。

## Storage Budget Rule
- 默认把 `/root/autodl-tmp` 视为服务器运行盘，当前口径按 `80G` 免费空间优先规划。
- 默认把 `/autodl-fs/data` 视为 AutoDL “文件存储”对应挂载点，当前口径按 `20G` 免费空间规划；超出部分可能计费。
- 因此不要默认把大模型、大数据集、训练输出在 `tmp` 和 `fs` 双份长期保留。

## UI Mapping
- 用户在 AutoDL 界面里看到的“文件存储”标签，对应服务器内的 `/autodl-fs/data`。
- 用户手动上传文件到“文件存储”后，服务侧默认从 `/autodl-fs/data/...` 取用。

## Placement Rule
- `tmp`：活跃项目、运行中的服务、当前训练、短期缓存。
- `fs`：用户手动上传的模型/数据集、长期保留的底模、跨实例复用的共享文件。
- `pub`：只读公共区，只当候选来源，不当默认落盘位置。

## Deploy-Start Reminder
- 部署开始时，如果当前场景需要模型、数据集或工作流素材，先告诉用户“要上传什么”，再继续部署。
- 默认只报必需物：
  - ComfyUI：checkpoint / LoRA / VAE / workflow（按当前需求）
  - LoRA 训练：base model / dataset / optional config
- 提醒用户上传到 AutoDL 界面的“文件存储”标签，不要先让用户猜服务器路径。

## Post-Deploy Fetch Rule
- 服务部署完成后，不默认擅自拷贝所有大文件到运行盘。
- 等用户明确说“用哪个模型 / 用哪份数据”后，再从 `/autodl-fs/data/...` 拿到当前运行目录。
- 需要性能时可复制到 `/root/autodl-tmp/...`；不需要时优先软链或直接引用共享路径。
- 如果训练集在用户本地电脑，也可以直接上传到当前服务器；默认先传到 `/autodl-fs/data/datasets`，再在服务器上做训练集检查和裁剪/补白。

## Download Branch
- 如果用户不想手动上传，场景层要明确告诉用户：后续也可以走下载脚本分支。
- 如果源站在 HuggingFace，默认优先考虑 `HF_ENDPOINT=https://hf-mirror.com` 的镜像下载路径。
- 下载脚本分支的默认落盘优先级：先落到 `/autodl-fs/data/models` 或 `/autodl-fs/data/datasets`，再按运行需要同步到 `/root/autodl-tmp`。
- 如果远端下载明显偏慢，也可以先在本地下载源文件，再上传到 AutoDL 的“文件存储”；上传后即可直接取用。
- 如果用户需要，可以给下载引导和上传引导；如果用户本地没有 VPN，且源文件难以获得，就提示他们联系脚本作者或社区寻求源文件。

## Copy-Control Rule
- 大模型默认不做“上传一份、运行一份、输出再留一份”的三份复制。
- 能复用共享路径就复用；只有在启动性能、工具兼容性或训练吞吐明确受影响时，才复制到 `tmp`。
