---
name: hotspot-monitor
description: "热点监控：从配置的RSS/API/热搜榜拉取热点，去重聚类后输出标准化热点列表。"
metadata: { "openclaw": { "emoji": "🔥" } }
user-invocable: true
---

# Hotspot Monitor

Poll configured hotspot sources, cluster duplicates, and output a clean list of candidate events.

## Workflow

1. Load `configs/hotspot_sources.yaml` to get source list and poll intervals.
2. For each source, fetch latest entries. For RSS sources use standard HTTP GET + XML parse. For API sources use the configured endpoint and auth.
3. Normalize each entry to the standard hotspot schema (see Output).
4. Run `skills/hotspot-monitor/scripts/cluster_hotspots.py` to deduplicate by title similarity, URL, and keyword overlap.
5. Output the deduplicated hotspot list as JSON.

## Input

- `configs/hotspot_sources.yaml` — list of sources with type (rss/api), url, auth if needed
- Optional: `--limit N` to cap results per source

## Output

```json
{
  "monitor_time": "2026-06-09T10:00:00Z",
  "total_hotspots": 15,
  "hotspots": [
    {
      "hotspot_id": "hs_20260609_001",
      "title": "某地发布新能源汽车补贴新政策",
      "url": "https://example.com/news/123",
      "source_name": "财经网",
      "published_at": "2026-06-09T08:30:00Z",
      "summary": "某地发布新能源汽车购置补贴政策...",
      "tags": ["新能源", "政策", "补贴"],
      "duplicate_of": null,
      "raw_sources": 3
    }
  ]
}
```

## Rules

- Never scrape platforms that require login or explicitly prohibit crawling.
- Mark `duplicate_of` when a hotspot is a near-duplicate of another entry.
- Prefer official APIs and RSS over HTML scraping.
- Skip sources that fail 3 consecutive polls; log the failure.
- Do NOT fabricate or generate hotspot data — only fetch from actual sources.

## First-run / testing

When no real sources are configured, use `samples/mock_hotspots.json` to test the pipeline. The output schema must be identical regardless of source type.
