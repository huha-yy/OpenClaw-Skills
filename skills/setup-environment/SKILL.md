---
name: setup-environment
description: "环境初始化：自检 + 安装 ComfyUI + 下载 SD 模型 + 验证。首次部署时执行，后续无需再跑。"
metadata: { "openclaw": { "emoji": "🔧" } }
user-invocable: true
platforms: [all]
---

# 环境初始化

你负责在新服务器上完成环境部署。所有操作通过 Bash 执行 shell 脚本完成。

## 前置条件

- 服务器已克隆本项目仓库
- 用户已 `cp .env.example .env` 并填写真实凭据
- 服务器有 NVIDIA GPU（如无 GPU，跳过 ComfyUI 安装）

## 执行步骤

### 步骤 1：运行环境自检

```bash
bash scripts/setup.sh
```

查看输出，确认 Python/OpenClaw/凭据 三项通过。ComfyUI 相关项失败可忽略（因为还没装）。

### 步骤 2：检测 GPU

```bash
nvidia-smi
```

- **有 GPU 输出** → 继续步骤 3 安装 ComfyUI
- **无 GPU / 命令不存在** → 跳过步骤 3，告知用户：`环境初始化完成（纯 Pexels 模式，无 AI 生图）。如需 AI 生图请安装 NVIDIA GPU 后重新运行。`

### 步骤 3：一键安装 ComfyUI + SD 1.5

```bash
bash skills/setup-environment/scripts/install_comfyui.sh
```

此脚本会自动完成：
1. GPU 检测 + 显存检查（<4GB 拒绝安装）
2. PyTorch CUDA 安装（如未安装）
3. ComfyUI 克隆 + 依赖安装
4. SD 1.5 模型下载（~4GB）
5. systemd 自启动服务创建
6. ComfyUI 启动 + 测试生图

预计耗时：首次 5-15 分钟（主要花在模型下载）。

### 步骤 4：确认 .env 配置

```bash
grep COMFYUI_URL .env
```

应该输出：`COMFYUI_URL=http://127.0.0.1:8188`

如果没有，提醒用户取消 `.env` 中该行的注释。

### 步骤 5：最终验证

```bash
bash scripts/setup.sh
```

这次应该全部通过（包括 ComfyUI 连通性检查）。

## 完成后汇报

向用户汇报以下信息：

```
🎉 环境初始化完成！

✓ 环境自检通过
✓ ComfyUI 已安装并运行
✓ SD 1.5 模型已就绪
✓ 测试生图成功

流水线图片策略：Pexels 优先 → ComfyUI 兜底

下一步：启动完整流水线测试
  openclaw agent --session-key "pipeline-test" --timeout 1800 \
    --message "执行完整11步内容运营流水线"
```

## 注意

- 本 skill 仅在首次部署时执行一次
- 如果 ComfyUI 已安装，脚本会检测并跳过重复步骤
- 模型首次加载需 10-30 秒，生图可能慢，属正常现象
