#!/usr/bin/env python3
"""
飞书发布主脚本 —— 读取发布包目录下的 md 文件，按顺序拼接为一篇飞书 Doc
并推送到飞书。支持 Markdown 图片语法 `![alt](path)` 和自动图片附录。
支持按平台分推（公众号 / 小红书 / 抖音 / 全量）。

用法:
  # 干跑测试（只验证转换逻辑，不调 API）
  python push_to_feishu.py --package-dir outputs/免陪照护_全链路2/ --dry-run

  # 真实推送（全量发布包）
  python push_to_feishu.py --package-dir outputs/免陪照护_全链路2/ --title "免陪照护服务 - 内容发布包"

  # 单平台推送（公众号文章，含内联图片）
  python push_to_feishu.py --package-dir outputs/免陪照护_全链路2/ --platform wechat

  # 单平台推送（小红书笔记，含内联图片）
  python push_to_feishu.py --package-dir outputs/免陪照护_全链路2/ --platform xhs

环境变量:
  FEISHU_APP_ID     飞书应用 App ID
  FEISHU_APP_SECRET 飞书应用 App Secret

依赖: 无外部 pip 依赖（全部使用标准库）
"""

import os
import re
import sys
import json
import time
import argparse
import urllib.request
import urllib.error

# 确保能 import 同目录模块
SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from feishu_auth import FeishuAuth
from md_to_feishu_blocks import md_to_blocks, _make_divider_block, chunk_blocks

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# 飞书 API 端点
# ---------------------------------------------------------------------------
FEISHU_BASE = "https://open.feishu.cn/open-apis"
CREATE_DOC_URL = f"{FEISHU_BASE}/docx/v1/documents"
GET_DOC_INFO_URL = f"{FEISHU_BASE}/docx/v1/documents/{{doc_id}}"
DRIVE_UPLOAD_URL = f"{FEISHU_BASE}/drive/v1/medias/upload_all"
IM_MESSAGE_URL = f"{FEISHU_BASE}/im/v1/messages?receive_id_type=open_id"

# 推完后的私聊通知（改为你的 open_id）
NOTIFY_OPEN_ID = "ou_165b23847a9da512d815a88e09fb8d89"

# 频率控制: 最少间隔秒数 (3 req/s → ~0.33s per req)
MIN_REQ_INTERVAL = 0.34
_last_request_time = 0.0

# 单平台推送文件列表
PLATFORM_FILES = {
    "wechat": ["wechat/article.md", "wechat/cover.md"],
    "xhs": ["xiaohongshu/note.md", "xiaohongshu/image_storyboard.md"],
    "douyin": ["douyin/video_script.md", "douyin/storyboard.md"],
}

# 平台名称后缀（用于文档标题）
PLATFORM_SUFFIX = {
    "wechat": "公众号文章",
    "xhs": "小红书笔记",
    "douyin": "抖音视频",
    "all": "内容发布包",
}


def rate_limit():
    """频率控制：确保两次请求之间至少间隔 MIN_REQ_INTERVAL 秒。"""
    global _last_request_time
    now = time.time()
    diff = now - _last_request_time
    if diff < MIN_REQ_INTERVAL:
        time.sleep(MIN_REQ_INTERVAL - diff)
    _last_request_time = time.time()


# ---------------------------------------------------------------------------
# 飞书 API 调用
# ---------------------------------------------------------------------------

def api_call(method, url, auth, body=None):
    """通用飞书 API 调用，自动附带 token 和频率控制。"""
    rate_limit()

    headers = {
        "Authorization": f"Bearer {auth.get_token()}",
        "Content-Type": "application/json; charset=utf-8",
        "User-Agent": "OpenClaw-FeishuPublisher/1.0",
    }

    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        return {"code": e.code, "msg": err_body}


