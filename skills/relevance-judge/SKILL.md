---
name: relevance-judge
description: "相关性判断：两级过滤（关键词初筛+LLM语义精判），判断热点是否与公司/品牌/行业相关。"
metadata: { "openclaw": { "emoji": "🎯" } }
user-invocable: true
---

# Relevance Judge

Two-tier filter: keyword pre-screening → LLM semantic judgment. Output relevance type, score, and matched keywords.

## Workflow

1. Load `configs/company_keywords.yaml` — categorized into: `direct` (company/brand/product/exec names), `industry` (sector terms), `competitor` (rival names).
2. For each hotspot in the input list, run keyword match first. If no keyword hits → `irrelevant`, skip.
3. For hotspots with keyword hits, use LLM to judge semantic relevance and assign a type + score.
4. Output filtered and scored list.

## Input

```json
{
  "hotspots": [ /* standard hotspot entries from hotspot-monitor */ ]
}
```

## Output

```json
{
  "relevant": [
    {
      "hotspot_id": "hs_20260609_001",
      "relevance_score": 85,
      "relevance_type": "行业相关",
      "matched_keywords": ["新能源汽车", "补贴政策"],
      "judgment_reason": "热点涉及新能源汽车消费政策，与公司所在行业高度相关，可做政策解读内容。"
    }
  ],
  "irrelevant_count": 10
}
```

Relevance types:
- `直接相关` — directly mentions company/brand/product/exec → highest priority, must have human review
- `行业相关` — about the company's industry, policy, market trends → can generate industry insight content
- `竞品相关` — about competitors → handle cautiously, never attack
- `借势相关` — social hotspot that can be linked to brand viewpoint → can generate lightweight content
- `不相关` — no relevance → skip

## Rules

- `直接相关` hotspots with risk potential (negative news, controversy) must be flagged.
- Do not force relevance. If semantic judgment is uncertain, default to `不相关`.
- Score: 0-100. Below 40 → `不相关`. 40-60 → `借势相关`. 60-80 → `行业相关`. 80+ → `直接相关`.
- `竞品相关` is a separate axis — can overlap with other types.
