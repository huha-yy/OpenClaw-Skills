---
name: douyin-content
description: "抖音内容生成：生成口播脚本、分镜脚本、字幕文案、封面和发布元数据。"
metadata: { "openclaw": { "emoji": "🎵" } }
user-invocable: true
---

# Douyin Content Generator

Generate complete Douyin video packages. Douyin is about **fast hook + high-density delivery** — the first 3 seconds determine whether viewers stay.

## Workflow

1. Load Douyin style guide from `configs/platform_style_guides/douyin.md`.
2. Load brand guidelines from `configs/brand_guidelines.md`.
3. Based on the content strategy's Douyin angle, generate the full package.

## Input

```json
{
  "hotspot_id": "hs_20260609_001",
  "title": "...",
  "research": { "confirmed_facts": [...], "uncertain_points": [...] },
  "strategy": {
    "platforms": {
      "douyin": { "angle": "...", "format": "...", "notes": "..." }
    }
  }
}
```

## Output

```json
{
  "platform": "douyin",
  "video_title": "新能源补贴政策变了，谁影响最大？",
  "hook": "最近新能源补贴政策又有新变化，但很多人只看到了补贴金额，其实真正影响你买车决策的是这三个变化——",
  "script": [
    {
      "scene": 1,
      "duration_sec": 5,
      "type": "host_talking",
      "dialogue": "最近某地发布了新能源补贴新政策，金额看似很大...",
      "visual_suggestion": "口播+屏幕下方出现'补贴新政'文字卡片",
      "on_screen_text": "补贴新政"
    },
    {
      "scene": 2,
      "duration_sec": 8,
      "type": "info_card",
      "dialogue": "第一点：适用地区和时间。很多人忽略了...",
      "visual_suggestion": "全屏信息卡片，列出地区和时间限制",
      "on_screen_text": "适用地区：XX省\n适用时间：2026年X月-X月"
    }
  ],
  "cover": {
    "title": "补贴变了？\n3点解读",
    "visual_description": "大字标题+新能源汽车元素，高对比度",
    "style": "信息密度高，适合竖屏"
  },
  "hashtags": ["#新能源车", "#购车补贴", "#汽车政策"],
  "best_publish_time": "工作日晚7-9点",
  "risk_notes": []
}
```

## Douyin-specific rules

- Hook (first 3s): use surprising numbers, counter-intuitive angles, or direct questions.
- Script style: spoken language, not written language. Read it aloud to check.
- Scene length: 3-8 seconds per scene. Avoid monologue blocks over 10 seconds.
- Visual variety: alternate between host talking, info cards, and B-roll suggestions.
- Cover: high contrast, large text, vertical (9:16).
- No fake urgency, no competitor mockery, no unverified data claims.
