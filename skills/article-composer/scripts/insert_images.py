#!/usr/bin/env python3
"""
图文编排执行层 —— 读取 pipeline_result.json，按 purpose 关键词匹配文章章节，
将图片以 `![purpose](../images/file.png)` 格式插入到对应位置。

LLM 负责语义匹配（出 JSON 映射），脚本负责确定性插入。
如果未提供 mapping JSON，脚本使用内置关键词规则自动匹配。

用法:
  python insert_images.py --pipeline <pipeline_result.json> \
      --article <article.md> --output-dir <images_relative_dir>

示例:
  python insert_images.py \
      --pipeline outputs/AI助力养老/images/pipeline_result.json \
      --article outputs/AI助力养老/publish_package/wechat/article.md
"""

import os
import re
import sys
import json
import argparse

# 章节标题匹配: 匹配 markdown heading 和 emoji 标题行
_HEADING_RE = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)
# 小红书/抖音风格: emoji + 文本标题 (如 "📍 场景1：..." "📊 几个关键数字")
_XHS_HEADING_RE = re.compile(
    r"^(?:[^\x00-\x7F#\-\*\d])(?:[^\x00-\x7F])?\s{1,3}(.+)$", re.MULTILINE
)

# pipeline_result.json 的 "(N bytes)" 后缀
_SIZE_SUFFIX_RE = re.compile(r"^(.*?)\s*\(\d+\s*bytes\)\s*$")

# 图片 markdown tag
_IMG_TAG_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)$", re.MULTILINE)


def clean_filename(file_path):
    """从 pipeline_result.json 的 file 字段提取干净文件名。"""
    m = _SIZE_SUFFIX_RE.match(file_path.strip())
    return m.group(1).strip() if m else file_path.strip()


