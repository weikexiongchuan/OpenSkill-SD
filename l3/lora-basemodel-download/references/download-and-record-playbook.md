# Download And Record Playbook

## Scope
- 这个 skill 先覆盖 LoRA 训练常用的 `NoobAI XL` 与 `Illustrious XL` 底模槽位。
- 当前默认来源是 catalog 内登记的 HuggingFace 官方模型页，默认下载模式是 `hf-mirror`。
- 这个 skill 只负责远端服务器下载；本地下载不在 skill 内执行。

## Default Path Rule
- 持久落盘：`/autodl-fs/data/models/...`
- 运行引用：`/root/autodl-tmp/lora-scripts/app/sd-models/...`
- 默认优先软链，不默认复制第二份大文件。

## Boundary
- 不接受任意外部下载网址；只使用 catalog 内已登记的官方 repo。
- 不把代理设置做成这个 skill 的输入、输出或用户选项。
- 本地如果要下载，由用户自行处理；这个 skill 只产出远端服务器命令。

## Recommended Flow
1. 先解析一个精确槽位，拿到 `repo_id`、文件名、持久路径和运行路径。
2. 若当前 AutoDL 网络慢，再用 `l3/autodl-academic-model-download-acceleration` 包住下载窗口。
3. 先汇报远端文件大小，再开始下载。
4. 取前几秒均速，给出首个 ETA 预估。
5. 按固定间隔汇报远端下载进度。
6. 需要给训练直接使用时，再把持久路径软链到运行目录。
7. 下载成功后，立刻把结果记录到本地 `training/models.md`。

## Status Rule
- `planned`：已选定槽位，尚未实际下载。
- `downloaded`：文件已落到持久目录。
- `linked`：运行目录已建立软链或等效引用。
- `failed`：下载或落盘失败。
- `manual-upload`：不是下载得到，而是用户自己上传后登记。

## Remote Execution Note
- 远端执行器默认优先调用系统级 `python`，仅在没有 `python` 时回退到 `python3`。
- 有 key 登录时，优先直接 `ssh` 在远端执行。
- 只有密码登录时，复用 `l3/ssh-server-connect/scripts/ssh_password_exec.sh`。
- 只在远端下载窗口内启用镜像或额外加速，不要长期残留环境改写。
- 如果上游文件名和默认槽位不一致，用 `--filename-override` 覆盖即可。

## Slow Download Fallback
- 如果远端下载底模明显偏慢，可以先在本地把源文件下载好，再传到服务器的“文件存储”。
- 如果用户需要在 Windows 本地实际执行这个预下载分支，切到 `l3/windows-local-model-download`。
- 如果用户需要，给下载引导和传输/上传引导即可，不在这个 skill 内代做本地下载。
- 如果用户本地没有 VPN，且源文件难以获得，就提示他们联系脚本作者或相关社区寻求可用源文件。
- 文件上传到 AutoDL “文件存储”后，就可以直接取用。
