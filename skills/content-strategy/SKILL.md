---
name: content-strategy
description: "内容策略：基于事实和相关性判断，确定内容角度、平台适配性和创作方向。强制要求品牌连接点。"
metadata: { "openclaw": { "emoji": "🧭" } }
user-invocable: true
---

# Content Strategy

Given confirmed facts and relevance, produce a content strategy that guides platform-specific generation.

**核心使命：从热点引出戴恩品牌和产品。** 每一篇内容的终点不是"行业分析"，而是"戴恩如何在这个议题中提供价值"。

## Workflow

1. Review facts, relevance type, and risk assessment from upstream.
2. Determine the overall content angle: policy interpretation? consumer guide? industry analysis? news alert?
3. Assess suitability for each platform (XHS/Douyin/WeChat) — not every hotspot fits every platform.
4. For unsuitable platforms, explain why.
5. **Identify the brand bridge** — which 戴恩 product/capability/value-proposition does this hotspot naturally connect to? This is NOT optional. Think:
   - 这个热点涉及的人群/场景（失能、卧床、术后、居家养老、机构护理…）与戴恩的产品线有什么重叠？
   - 这个热点暴露的痛点（护工短缺、褥疮风险、洗浴困难、排泄护理…）戴恩的哪个产品能解决？
   - 这个热点的政策/行业信号对戴恩意味着什么（利好、趋势验证、新需求…）？
6. Load `configs/company_keywords.yaml` to match hotspot keywords to specific products. Also review `configs/brand_guidelines.md` for product names and value propositions.

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
    "main_angle": "从长护险扩面看失能护理行业变革——戴恩智能护理设备如何回应居家照护痛点",
    "tone": "专业、温暖、不夸大",
    "brand_bridge": {
      "hotspot_connection": "长护险扩面意味着更多失能家庭获得护理补贴，直接提升了居家护理设备的可及性，戴恩的智能便携助浴和护理机器人正是受益品类",
      "primary_product": "智能便携助浴（DEN FlexBath 360）",
      "brand_value": "戴恩用智能硬件减轻照护者的体力负担，让失能人群有尊严地生活",
      "natural_entry_point": "从'长护险报销范围扩大'自然过渡到'哪些护理设备能真正帮到家庭照护者'，引出戴恩产品"
    },
    "platforms": {
      "xiaohongshu": {
        "suitable": true,
        "angle": "家里有失能老人的注意了！长护险新政策背后，这个护理方案太省心了",
        "format": "图文笔记，个人经验分享体",
        "notes": "从照护者视角切入，软植入戴恩便携助浴，避免硬广语气"
      },
      "douyin": {
        "suitable": true,
        "angle": "长护险又扩大了！家里有卧床老人的，这笔钱记得申请",
        "format": "口播+信息卡，反常识开头",
        "notes": "前3秒用'你家长护险报销了吗'抓注意力，后半段自然展示产品使用场景"
      },
      "wechat": {
        "suitable": true,
        "angle": "从长护险扩面看失能护理行业变革——戴恩智能护理如何回应居家照护痛点",
        "format": "深度分析文章，分小节",
        "notes": "行业分析+戴恩解决方案，需引用政策来源、保留数据、避免绝对化判断"
      }
    },
    "unsuitable_platforms": []
  },
  "risk_notes": [
    "需确认长护险最新覆盖城市名单，避免写成全国已覆盖"
  ]
}
```

## brand_bridge 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| `hotspot_connection` | 这则热点与戴恩的关联点——为什么戴恩应该回应这个话题 | "长护险扩面提升了居家护理设备的可及性" |
| `primary_product` | 最相关的产品线 | 智能便携助浴 / 智能护理机器人 / 智能助浴陪护一体床 / 养老服务系统 |
| `brand_value` | 这篇内容要传递的戴恩核心信息（1句话） | "戴恩用智能硬件减轻照护者的体力负担" |
| `natural_entry_point` | 文章中从热点过渡到戴恩的自然切入点 | "从政策过渡到'哪些设备能帮到家庭照护者'" |

## Platform suitability quick guide

| 平台 | 适合 | 不适合 |
|------|------|--------|
| 小红书 | 经验分享、清单、避坑、消费决策、照护经验 | 纯硬新闻、长篇政策原文 |
| 抖音 | 快速观点、反常识、3点解读、产品演示 | 深度长文、复杂数据 |
| 公众号 | 行业分析、政策解读、趋势研判、品牌深度 | 碎片化短内容、纯娱乐 |

## Rules

- Do not recommend content for `风险等级: high` hotspots — flag and stop.
- `竞品相关` hot topics: angle must be industry-level, never attack competitors.
- Avoid clickbait angles. The strategy must be grounded in confirmed facts, not speculation.
- **Every strategy MUST include a brand_bridge. Strategy without one is incomplete.**
- **brand_bridge must reference specific products from brand_guidelines.md** — 智能便携助浴 / 智能护理机器人 / 智能助浴陪护一体床 / 养老服务系统.
- Platform angles must be written from 戴恩's perspective, not generic industry analysis.
