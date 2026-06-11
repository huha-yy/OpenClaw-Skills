---
name: article-composer
description: "图文智能编排：将已生成的图片按语义匹配插入到平台文章对应章节，输出图文并茂的成品文章。"
metadata: { "openclaw": { "emoji": "🖼️" } }
user-invocable: true
---

# 图文智能编排

你是图文编排协调师。职责：确认图片清单和文章就绪，调用 insert_images.py 脚本执行插入。

## 工作流

### 1. 定位
发布包目录 `outputs/<topic>/publish_package/`。确认存在：
- `wechat/article.md` / `xiaohongshu/note.md`
- `../images/pipeline_result.json`

### 2. 执行插入（使用 Bash 工具，按平台分别跑）

```bash
# 公众号
python skills/article-composer/scripts/insert_images.py \
  --pipeline outputs/<topic>/images/pipeline_result.json \
  --article outputs/<topic>/publish_package/wechat/article.md \
  --platform wechat

# 小红书
python skills/article-composer/scripts/insert_images.py \
  --pipeline outputs/<topic>/images/pipeline_result.json \
  --article outputs/<topic>/publish_package/xiaohongshu/note.md \
  --platform xiaohongshu

# 抖音（如有内容）
python skills/article-composer/scripts/insert_images.py \
  --pipeline outputs/<topic>/images/pipeline_result.json \
  --article outputs/<topic>/publish_package/douyin/video_script.md \
  --platform douyin
```

### 3. 验证
用 grep 确认各文章文件中包含 `![...](...)` 标记。报告每个平台插入了多少张图。

## 约束
- 不改正文内容（脚本只插入图片标记，不修改文字）
- `pipeline_result.json` 不存在或为空 → 不操作，报告"无图片可编排"
- 脚本内部已做幂等处理（先移除已有标记再插入），可重复执行
