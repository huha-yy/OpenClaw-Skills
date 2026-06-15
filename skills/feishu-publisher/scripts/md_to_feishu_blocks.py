#!/usr/bin/env python3
"""
Markdown → 飞书块转换器。

将 Markdown 文本按行解析为飞书 Doc 的 block 数组（JSON 格式）。
支持: 标题(h1-h3)、段落、加粗、行内代码、无序列表、有序列表、代码块、引用、分割线、
      表格(降级为代码块)、图片(block_type=27，_file_path 占位等待上传阶段解析)。

用法:
  from md_to_feishu_blocks import md_to_blocks
  blocks = md_to_blocks(markdown_text)

飞书块类型速查:
  2=text  3=heading1  4=heading2  5=heading3
  12=bullet  13=ordered  14=code  15=quote  22=divider  27=image
"""

import re
import sys

# ---------------------------------------------------------------------------
# 内联样式解析
# ---------------------------------------------------------------------------

_BOLD_RE = re.compile(r"\*\*(.+?)\*\*")
_INLINE_CODE_RE = re.compile(r"`([^`]+)`")


def _parse_inline(text):
    """
    将一行文本中的 **bold** 和 `code` 转换为飞书 text_run 数组。

    返回 list[dict]：
        [{"text_run": {"content": "...", "text_element_style": {}}}]
    """
    if not text:
        return [{"text_run": {"content": "", "text_element_style": {}}}]

    # 先把两个正则的匹配位置都找出来，然后按位置排序合并
    tokens = []

    for m in _BOLD_RE.finditer(text):
        tokens.append((m.start(), m.end(), "bold", m.group(1)))

    for m in _INLINE_CODE_RE.finditer(text):
        tokens.append((m.start(), m.end(), "code", m.group(1)))

    if not tokens:
        return [{"text_run": {"content": text, "text_element_style": {}}}]

    # 按位置排序，处理冲突（重叠取先出现的）
    tokens.sort(key=lambda x: (x[0], -x[1]))  # 长匹配优先

    # 去重叠
    filtered = []
    last_end = 0
    for start, end, kind, content in tokens:
        if start < last_end:
            continue
        filtered.append((start, end, kind, content))
        last_end = end

    # 按位置构建 text_run 数组
    elements = []
    pos = 0
    for start, end, kind, content in filtered:
        # 前面普通文本
        if start > pos:
            elements.append({
                "text_run": {
                    "content": text[pos:start],
                    "text_element_style": {},
                }
            })

        # 样式文本
        style = {}
        if kind == "bold":
            style["bold"] = True
        elif kind == "code":
            style["inline_code"] = True

        elements.append({
            "text_run": {
                "content": content,
                "text_element_style": style,
            }
        })
        pos = end

    # 尾部普通文本
    if pos < len(text):
        elements.append({
            "text_run": {
                "content": text[pos:],
                "text_element_style": {},
            }
        })

    return elements


# ---------------------------------------------------------------------------
# 块构建辅助
# ---------------------------------------------------------------------------

def _make_text_block(text):
    """构建 text 块 (block_type=2)。"""
    return {
        "block_type": 2,
        "text": {
            "elements": _parse_inline(text),
        },
    }


def _make_heading_block(level, text):
    """构建 heading 块 (block_type=3/4/5)。"""
    key = {1: "heading1", 2: "heading2", 3: "heading3"}[level]
    return {
        "block_type": 2 + level,  # 3=heading1, 4=heading2, 5=heading3
        key: {
            "elements": _parse_inline(text),
        },
    }


def _make_bullet_block(text):
    """构建 bullet 块 (block_type=12)。"""
    return {
        "block_type": 12,
        "bullet": {
            "elements": _parse_inline(text),
        },
    }


def _make_ordered_block(text):
    """构建 ordered 块 (block_type=13)。"""
    return {
        "block_type": 13,
        "ordered": {
            "elements": _parse_inline(text),
        },
    }


def _make_code_block(lines):
    """构建 code 块 (block_type=14)。"""
    # code 块不需要 rich text elements，直接传 content 字符串
    content = "\n".join(lines)
    return {
        "block_type": 14,
        "code": {
            "elements": [
                {"text_run": {"content": content, "text_element_style": {}}}
            ],
        },
    }


def _make_quote_block(text):
    """构建 quote 块 (block_type=15)。"""
    return {
        "block_type": 15,
        "quote": {
            "elements": _parse_inline(text),
        },
    }


def _make_divider_block():
    """构建 divider 块 (block_type=22)。"""
    return {
        "block_type": 22,
        "divider": {},
    }


def _make_image_block(file_path, alt_text, width=800):
    """构建 image 块 (block_type=27)，用 _file_path 存本地路径待上传阶段解析。

    上传阶段 resolve_and_upload_images() 会扫描 _file_path，
    上传图片后将 _file_path 替换为飞书 image_key token。

    默认宽度 800px（飞书文档内合适尺寸）。封面图宽度保持 0（原始全宽）。
    """
    return {
        "block_type": 27,
        "image": {
            "_file_path": file_path,
            "alt": alt_text,
            "width": width,
            "height": 0,
        },
    }


