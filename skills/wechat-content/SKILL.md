---
name: wechat-content
description: "公众号内容生成：生成文章标题、摘要、分节正文、封面和正文插图方案。"
metadata: { "openclaw": { "emoji": "📰" } }
user-invocable: true
---

# WeChat Content Generator

Generate complete WeChat Official Account article packages. WeChat articles require **depth, structure, and source citations** — readers expect authority and analysis.

## Workflow

1. Load WeChat style guide from `configs/platform_style_guides/wechat.md`.
2. Load brand guidelines from `configs/brand_guidelines.md`.
3. Based on the content strategy's WeChat angle, generate the full article.

## Input

```json
{
  "hotspot_id": "hs_20260609_001",
  "title": "...",
  "research": { "confirmed_facts": [...], "uncertain_points": [...], "sources": [...] },
  "strategy": {
    "platforms": {
      "wechat": { "angle": "...", "format": "...", "notes": "..." }
    }
  }
}
```

## Output

```json
{
  "platform": "wechat",
  "title": "从最新补贴政策看2026年新能源汽车消费趋势",
  "summary": "近期某地发布新能源汽车补贴政策，释放出地方消费刺激和产业支持的双重信号。本文从消费端、品牌端和市场端三个角度进行分析。",
  "body": [
    {
      "section": 1,
      "subheading": "一、政策要点：这次补贴改了什么？",
      "content": "...",
      "inline_image_suggestion": {
        "position": "after_subheading",
        "description": "政策要点总结信息图",
        "search_keywords": ["policy summary", "infographic background"]
      }
    },
    {
      "section": 2,
      "subheading": "二、消费端影响：谁受益最大？",
      "content": "...",
      "inline_image_suggestion": null
    },
    {
      "section": 3,
      "subheading": "三、行业信号：补贴背后的市场逻辑",
      "content": "...",
      "inline_image_suggestion": {
        "position": "mid_section",
        "description": "新能源汽车市场趋势图",
        "search_keywords": ["new energy vehicle", "market trend", "data visualization"]
      }
    }
  ],
  "cover": {
    "title": "补贴新政\n2026新能源消费趋势",
    "visual_description": "简洁商务风格，深蓝或深灰底色，白色大字标题，新能源汽车元素点缀",
    "style": "专业、有质感，适合公众号头图（2.35:1）"
  },
  "sources_cited": [
    "财经网报道 (2026-06-09)",
    "某地政府官网政策文件"
  ],
  "risk_notes": [
    "政策适用范围需再次确认",
    "避免使用'全国通用'等绝对化表述"
  ]
}
```

## WeChat-specific rules

- Title: informative and specific, not clickbait. Can be longer than XHS titles.
- Summary: 1-2 sentences that preview the article's value, not a teaser trap.
- Structure: use numbered subheadings. Each section makes one point.
- Sources: cite all external sources. Links preferred, at minimum source name + date.
- Tone: professional, analytical, but not academic. Accessible to industry-interested readers.
- Cover: 2.35:1 aspect ratio. Professional, not sensational.
- No fabricated data, no unverified trends, no market predictions without stating uncertainty.
- Avoid 广告法 risk words and over-promising language.
