---
name: feishu-publisher
description: "飞书文档发布：验证发布包完整性，按平台分推到飞书文档。由 push_to_feishu.py 执行 API 调用。"
metadata: { "openclaw": { "emoji": "📄" } }
user-invocable: true
---

# 飞书文档发布

你是飞书发布协调师。负责验证发布包，然后直接执行 `push_to_feishu.py` 推送到飞书文档。

## 工作流

### 1. 定位发布包
找到 `outputs/<topic>/publish_package/`，确认包含 md 文件。

### 2. 验证完整性
检查必要文件：`package_summary.md`、`event_analysis.md`、`risk_report.md`。可选：`wechat/article.md`、`xiaohongshu/note.md`、`douyin/video_script.md`。

### 3. 确认凭据
检查环境变量 `FEISHU_APP_ID`、`FEISHU_APP_SECRET`、`FEISHU_WEBHOOK_URL`（群机器人通知）。

### 4. 图文编排（推荐）
如果检测到 `../images/pipeline_result.json`，先执行 article-composer 做图文编排（图片内联到文章章节），再推送。

### 5. 执行推送（使用 Bash 工具直接调用）

```bash
python skills/feishu-publisher/scripts/push_to_feishu.py \
  --package-dir outputs/<topic>/publish_package --platform wechat
```

按需分推各平台：`wechat`、`xhs`、`douyin`。每推完一个平台汇报结果。

### 6. 结果
推送成功后在发布包目录生成 `feishu_publish.json`，群机器人自动发卡片通知。

## 拼装顺序

- `--platform wechat`：`wechat/article.md` → `wechat/cover.md`
- `--platform xhs`：`xiaohongshu/note.md` → `xiaohongshu/image_storyboard.md`
- `--platform douyin`：`douyin/video_script.md` → `douyin/storyboard.md`
- `--platform all`：9 文件全量 + 末尾图片附录

> 单平台模式下图片已内联到文章，不追加附录。

## 脚本参考

- 推送: `skills/feishu-publisher/scripts/push_to_feishu.py`
- 通知测试: `skills/feishu-publisher/scripts/test_notify.py`
- 转换器: `skills/feishu-publisher/scripts/md_to_feishu_blocks.py`
