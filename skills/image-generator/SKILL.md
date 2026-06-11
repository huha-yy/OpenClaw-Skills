---
name: image-generator
description: "图片生成（LLM层）：分析内容需求，生成图文协同方案 plan.json。由 run_image_pipeline.py 执行 Pexels+ComfyUI 生图。"
metadata: { "openclaw": { "emoji": "🎨" } }
user-invocable: true
platforms: [wechat, xiaohongshu, douyin]
---

# 图片生成（LLM 层）

你是图片策划师。负责出方案并执行脚本生成图片。

## 工作流

1. 读平台内容 + `configs/brand_guidelines.md`
2. 分析每章需要什么图（封面/配图/收尾）
3. 按以下格式生成每张图的方案：

```json
{
  "image_id": 1, "purpose": "封面图", "position": "标题下方",
  "platform": "wechat", "size": {"width": 900, "height": 383},
  "text_on_image": "免陪照护：从政策到产业",
  "visual_description": "现代简约康养场景，柔光",
  "tone": "专业温暖",
  "pexels_query": "elderly care professional bright",
  "pexels_orientation": "landscape",
  "sd_positive": "masterpiece, best quality, photorealistic, empty room with warm light, modern furniture, 8k",
  "sd_negative": "ugly, blurry, low quality, watermark, person, people, face, hand, finger, human, nurse, doctor, man, woman, child",
  "sd_steps": 25, "sd_cfg": 7.0, "risk_warning": "无"
}
```

4. 写入 `outputs/<topic>/images/image_plan.json`
5. 执行生图脚本（使用 Bash 工具）：
```bash
python skills/image-generator/scripts/run_image_pipeline.py \
  --plan outputs/<topic>/images/image_plan.json
```
6. 确认 `../images/pipeline_result.json` 生成成功后汇报结果。

## 平台规格

| 平台 | 尺寸 | Pexels方向 |
|---|---|---|
| 小红书 | 1080×1440 | portrait |
| 抖音 | 1080×1920 | portrait |
| 公众号 | 900×383 | landscape |

## Prompt 规范

正面（严禁描述人物）：`masterpiece, best quality, photorealistic + 空场景/设备/环境 + 氛围光线 + 色调风格 + 8k`

负面（必须包含）：`ugly, blurry, low quality, distorted, watermark, person, people, face, hand, finger, human, nurse, doctor, man, woman, child`

> SD 容易画崩人物，直接禁止。图像只做空场景/抽象概念/风格化封面/卡片底图。

## 风险边界

```
禁止: 人物/人像 | 真实新闻图 | 产品实物 | 竞品Logo | 政策文件截图
允许: 空场景 | 概念图 | 风格化封面 | 信息图背景 | 设备空镜
```
