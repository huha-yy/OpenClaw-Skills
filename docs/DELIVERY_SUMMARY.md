# OpenClaw 内容运营流水线 —— 交付总结

## 仓库信息

| 项 | 值 |
|------|-----|
| 仓库地址 | `https://github.com/huha-yy/OpenClaw-Skills.git` |
| 交付分支 | `delivery` |
| 目标环境 | Linux 服务器，RTX 4060 8GB，OpenClaw npm 全局安装 |

---

## 运维部署清单（6 步）

| 步骤 | 操作 | 目的 |
|------|------|------|
| **① 克隆** | `git clone -b delivery https://github.com/huha-yy/OpenClaw-Skills.git /opt/openclaw/D-OpenClaw` | 代码拉到服务器 |
| **② 进入目录** | `cd /opt/openclaw/D-OpenClaw` | OpenClaw 自动扫描 `skills/` 发现 13 个 skill |
| **③ 填凭据** | `cp .env.example .env && vim .env` | 飞书/DeepSeek/Pexels Key（唯一手动步骤） |
| **④ 安装环境** | `openclaw agent --session-key "setup" --timeout 1200 --message "执行 setup-environment skill"` | OpenClaw 自动装 ComfyUI + SDXL + systemd |
| **⑤ 配置 Provider** | 按 `docs/openclaw_config_guide.md` 编辑 `openclaw.json` | DeepSeek provider + 飞书 channel + Agent 默认参数 |
| **⑥ 创建定时任务** | `openclaw cron create --name "daily-content-pipeline" --schedule "0 23 * * *" --timezone "Asia/Shanghai" --timeout 1800 --message "$(cat scripts/pipeline-prompt.txt)"` | 每日 23:00 自动跑 11 步流水线 |

### 执行依赖

```
①② → ③ → ④ → ⑤ → ⑥
         ↑
    先有凭据才能装环境（setup.sh 会检查）
    ④ 和 ⑤⑥ 互不依赖，可并行
```

---

## 交付物清单

| 类型 | 文件 | 说明 |
|------|------|------|
| 部署指南 | `docs/DEPLOYMENT.md` | 快速部署 + 手动参考 + 问题排查（7 个 FAQ） |
| 配置指南 | `docs/openclaw_config_guide.md` | openclaw.json 配置块 + 完整 JSON 骨架 + Cron 管理命令 |
| 凭据模板 | `.env.example` | 6 个环境变量模板，运维照着填 |
| 自检脚本 | `scripts/setup.sh` | 一键检查 16 项（Python/OpenClaw/凭据/API 连通性） |
| 安装技能 | `skills/setup-environment/` | SKILL.md + install_comfyui.sh，OpenClaw 自动装 ComfyUI + SDXL |
| 流水线指令 | `scripts/pipeline-prompt.txt` | 11 步无人值守指令，Cron 和手动测试统一引用 |
| 项目概览 | `README.md` | 架构图 + 快速开始 + 文档索引 |

---

## 技术决策

| 决策 | 选择 | 原因 |
|------|------|------|
| 图片模型 | SDXL（`sd_xl_base_1.0`） | RTX 4060 8GB 能跑，1024×1024 画质质的提升 |
| 图片策略 | Pexels 优先 → ComfyUI (SDXL) 兜底 | Pexels 免费 + SDXL 保底，两者互补 |
| COMFYUI_URL 未设置 | 自动跳过 AI 生图 | 适配无 GPU 环境 |
| Skills 安装 | 无需安装，自动发现 | OpenClaw 扫描 `skills/*/SKILL.md` |
| Python 依赖 | 零依赖，仅标准库 | 无需 pip install |
| 凭据管理 | `.env` 不进 git | `.env.example` 模板 + 运维手动填 |

---

## 流水线架构（11 步）

```
① hotspot-monitor    → 扫描热点
② relevance-judge    → 打分排序（<70 分退出）
③ fact-research      → 多信源交叉核验
④ content-strategy   → 双平台内容策略
⑤ wechat-content     → 公众号文章
⑥ xhs-content        → 小红书笔记
⑦ image-generator    → Pexels + SDXL 配图
⑧ article-composer   → 图文编排
⑨ compliance-check   → 四维风险审核
⑩ feishu-publisher   → 飞书推送（公众号 + 小红书各自独立文档）
```

---

## 环境变量

| 变量 | 必填 | 获取方式 |
|------|------|----------|
| `FEISHU_APP_ID` | 是 | 飞书开放平台 → 应用凭证 |
| `FEISHU_APP_SECRET` | 是 | 同上 |
| `FEISHU_WEBHOOK_URL` | 是 | 飞书群 → 群机器人 → Webhook |
| `DEEPSEEK_API_KEY` | 是 | DeepSeek 开放平台 |
| `PEXELS_API_KEY` | 是 | Pexels API 免费注册 |
| `COMFYUI_URL` | 否 | 不填则跳过 AI 生图，仅 Pexels |

---

## 交付改动量（相对 master）

- **+9 个文件**，约 1350 行（部署文档 + 脚本 + 技能 + 流水线指令）
- **-176 个文件**，约 15245 行（移除 `.clawhub` 和 `clawhub-skills-teach` 无关内容）
- **修改 3 个文件**（`.gitignore` + Python 脚本 Linux 兼容修复）

---

## 凭据交接

`.env.example` 已进 git（模板，无真实值）。真实凭据由管理员通过企业微信/内部渠道单独发给运维，运维执行：

```bash
cp .env.example .env && vim .env
```
