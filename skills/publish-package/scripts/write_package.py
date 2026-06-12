#!/usr/bin/env python3
"""
发布包文件写入工具 —— 将流水线产物写入标准化的 outputs/<topic>/ 目录结构。

用法:
  python write_package.py --input input.json --output-dir outputs/2026-06-12_topic_slug/

输入:
  上游汇总的 JSON，包含 monitor/relevance/research/strategy/content/compliance 各环节输出。
输出:
  标准化发布包目录，含各平台 article.md / note.md / package_summary.md 等。
"""

import json
import os
import sys
import argparse


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def write_text_file(path, content):
    """写入文本文件，自动创建父目录"""
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        f.write(content if isinstance(content, str) else json.dumps(content, ensure_ascii=False, indent=2))
    return path


def write_json_file(path, data):
    """写入JSON文件"""
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path


def write_package(input_data, output_dir):
    """写入完整发布包结构"""
    ensure_dir(output_dir)

    files_written = []

    # sources.json
    sources = input_data.get("monitor", {})
    path = write_json_file(os.path.join(output_dir, "sources.json"), sources)
    files_written.append(path)

    # event_analysis.md
    research = input_data.get("research", {})
    relevance = input_data.get("relevance", {})
    event_text = f"# {input_data.get('title', 'Hotspot Analysis')}\n\n"
    event_text += f"## 相关性评估\n\n评分: {relevance.get('score', 'N/A')}/100\n"
    event_text += f"类型: {relevance.get('type', 'N/A')}\n\n"
    event_text += f"## 事实核验\n\n{json.dumps(research, ensure_ascii=False, indent=2)}\n"
    path = write_text_file(os.path.join(output_dir, "event_analysis.md"), event_text)
    files_written.append(path)

    # risk_report.md
    compliance = input_data.get("compliance", {})
    risk_text = f"# 合规审核报告\n\n风险等级: {compliance.get('overall_risk', 'N/A')}\n"
    risk_text += f"\n{json.dumps(compliance, ensure_ascii=False, indent=2)}\n"
    path = write_text_file(os.path.join(output_dir, "risk_report.md"), risk_text)
    files_written.append(path)

    # 各平台内容
    content = input_data.get("content", {})
    strategy = input_data.get("strategy", {})

    for platform in ["wechat", "xiaohongshu", "douyin"]:
        platform_data = content.get(platform)
        if not platform_data:
            continue

        platform_dir = os.path.join(output_dir, platform)
        ensure_dir(platform_dir)

        if platform == "wechat":
            article = platform_data.get("article", platform_data.get("body", ""))
            path = write_text_file(os.path.join(platform_dir, "article.md"), article)
            files_written.append(path)

            cover = platform_data.get("cover", {})
            if cover:
                cover_text = json.dumps(cover, ensure_ascii=False, indent=2)
                path = write_text_file(os.path.join(platform_dir, "cover.md"), cover_text)
                files_written.append(path)

        elif platform == "xiaohongshu":
            note = platform_data.get("note", platform_data.get("body", ""))
            path = write_text_file(os.path.join(platform_dir, "note.md"), note)
            files_written.append(path)

            storyboard = platform_data.get("image_storyboard", platform_data.get("images", []))
            if isinstance(storyboard, list):
                storyboard_text = json.dumps(storyboard, ensure_ascii=False, indent=2)
            else:
                storyboard_text = str(storyboard)
            path = write_text_file(os.path.join(platform_dir, "image_storyboard.md"), storyboard_text)
            files_written.append(path)

        elif platform == "douyin":
            script = platform_data.get("video_script", platform_data.get("body", ""))
            path = write_text_file(os.path.join(platform_dir, "video_script.md"), script)
            files_written.append(path)

            storyboard = platform_data.get("storyboard", [])
            if isinstance(storyboard, list):
                storyboard_text = json.dumps(storyboard, ensure_ascii=False, indent=2)
            else:
                storyboard_text = str(storyboard)
            path = write_text_file(os.path.join(platform_dir, "storyboard.md"), storyboard_text)
            files_written.append(path)

        # publish_meta.json
        meta = platform_data.get("publish_meta", {})
        if not meta:
            meta = {
                "platform": platform,
                "angle": strategy.get(platform, {}).get("angle", ""),
                "generated_at": input_data.get("timestamp", ""),
            }
        path = write_json_file(os.path.join(platform_dir, "publish_meta.json"), meta)
        files_written.append(path)

    # package_summary.md
    title = input_data.get("title", "Untitled")
    relevance_score = relevance.get("score", "N/A")
    relevance_type = relevance.get("type", "N/A")
    risk_level = compliance.get("overall_risk", "N/A")

    summary = f"""# {title}

**生成时间:** {input_data.get('timestamp', 'N/A')}
**相关性:** {relevance_type} ({relevance_score}/100)
**风险等级:** {risk_level}

## 热点摘要
{research.get('summary', research.get('confirmed_facts', ['待补充']))}

## 内容概览

| 平台 | 角度 | 状态 |
|------|------|------|
| 小红书 | {strategy.get('xiaohongshu', {}).get('angle', 'N/A')} | 待审核 |
| 抖音 | {strategy.get('douyin', {}).get('angle', 'N/A')} | 待审核 |
| 公众号 | {strategy.get('wechat', {}).get('angle', 'N/A')} | 待审核 |

## 审核重点
- 人工核查事实准确性
- 品牌口径一致性确认

## 下一步
人工审核各平台内容，确认事实准确性和品牌口径后发布。
"""
    path = write_text_file(os.path.join(output_dir, "package_summary.md"), summary)
    files_written.append(path)

    return files_written


def main():
    parser = argparse.ArgumentParser(description="发布包文件写入工具")
    parser.add_argument("--input", required=True, help="上游汇总 JSON 文件路径")
    parser.add_argument("--output-dir", required=True, help="输出目录（如 outputs/2026-06-12_xxx/）")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    files = write_package(input_data, args.output_dir)

    print(f"  Written {len(files)} files to {args.output_dir}:")
    for fp in files:
        print(f"    {os.path.relpath(fp, args.output_dir)}")


if __name__ == "__main__":
    main()
