# ComfyUI + Stable Diffusion 完整安装教程

> 适用环境：Windows 10/11 工作站 或 Windows Server，NVIDIA 显卡

---

## 1. 前置要求

### 1.1 硬件最低要求

| 配置 | SD 1.5 最低 | SDXL 最低 | 推荐 |
|---|---|---|---|
| 显卡 | NVIDIA 4GB VRAM | NVIDIA 8GB VRAM | NVIDIA 6GB+ |
| 内存 | 8GB | 16GB | 16GB+ |
| 磁盘 | 20GB 可用 | 30GB 可用 | 50GB+ |

> AMD 显卡和 Intel 显卡理论上可行但配置复杂，本教程仅针对 NVIDIA。

### 1.2 软件依赖

安装前需准备好以下工具：

| 工具 | 用途 | 下载地址 |
|---|---|---|
| **Git** | 克隆 ComfyUI 仓库 | https://git-scm.com/download/win |
| **Python 3.10-3.13** | 运行环境 | https://www.python.org/downloads/ |
| **NVIDIA 驱动** | CUDA 支持 | https://www.nvidia.com/download/index.aspx |

> Python 安装时务必勾选 **"Add Python to PATH"**。

### 1.3 验证安装

打开终端（PowerShell 或 CMD），确认以下命令都有输出：

```bash
git --version
python --version
nvidia-smi
```

`nvidia-smi` 应显示你的显卡型号和 CUDA 版本（需 ≥ 11.8）。

---

## 2. 安装 ComfyUI

### 2.1 克隆仓库

```bash
# 安装到 D 盘（可自行修改路径）
git clone https://github.com/comfyanonymous/ComfyUI.git D:/ComfyUI
```

### 2.2 创建 Python 虚拟环境

```bash
# 进入目录
cd D:/ComfyUI

# 创建虚拟环境
python -m venv venv
```

> 虚拟环境隔离了 ComfyUI 的依赖包，不会影响系统的其他 Python 项目。

### 2.3 安装 PyTorch（CUDA 版）

```bash
# 激活虚拟环境后安装
D:/ComfyUI/venv/Scripts/python.exe -m pip install --upgrade pip
D:/ComfyUI/venv/Scripts/python.exe -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

> 这一步下载约 2.5GB，可能需要几分钟。`cu124` 表示 CUDA 12.4，兼容大多数近期 NVIDIA 显卡。

### 2.4 安装 ComfyUI 依赖

```bash
D:/ComfyUI/venv/Scripts/python.exe -m pip install -r D:/ComfyUI/requirements.txt
```

### 2.5 验证 CUDA 可用

```bash
D:/ComfyUI/venv/Scripts/python.exe -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0))"
```

应输出：

```
CUDA: True
GPU: NVIDIA GeForce RTX xxxx
```

---

## 3. 下载 Stable Diffusion 模型

### 3.1 SD 1.5 基础模型（必装）

```bash
D:/ComfyUI/venv/Scripts/python.exe -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='runwayml/stable-diffusion-v1-5', filename='v1-5-pruned-emaonly.safetensors', local_dir='D:/ComfyUI/models/checkpoints')"
```

> 下载约 4GB，耗时取决于网速。存放路径：`D:\ComfyUI\models\checkpoints\v1-5-pruned-emaonly.safetensors`

### 3.2 其他推荐模型（可选）

下载后放到 `D:\ComfyUI\models\checkpoints\` 目录即可，ComfyUI 启动时自动识别。

| 模型 | 画风 | 大小 | HuggingFace repo |
|---|---|---|---|
| **DreamShaper** | 电影感、色彩浓郁 | ~2GB | `Lykon/DreamShaper` |
| **RealisticVision** | 照片级写实 | ~2GB | `SG161222/Realistic_Vision_V5.1_noVAE` |
| **SDXL 1.0** | 高画质、构图好 | ~7GB | `stabilityai/stable-diffusion-xl-base-1.0` |

> SDXL 需要 8GB 显存较舒适，6GB 需加 `--lowvram` 启动。

---

## 4. 启动 ComfyUI

### 4.1 本地工作站启动

```bash
D:/ComfyUI/venv/Scripts/python.exe D:/ComfyUI/main.py --port 8188 --listen 127.0.0.1
```

启动成功后终端显示：

```
Total VRAM 6144 MB, total RAM 16236 MB
Device: cuda:0 NVIDIA GeForce RTX 3060 ...
ComfyUI version: 0.24.0
To see the GUI go to: http://127.0.0.1:8188
```

浏览器打开 **http://127.0.0.1:8188** 即可使用。

### 4.2 服务器启动（允许局域网访问）

```bash
D:/ComfyUI/venv/Scripts/python.exe D:/ComfyUI/main.py --port 8188 --listen 0.0.0.0
```

局域网内其他设备通过 `http://服务器IP:8188` 访问。

> 需要确保 Windows 防火墙开放 8188 端口。

### 4.3 低显存启动

