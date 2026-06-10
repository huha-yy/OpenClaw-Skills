# ComfyUI 本地使用指南

## 1. 安装信息

### 安装位置

```
D:\ComfyUI\                        ← ComfyUI 主程序 + Python 虚拟环境
D:\ComfyUI\venv\                   ← Python 虚拟环境（torch 等所有依赖）
D:\ComfyUI\models\checkpoints\     ← SD 模型存放位置
D:\ComfyUI\models\vae\             ← VAE 模型（目前为空）
D:\ComfyUI\models\loras\           ← LoRA 模型（目前为空）
D:\ComfyUI\models\controlnet\      ← ControlNet 模型（目前为空）
D:\ComfyUI\output\                 ← 生成的图片输出位置
```

### 环境信息

| 项目         | 值                                         |
| ------------ | ------------------------------------------ |
| GPU          | NVIDIA GeForce RTX 3060 Laptop (6 GB VRAM) |
| 内存         | 16 GB                                      |
| Python       | 3.13.7                                     |
| PyTorch      | 2.6.0 + CUDA 12.4                          |
| ComfyUI 版本 | 0.24.0                                     |

---

## 2. 如何启动

### 启动命令

打开终端，执行：

```bash
D:/ComfyUI/venv/Scripts/python.exe D:/ComfyUI/main.py --port 8188 --listen 127.0.0.1
```

### 访问地址

启动后打开浏览器访问：**http://127.0.0.1:8188**

### 关闭

在终端按 `Ctrl+C` 即可关闭。

> 注意：ComfyUI 是前台进程，关机或关闭终端后进程消失。重启电脑后需要重新执行上述命令。

---

## 3. 三者关系：ComfyUI / 模型 / Stable Diffusion

```
Stable Diffusion   = 发动机（开源 AI 画图算法）
模型 (Checkpoint)   = 调校好的整车（训练好的权重文件）
ComfyUI            = 驾驶舱（图形化操作界面）
```

### 当前已安装的模型

| 模型            | 文件                              | 大小   |
| --------------- | --------------------------------- | ------ |
| SD 1.5 基础模型 | `v1-5-pruned-emaonly.safetensors` | 4.0 GB |

SD 1.5 是通用模型，什么都能画但画风朴素。可以后续下载其他模型（DreamShaper、RealisticVision 等）放到 `D:\ComfyUI\models\checkpoints\` 目录。

---

## 4. 基础使用流程

### 第一步：加载工作流

打开 http://127.0.0.1:8188，如果画布为空，点 **Load Default** 加载默认文生图工作流。

### 第二步：设置图片尺寸

找到 **Empty Latent Image** 节点（紫色）：

```
width:  768        （常用：公众号封面 900×383，小红书 1080×1440）
height: 512
batch_size: 1      （6GB 显存建议保持 1）
```

### 第三步：填写提示词（必须用英文）

**CLIP Text Encode (Positive Prompt)** — 正面提示词，写你想要的：

```
masterpiece, best quality, photorealistic, a bright and clean modern elderly care room,
soft warm sunlight through window, a sleek white smart medical device beside a comfortable bed,
professional nursing scene, gentle blue and white color palette,
sense of dignity and warmth, minimalist healthcare technology,
shallow depth of field, cinematic lighting, 8k
```

**CLIP Text Encode (Negative Prompt)** — 负面提示词，写你不想要的：

```
ugly, blurry, low quality, distorted, bad anatomy, deformed, watermark, text,
signature, messy room, dark, gloomy, scary, hospital horror, crowded, cluttered,
people, face, person, patient, sad, depressing
```

> **为什么不能用中文？** SD 1.5 的 CLIP 编码器是英文训练的，不认识中文。写中文提示词生成效果会非常差。

### 第四步：调采样参数

找到 **KSampler** 节点（黄色）：

```
seed:                  点击右侧 🔄 随机
control_after_generate: randomize
steps:                  25        （20-30 之间，越高越精细但越慢）
cfg:                    7.0       （提示词遵循度，5-10 之间）
sampler_name:           DPM++ 2M Karras
scheduler:              Karras
denoise:                1.00
```

### 第五步：生成

按 **Ctrl + Enter** 或点击底部 **Queue Prompt**。约 8-12 秒出图。

### 生成的图片在哪

`D:\ComfyUI\output\` 目录下，文件名格式为 `ComfyUI-日期_序号_.png`。

---

## 5. 常用快捷键

| 快捷键         | 功能         |
| -------------- | ------------ |
| `Ctrl + Enter` | 开始生成     |
| `Ctrl + S`     | 保存工作流   |
| `Ctrl + O`     | 加载工作流   |
| `Ctrl + Z/Y`   | 撤销/重做    |
| 鼠标滚轮       | 缩放画布     |
| 空格 + 拖拽    | 平移画布     |
| 双击空白画布   | 搜索添加节点 |

---

## 6. 常用尺寸参考

| 用途       | 建议分辨率 | 备注           |
| ---------- | ---------- | -------------- |
| 公众号封面 | 900×383    | 2.35:1 比例    |
| 小红书图文 | 1080×1440  | 3:4 竖版       |
| 抖音封面   | 1080×1920  | 9:16 竖版      |
| 通用测试   | 512×512    | 6GB 显存最舒适 |

> SD 1.5 原生分辨率约 512×512，更大尺寸建议先生成小图再用高清放大（Upscale）。

---

## 7. 硬件限制

| 模型     | 显存需求 | 6GB 能否跑               | 备注             |
| -------- | -------- | ------------------------ | ---------------- |
| SD 1.5   | 2-4 GB   | 舒适                     | 当前已安装       |
| SDXL 1.0 | 6-8 GB   | 能跑但紧，需 `--lowvram` | 画质更好，慢一些 |
| FLUX     | 12 GB+   | 跑不了                   | -                |

---

## 8. 常用相关地址

| 地址                             | 用途                       |
| -------------------------------- | -------------------------- |
| `http://127.0.0.1:8188`          | ComfyUI 主界面             |
| `http://127.0.0.1:8188/history`  | 生成历史                   |
| `http://127.0.0.1:19000`         | OpenClaw Gateway Dashboard |
| `D:\ComfyUI\output\`             | 生成的图片存放位置         |
| `D:\ComfyUI\models\checkpoints\` | 模型存放位置               |

---

## 9. 扩展方向

后续可以添加：

- **DreamShaper 模型** — 更有电影感的画风，适合封面图
- **LoRA 模型** — 微调特定风格/人物/场景，文件小（几十 MB）
- **ControlNet** — 精确控制构图、姿势、深度
- **Upscale 工作流** — 将小图高清放大到适合发布的尺寸
