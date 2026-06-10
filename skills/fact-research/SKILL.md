---
name: fact-research
description: "事实核验：拉取2-3个以上来源，多源交叉验证，提取确认事实与不确定信息点。"
metadata: { "openclaw": { "emoji": "🔍" } }
user-invocable: true
---

# Fact Research

Multi-source fact verification. Never generate content based on a single source.

## Workflow

1. For each relevant hotspot, fetch full article text from 2-3 distinct sources (different domains).
2. Extract key facts from each source: who, what, when, where, policy scope, amounts, conditions.
3. Cross-compare facts across sources. Mark consistency.
4. Output confirmed facts and uncertain points separately.
5. Save all source URLs and fetch timestamps.

## Input

```json
{
  "hotspot_id": "hs_20260609_001",
  "title": "...",
  "urls": ["https://source-a.com/...", "https://source-b.com/...", "https://source-c.com/..."],
  "relevance": { "relevance_type": "行业相关", "relevance_score": 85 }
}
```

## Output

```json
{
  "hotspot_id": "hs_20260609_001",
  "research_time": "2026-06-09T10:05:00Z",
  "source_count": 3,
  "sources": [
    {
      "name": "财经网",
      "url": "https://example.com/news/123",
      "published_at": "2026-06-09T08:30:00Z",
      "fetched_at": "2026-06-09T10:05:00Z"
    }
  ],
  "confirmed_facts": [
    "某地发布新能源汽车补贴政策",
    "政策适用时间为2026年某月至某月",
    "补贴对象包含指定条件下的个人消费者"
  ],
  "uncertain_points": [
    "具体车型范围需以官方政策文件为准"
  ],
  "risk_level": "low"
}
```

## Rules

- Minimum 2 distinct sources before generating any content. If only 1 source is available, flag as `risk_level: high` and mark all facts as uncertain.
- Prefer authoritative sources: government, major media, official announcements.
- If sources conflict on key facts, flag in `uncertain_points` and set `risk_level: high`.
- Never fabricate facts or fill in gaps with assumptions.
- When the research confirms a `直接相关` + high-risk hotspot (negative news about company), immediately escalate — do NOT proceed to content generation.
