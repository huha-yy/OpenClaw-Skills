# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Project Overview

**AI内容运营自动化流水线** — 从热点发现到飞书发布的 11 步 Agent pipeline，运行在 OpenClaw 平台上。

- 12 个 workspace skill（LLM 策划层）+ Python 脚本（执行层）
- 目标平台：公众号、小红书（抖音暂未启用）
- 小模型适配：MiMo v2-pro，所有 prompt 针对小模型优化
- 文件交接制：skill 之间通过 `outputs/<topic>/` 目录下的 JSON/Markdown 文件传递状态

## Runtime

- **框架:** OpenClaw 2026.6.1（Node.js agent orchestration）
- **默认模型:** DeepSeek v4 Pro (`deepseek/deepseek-v4-pro`) via OpenClaw gateway
- **Fallback:** Xiaomi MiMo v2.5 Pro → v2 Pro
- **Gateway:** `ws://127.0.0.1:19000`
- **平台:** Windows 11 (China)，使用 Unix 风格路径
- **OpenClaw CLI:** `openclaw agent --session-key <key> --message "<prompt>"`

## 凭据管理

**两层架构：**

| 层级 | 方式 | 用途 |
|------|------|------|
| Python 脚本 | `load_dotenv()` → 读 `D:\D-OpenClaw\.env` | Pexels、飞书 webhook、飞书 App ID/Secret |
| OpenClaw 自身 | 系统环境变量（Windows `setx`） | DeepSeek API Key（`DEEPSEEK_API_KEY`） |

**关键约定：**
- `.env` 在 `.gitignore` 中，**绝不提交**
- `.env.example` 是模板文件，提交到 git（只有占位符 `xxx`）
- 所有 `os.environ.get()` 的脚本都必须有 `load_dotenv()` 调用
- 路径推导：从脚本位置向上 4 层到 workspace 根拼接 `.env`
- 依赖：`pip install python-dotenv`

**所有使用 env 的脚本：**
| 脚本 | 读取的 env |
|------|-----------|
| `skills/image-generator/scripts/run_image_pipeline.py` | PEXELS_API_KEY |
| `skills/image-generator/scripts/pexels_search.py` | PEXELS_API_KEY |
| `skills/image-generator/scripts/comfyui_client.py` | COMFYUI_URL |
| `skills/feishu-publisher/scripts/feishu_auth.py` | FEISHU_APP_ID, FEISHU_APP_SECRET |
| `skills/feishu-publisher/scripts/push_to_feishu.py` | FEISHU_APP_ID, FEISHU_APP_SECRET, FEISHU_WEBHOOK_URL, FEISHU_NOTIFY_OPEN_ID |
| `skills/feishu-publisher/scripts/test_notify.py` | FEISHU_WEBHOOK_URL |

## Repository Structure

```
D:\D-OpenClaw\
  skills/                 # 12 个 workspace skill（LLM prompt + Python 脚本）
    hotspot-monitor/      # ① 热点监控
      scripts/
        cluster_hotspots.py   # 标题Jaccard+URL同源+关键词重叠 三层去重
    relevance-judge/      # ② 相关性打分
    fact-research/        # ③ 事实核验（多信源交叉验证）
    content-strategy/     # ④ 内容策略
    wechat-content/       # ⑤ 公众号文章生成
    xhs-content/          # ⑥ 小红书笔记生成
    douyin-content/       # ⑦ 抖音内容（暂未启用）
    image-generator/      # ⑧ 图片生成（Pexels → ComfyUI 两层策略）
      scripts/
        pexels_search.py      # Pexels 搜索 + 评分（中英双语关键词，阈值50）
        run_image_pipeline.py # 图片生产编排（强制人物屏蔽词兜底）
        comfyui_client.py     # ComfyUI 文生图客户端
    article-composer/     # ⑨ 图文编排（insert_images.py 确定性插入）
      scripts/
        insert_images.py      # 图片标记插入/替换/清理
    compliance-check/     # ⑩ 合规审核（四维：事实/品牌/平台/AI痕迹）
    feishu-publisher/     # ⑪ 飞书推送（--platform wechat/xhs 分推）
      scripts/
        push_to_feishu.py     # 主推送脚本
        feishu_auth.py        # Token 管理（自动缓存/刷新）
        md_to_feishu_blocks.py # Markdown → 飞书 Block 转换
        test_notify.py        # Webhook 通知测试
    publish-package/      # ⑫ 发布包汇总（备用）
      scripts/
        write_package.py      # 标准化写入发布包目录
    setup-environment/    # 🛠 ComfyUI + SDXL 一键安装
      scripts/
        install_comfyui.sh
  samples/                # 测试样本数据
    mock_hotspots.json        # 6 条测试热点（含故意不相关的对照组）
  configs/                # 品牌指南 + 平台风格指南 + 关键词配置
    brand_guidelines.md
    company_keywords.yaml
    hotspot_sources.yaml
    platform_style_guides/
      wechat.md
      xiaohongshu.md
      douyin.md
  outputs/                # 流水线产物（gitignore）
    <topic>/
      images/
        image_plan.json       # LLM 生成的图片方案
        pipeline_result.json  # 图片生产结果
      publish_package/
        wechat/article.md     # 公众号成品（含内联图）
        xiaohongshu/note.md   # 小红书成品（含内联图）
  .env.example            # 环境变量模板（提交到 git）
  .env                    # 实际凭据（gitignore，不提交）
  docs/                   # 系统设计文档
  运营Agent开发计划/       # 分阶段实施路线图
  .openclaw/              # OpenClaw 运行时状态
  logs/                   # Gateway 日志
```

