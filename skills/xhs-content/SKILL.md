---
name: xhs-content
description: "小红书内容生成：生成标题、正文、标签、图文分镜方案和评论区引导语。"
metadata: { "openclaw": { "emoji": "📕" } }
user-invocable: true
---

# Xiaohongshu Content Generator

Generate complete Xiaohongshu note packages. The key to XHS is **text-image synergy** — every image has a purpose and on-image text.

## Workflow

1. Load XHS style guide from `configs/platform_style_guides/xiaohongshu.md`.
2. Load brand guidelines from `configs/brand_guidelines.md`.
3. Based on the content strategy's XHS angle, generate the full package.
4. Reference any available good examples from `samples/reference/`.

## Input

```json
{
  "hotspot_id": "hs_20260609_001",
  "title": "...",
  "research": { "confirmed_facts": [...], "uncertain_points": [...] },
  "strategy": {
    "platforms": {
      "xiaohongshu": { "angle": "...", "format": "...", "notes": "..." }
    }
  }
}
```

## Output

```json
{
  "platform": "xiaohongshu",
  "title": "新能源车补贴又变了？普通消费者最该关注这3点",
  "body": "最近某地发布了新能源车相关补贴政策，很多人第一眼只看补贴金额...",
  "tags": ["#新能源车", "#购车补贴", "#买车攻略"],
  "images": [
    {
      "position": 1,
      "purpose": "封面",
      "on_image_text": "补贴又变了？\n普通人最该关注的3点",
      "visual_description": "简洁的新能源汽车充电场景，暖色调，生活感",
      "corresponding_text": "标题",
      "search_keywords": ["electric car charging", "urban lifestyle", "warm tone"],
      "ai_prompt": "A modern electric car charging at a city charging station, warm sunset lighting, lifestyle photography style, clean composition"
    },
    {
      "position": 2,
      "purpose": "核心观点",
      "on_image_text": "第1点\n适用地区和时间限制",
      "visual_description": "信息卡片风格，浅色背景，突出文字",
      "corresponding_text": "正文第一段",
      "search_keywords": [],
      "ai_prompt": "Clean information card with text overlay, minimalist design, light beige background"
    }
  ],
  "comment_prompt": "你觉得补贴金额重要还是适用条件更重要？评论区聊聊你的看法👇",
  "risk_notes": ["避免使用'全国通用'等绝对化表述"]
}
```

## XHS-specific rules

- Title: hook-driven, emotional, numbers work well (e.g., "这3点", "别再").
- Body: conversational tone, short paragraphs, use emoji naturally, not forced.
- Tags: 3-5 relevant tags, mix broad (#新能源车) and specific (#买车攻略).
- Images: every image must have a clear purpose. 5-9 images for a standard note.
- No fake scarcity ("限时", "最后一天" etc.).
- No competitor attacks.
- Avoid 广告法 risk words: "最好", "第一", "绝对", "100%", etc.
