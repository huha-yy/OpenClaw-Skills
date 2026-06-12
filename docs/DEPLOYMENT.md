# OpenClaw 内容运营流水线 —— 部署指南

本文档面向运维人员，指导在 Linux 服务器上完成 OpenClaw 内容运营流水线的部署。

---

## 快速部署（推荐）

运维人员只需三步，OpenClaw 自动完成环境安装。

```bash
# 1. 克隆仓库（skills 在 skills/ 目录下，无需手动安装）
git clone -b delivery https://github.com/huha-yy/OpenClaw-Skills.git /opt/openclaw/D-OpenClaw
cd /opt/openclaw/D-OpenClaw

# 2. 填写凭据（唯一手动步骤）
cp .env.example .env && vim .env

# 3. 让 OpenClaw 接管一切（在项目目录内执行，OpenClaw 自动发现 skills/）
openclaw agent --session-key "setup" --timeout 1200 \
  --message "执行 setup-environment skill，安装所有环境依赖（ComfyUI + SD模型 + 验证）"
```

OpenClaw 会自动：检测 GPU → 安装 PyTorch CUDA → 克隆 ComfyUI → 下载 SDXL 模型 → 创建 systemd 服务 → 启动并测试生图。

> **Skills 无需安装**：OpenClaw 启动时自动扫描当前目录下的 `skills/*/SKILL.md`，`git clone` 完成即全部可用。`cd` 到项目目录再执行 `openclaw agent` 即可。

> 如果服务器没有 GPU，OpenClaw 会自动跳过 ComfyUI 安装，以纯 Pexels 模式运行。

---

## 详细步骤（手动部署参考）

以下为手动部署的详细说明，遇到问题时可参考各章节。

## 1. 环境要求

| 组件 | 要求 | 说明 |
|------|------|------|
| Python | 3.8+ | 所有脚本仅用标准库，无需 pip install |
| OpenClaw | 2026.6.1+ | Node.js agent 编排平台 |
| Node.js | 18+ | OpenClaw 的运行环境 |
| GPU | 可选 | 仅 ComfyUI AI 生图需要（Pexels 图库不需要） |
| 网络 | 出网 | 需访问 DeepSeek API、Pexels API、飞书 API |

**Python 零依赖**：本项目的所有 Python 脚本仅使用标准库（`json`, `os`, `sys`, `urllib`, `argparse`, `subprocess` 等），不需要 `pip install`。

---

## 2. 克隆仓库

```bash
# 克隆到目标目录（指定 delivery 分支）
git clone -b delivery https://github.com/huha-yy/OpenClaw-Skills.git /opt/openclaw/D-OpenClaw
cd /opt/openclaw/D-OpenClaw
```

### 2.1 设置 OpenClaw 工作区

确保 OpenClaw 的工作区路径指向此目录。OpenClaw 会自动扫描 `skills/` 目录下的 `SKILL.md` 文件，无需手动注册技能。

---

## 3. 环境变量配置

### 3.1 复制模板

```bash
cp .env.example .env
chmod 600 .env   # 限制权限，保护凭据
```

### 3.2 填写凭据

编辑 `.env`，填入真实值：

```bash
vim .env
```

