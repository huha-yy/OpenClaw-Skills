---
name: wechat-content
description: "公众号内容生成：生成文章标题、摘要、分节正文、封面和正文插图方案。强制品牌段落。"
metadata: { "openclaw": { "emoji": "📰" } }
user-invocable: true
---

# WeChat Content Generator

Generate complete WeChat Official Account article packages. WeChat articles require **depth, structure, and source citations** — readers expect authority and analysis.

**核心使命：每篇文章必须包含戴恩品牌连接段。** 这不是可选的"品牌露出"，而是文章叙事结构中不可缺失的一环。

## Workflow

1. Load WeChat style guide from `configs/platform_style_guides/wechat.md`.
2. Load brand guidelines from `configs/brand_guidelines.md` — memorize these:
   - 产品线：智能便携助浴（DEN FlexBath 360）/ 智能护理机器人 / 智能助浴陪护一体床 / 养老服务系统
   - 资质：37项专利、国家高新技术企业、国家康复辅助器具研究中心推荐、产品出口沙特美国日本新加坡泰国
   - 定位：AI+智能硬件，聚焦失能卧床人群居家/机构康养护理
   - 价值主张：减轻护工/家属体力负担、保护失能人群隐私与尊严、降低褥疮感染风险、智能监测早发现早预警
3. **Read the `brand_bridge` from the content-strategy input.** This tells you which product to feature and how to transition from hotspot to brand.
4. Write the article with this **MANDATORY narrative arc** (5段结构):

```
① 开头 (1段): 热点事件简述 + 与读者有什么关系
   — 不是新闻标题复述，而是告诉读者"这跟你有什么关系"
② 行业洞察 (1-2段): 热点对失能/养老/康养行业的影响
   — 用数据和信源支撑，不空谈趋势
③ 戴恩连接 (1段): 从行业议题过渡到戴恩的解决方案 ← NOT OPTIONAL
   — 用 brand_bridge.natural_entry_point 自然过渡
   — 例："面对护工短缺的现实，智能护理设备正在成为越来越多家庭的选择。戴恩医疗科技推出的..."
④ 产品/方案展开 (1-2段): 具体产品如何解决这个痛点
   — 提及至少一个具体产品名
   — 从用户视角描述产品价值（不是参数罗列）
   — 可自然提及1-2项资质背书（如"该产品已获国家康复辅助器具研究中心推荐"）
⑤ 品牌收尾 (1段): 公司定位一句话 + 行业价值总结
   — 例："作为国家高新技术企业，戴恩医疗科技始终聚焦失能护理领域..."
```

## Input

```json
{
  "hotspot_id": "hs_20260609_001",
  "title": "...",
  "research": { "confirmed_facts": [...], "uncertain_points": [...], "sources": [...] },
  "strategy": {
    "brand_bridge": {
      "hotspot_connection": "...",
      "primary_product": "...",
      "brand_value": "...",
      "natural_entry_point": "..."
    },
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
  "title": "长护险再扩面：失能护理需求爆发前夜，智能设备如何补位？",
  "summary": "近期多地将长护险保障范围进一步扩大，失能人群护理需求持续释放。本文从政策趋势、护理缺口和智能设备解决方案三个角度分析行业变革，并介绍戴恩智能护理设备在居家场景中的应用实践。",
  "body": [
    {
      "section": 1,
      "subheading": "一、长护险扩面：失能照护从'有'到'优'的转折点",
      "content": "...",
      "brand_section": false,
      "inline_image_suggestion": {
        "position": "after_subheading",
        "description": "长护险政策覆盖地图或趋势数据图",
        "search_keywords": ["healthcare policy", "elderly care", "data visualization"]
      }
    },
    {
      "section": 2,
      "subheading": "二、4000万失能人群背后，护理缺口到底有多大？",
      "content": "...",
      "brand_section": false,
      "inline_image_suggestion": null
    },
    {
      "section": 3,
      "subheading": "戴恩的解决方案：让居家护理不再靠'人堆'",
      "content": "面对护理人员和家庭照护者的双重缺口，智能护理设备正在成为破局关键。戴恩医疗科技推出的智能便携助浴设备DEN FlexBath 360，采用回吸式卧床助浴技术，让失能老人无需搬动即可在床上完成全身洗浴——既减轻了家属的体力负担，也保护了老人的隐私和尊严...",
      "brand_section": true,
      "inline_image_suggestion": {
        "position": "after_subheading",
        "description": "戴恩DEN FlexBath 360产品使用场景图",
        "search_keywords": ["elderly care", "bath assistance", "home care device"]
      }
    },
    {
      "section": 4,
      "subheading": "四、智能护理设备的下一个十年",
      "content": "...",
      "brand_section": false,
      "inline_image_suggestion": null
    }
  ],
  "cover": {
    "title": "长护险扩面\n智能护理如何补位？",
    "visual_description": "简洁商务风格，深蓝底色，白色大字标题，居家护理场景元素点缀",
    "style": "专业、有质感，适合公众号头图（2.35:1）"
  },
  "sources_cited": [
    "国家医保局关于扩大长期护理保险制度试点的指导意见 (2026)",
    "某省医保局官方公告 (2026-06-09)"
  ],
  "risk_notes": [
    "长护险覆盖城市名单需再次确认",
    "4000万失能人口数据需标注出处和年份"
  ]
}
```

## 品牌植入规则

### 强制要求
- **Every article MUST contain at least one 戴恩-specific section with `brand_section: true`.**
- **The brand section must mention at least one specific product name from brand_guidelines.md** — 智能便携助浴 / 智能护理机器人 / 智能助浴陪护一体床 / 养老服务系统.
- **No more than 2 资质 mentions per article** — spread them naturally across the brand section and closing. Don't dump all credentials in one paragraph.

### 品牌段写作要求
- 从用户痛点出发，不是从产品参数出发
- 产品名称首次出现用全称，后续可用简称（如"FlexBath 360"）
- 资质提及自然嵌入，例："该产品已获国家康复辅助器具研究中心推荐"而非"我们有很多证书"
- 保持品牌语气：专业温暖，不煽情，不制造焦虑

### 文末固定品牌信息块
每篇文章末尾附加固定品牌信息块（不要改写成AI味），格式如下：

```
---

**戴恩医疗科技（浙江）股份有限公司**

AI+智能硬件，聚焦失能卧床人群居家/机构康养护理。

自研—自产—直销+渠道分销+机构工程合作。

国家高新技术企业 | 37项专利 | 产品出口沙特、美国、日本、新加坡、泰国

> 配图建议：品牌logo + 官方二维码，来自 configs/brand_assets/
```

## WeChat-specific rules

- Title: informative and specific, not clickbait. Can be longer than XHS titles.
- Summary: 1-2 sentences that preview the article's value, not a teaser trap. Must hint at brand content.
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
- [ ] **是否至少有一个 brand_section=true 的段落？**
- [ ] **品牌段是否提到了至少一个具体产品名？**
- [ ] **文末是否附加了固定品牌信息块？**