def load_images(pipeline_path, platform=None):
    """读取 pipeline_result.json，返回图片列表。

    platform: 可选平台过滤 ("wechat", "xiaohongshu", "douyin")。
              匹配规则：purpose 包含平台关键词（公众号/小红书/抖音/wechat/xhs/douyin）。
    """
    with open(pipeline_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    PLATFORM_KW = {
        "wechat": ["公众号", "wechat"],
        "xiaohongshu": ["小红书", "xiaohongshu", "xhs"],
        "douyin": ["抖音", "douyin"],
    }
    kw_list = PLATFORM_KW.get(platform, []) if platform else []

    images = []
    for r in data.get("results", []):
        fp = clean_filename(r.get("file", ""))
        purpose = r.get("purpose", "")
        if fp:
            # 平台过滤
            if kw_list and not any(kw in purpose for kw in kw_list):
                continue
            images.append({
                "file": fp,
                "filename": os.path.basename(fp),
                "purpose": purpose,
                "image_id": r.get("image_id", 0),
            })
    return images


# ---------------------------------------------------------------------------
# 关键词匹配规则
# ---------------------------------------------------------------------------

MATCH_RULES = [
    (["封面", "头图", "首图"], "title"),
    (["政策", "监管", "背景", "补贴", "发文"], "政策"),
    (["数据", "趋势", "统计", "报告", "关键数字"], "数据"),
    (["案例", "实操", "落地", "实践", "试点", "场景"], "案例"),
    (["费用", "收费", "价格", "模式", "盈利"], "模式"),
    (["品牌", "收尾", "总结", "结语", "展望", "感受"], "结尾"),
    (["监测", "机器人", "远程", "医疗", "设备", "外骨骼", "轮椅", "雷达"], "技术"),
    (["交互", "语音", "管家", "AI管家", "健康管理", "服务找人"], "智能"),
    (["场景", "场景1", "场景2", "场景3", "场景4", "场景5"], "案例"),
]


def find_section_positions(text):
    """解析文章章节标题及其在文本中的位置。返回 [(level, title, start, end), ...]

    支持两种格式:
      1. Markdown: # / ## / ### 标题
      2. 小红书: emoji/符号 + 标题 (如 📍 场景1：...)
    """
    sections = []

    # Markdown heading
    for m in _HEADING_RE.finditer(text):
        level = len(m.group(1))
        title = m.group(2).strip()
        sections.append((level, title, m.start(), m.end()))

    # XHS emoji/symbol heading (lower "level" than markdown, so use 4)
    for m in _XHS_HEADING_RE.finditer(text):
        title = m.group(1).strip()
        if title and len(title) > 1:
            sections.append((4, title, m.start(), m.end()))

    sections.sort(key=lambda s: s[2])  # sort by position
    return sections


def match_image_to_section(purpose, sections):
    """根据 purpose 关键词匹配最合适的章节。返回该章节的 end 位置。"""
    # 找到匹配规则
    matched_keyword = None
    for keywords, _ in MATCH_RULES:
        for kw in keywords:
            if kw in purpose:
                matched_keyword = keywords
                break
        if matched_keyword:
            break

    if not matched_keyword:
        # 默认：放摘要下方或第一段后
        return None, "摘要下方"

    # 在章节标题中搜索匹配
    for level, title, start, end in sections:
        for kw in matched_keyword:
            if kw in title:
                return end, title

    return None, f"未匹配（purpose={purpose[:20]}）"


def insert_images_into_text(text, images, sections, images_rel_dir=".."):
    """将图片插入到文章对应位置。返回 (new_text, report_lines)。"""
    report = []
    # 先移除已有的图片标记（幂等）
    text = _IMG_TAG_RE.sub("", text)
    # 清理多余空行
    text = re.sub(r"\n{3,}", "\n\n", text)

    inserted = 0
    skipped = 0
    report_lines = []

    for img in images:
        purpose = img["purpose"]
        filename = img["filename"]
        tag = f"![{purpose}]({images_rel_dir}/{filename})"

        # 封面 → 标题下方（第一个 heading 之后，或第一段之后）
        if any(kw in purpose for kw in ["封面", "头图", "首图"]):
            first_heading = None
            for m in _HEADING_RE.finditer(text):
                first_heading = m.end()
                break
            # XHS: 没有 markdown heading，用第一个 emoji 行或第3行
            if first_heading is None:
                lines = text.split("\n")
                # 找第一个非空行之后的位置（标题行后）
                non_empty = 0
                for idx, line in enumerate(lines):
                    if line.strip():
                        non_empty += 1
                        if non_empty == 2:  # 标题行后第一段前
                            first_heading = sum(len(l) + 1 for l in lines[:idx+1])
                            break
            if first_heading:
                before = text[:first_heading]
                after = text[first_heading:]
                text = before + f"\n\n{tag}\n" + after
                inserted += 1
                report_lines.append(f"  [{img['image_id']}] {purpose} → 标题下方")
                continue

        # 其他 → 按关键词匹配章节
        pos, section_title = match_image_to_section(purpose, sections)
        if pos is not None:
            lines = text.split("\n")
            # 找到 pos 对应的行号
            char_count = 0
            line_idx = 0
            for i, line in enumerate(lines):
                char_count += len(line) + 1  # +1 for newline
                if char_count > pos:
                    line_idx = i
                    break

            # 在章节标题后的第一行插入
            insert_at = line_idx + 1
            # 跳过空行
            while insert_at < len(lines) and lines[insert_at].strip() == "":
                insert_at += 1
            lines.insert(insert_at, "")
            lines.insert(insert_at, tag)
            text = "\n".join(lines)
            inserted += 1
            report_lines.append(f"  [{img['image_id']}] {purpose} → {section_title}")
        else:
            # 无法匹配，放摘要下方
            inserted_tag = False
            for m in _HEADING_RE.finditer(text):
                if "摘要" in m.group(2):
                    before = text[:m.end()]
                    after = text[m.end():]
                    text = before + f"\n\n{tag}" + after
                    inserted += 1
                    inserted_tag = True
                    report_lines.append(f"  [{img['image_id']}] {purpose} → 摘要下方（默认）")
                    break
            if not inserted_tag:
                skipped += 1
                report_lines.append(f"  [{img['image_id']}] {purpose} → 跳过（无匹配位置）")

    # 清理多余空行
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text, report_lines


def main():
    parser = argparse.ArgumentParser(description="图文编排执行层 — 将图片内联到平台文章")
    parser.add_argument("--pipeline", required=True, help="pipeline_result.json 路径")
    parser.add_argument("--article", required=True, help="目标文章 .md 文件路径")
    parser.add_argument("--platform", default=None,
                        choices=["wechat", "xiaohongshu", "douyin"],
                        help="平台过滤（只插入该平台的图片）")
    parser.add_argument("--images-rel-dir", default="../images", help="文章中引用图片的相对目录")
    args = parser.parse_args()

    # 读取图片清单
    images = load_images(args.pipeline, args.platform)
    if not images:
        print("无图片可编排，退出")
        return

    print(f"图片清单: {len(images)} 张")

    # 读取文章
    with open(args.article, "r", encoding="utf-8") as f:
        text = f.read()

    # 解析章节
    sections = find_section_positions(text)
    print(f"文章章节: {len(sections)} 个")

    # 插入
    new_text, report = insert_images_into_text(text, images, sections, args.images_rel_dir)

    # 写回
    with open(args.article, "w", encoding="utf-8") as f:
        f.write(new_text)

    print(f"插入结果: {new_text.count('![')} 个图片标记")
    for line in report:
        print(line)

    # 验证
    tag_count = len(_IMG_TAG_RE.findall(new_text))
    print(f"\n验证: 文章包含 {tag_count} 个 ![...](...) 标记")


if __name__ == "__main__":
    main()
