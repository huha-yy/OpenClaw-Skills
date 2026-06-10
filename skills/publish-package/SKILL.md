---
name: publish-package
description: "发布包汇总：将所有上游输出汇总写入 outputs/ 目录下的标准化发布包。"
metadata: { "openclaw": { "emoji": "📦" } }
user-invocable: true
---

# Publish Package

Aggregate all research, strategy, content, and compliance results into a standardized publish package directory. This is the final step — the output that operations staff review.

## Workflow

1. Collect all upstream outputs by hotspot_id.
2. Generate the package directory name: `outputs/{date}_{hotspot_title_slug}/`.
3. Write each file according to the standard directory layout.
4. Generate `package_summary.md` — a single overview file for quick review.
5. Validate that all required files exist.

## Input

```json
{
  "hotspot_id": "hs_20260609_001",
  "title": "某地发布新能源汽车补贴新政策",
  "monitor": { /* hotspot entry */ },
  "relevance": { /* relevance judgment */ },
  "research": { /* fact research */ },
  "strategy": { /* content strategy */ },
  "content": {
    "xiaohongshu": { /* XHS package */ },
    "douyin": { /* Douyin package */ },
    "wechat": { /* WeChat package */ }
  },
  "compliance": { /* compliance report */ }
}
```

## Output directory layout

```text
outputs/{date}_{title_slug}/
  sources.json              # All source URLs, names, fetch times
  event_analysis.md         # Hotspot summary + relevance + confirmed facts
  risk_report.md            # Full compliance check report
  package_summary.md        # One-page overview for operations staff

  xiaohongshu/
    note.md                 # Full note with title, body, tags, image descriptions
    image_storyboard.md     # Image-by-image visual plan
    publish_meta.json       # Platform-specific publishing metadata

  douyin/
    video_script.md         # Full script with scenes, dialogue, visuals
    storyboard.md           # Scene-by-scene visual plan
    publish_meta.json       # Hashtags, best publish time, cover specs

  wechat/
    article.md              # Full article with sections, subheadings, sources
    cover.md                # Cover image specification
    publish_meta.json       # Summary, source list, risk notes
```

## package_summary.md template

```markdown
# {hotspot_title}

**生成时间:** {timestamp}
**相关性:** {relevance_type} ({relevance_score}/100)
**风险等级:** {risk_level}

## 热点摘要
{one paragraph from research}

## 内容概览

| 平台 | 角度 | 状态 |
|------|------|------|
| 小红书 | {XHS angle} | 待审核 |
| 抖音 | {Douyin angle} | 待审核 |
| 公众号 | {WeChat angle} | 待审核 |

## 审核重点
- {top risk items from compliance}

## 下一步
人工审核各平台内容，确认事实准确性和品牌口径后发布。
```

## Rules

- If `compliance.overall_risk === "high"`, do NOT generate the package. Output an error with reasons.
- If `compliance.requires_human_review === true`, mark all platform statuses as "待审核" with the specific review items called out.
- Validate that no required file is empty before considering the package complete.
- All file paths use Unix-style forward slashes.
- Use `scripts/write_package.py` for file I/O operations.