def create_document(title, auth):
    """
    创建飞书 Doc 文档。

    返回: (document_id, doc_url) 或 (None, error_str)
    """
    body = {"title": title}
    resp = api_call("POST", CREATE_DOC_URL, auth, body)

    if resp.get("code") != 0:
        return None, f"创建文档失败: code={resp.get('code')} msg={resp.get('msg')}"

    doc = resp.get("data", {}).get("document", {})
    doc_id = doc.get("document_id", "")
    doc_url = doc.get("url", f"https://bytedance.feishu.cn/docx/{doc_id}")

    return doc_id, doc_url


def add_blocks(doc_id, parent_block_id, blocks, auth):
    """
    向飞书文档添加子块。

    参数:
        doc_id: str            — 文档 ID
        parent_block_id: str   — 父块 ID（添加顶级块时用 doc_id）
        blocks: list[dict]     — 要添加的 block 数组
        auth: FeishuAuth

    返回: (success: bool, result: list|str)
        成功时 result 为创建后的 children 列表（含 block_id），
        失败时 result 为错误描述字符串。
    """
    url = f"{FEISHU_BASE}/docx/v1/documents/{doc_id}/blocks/{parent_block_id}/children"
    body = {
        "children": blocks,
        "index": -1,  # 追加到末尾
    }
    resp = api_call("POST", url, auth, body)

    if resp.get("code") != 0:
        return False, f"添加块失败: code={resp.get('code')} msg={resp.get('msg')}"

    children = resp.get("data", {}).get("children", [])
    return True, children


# ---------------------------------------------------------------------------
# 图片路径解析与上传（三步法：建空块→Drive上传→PATCH更新）
# ---------------------------------------------------------------------------

def _resolve_image_path(file_path, package_dir):
    """解析图片文件路径，返回存在的绝对路径或 None。"""
    candidate_paths = [
        os.path.normpath(os.path.join(package_dir, file_path)),
        os.path.normpath(os.path.join(package_dir, "..", "images", os.path.basename(file_path))),
        os.path.normpath(file_path),
    ]
    for p in candidate_paths:
        if os.path.isfile(p):
            return p
    return None


def _upload_to_drive(file_path, block_id, auth):
    """Drive API 上传图片到文档图片块，返回 file_token 或 None。

    POST /drive/v1/medias/upload_all
    parent_type=docx_image, parent_node=<block_id>
    """
    url = DRIVE_UPLOAD_URL
    file_size = os.path.getsize(file_path)
    file_name = os.path.basename(file_path)

    with open(file_path, "rb") as f:
        img_data = f.read()

    boundary = f"----FormBoundary{int(time.time() * 1000)}"

    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file_name"\r\n\r\n'
        f"{file_name}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="parent_type"\r\n\r\n'
        f"docx_image\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="parent_node"\r\n\r\n'
        f"{block_id}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="size"\r\n\r\n'
        f"{file_size}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{file_name}"\r\n'
        f"Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8") + img_data + f"\r\n--{boundary}--\r\n".encode("utf-8")

    rate_limit()
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {auth.get_token()}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "User-Agent": "OpenClaw-FeishuPublisher/1.0",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            if result.get("code") != 0:
                print(f"  WARNING: Drive 上传失败 {file_path}: "
                      f"code={result.get('code')} msg={result.get('msg')}", file=sys.stderr)
                return None
            return result["data"]["file_token"]
    except Exception as e:
        print(f"  WARNING: Drive 上传异常 {file_path}: {e}", file=sys.stderr)
        return None


def _patch_image_block(doc_id, block_id, file_token, auth):
    """PATCH 更新图片块，将 file_token 挂入 replace_image。"""
    url = f"{FEISHU_BASE}/docx/v1/documents/{doc_id}/blocks/{block_id}"
    body = {"replace_image": {"token": file_token}}
    resp = api_call("PATCH", url, auth, body)
    return resp.get("code") == 0


