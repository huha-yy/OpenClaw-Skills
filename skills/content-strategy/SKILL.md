---
name: content-strategy
description: "内容策略：基于事实和相关性判断，确定内容角度、平台适配性和创作方向。"
metadata: { "openclaw": { "emoji": "🧭" } }
user-invocable: true
---

# Content Strategy

Given confirmed facts and relevance, produce a content strategy that guides platform-specific generation.

## Workflow

1. Review facts, relevance type, and risk assessment from upstream.
2. Determine the overall content angle: policy interpretation? consumer guide? industry analysis? news alert?
3. Assess suitability for each platform (XHS/Douyin/WeChat) — not every hotspot fits every platform.
4. For unsuitable platforms, explain why.
5. Load brand guidelines from `configs/brand_guidelines.md` and apply to angle selection.

## Input

```json
{
  "hotspot_id": "hs_20260609_001",
  "title": "...",
  "relevance": { "relevance_type": "行业相关", "relevance_score": 85, "matched_keywords": [...] },
  "research": { "confirmed_facts": [...], "uncertain_points": [...], "risk_level": "low" }
}
```

## Output

```json
{
  "hotspot_id": "hs_20260609_001",
  "strategy": {
    "main_angle": "政策解读：从消费端分析新补贴对购车决策的影响",
    "tone": "专业、易懂、不夸大",
    "platforms": {
      "xiaohongshu": {
        "suitable": true,
        "angle": "普通消费者视角：补贴变了，买车该关注哪几点",
        "format": "图文笔记，清单体",
        "notes": "避免写成政策原文搬运，用消费者语言转化"
      },
      "douyin": {
        "suitable": true,
        "angle": "3分钟快速解读：补贴新政影响谁最大",
        "format": "口播+信息卡，反常识开头",
        "notes": "前3秒用数字抓注意力"
      },
      "wechat": {
        "suitable": true,
        "angle": "从最新补贴政策看2026年行业消费趋势",
        "format": "深度分析文章，分小节",
        "notes": "需引用来源、保留数据、避免绝对化判断"
      }
    },
    "unsuitable_platforms": []
  },
  "risk_notes": [
    "需确认政策适用地区，避免写成全国通用"
  ]
}
```

## Platform suitability quick guide

| 平台 | 适合 | 不适合 |
|------|------|--------|
| 小红书 | 经验分享、清单、避坑、消费决策 | 纯硬新闻、长篇政策原文 |
| 抖音 | 快速观点、反常识、3点解读 | 深度长文、复杂数据 |
| 公众号 | 行业分析、政策解读、趋势研判 | 碎片化短内容、纯娱乐 |

## Rules

- Do not recommend content for `风险等级: high` hotspots — flag and stop.
- `竞品相关` hot topics: angle must be industry-level, never attack competitors.
- Avoid clickbait angles. The strategy must be grounded in confirmed facts, not speculation.
