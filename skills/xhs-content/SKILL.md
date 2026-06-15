---
name: xhs-content
description: "小红书内容生成：生成标题、正文、标签、图文分镜方案和评论区引导语。品牌软植入。"
metadata: { "openclaw": { "emoji": "📕" } }
user-invocable: true
---

# Xiaohongshu Content Generator

Generate complete Xiaohongshu note packages. The key to XHS is **text-image synergy** — every image has a purpose and on-image text.

**核心使命：品牌软植入。** 小红书的品牌植入必须是"用户视角的经验分享"，而非企业官方宣传。用"我发现"、"帮家人用过"、"护理师推荐"的口吻自然带出戴恩。

## Workflow

1. Load XHS style guide from `configs/platform_style_guides/xiaohongshu.md`.
2. Load brand guidelines from `configs/brand_guidelines.md` — memorize:
   - 产品线：智能便携助浴（DEN FlexBath 360）/ 智能护理机器人 / 智能助浴陪护一体床
   - 定位：AI+智能硬件，聚焦失能卧床人群居家/机构康养护理
   - 语气：专业温暖，用户视角，不制造焦虑
3. Read the `brand_bridge` from the content-strategy input.
4. **品牌软植入（小红书特有）**：
   - 用"我最近发现"、"帮家人用过"、"护理师朋友推荐"、"体验了"的语气引入戴恩产品
   - 品牌信息融入个人经验分享中，而非单独成段
   - 图片中可以有产品使用场景图，但不能是硬广风格（白底产品图+大字slogan）
   - 产品作为"解决方案"出现，而非"推销对象"
   - 选择一种植入风格：product_mention（产品提及）/ personal_experience（个人经验）/ industry_insight（行业洞察）

## Input

```json
{
  "hotspot_id": "hs_20260609_001",
  "title": "...",
  "research": { "confirmed_facts": [...], "uncertain_points": [...] },
  "strategy": {
    "brand_bridge": {
      "hotspot_connection": "...",
      "primary_product": "...",
      "brand_value": "...",
      "natural_entry_point": "..."
    },
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
  "title": "家里有失能老人的注意了！长护险新政策，这个护理方案太省心",
  "body": "最近我妈跟我说长护险又扩面了，报销范围比以前大了不少...说真的，照顾失能老人最头疼的不是钱，是体力。洗个澡要两个人搬，我妈腰不好根本弄不动。后来护理师朋友推荐了一款戴恩的便携洗浴机，回吸式的，老人在床上就能洗，一个人就能操作...",
  "tags": ["#长护险", "#失能护理", "#居家养老", "#戴恩科技", "#智能护理", "#照顾老人", "#护理神器"],
  "brand_placement": {
    "style": "personal_experience",
    "product_mentioned": "智能便携助浴（DEN FlexBath 360）",
    "placement_text": "护理师朋友推荐了一款戴恩的便携洗浴机，回吸式的，老人在床上就能洗，一个人就能操作"
  },
  "images": [
    {
      "position": 1,
      "purpose": "封面",
      "on_image_text": "长护险又扩面了！\n家里有老人的记得申请",
      "visual_description": "温馨的居家养老场景，老人和家属互动的温暖画面",
      "corresponding_text": "标题",
      "search_keywords": ["elderly home care", "family care", "warm lighting"],
      "ai_prompt": "Warm home care scene, elderly person with family caregiver in cozy living room, natural lighting, lifestyle photography"
    },
    {
      "position": 2,
      "purpose": "核心观点",
      "on_image_text": "照顾失能老人\n最头疼的不是钱",
      "visual_description": "信息卡片风格，浅色背景，突出文字",
      "corresponding_text": "正文第一段",
      "search_keywords": [],
      "ai_prompt": "Clean information card with text overlay, minimalist design, light beige background"
    },
    {
      "position": 5,
      "purpose": "产品使用场景",
      "on_image_text": "床上就能洗\n一个人就能操作",
      "visual_description": "便携助浴设备在居家场景中的使用示意，干净明亮，不硬广",
      "corresponding_text": "品牌植入段",
      "search_keywords": ["home care device", "elderly bathroom", "assistive technology"],
      "ai_prompt": "Modern portable bathing device in a clean home bathroom setting, natural light, editorial style, not commercial looking"
    },
    {
      "position": 7,
      "purpose": "品牌收尾",
      "on_image_text": "戴恩科技\n让护理更简单",
      "visual_description": "品牌logo + 简洁收尾画面",
      "corresponding_text": "结尾",
      "search_keywords": [],
      "ai_prompt": "Clean brand closing image with subtle logo placement, minimalist design, warm professional tone"
    }
  ],
  "comment_prompt": "你们家照顾老人最头疼的是什么？洗澡、翻身还是排泄护理？评论区聊聊👇",
  "risk_notes": ["避免使用'最好''第一'等广告法禁用词", "产品描述不做医疗功效承诺"]
}
```

## brand_placement 字段说明

