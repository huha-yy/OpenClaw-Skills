# OpenClaw 内容运营自动化流水线

从热点发现到飞书发布的 11 步 AI Agent 内容运营流水线，运行在 OpenClaw 平台上。

**目标平台**：公众号、小红书（抖音暂未启用）

## 快速开始

```bash
# 1. 配置环境变量
cp .env.example .env && vim .env

# 2. 环境自检
bash scripts/setup.sh

# 3. 启动完整流水线
openclaw agent --session-key "pipeline-<主题名>" --timeout 1800 \
  --message "执行完整11步内容运营流水线..."
```

## 流水线架构

```
① 热点监控 → ② 相关性打分 → ③ 事实核验 → ④ 内容策略
       ↓
⑤ 公众号文章 → ⑥ 小红书笔记 → (⑦ 抖音 暂未启用)
       ↓
⑧ 图片生成 → ⑨ 图文编排 → ⑩ 合规审核 → ⑪ 飞书推送
```

## 目录结构

```
skills/          # 12 个 workspace skill（LLM prompt + Python 脚本）
outputs/         # 流水线产物（gitignore）
configs/         # 品牌指南 + 平台风格指南
scripts/         # 运维工具脚本
docs/            # 系统设计与部署文档
```

## 依赖

- **Python 3.8+**（所有脚本仅用标准库，无需 pip install）
- **OpenClaw** 平台（2026.6.1+）
- **DeepSeek API**（默认模型）
- **飞书开放平台**（用于内容推送）

## 文档索引

| 文档 | 说明 |
|------|------|
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | 部署指南（运维人员必读） |
| [openclaw_config_guide.md](docs/openclaw_config_guide.md) | OpenClaw 配置文件指南 |
| [DELIVERY_SUMMARY.md](docs/DELIVERY_SUMMARY.md) | 交付总结（运维清单 + 技术决策 + 架构总览） |
| CLAUDE.md | 开发者参考（项目架构、设计原则、最近修复） |