# ---------------------------------------------------------------------------
# 表格 → 代码块降级
# ---------------------------------------------------------------------------

def _table_to_code_block(lines):
    """将表格行转为代码块（降级策略）。"""
    return _make_code_block(lines)


# ---------------------------------------------------------------------------
# 主解析器：行级状态机
# ---------------------------------------------------------------------------

def md_to_blocks(text):
    """
    将 Markdown 文本解析为飞书 blocks 列表。

    参数:
        text: str — 完整 Markdown 文本

    返回:
        list[dict] — 飞书 block 对象数组
    """
    lines = text.split("\n")
    blocks = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # 空行
        if not line.strip():
            i += 1
            continue

        # 代码块 ```...```
        if line.strip().startswith("```"):
            code_lines = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # 跳过结束 ```
            blocks.append(_make_code_block(code_lines))
            continue

        # 表格 | ... |
        if line.strip().startswith("|") and line.strip().endswith("|"):
            table_lines = []
            while i < n and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                table_lines.append(lines[i])
                i += 1
            # 过滤分隔行 |---|---|
            filtered = [
                tl for tl in table_lines
                if not re.match(r"^\|[\s\-:|]+\|$", tl.strip())
            ]
            if filtered:
                blocks.append(_table_to_code_block(filtered))
            continue

        # 分割线 --- / *** / ___
        if re.match(r"^[-*_]{3,}\s*$", line.strip()):
            blocks.append(_make_divider_block())
            i += 1
            continue

        # 标题 # ## ###
        heading_match = re.match(r"^(#{1,3})\s+(.+)$", line)
        if heading_match:
            level = len(heading_match.group(1))
            heading_text = heading_match.group(2).strip()
            blocks.append(_make_heading_block(level, heading_text))
            i += 1
            continue

        # 无序列表 - 或 *
        bullet_match = re.match(r"^[-*]\s+(.+)$", line)
        if bullet_match:
            blocks.append(_make_bullet_block(bullet_match.group(1).strip()))
            i += 1
            continue

        # 有序列表 1. 2.
        ordered_match = re.match(r"^\d+[.)]\s+(.+)$", line)
        if ordered_match:
            blocks.append(_make_ordered_block(ordered_match.group(1).strip()))
            i += 1
            continue

        # 引用 >
        quote_match = re.match(r"^>\s?(.*)$", line)
        if quote_match:
            blocks.append(_make_quote_block(quote_match.group(1).strip()))
            i += 1
            continue

        # 图片 ![alt](path)
        image_match = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)$", line)
        if image_match:
            alt_text = image_match.group(1).strip()
            img_path = image_match.group(2).strip()
            # 封面图保持原始全宽
            if "封面" in alt_text:
                blocks.append(_make_image_block(img_path, alt_text, width=0))
            else:
                blocks.append(_make_image_block(img_path, alt_text))
            i += 1
            continue

        # 普通段落：收集连续非空行，用空格拼接
        para_lines = []
        while i < n and lines[i].strip() and not lines[i].strip().startswith("|"):
            stripped = lines[i].strip()
            # 只有 # + 空格才算标题，避免误拦 #tag 类内容
            if (re.match(r"^#{1,3}\s+", stripped) or stripped.startswith("```") or
                stripped.startswith("- ") or stripped.startswith("* ") or
                re.match(r"^\d+[.)]\s+", stripped) or
                stripped.startswith("> ") or
                re.match(r"^[-*_]{3,}\s*$", stripped)):
                break
            para_lines.append(lines[i])
            i += 1

        if para_lines:
            para_text = " ".join(p.strip() for p in para_lines)
            blocks.append(_make_text_block(para_text))

    return blocks


# ---------------------------------------------------------------------------
# 分块工具：按 50 个 block 切分
# ---------------------------------------------------------------------------

CHUNK_SIZE = 50


def chunk_blocks(blocks, chunk_size=CHUNK_SIZE):
    """将 blocks 列表按 chunk_size 切片。"""
    for i in range(0, len(blocks), chunk_size):
        yield blocks[i:i + chunk_size]


# ---------------------------------------------------------------------------
# 入口（调试用）
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    sample = """\
# 一级标题

这是普通段落，带有 **加粗** 和 `行内代码`。

## 二级标题

- 无序列表项
- 另一项

1. 有序第一
2. 有序第二

> 引用文字

---

```
print("hello world")
```

| 列A | 列B |
|-----|-----|
| 值1 | 值2 |
"""

    blocks = md_to_blocks(sample)
    print(f"Parsed {len(blocks)} blocks:")
    print(json.dumps(blocks, ensure_ascii=False, indent=2))
