# 阶段 2：Agent 工作流设计计划

## 1. 阶段目标

本阶段目标是将 POC 中的步骤拆成可维护的 Agent 和工具调用，让流程可以被 OpenClaw 编排。

## 2. Agent 划分

| Agent | 职责 | 输入 | 输出 |
| --- | --- | --- | --- |
| Monitor Agent | 获取热点输入 | 热点源配置 | 候选热点 |
| Relevance Agent | 判断相关性 | 热点、关键词 | 相关性评分 |
| Research Agent | 整理来源和事实 | 热点链接 | 事实摘要 |
| Strategy Agent | 规划内容角度 | 事实摘要、相关性 | 内容策略 |
| XHS Content Agent | 生成小红书内容包 | 内容策略 | 小红书图文包 |
| Douyin Content Agent | 生成抖音内容包 | 内容策略 | 抖音视频包 |
| WeChat Content Agent | 生成公众号内容包 | 内容策略 | 公众号图文包 |
| Compliance Agent | 风险检查 | 三平台内容、来源 | 风险报告 |
| Package Agent | 汇总输出 | 所有结果 | 发布包 |

## 3. 工具函数设计

第一版建议抽象以下工具函数：

```text
load_keywords()
load_brand_guidelines()
load_hotspot_sources()
fetch_hotspots()
fetch_article()
score_relevance()
extract_facts()
generate_content_strategy()
generate_xhs_package()
generate_douyin_package()
generate_wechat_package()
check_risk()
write_publish_package()
```

## 4. 工作流执行方式

第一版建议采用串行流程，保证结果稳定：

```text
Monitor → Relevance → Research → Strategy → Platform Writers → Compliance → Package
```

后续可优化为并行：

```text
XHS Content Agent
Douyin Content Agent       并行生成
WeChat Content Agent
```

## 5. Agent 输出规范

所有 Agent 输出都应结构化，避免只输出自然语言。

示例：

```json
{
  "status": "success",
  "summary": "判断结果摘要",
  "data": {},
  "risks": [],
  "next_action": "continue"
}
```

## 6. 本阶段交付物

- Agent 职责说明
- 工具函数列表
- 工作流配置文件
- 标准输入输出格式
- 一条热点的完整执行日志
