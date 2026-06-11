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

## 去AI味规则（公众号版）

### 禁止使用的AI高频词
```
此外 值得一提的是 不可忽视的是 标志着 作为……的证明
格局 展示 充满活力的 各种 备受 深入探讨
不仅……而且…… 综上所述 总而言之 在这个……的时代
值得注意的是 随着……的发展 让我们拭目以待
```

### 禁止的模板化结构
- **"挑战与展望"板块**：避免"尽管面临若干挑战……未来展望……"的套话结尾
- **三段式排比**：公众号最常见AI痕迹，用两项或四项打破
- **虚假范围句式**："从X到Y"仅在X和Y在有意义的尺度上时使用
- **系动词回避**：减少"作为""代表""标志着""充当"的使用频率

### 交付前自检清单
- [ ] 每段是否有具体数据/案例/来源支撑？
- [ ] 是否存在"值得注意的是""值得一提的是"等填充过渡？
- [ ] 结尾是否模板化？最后一段用具体结论替代套话
- [ ] 是否过度使用分号连接从句？改成短句，用句号断开
- [ ] "的"使用频率：每句不超过3个