```bash
# 低显存模式
D:/ComfyUI/venv/Scripts/python.exe D:/ComfyUI/main.py --lowvram

# 极低显存模式（更慢但更省显存）
D:/ComfyUI/venv/Scripts/python.exe D:/ComfyUI/main.py --novram
```

| 模式 | 显存占用 | 速度 |
|---|---|---|
| 默认 (`NORMAL_VRAM`) | 模型一次加载到显存 | 最快 |
| `--lowvram` | 按需加载部分模型权重 | 中等 |
| `--novram` | 几乎不占显存（用内存） | 很慢 |

---

## 5. 安装后目录结构

```
D:\ComfyUI\
├── main.py                  ← 启动入口
├── requirements.txt         ← 依赖清单
├── venv\                    ← Python 虚拟环境（~2.5GB）
├── models\
│   ├── checkpoints\         ← 主模型 (.safetensors)
│   │   └── v1-5-pruned-emaonly.safetensors  (4GB)
│   ├── vae\                 ← VAE 模型
│   ├── loras\               ← LoRA 微调模型
│   └── controlnet\          ← ControlNet 模型
├── output\                  ← 生成的图片（默认输出位置）
├── input\                   ← 输入的图片（图生图素材）
└── custom_nodes\            ← 安装的插件
```

---

## 6. 空间预算

| 内容 | 大小 |
|---|---|
| ComfyUI 代码 | ~200 MB |
| Python 虚拟环境 + 依赖 | ~2.5 GB |
| SD 1.5 基础模型 | ~4 GB |
| pip 下载缓存 | ~3 GB（建议清理） |
| **首次安装合计** | **~7 GB（不含缓存）** |
| SDXL 模型（可选） | +7 GB |
| 每个 LoRA（可选） | +10-200 MB |

### 清理 pip 缓存（释放磁盘空间）

```bash
D:/ComfyUI/venv/Scripts/python.exe -m pip cache purge
```

### 将 pip 缓存改到其他盘（避免占用系统盘）

```bash
D:/ComfyUI/venv/Scripts/python.exe -m pip config set global.cache-dir D:/pip-cache
```

---

## 7. 常见问题

### Q1: 启动时报 `Environment variable "XIAOMI_MIMO_API_KEY" is missing`

这是 OpenClaw Gateway 的问题，与 ComfyUI 无关。ComfyUI 不需要 API Key。

### Q2: 显存不足报 CUDA Out of Memory

降低分辨率或使用低显存模式：

```bash
# 方案一：降低图片尺寸（Empty Latent Image 节点里调小 width/height）
# 方案二：加启动参数
D:/ComfyUI/venv/Scripts/python.exe D:/ComfyUI/main.py --lowvram
```

### Q3: 生成时卡住不动

检查 `steps` 参数是否过高。SD 1.5 推荐 20-30 步，超过 50 步收益递减且耗时剧增。

### Q4: 中文提示词生成效果很差

SD 1.5 的文本编码器只理解英文，中文提示词会被当作乱码。必须使用英文 prompt。

### Q5: 关闭终端后 ComfyUI 也停了

这是正常的——ComfyUI 是前台进程。要后台运行，可以将命令封装为 `.bat` 文件双击启动。

---

## 8. 完整安装步骤速查

```bash
# 1. 克隆
git clone https://github.com/comfyanonymous/ComfyUI.git D:/ComfyUI

# 2. 虚拟环境
D:/ComfyUI/venv/Scripts/python.exe -m venv D:/ComfyUI/venv
D:/ComfyUI/venv/Scripts/python.exe -m pip install --upgrade pip

# 3. PyTorch
D:/ComfyUI/venv/Scripts/python.exe -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# 4. 依赖
D:/ComfyUI/venv/Scripts/python.exe -m pip install -r D:/ComfyUI/requirements.txt

# 5. 下载 SD 1.5 模型
D:/ComfyUI/venv/Scripts/python.exe -c "from huggingface_hub import hf_hub_download; hf_hub_download(repo_id='runwayml/stable-diffusion-v1-5', filename='v1-5-pruned-emaonly.safetensors', local_dir='D:/ComfyUI/models/checkpoints')"

# 6. 清理缓存
D:/ComfyUI/venv/Scripts/python.exe -m pip cache purge

# 7. 启动
D:/ComfyUI/venv/Scripts/python.exe D:/ComfyUI/main.py --port 8188 --listen 127.0.0.1
```

---

## 9. 与 OpenClaw 内容运营流水线的关系

```
content-strategy 技能生成内容策略
        ↓
图文协同方案（图片用途、画面描述、尺寸）
        ↓
检索类：Pexels 图库 API 搜索
        ↓
找不到合适图 → 调用 ComfyUI API 生图
        ↓
图片写入 outputs/ 发布包
```

ComfyUI 在这个流程里扮演 **P2 兜底生图** 的角色——图库找不到合适素材时，由它按需生成封面、图卡、概念配图。

> 参考：`运营Agent开发计划/08_图片策略文档.md`
