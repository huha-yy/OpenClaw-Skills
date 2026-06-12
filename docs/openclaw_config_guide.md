# OpenClaw 配置指南

本文档指导运维人员在 `openclaw.json` 中添加 DeepSeek provider、飞书 channel、Agent 默认配置和 Cron 定时任务。

> 注意：OpenClaw 的配置文件结构复杂（嵌套 JSON），不建议直接覆盖。请按以下章节逐一添加配置块。

---

## 1. DeepSeek Provider

在 `providers` 数组中添加 DeepSeek provider。如果已经有其他 provider，追加到数组末尾。

```jsonc
// openclaw.json → providers[]
{
  "id": "deepseek",
  "label": "DeepSeek",
  "type": "openai-compatible",
  "baseURL": "https://api.deepseek.com/v1",
  "apiKey": "${DEEPSEEK_API_KEY}",  // 从环境变量读取，无需硬编码
  "models": [
    {
      "id": "deepseek-v4-pro",
      "label": "DeepSeek V4 Pro",
      "contextWindow": 125000,
      "maxTokens": 8192
    }
  ]
}
```

**要点**：
- `apiKey` 使用 `${DEEPSEEK_API_KEY}` 语法引用环境变量，不要在配置文件中硬编码 API Key
- `type` 设为 `openai-compatible`，DeepSeek 的 API 兼容 OpenAI 格式

---

## 2. 飞书 Channel（可选）

如果需要 OpenClaw 直接通过飞书收发消息，添加飞书 channel。

```jsonc
// openclaw.json → channels[]
{
  "id": "feishu",
  "type": "feishu",
  "appId": "${FEISHU_APP_ID}",
  "appSecret": "${FEISHU_APP_SECRET}"
}
```

**注意**：流水线的飞书推送通过 `feishu-publisher` skill 的 Python 脚本独立完成，不依赖此 channel。此配置仅在需要通过飞书与 OpenClaw 交互时使用。

---

## 3. Agent 默认配置

在 `agents.defaults` 中设置默认模型和 workspace 路径。

```jsonc
// openclaw.json → agents.defaults
{
  "defaults": {
    "model": "deepseek/deepseek-v4-pro",
    "fallbackModels": [
      "deepseek/deepseek-v4-pro"
    ],
    "timeout": 1800,           // 30分钟超时，流水线费时
    "maxTurns": 50,            // 流水线步骤多，需要足够轮次
    "workspace": "/path/to/D-OpenClaw"  // 替换为实际路径
  }
}
```

**路径替换**：将 `/path/to/D-OpenClaw` 替换为服务器上的实际仓库路径，例如 `/opt/openclaw/D-OpenClaw`。

---

## 4. Cron 定时任务

创建每日自动执行流水线的 cron 任务。

### 4.1 新建任务

```bash
openclaw cron create \
  --name "daily-content-pipeline" \
  --schedule "0 23 * * *" \
  --timezone "Asia/Shanghai" \
  --timeout 1800 \
  --message "执行完整11步内容运营流水线：从热点监控到飞书推送。今天是<current_date>，请基于当天热点生成公众号和小红书内容。"
```

### 4.2 配置 Webhook 通知（飞书群机器人）

```bash
openclaw cron update daily-content-pipeline \
  --webhook "${FEISHU_WEBHOOK_URL}"
```

### 4.3 管理命令

```bash
# 查看所有定时任务
openclaw cron list

# 查看任务详情
openclaw cron get daily-content-pipeline

# 手动触发一次（测试用）
openclaw cron trigger daily-content-pipeline

# 暂停 / 启用
openclaw cron disable daily-content-pipeline
openclaw cron enable daily-content-pipeline

# 查看最近执行日志
openclaw cron logs daily-content-pipeline --limit 10
```

---

## 5. 完整 openclaw.json 骨架

合并以上配置后的 `openclaw.json` 大致结构：

```jsonc
{
  "providers": [
    // ... 可能已有其他 provider ...
    {
      "id": "deepseek",
      "label": "DeepSeek",
      "type": "openai-compatible",
      "baseURL": "https://api.deepseek.com/v1",
      "apiKey": "${DEEPSEEK_API_KEY}",
      "models": [
        {
          "id": "deepseek-v4-pro",
          "label": "DeepSeek V4 Pro",
          "contextWindow": 125000,
          "maxTokens": 8192
        }
      ]
    }
  ],
  "channels": [
    // ... 可能已有其他 channel ...
    {
      "id": "feishu",
      "type": "feishu",
      "appId": "${FEISHU_APP_ID}",
      "appSecret": "${FEISHU_APP_SECRET}"
    }
  ],
  "agents": {
    "defaults": {
      "model": "deepseek/deepseek-v4-pro",
      "fallbackModels": ["deepseek/deepseek-v4-pro"],
      "timeout": 1800,
      "maxTurns": 50,
      "workspace": "/opt/openclaw/D-OpenClaw"
    }
  }
}
```

---

## 6. 验证配置

```bash
# 检查配置文件语法
cat openclaw.json | python3 -m json.tool > /dev/null && echo "JSON 有效"

# 测试 Agent 是否能正常启动
openclaw agent --message "测试消息：请回复'OpenClaw 配置成功'" --timeout 60
```