## 完整流水线（11步）

```
① hotspot-monitor ──→ ② relevance-judge ──→ ③ fact-research ──→ ④ content-strategy
                                          ↓
⑤ wechat-content ── ⑥ xhs-content ── (⑦ douyin-content 暂跳)
                                          ↓
⑧ image-generator ──→ ⑨ article-composer ──→ ⑩ compliance-check ──→ ⑪ feishu-publisher
```

### 启动命令

```bash
openclaw agent --session-key "pipeline-<topic>" --timeout 1800 --message "执行完整11步..."
```

### 图片策略（两层）

```
image_plan.json (LLM出方案)
  → run_image_pipeline.py
    → 策略一：Pexels 搜索 → 中英双语评分 ≥50 → 下载
    → 策略二：ComfyUI 生图兜底（需 COMFYUI_URL 环境变量）
      → 强制合入 15 个人物屏蔽词（代码层兜底，不受LLM质量影响）
      → 每张图优先用自己的 platform 评分（img.get("platform", plan_platform)）
```

### 推送策略

```
push_to_feishu.py --platform wechat → 飞书文档（公众号+内联图）
push_to_feishu.py --platform xhs    → 飞书文档（小红书+内联图）
```

## 关键设计原则

- **LLM 管方案，脚本管执行** — 确定性操作（生图、编排、推送）走 Python 脚本，不由 LLM 直接改文件
- **代码层兜底** — 小模型不可靠的地方，代码强制执行（如人物屏蔽词、Pexels 阈值、路径后缀清理）
- **凭据分层管理** — Python 脚本读 `.env`，OpenClaw 自身读系统环境变量，绝不硬编码
- **幂等** — `insert_images.py` 先清后插，可重复执行
- **文件交接** — skill 间不直接通信，通过 `outputs/` 下的标准化文件传递
- **分平台推送** — 公众号和小红书各自独立飞书文档，不混在一起

## 重要约定

- **不要修改 `clawhub-skills-teach/`** — 这是参考库，不是项目代码
- **不要手动替 OpenClaw 完成任务** — 目的是让 OpenClaw 自给自足跑通全链路
- **改 SKILL.md 前确保远程备份** — `git log` 确认已 push
- **小模型约束**：prompt 要具体、给正面示例、避免抽象规则
- **路径规范**：SKILL.md 引用脚本统一用 `skills/<name>/scripts/<file>.py`（workspace 根目录基准）
- **`.env` 绝不提交** — 凭据变更只改 `.env.example`（占位符），真实 key 通过安全渠道传递

## 最近修复 (2026-06-15)

| 问题 | 根因 | 修复 |
|------|------|------|
| cron 环境脚本读不到 env | 子进程不继承 shell 环境变量，脚本无 load_dotenv | 6 个脚本增加 load_dotenv()，从 workspace/.env 加载 |
| 小红书图片全部缺失 | run_image_pipeline 全局 platform="wechat" 覆盖了每张图的平台 | 改为 `img.get("platform", platform)` 优先用图片自身平台 |
| 飞书 open_id 硬编码 | push_to_feishu.py 写死了个人 open_id | 改为 `FEISHU_NOTIFY_OPEN_ID` 环境变量 |
| 缺少 cluster_hotspots.py | 写 SKILL.md 时规划了但从未实现 | 新建脚本，标题 Jaccard + URL + 关键词三层去重 |
| 缺少 write_package.py | 同上 | 新建脚本，标准化写入 outputs 发布包目录 |
| `.gitignore` 误屏蔽 `scripts/` | 最初标记为临时脚本，后来变成永久目录但未更新 | 从 .gitignore 中移除 scripts/ |
| image-generator 歧义路径 | `../images/pipeline_result.json` 从 workspace 根解析到仓库外 | 改为 `outputs/<topic>/images/pipeline_result.json` |
| 路径引用风格不一致 | hotspot-monitor/publish-package 用了简写路径 | 统一为 `skills/<name>/scripts/<file>.py` |
