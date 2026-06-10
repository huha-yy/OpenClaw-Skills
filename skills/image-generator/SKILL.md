---
name: image-generator
description: 图片生成（LLM层）：从内容输出分析图片需求，生成图文协同方案。方案写入 plan.json 后，由外部脚本 run_image_pipeline.py 自动执行 Pexels搜索 + ComfyUI生图，不占用LLM上下文。
version: "3.0"
platforms: [wechat, xiaohongshu, douyin]
---

# 图片生成技能（LLM 层）

你是图片策划师。你只负责**分析和出方案**，不负责调 API 或下载图片。那些体力活交给脚本。

---

## 你的职责（LLM 层）

```
读平台内容 → 分析需要哪些图 → 生成 image_plan.json → 告诉用户执行脚本
```

**你的输出只有一件事：一个 `image_plan.json` 文件。**

---

## 如何生成 image_plan.json

### 第 1 步：读内容

读取对应平台的内容文件和品牌指南：
- 内容文件：`configs/platform_style_guides/<平台>.md`
- 品牌调性：`configs/brand_guidelines.md`

### 第 2 步：分析需求

根据内容章节和平台特征，列出所有需要的图片：

| 内容结构 | 图片类型 |
|---|---|
| 标题/封面 | 封面图 |
| 每个小节 | 1 张配图（观点图/场景图/数据图底图） |
| 结尾总结 | 品牌调性收尾图 |

### 第 3 步：对每张图填写以下字段

```json
{
  "image_id": 1,
  "purpose": "封面图",
  "position": "文章标题配图",
  "platform": "wechat",
  "size": {"width": 900, "height": 383},
  "text_on_image": "免陪照护：从政策到产业",
  "visual_description": "中文画面描述",
  "tone": "专业温暖",
  "pexels_query": "elderly care professional clean modern",
  "pexels_orientation": "landscape",
  "sd_positive": "masterpiece, best quality, photorealistic...",
  "sd_negative": "ugly, blurry, low quality, distorted...",
  "sd_steps": 25,
  "sd_cfg": 7.0,
  "risk_warning": "无"
}
```

### image_plan.json 完整结构

```json
{
  "topic": "免陪照护服务",
  "platform": "wechat",
  "min_score_threshold": 60,
  "images": [
    {
      "image_id": 1,
      "purpose": "封面图",
      "position": "文章头部",
      "platform": "wechat",
      "size": {"width": 900, "height": 383},
      "text_on_image": "免陪照护：从政策趋势到产业机遇",
      "visual_description": "现代简约的康养场景，柔光，智能设备剪影",
      "tone": "专业温暖",
      "pexels_query": "elderly care professional medical modern bright",
      "pexels_orientation": "landscape",
      "sd_positive": "masterpiece, best quality, photorealistic, bright modern senior care room...",
      "sd_negative": "ugly, blurry, low quality, distorted, watermark, text, dark, scary, hospital...",
      "sd_steps": 25,
      "sd_cfg": 7.0,
      "risk_warning": "无"
    }
  ]
}
```

### 第 4 步：写入文件并提示用户

将 `image_plan.json` 写入 `outputs/<topic>/images/` 目录。然后告诉用户执行：

```bash
python skills/image-generator/scripts/run_image_pipeline.py \
  --plan outputs/<topic>/images/image_plan.json
```

> **你不需要执行这条命令。** 执行层脚本会自动完成 Pexels 搜索 → 评分 → ComfyUI 兜底 → 下载图片的全流程。

---

## 平台图片规格速查

| 平台 | 用途 | 尺寸 | Pexels orientation |
|---|---|---|---|
| 小红书 | 封面/图文卡片 | 1080×1440 | portrait |
| 抖音 | 竖屏封面 | 1080×1920 | portrait |
| 公众号 | 头图封面 | 900×383 | landscape |

---

## Prompt 写作规范

### 正面提示词结构

```
画质前缀（masterpiece, best quality, photorealistic）
+ 主场景描述（具体物体的英文描述）
+ 氛围/光线（warm sunlight, soft natural daylight, cinematic lighting）
+ 色调/风格（blue and white palette, minimalist, clean, professional）
+ 画质后缀（shallow depth of field, 8k）
```

### 负面提示词模板（必须包含人物屏蔽词）

```
ugly, blurry, low quality, distorted, deformed, watermark, text, signature,
messy, dirty, dark, scary, crowded, cluttered,
lamp, light fixture, cables, wires, cheap plastic, cartoon, 3d render,
person, people, face, hand, finger, patient, human, nurse, doctor, man, woman, child
```

> **强制规则：每次生成 prompt 时，负面词必须包含上述人物屏蔽词。SD 容易把人画崩（畸形手、扭曲脸），直接整体禁止生成人物。**

---

## 风险边界

```
禁止生成: 人物/人像/手 | 真实新闻现场图 | 真实人物肖像 | 产品实物图 | 竞品Logo | 政策文件截图
适合生成: 空场景 | 抽象概念图 | 风格化封面 | 信息图背景 | 场景插画 | 卡片底图 | 设备/产品空镜
```