| 字段 | 说明 | 可选值 |
|------|------|--------|
| `style` | 品牌植入风格 | `product_mention` — 自然提及产品 / `personal_experience` — 个人使用经验 / `industry_insight` — 行业观察视角 |
| `product_mentioned` | 文中提到的具体产品 | 智能便携助浴 / 智能护理机器人 / 智能助浴陪护一体床 |
| `placement_text` | 文章中品牌植入的关键句（照护者视角、非推销语气） | — |

## 品牌植入规则（小红书版）

### 强制要求
- **品牌植入须以个人经验/他人推荐/专业视角自然融入，不得使用硬广语气。**
- **必须加入品牌标签**：`#戴恩科技`、`#智能护理` 至少2个品牌相关标签。
- **产品图作为第5-7张图附上**（不要放在前3张），正文中不直接推销。产品图风格应为使用场景，非白底商品图。
- **禁止企业官方语气**：不得出现"我司"、"公司推出"、"欢迎咨询"、"点击购买"等。
- **禁止堆砌资质**：37项专利等资质信息至多提及1项，且须自然嵌入（如"查了下发现还是国家高新技术企业"）。

### 品牌软植入写法指南

| 硬广写法（禁止） | 软植入写法（推荐） |
|------------------|---------------------|
| "戴恩推出全新智能护理机器人，功能强大" | "朋友给我推荐了一款护理机器人，说是能自动处理排泄物，老人戴上就..." |
| "我司产品已通过XX认证，值得信赖" | "后来查了一下，发现这家还是国家高新技术企业，不是杂牌" |
| "欢迎私信咨询购买" | （正文中不提购买，评论区引导中也不直接导流） |

### 品牌图片规则
- 产品相关图片放在第5张及以后（前3张决定点击率，不放品牌内容）
- 产品图用使用场景图（有人在用的画面），不用白底商品图
- 最后1张图可以是品牌收尾图（logo+一句话），但不能是大字报风格

## XHS-specific rules

### 标题规则
- **字数**：8-22字。前13字必须包含核心关键词（搜索权重占40%）。
- **公式**：从以下4个中选1-2个组合：
  1. `[Emoji] + [受众呼唤] + [收益]`  → 家里有老人的注意了！这个护理方案太省心
  2. `[否定式警告] + [更好替代]`        → 别再用手搬了！床上洗浴一个设备就搞定
  3. `[悬念] + [结果]`                  → 照顾失能老人3年，终于找到一个省力的方法
  4. `[数字] + [过程] + [权威]`         → 3个步骤，护理师手把手教你选护理设备
- **视觉钩子**：必须包含至少1个emoji或感叹号。

### 正文规则
- **字数**：300-600字，短句为主，每段2-3句。
- **结构**：三段式——① 观点段（第一人称，直接亮态度）→ ② 证据段（数据/案例/细节）→ ③ 品牌融入段（个人经验自然带出戴恩，非硬推）。
- **开头钩子**：正文前1-2句必须是高能开篇（情绪、冲突、悬念），不得平淡引入。
- **风格**：日记体优先（互动率最高），其次测评体、教程体。口语化，允许不完美感。
- **CTA**：优先引导关注（CES权重：关注8分 > 评论/转发4分 > 点赞/收藏1分）。

### 标签规则
- 5-8个标签，混合热门（流量）和长尾（精准）。
- **强制加入 `#AI生成内容`**（2026年1月起小红书要求，否则限流）。
- **强制加入品牌标签**：`#戴恩科技` `#智能护理`（至少2个）。

### 图片规则
- Every image must have a clear purpose. 5-9 images for a standard note.
- 品牌相关图片放在第5张及以后。

### 禁区
- No fake scarcity, no competitor attacks.
- 广告法风险词：`最好` `第一` `绝对` `100%` `唯一` `顶级` `最`.
- 医疗类声明：`治愈` `根除` `100%有效`.

## 去AI味规则

### 禁止使用的AI高频词
```
此外 至关重要 深入探讨 强调 值得注意的是 值得一提的是
不可忽视的是 格局 展示 充满活力的 各种 备受
不仅……而且…… 综上所述 总而言之 在这个……的时代
随着……的发展 让我们拭目以待 未来可期
```

### 交付前自检清单
输出内容前逐项检查：
- [ ] 连续三个句子长度是否相同？打断其中一个
- [ ] 是否使用了"此外""然而""值得注意的是"？删除之
- [ ] 是否出现了三段式排比？改为两项或四项
- [ ] 每200字是否有至少一个具体数字/场景/感受？
- [ ] 是否出现了"不仅……而且……"？改为直接陈述
- [ ] "的"的使用频率：每句不超过2个
- [ ] 结尾是否模板化？用具体结论替代套话
- [ ] **品牌植入是否为软植入风格（个人经验/他人推荐/行业洞察）？**
- [ ] **是否包含 `#戴恩科技` 和 `#智能护理` 标签？**
- [ ] **brand_placement 是否填写完整（style, product_mentioned, placement_text）？**