def push_chunk_with_images(doc_id, chunk, package_dir, auth):
    """推送一个分块到飞书文档，对图片块使用三步法。

    1. 图片块替换为空 image block，一起推送
    2. 从返回结果提取图片 block_id
    3. Drive API 上传图片到 block_id
    4. PATCH 更新图片块 token

    返回: (success: bool, details: str)
    """
    image_info = []  # [(file_path, block_id), ...]
    clean_chunk = []

    for block in chunk:
        if block.get("block_type") == 27:
            fp = block.get("image", {}).get("_file_path", "")
            image_info.append(fp)
            clean_chunk.append({"block_type": 27, "image": {}})
        else:
            clean_chunk.append(block)

    # 推送整批块
    ok, children_or_err = add_blocks(doc_id, doc_id, clean_chunk, auth)
    if not ok:
        return False, children_or_err

    # 处理图片
    if not image_info:
        return True, "OK"

    children = children_or_err if isinstance(children_or_err, list) else []
    returned_images = [c for c in children if c.get("block_type") == 27]

    upload_ok = 0
    upload_fail = 0
    for fp, img_block in zip(image_info, returned_images):
        block_id = img_block.get("block_id", "")
        if not fp or not block_id:
            continue

        resolved = _resolve_image_path(fp, package_dir)
        if not resolved:
            print(f"  WARNING: 图片文件未找到: {fp}", file=sys.stderr)
            upload_fail += 1
            continue

        # Drive 上传
        file_token = _upload_to_drive(resolved, block_id, auth)
        if file_token is None:
            upload_fail += 1
            continue

        # PATCH 更新块
        if _patch_image_block(doc_id, block_id, file_token, auth):
            upload_ok += 1
        else:
            upload_fail += 1

    if upload_fail > 0:
        return True, f"块已添加，{upload_ok}/{len(image_info)} 张图片上传成功"

    return True, "OK"


# ---------------------------------------------------------------------------
# 图片收集与附录
# ---------------------------------------------------------------------------

_IMAGE_FILE_RE = re.compile(r"^(.*?)\s*\(\d+\s*bytes\)\s*$")


