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
- **模型:** Xiaomi MiMo (mimo-v2-pro) via OpenClaw gateway
- **Gateway:** `ws://127.0.0.1:19000`
- **平台:** Windows 11 (China)，使用 Unix 风格路径
- **OpenClaw CLI:** `openclaw agent --session-key <key> --message "<prompt>"`

## Repository Structure

```
D:\D-OpenClaw\
  skills/                 # 12 个 workspace skill（LLM prompt + Python 脚本）
    hotspot-monitor/      # ① 热点监控
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
    article-composer/     # ⑨ 图文编排（insert_images.py 脚本确定性插入）
    compliance-check/     # ⑩ 合规审核（四维：事实/品牌/平台/AI痕迹）
    feishu-publisher/     # ⑪ 飞书推送（--platform wechat/xhs 分推）
    publish-package/      # ⑫ 发布包汇总（未启用，feishu-publisher 已覆盖）
  outputs/                # 流水线产物（gitignore）
    <topic>/
      images/
        image_plan.json       # LLM 生成的图片方案
        pipeline_result.json  # 图片生产结果
      publish_package/
        wechat/article.md     # 公众号成品（含内联图）
        xiaohongshu/note.md   # 小红书成品（含内联图）
  configs/                # 品牌指南 + 平台风格指南
  clawhub-skills-teach/   # 📖 ClawHub 参考 skill 库（只读，不要修改）
    README.md             # 说明：仅用于借鉴设计模式/prompt写法
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
    → 策略二：ComfyUI 生图兜底
      → 强制合入 15 个人物屏蔽词（代码层兜底，不受LLM质量影响）
```

### 推送策略

```
push_to_feishu.py --platform wechat → 飞书文档（公众号+内联图）
push_to_feishu.py --platform xhs    → 飞书文档（小红书+内联图）
```

## 关键设计原则

- **LLM 管方案，脚本管执行** — 确定性操作（生图、编排、推送）走 Python 脚本，不由 LLM 直接改文件
- **代码层兜底** — 小模型不可靠的地方，代码强制执行（如人物屏蔽词、Pexels 阈值）
- **幂等** — `insert_images.py` 先清后插，可重复执行
- **文件交接** — skill 间不直接通信，通过 `outputs/` 下的标准化文件传递
- **分平台推送** — 公众号和小红书各自独立飞书文档，不混在一起

## 重要约定

- **不要修改 `clawhub-skills-teach/`** — 这是参考库，不是项目代码
- **不要手动替 OpenClaw 完成任务** — 目的是让 OpenClaw 自给自足跑通全链路
- **改 SKILL.md 前确保远程备份** — `git log` 确认已 push
- **小模型约束**：prompt 要具体、给正面示例、避免抽象规则

## 最近修复 (2026-06-11)

| 问题 | 根因 | 修复 |
|------|------|------|
| Pexels 永远 0 命中 | 英文关键词 vs 中文 alt → 评分天花板53<阈值60 | 中英双语关键词 + 阈值60→50 |
| 生图出现人物 | LLM漏写负面词 + 代码直接透传 | run_image_pipeline.py 强制合入人物屏蔽词 |
| 图片路径解析失败 | pipeline_result.json 带 `(N bytes)` 后缀 | push_to_feishu.py 增加后缀清理 |
| 图文编排不可靠 | LLM直接编辑 markdown → 经常漏写图片标记 | 改为 insert_images.py 脚本确定性插入 |