| 变量 | 必填 | 获取方式 |
|------|------|----------|
| `FEISHU_APP_ID` | 是 | [飞书开放平台](https://open.feishu.cn/app) → 应用凭证 |
| `FEISHU_APP_SECRET` | 是 | 同上 |
| `FEISHU_WEBHOOK_URL` | 是 | 飞书群 → 群设置 → 群机器人 → 添加 → Webhook |
| `DEEPSEEK_API_KEY` | 是 | [DeepSeek 开放平台](https://platform.deepseek.com/api_keys) |
| `PEXELS_API_KEY` | 是 | [Pexels API](https://www.pexels.com/api/) 免费注册 |
| `COMFYUI_URL` | 否 | ComfyUI 服务地址（不填则跳过 AI 生图） |

### 3.3 加载环境变量

```bash
# 方式一：手动 export（推荐，用于 systemd/cron）
set -a; source .env; set +a

# 方式二：每次运行前 source
source .env
```

**注意**：`.env` 已在 `.gitignore` 中，不会被提交到 git。

---

## 4. OpenClaw 配置

### 4.1 自检

运行环境自检脚本，确认所有依赖就绪：

```bash
bash scripts/setup.sh
```

### 4.2 配置 Provider 和 Agent

参考 [openclaw_config_guide.md](openclaw_config_guide.md) 完成以下配置：

1. 在 `openclaw.json` 中添加 **DeepSeek provider**
2. （可选）添加飞书 channel
3. 设置 Agent 默认参数（模型、超时、workspace 路径）

### 4.3 创建定时任务

流水线指令已预置在 `scripts/pipeline-prompt.txt`，创建 Cron 时直接引用：

```bash
openclaw cron create \
  --name "daily-content-pipeline" \
  --schedule "0 23 * * *" \
  --timezone "Asia/Shanghai" \
  --timeout 1800 \
  --message "$(cat scripts/pipeline-prompt.txt)"
```

配置 Webhook 通知：

```bash
openclaw cron update daily-content-pipeline \
  --webhook "${FEISHU_WEBHOOK_URL}"
```

---

## 5. ComfyUI 安装（可选，公司服务器推荐启用）

ComfyUI 用于 AI 文生图（Pexels 搜不到合适图片时兜底）。公司服务器 RTX 4060 8GB 完全够用。

### 5.1 硬件要求

| GPU | 可用模型 | 单图耗时 |
|-----|---------|---------|
| RTX 4060 8GB | SDXL | ~30-60s |
| RTX 3060 6GB | SD 1.5 | ~20-40s |
| 无 GPU / < 6GB | 不建议 | — |

**默认使用 SDXL**（`sd_xl_base_1.0`）：原生 1024×1024 分辨率，画质明显优于 SD 1.5，RTX 4060 8GB 完美运行。

### 5.2 安装 ComfyUI

```bash
# 安装
git clone https://github.com/comfyanonymous/ComfyUI.git /opt/ComfyUI
cd /opt/ComfyUI
pip install -r requirements.txt

# 下载 SDXL 模型（~7GB）
mkdir -p models/checkpoints
wget -O models/checkpoints/sd_xl_base_1.0.safetensors \
  https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors
```

### 5.3 NVIDIA 驱动 + CUDA 检查

```bash
nvidia-smi                          # 应显示 RTX 4060 和驱动版本
python3 -c "import torch; print(torch.cuda.is_available())"  # 应输出 True
```

**如果 torch 未安装 CUDA 版本：**

```bash
pip uninstall torch torchvision -y
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

### 5.4 启动

```bash
# 前台启动（测试用）
python main.py --listen 0.0.0.0 --port 8188

# 后台启动（生产用）
nohup python main.py --listen 0.0.0.0 --port 8188 > /var/log/comfyui.log 2>&1 &

# systemd 服务（推荐）
cat > /etc/systemd/system/comfyui.service << 'SERVICE'
[Unit]
Description=ComfyUI Stable Diffusion Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ComfyUI
ExecStart=/usr/bin/python3 main.py --listen 127.0.0.1 --port 8188
Restart=on-failure

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable --now comfyui
```

### 5.5 配置 COMFYUI_URL

在 `.env` 中取消注释并设置：

```bash
COMFYUI_URL=http://127.0.0.1:8188
```

### 5.6 降级为 SD 1.5（低配 GPU 备选）

如果显存 < 8GB，可降级为 SD 1.5：

```bash
# 1. 下载 SD 1.5 模型（~4GB）
cd /opt/ComfyUI/models/checkpoints
wget -O v1-5-pruned-emaonly.safetensors \
  https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned-emaonly.safetensors

# 2. 修改默认模型 + 分辨率
sed -i 's/sd_xl_base_1.0/v1-5-pruned-emaonly/' \
  /opt/openclaw/D-OpenClaw/skills/image-generator/scripts/comfyui_client.py
sed -i 's/1024, 1024/768, 512/' \
  /opt/openclaw/D-OpenClaw/skills/image-generator/scripts/run_image_pipeline.py
```

---

## 6. 验证测试

按以下顺序逐步验证，确保每个组件正常。

### 6.1 环境自检

```bash
bash scripts/setup.sh
```

预期输出：所有检查项通过（或仅 ComfyUI 相关项有警告）。

### 6.2 凭据安全检查

```bash
# 检查是否有机密泄漏
grep -r "sk-" . --include="*.py" --include="*.md" --include="*.json" 2>/dev/null
# 预期：0 结果

grep -r "FEISHU_APP_SECRET" . --include="*.py" --include="*.md" 2>/dev/null
# 预期：只出现 os.environ 引用，没有硬编码的 Secret 值
```

### 6.3 单步测试：飞书推送

```bash
# Dry-run 模式，不真正推送
python3 skills/feishu-publisher/scripts/push_to_feishu.py \
  --package-dir outputs/养老机器人逐浪新蓝海/publish_package \
  --platform wechat --dry-run
```

注意：如果 `outputs/` 下没有历史产物，先跳过此测试。

### 6.4 单步测试：Pexels 图库

```bash
python3 skills/image-generator/scripts/pexels_search.py \
  --keyword "elderly care robot" --count 3 --output /tmp/test_pexels.json
```

预期：返回最多 3 张图片的 JSON，评分均 ≥ 50。

### 6.5 单步测试：ComfyUI（如果部署了）

```bash
python3 skills/image-generator/scripts/comfyui_client.py \
  --positive "elderly care robot modern technology" \
  --negative "person, people, face, human" \
  --output /tmp/
```

预期：生成一张 1024x1024 的 PNG 图片。

### 6.6 全流程测试

```bash
openclaw agent \
  --session-key "pipeline-test-$(date +%Y%m%d)" \
  --timeout 1800 \
  --message "$(cat scripts/pipeline-prompt.txt)"
```

**预期**：30 分钟内完成，飞书群收到推送消息。

---

## 7. 常见问题排查

### 7.1 环境变量未生效

**症状**：`FEISHU_APP_ID 已设置` 检查失败，但 `.env` 已填写。

**解决**：

```bash
# 确认 .env 存在且格式正确
cat .env | head -5

# 手动加载
set -a; source .env; set +a
echo $FEISHU_APP_ID  # 应输出实际值，不是 cli_xxx

# 如果是 systemd 管理的进程，使用 EnvironmentFile
EnvironmentFile=/opt/openclaw/D-OpenClaw/.env
```

### 7.2 Pexels 返回 0 结果

**症状**：Pexels 搜索总是 0 命中。

**原因**：API Key 未设置或无效、关键词问题。

**解决**：

```bash
# 测试 API Key
curl -s -H "Authorization: $PEXELS_API_KEY" \
  "https://api.pexels.com/v1/search?query=test&per_page=1" | python3 -m json.tool

# 使用中英双语关键词（脚本已内置此逻辑）
```

### 7.3 ComfyUI 连接失败

**症状**：`ERROR: Cannot connect to ComfyUI at ...`

**原因**：ComfyUI 未启动、端口不通、防火墙拦截。

**解决**：

```bash
# 检查 ComfyUI 是否运行
curl -s http://127.0.0.1:8188/system_stats

# 检查进程
ps aux | grep comfyui

# 检查防火墙
ufw status
```

### 7.4 飞书推送失败

**症状**：`push_to_feishu.py` 报错。

**解决**：

```bash
# 验证 Token
curl -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{\"app_id\":\"$FEISHU_APP_ID\",\"app_secret\":\"$FEISHU_APP_SECRET\"}"

# 验证 Webhook
curl -X POST "$FEISHU_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"msg_type":"text","content":{"text":"部署验证: 飞书连通性测试"}}'
```

### 7.5 OpenClaw Agent 超时

**症状**：流水线超过 30 分钟未完成。

**解决**：

- 检查 DeepSeek API 是否限流
- 增加 `--timeout` 参数（如 `--timeout 3600`）
- 检查网络延迟（服务器到 `api.deepseek.com` 的延迟）

### 7.6 图片中出现人物

**症状**：生成的图片中出现人物、人脸。

**原因**：此问题已在 `run_image_pipeline.py` 中通过代码层强制合入人物屏蔽词修复。如果仍有问题，检查是否使用了最新代码。

---

## 8. 日常维护

```bash
# 查看最近执行记录
openclaw cron logs daily-content-pipeline --limit 5

# 查看产物
ls outputs/

# 清理旧产物（保留最近 7 天）
find outputs/ -maxdepth 1 -type d -mtime +7 -exec rm -rf {} \;

# 更新代码
cd /opt/openclaw/D-OpenClaw
git pull origin master
```

---

## 附录 A：文件清单

### 会修改的文件

| 文件 | 说明 |
|------|------|
| `.env` | 环境变量（不进 git，需手动创建） |
| `openclaw.json` | OpenClaw 配置（需手动添加 provider/cron） |

### 只读/不修改的文件

| 文件 | 说明 |
|------|------|
| `skills/*/SKILL.md` | 技能 prompt，与运行环境无关 |
| `skills/*/scripts/*.py` | Python 脚本，跨平台兼容 |
| `configs/` | 品牌指南，无需修改 |
| `docs/` | 项目文档 |

---

## 附录 B：网络访问列表

| 目标 | 端口 | 用途 |
|------|------|------|
| `api.deepseek.com` | 443 | LLM 推理 |
| `api.pexels.com` | 443 | 图片搜索 |
| `open.feishu.cn` | 443 | 飞书推送 + 认证 |
| `127.0.0.1:8188` | 8188 | ComfyUI（本地，仅 GPU 服务器） |