def collect_generated_images(package_dir):
    """检测 ../images/pipeline_result.json，提取已生成图片列表。

    返回: list[dict] 每项 {"file": 完整路径, "filename": 文件名, "purpose": 用途描述}
    """
    pipeline_json = os.path.normpath(
        os.path.join(package_dir, "..", "images", "pipeline_result.json")
    )
    if not os.path.isfile(pipeline_json):
        print("  未找到 pipeline_result.json，跳过图片附录收集")
        return []

    with open(pipeline_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    images = []
    for r in data.get("results", []):
        file_field = r.get("file", "")
        # file 格式: "outputs/...\\openclaw-gen_00020_.png (457218 bytes)"
        m = _IMAGE_FILE_RE.match(file_field.strip())
        if m:
            file_path = m.group(1).strip()
        else:
            file_path = file_field.strip()

        if file_path:
            images.append({
                "file": file_path,
                "filename": os.path.basename(file_path),
                "purpose": r.get("purpose", ""),
            })

    return images


def append_image_appendix(all_blocks, images):
    """在文档末尾追加 divider + heading2"图片附录" + 每张图(purpose + image block)。"""
    if not images:
        return

    all_blocks.append(_make_divider_block())
    all_blocks.append({
        "block_type": 4,  # heading2
        "heading2": {
            "elements": [
                {"text_run": {"content": "图片附录", "text_element_style": {}}}
            ],
        },
    })

    for img in images:
        purpose_text = img.get("purpose", "未命名图片")
        # purpose 加粗说明文字
        all_blocks.append({
            "block_type": 2,
            "text": {
                "elements": [
                    {"text_run": {"content": purpose_text, "text_element_style": {"bold": True}}}
                ],
            },
        })
        # 图片块（_file_path 占位，稍后由 push_chunk_with_images 统一上传）
        all_blocks.append({
            "block_type": 27,
            "image": {
                "_file_path": img.get("file", img.get("filename", "")),
                "alt": purpose_text,
                "width": 0,
                "height": 0,
            },
        })


# ---------------------------------------------------------------------------
# 发布包读取
# ---------------------------------------------------------------------------

# 按此顺序收集 md 文件
MD_FILE_ORDER = [
    "package_summary.md",
    "event_analysis.md",
    "risk_report.md",
    "xiaohongshu/note.md",
    "xiaohongshu/image_storyboard.md",
    "douyin/video_script.md",
    "douyin/storyboard.md",
    "wechat/article.md",
    "wechat/cover.md",
]


def collect_md_files(package_dir, platform="all"):
    """
    收集发布包目录下的 md 文件，按顺序返回。

    返回: (files: list[(path, label)], errors: list[str])
    """
    files = []
    errors = []

    # 根据平台确定要收集的文件列表
    if platform == "all":
        file_order = list(MD_FILE_ORDER)
    else:
        file_order = list(PLATFORM_FILES.get(platform, []))

    for rel_path in file_order:
        full = os.path.join(package_dir, rel_path)
        if os.path.isfile(full):
            label = os.path.splitext(os.path.basename(rel_path))[0]
            files.append((full, rel_path))
        else:
            errors.append(f"文件不存在: {rel_path}")

    # 仅全量模式收集未被列入顺序表的额外 md 文件
    if platform == "all":
        known_paths = set(MD_FILE_ORDER)
        for root, dirs, fnames in os.walk(package_dir):
            for fname in fnames:
                if fname.endswith(".md"):
                    rel = os.path.relpath(os.path.join(root, fname), package_dir).replace("\\", "/")
                    if rel not in known_paths:
                        files.append((os.path.join(root, fname), rel))
                        known_paths.add(rel)

    return files, errors


def build_document_content(package_dir, platform="all"):
    """
    读取所有 md 文件，拼成一篇主文档的飞书 blocks。

    返回:
        all_blocks: list[dict]  — 飞书 block 数组
        stats: dict             — 统计信息 {md_files: int, total_blocks: int, chunks: int}
    """
    files, errors = collect_md_files(package_dir, platform)
    all_blocks = []

    for i, (file_path, rel_path) in enumerate(files):
        with open(file_path, "r", encoding="utf-8") as f:
            md_text = f.read()

        blocks = md_to_blocks(md_text)

        if blocks:
            # 在每篇文档前加一个 heading1 章节标题 + 分割线（第一篇除外）
            if i > 0:
                all_blocks.append({
                    "block_type": 22,
                    "divider": {},
                })
                # 用文件名作为章节标题
                section_name = os.path.splitext(os.path.basename(rel_path))[0]
                all_blocks.append({
                    "block_type": 3,
                    "heading1": {
                        "elements": [
                            {"text_run": {"content": f" {section_name}", "text_element_style": {}}}
                        ],
                    },
                })
            all_blocks.extend(blocks)

    chunks = list(chunk_blocks(all_blocks))

    stats = {
        "md_files": len(files),
        "total_blocks": len(all_blocks),
        "chunks": len(chunks),
        "errors": errors,
    }

    return all_blocks, chunks, stats


# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# 推送完成通知
# ---------------------------------------------------------------------------

def send_notification(title, doc_url, stats, image_count, image_fail, auth=None):
    """推送完成后发送飞书通知。

    优先使用群机器人 webhook（FEISHU_WEBHOOK_URL），
    其次使用 IM 私聊（需 FEISHU_APP_ID/APP_SECRET + im:message 权限）。

    Webhook 方式无需 token，最简单可靠。
    """
    webhook_url = os.environ.get("FEISHU_WEBHOOK_URL", "").strip()

    md_count = stats.get("md_files", 0)
    block_count = stats.get("total_blocks", 0)

    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": "📄 飞书推送完成"},
            "template": "blue",
        },
        "elements": [
            {
                "tag": "div",
                "fields": [
                    {"is_short": True, "text": {"tag": "lark_md", "content": f"**标题**\n{title}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": "**状态**\n✅ 推送成功"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": f"**内容**\n{md_count} 篇 · {block_count} blocks"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": f"**图片**\n{image_count} 张" if image_count else "**图片**\n无"}},
                ],
            },
            {"tag": "hr"},
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "🔗 查看文档"},
                        "type": "primary",
                        "url": doc_url,
                    }
                ],
            },
        ],
    }

    # --- Webhook 方式（优先）---
    if webhook_url:
        payload = {"msg_type": "interactive", "card": card}
        try:
            rate_limit()
            req = urllib.request.Request(
                webhook_url,
                data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
                headers={"Content-Type": "application/json; charset=utf-8"},
                method="POST",
            )
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read())
            if result.get("code") == 0 or result.get("StatusCode") == 0:
                print(f"  群机器人通知已发送")
            else:
                print(f"  群机器人通知失败: {result}", file=sys.stderr)
        except Exception as e:
            print(f"  群机器人通知异常: {e}", file=sys.stderr)
        return

    # --- IM 私聊方式（fallback）---
    if not auth:
        print("  跳过通知: 未配置 FEISHU_WEBHOOK_URL 且无 auth")
        return
    if not NOTIFY_OPEN_ID or NOTIFY_OPEN_ID == "这里填你的飞书open_id":
        print("  跳过通知: 未配置 NOTIFY_OPEN_ID")
        return

    body = {
        "receive_id": NOTIFY_OPEN_ID,
        "msg_type": "interactive",
        "content": json.dumps(card, ensure_ascii=False),
    }

    rate_limit()
    resp = api_call("POST", IM_MESSAGE_URL, auth, body)

    if resp.get("code") == 0:
        print(f"  私聊通知已发送")
    else:
        print(f"  私聊通知发送失败: code={resp.get('code')} msg={resp.get('msg')}", file=sys.stderr)


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="飞书发布 — 将发布包推送到飞书 Doc")
    parser.add_argument("--package-dir", required=True, help="发布包目录路径")
    parser.add_argument("--title", default=None, help="文档标题（默认使用目录名 + 平台后缀）")
    parser.add_argument("--platform", default="all", choices=["all", "wechat", "xhs", "douyin"],
                        help="推送目标平台 (all=全量, wechat=公众号, xhs=小红书, douyin=抖音)")
    parser.add_argument("--dry-run", action="store_true", help="干跑模式：只转换不调 API")
    parser.add_argument("--output-json", default=None, help="干跑时将 blocks JSON 写到指定文件")
    args = parser.parse_args()

    package_dir = os.path.abspath(args.package_dir)
    if not os.path.isdir(package_dir):
        print(f"ERROR: 目录不存在: {package_dir}", file=sys.stderr)
        sys.exit(1)

    title = args.title or f"{os.path.basename(package_dir)} - {PLATFORM_SUFFIX[args.platform]}"

    print(f"Package dir: {package_dir}")
    print(f"Title: {title}")
    print(f"Platform: {args.platform}")
    print()

    # 1. 解析 Markdown → blocks
    print("--- 解析 Markdown 文件 ---")
    all_blocks, chunks, stats = build_document_content(package_dir, args.platform)

    print(f"  MD 文件: {stats['md_files']}")
    print(f"  Blocks: {stats['total_blocks']}")
    print(f"  Chunks (≤50 each): {stats['chunks']}")
    if stats["errors"]:
        print("  缺失文件:")
        for e in stats["errors"]:
            print(f"    - {e}")
    print()

    # 1.5 收集已生成图片 → 追加附录（仅全量模式；单平台模式下图片已内联到文章）
    if args.platform == "all":
        images = collect_generated_images(package_dir)
        if images:
            print(f"  收集到 {len(images)} 张图片，追加图片附录")
            append_image_appendix(all_blocks, images)
            stats["total_blocks"] = len(all_blocks)
            print(f"  追加附录后 Blocks: {stats['total_blocks']}")
            print()

    if not all_blocks:
        print("ERROR: 没有解析到任何内容块", file=sys.stderr)
        sys.exit(1)

    # 2. 干跑模式
    if args.dry_run:
        print("--- DRY RUN: 不调用飞书 API ---")
        # 重新分块（附录追加后 block 数量变化）
        chunks = list(chunk_blocks(all_blocks))
        stats["chunks"] = len(chunks)
        output_path = args.output_json or os.path.join(package_dir, "feishu_blocks_dryrun.json")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump({
                "title": title,
                "stats": stats,
                "chunks": [
                    {"index": i, "block_count": len(chunk), "blocks": chunk}
                    for i, chunk in enumerate(chunks)
                ],
            }, f, ensure_ascii=False, indent=2)
        print(f"  Blocks JSON 已写入: {output_path}")
        print("  DRY RUN 完成。如需真实推送，去掉 --dry-run 参数。")
        return

    # 3. 检查凭据
    try:
        auth = FeishuAuth()
        auth.get_token()
        print(f"飞书认证 OK (app_id={auth.app_id})")
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("请先设置 FEISHU_APP_ID 和 FEISHU_APP_SECRET 环境变量", file=sys.stderr)
        sys.exit(1)

    # 4. 创建文档
    print()
    print("--- 创建飞书文档 ---")
    doc_id, result = create_document(title, auth)

    if doc_id is None:
        print(f"ERROR: {result}", file=sys.stderr)
        sys.exit(1)

    doc_url = result
    print(f"  Document ID: {doc_id}")
    print(f"  URL: {doc_url}")
    print()

    # 5. 逐块推入内容（图片块用三步法：建空块→Drive上传→PATCH更新）
    print("--- 推送内容 ---")
    chunks = list(chunk_blocks(all_blocks))
    stats["chunks"] = len(chunks)

    success_count = 0
    fail_count = 0
    image_count = 0
    image_fail = 0

    for i, chunk in enumerate(chunks):
        img_in_chunk = sum(1 for b in chunk if b.get("block_type") == 27)

        ok, detail = push_chunk_with_images(doc_id, chunk, package_dir, auth)
        if ok:
            success_count += 1
            if img_in_chunk:
                image_count += img_in_chunk
            if detail != "OK":
                image_fail += 1
            img_info = f" (含{img_in_chunk}张图)" if img_in_chunk else ""
            print(f"  Chunk {i+1}/{stats['chunks']}: {len(chunk)} blocks OK{img_info}")
            if detail != "OK":
                print(f"    {detail}")
        else:
            fail_count += 1
            print(f"  Chunk {i+1}/{stats['chunks']}: FAILED — {detail}", file=sys.stderr)

    print()
    msg = f"  推送完成: {success_count}/{stats['chunks']} 分块成功"
    if image_count:
        msg += f"，{image_count} 张图片已上传"
    print(msg)
    if image_fail > 0:
        print(f"  WARNING: 部分图片上传有问题，请检查", file=sys.stderr)

    # 6. 写结果文件
    result_data = {
        "title": title,
        "document_id": doc_id,
        "doc_url": doc_url,
        "stats": stats,
        "chunks_sent": success_count,
        "chunks_failed": fail_count,
    }
    result_path = os.path.join(package_dir, "feishu_publish.json")
    with open(result_path, "w", encoding="utf-8") as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    print(f"  结果已写入: {result_path}")

    if fail_count > 0:
        print(f"  WARNING: {fail_count} 个分块失败，文档内容可能不完整", file=sys.stderr)
        sys.exit(1)

    # 私聊通知
    send_notification(title, doc_url, stats, image_count, image_fail, auth)

    print()
    print("Done! 飞书文档已就绪。")
    print(f"   {doc_url}")


if __name__ == "__main__":
    main()
