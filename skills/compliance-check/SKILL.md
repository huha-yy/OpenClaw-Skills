---
name: compliance-check
description: "风控审核：三维风险审查——事实准确性、品牌口径合规、平台与广告法合规。"
metadata: { "openclaw": { "emoji": "🛡️" } }
user-invocable: true
---

# Compliance Check

Risk review covering four dimensions: facts, brand, platform compliance, and AI trace detection. The output determines whether content can proceed to packaging.

## Workflow

1. Load brand guidelines from `configs/brand_guidelines.md`.
2. Review all three platform content packages + research sources.
3. Check each of the four dimensions independently.
4. Assign an overall risk level and determine if human review is required.
5. For every flagged item, provide a specific reason and suggested fix.

## Input

```json
{
  "hotspot_id": "hs_20260609_001",
  "research": { "confirmed_facts": [...], "uncertain_points": [...], "sources": [...] },
  "content": {
    "xiaohongshu": { /* full XHS package */ },
    "douyin": { /* full Douyin package */ },
    "wechat": { /* full WeChat package */ }
  }
}
```

## Output

```json
{
  "hotspot_id": "hs_20260609_001",
  "overall_risk": "medium",
  "dimensions": {
    "fact_check": {
      "risk": "low",
      "issues": [],
      "passed": true
    },
    "brand_compliance": {
      "risk": "medium",
      "issues": [
        {
          "platform": "xiaohongshu",
          "location": "title",
          "issue": "标题中'又变了'可能暗示政策频繁变动，建议改为更中性的表述",
          "severity": "medium",
          "suggestion": "改为：'新能源车补贴更新了，普通消费者最该关注这3点'"
        }
      ],
      "passed": false
    },
    "platform_compliance": {
      "risk": "medium",
      "issues": [
        {
          "platform": "all",
          "location": "body",
          "issue": "避免使用'全国通用'等绝对化表述",
          "severity": "medium",
          "suggestion": "明确标注适用地区范围，改为'该地区范围内'"
        }
      ],
      "passed": false
    },
    "ai_trace_check": {
      "risk": "low",
      "score": 42,
      "issues": [
        {
          "platform": "wechat",
          "location": "body",
          "issue": "命中AI高频词'值得注意的是'1次",
          "severity": "low",
          "suggestion": "删除或替换为直接陈述"
        }
      ],
      "passed": true
    }
  },
  "requires_human_review": true,
  "review_summary": "内容整体风险可控，需修改2处品牌表述后可由运营审核发布。"
}
```

## Four dimensions

### 1. Fact Check (事实审核)
- Are sources reliable and authoritative?
- Are facts supported by multiple sources?
- Is any unverified information presented as fact?
- Are dates, locations, policy scope accurate?
- Is any source content directly copied (copyright risk)?

### 2. Brand Compliance (品牌审核)
- Does the content align with brand voice?
- Is there excessive marketing language?
- Does it attack or mock competitors?
- Are any prohibited expressions used?
- Does it match the company's stated positions?

### 3. Platform & Regulatory Compliance (平台合规)
- Advertising law risk words: "最好", "第一", "绝对", "100%", "全网", "唯一" etc.
- Sensitive industry claims: finance, medical, legal areas have extra restrictions.
- Platform-specific rules: XHS, Douyin, WeChat each have unique policy constraints.
- Does content risk being flagged as misinformation?
- 小红书强制标签检查：确认包含 `#AI生成内容`。

### 4. AI痕迹检查（内容质量）

对每篇平台内容进行AI痕迹评分，总分50，< 35标记为"需人工润色"，< 25触发整体风险升级一级。

| 维度 | 满分 | 扣分规则 |
|------|------|----------|
| 直接性 | 10 | 绕圈子铺垫扣3-5分 |
| 节奏 | 10 | 连续3句同长度扣3分，模板化排比扣5分 |
| 信任度 | 10 | "值得注意的是"等填充词每处扣2分（上限10分） |
| 真实性 | 10 | "不仅……而且……"扣3分，系动词回避结构扣2分/处 |
| 精炼度 | 10 | 冗余修饰每处扣2分，"的"超限扣分 |

### AI高频词命中清单

以下词汇每命中一个即标记，不直接扣分但计入审核建议：
```
此外 至关重要 深入探讨 值得注意的是 值得一提的是
不可忽视的是 格局 展示 充满活力的 各种 备受
不仅……而且…… 综上所述 总而言之 标志着 作为……的证明
在这个……的时代 随着……的发展
```

## Risk levels

```text
low    — No issues or minor style suggestions. Can proceed to packaging.
medium — Issues found. Fix required before human review.
high   — Critical issues (unverified facts, legal risk, brand crisis). Do NOT package. Escalate for manual decision.
```

## Rules

- **When in doubt, escalate.** False negatives (missing a risk) are worse than false positives (flagging something harmless).
- `直接相关` + potentially negative content about company → automatically `high`, require human review.
- Any mention of competitors → flag for brand compliance check.
- Financial, medical, legal topics → automatically require platform compliance deep check.
- If any single dimension is `high`, the overall risk is `high`.
