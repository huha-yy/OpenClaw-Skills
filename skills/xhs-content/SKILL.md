---
name: xhs-content
description: "小红书内容生成：生成标题、正文、标签、图文分镜方案和评论区引导语。"
metadata: { "openclaw": { "emoji": "📕" } }
user-invocable: true
---

# Xiaohongshu Content Generator

Generate complete Xiaohongshu note packages. The key to XHS is **text-image synergy** — every image has a purpose and on-image text.

## Workflow

1. Load XHS style guide from `configs/platform_style_guides/xiaohongshu.md`.
2. Load brand guidelines from `configs/brand_guidelines.md`.
3. Based on the content strategy's XHS angle, generate the full package.

## Input

```json
{
  "hotspot_id": "hs_20260609_001",
  "title": "...",
  "research": { "confirmed_facts": [...], "uncertain_points": [...] },
  "strategy": {
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
  "title": "新能源车补贴又变了？普通消费者最该关注这3点",
  "body": "最近某地发布了新能源车相关补贴政策，很多人第一眼只看补贴金额...",
  "tags": ["#新能源车", "#购车补贴", "#买车攻略"],
  "images": [
    {
      "position": 1,
      "purpose": "封面",
      "on_image_text": "补贴又变了？\n普通人最该关注的3点",
      "visual_description": "简洁的新能源汽车充电场景，暖色调，生活感",
      "corresponding_text": "标题",
      "search_keywords": ["electric car charging", "urban lifestyle", "warm tone"],
      "ai_prompt": "A modern electric car charging at a city charging station, warm sunset lighting, lifestyle photography style, clean composition"
    },
    {
      "position": 2,
      "purpose": "核心观点",
      "on_image_text": "第1点\n适用地区和时间限制",
      "visual_description": "信息卡片风格，浅色背景，突出文字",
      "corresponding_text": "正文第一段",
      "search_keywords": [],
      "ai_prompt": "Clean information card with text overlay, minimalist design, light beige background"
    }
  ],
  "comment_prompt": "你觉得补贴金额重要还是适用条件更重要？评论区聊聊你的看法👇",
  "risk_notes": ["避免使用'全国通用'等绝对化表述"]
}
```

## XHS-specific rules

### 标题规则
- **字数**：8-22字。前13字必须包含核心关键词（搜索权重占40%）。
- **公式**：从以下4个中选1-2个组合：
  1. `[Emoji] + [受众呼唤] + [收益]`  → 学生党必看！宿舍收纳神器
  2. `[否定式警告] + [更好替代]`        → 别买iPad了！这个更香
  3. `[悬念] + [结果]`                  → 坚持了3天，没想到结果...
  4. `[数字] + [过程] + [权威]`         → 3个步骤，HR手把手教你改简历
- **视觉钩子**：必须包含至少1个emoji或感叹号。

### 正文规则
- **字数**：300-600字，短句为主，每段2-3句。
- **结构**：三段式——① 观点段（第一人称，直接亮态度）→ ② 证据段（数据/案例/细节）→ ③ 反方/局限段（边界，增加真实感）。
- **开头钩子**：正文前1-2句必须是高能开篇（情绪、冲突、悬念），不得平淡引入。
- **风格**：日记体优先（互动率最高），其次测评体、教程体。口语化，允许不完美感。
- **CTA**：优先引导关注（CES权重：关注8分 > 评论/转发4分 > 点赞/收藏1分）。

### 标签规则
- 5-8个标签，混合热门（流量）和长尾（精准）。
- **强制加入 `#AI生成内容`**（2026年1月起小红书要求，否则限流）。

### 图片规则
- Every image must have a clear purpose. 5-9 images for a standard note.

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
