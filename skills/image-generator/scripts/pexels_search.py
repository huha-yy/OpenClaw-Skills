#!/usr/bin/env python3
"""
Pexels 图库检索 —— 按关键词搜索图片，输出候选结果和评分。

用法:
  python pexels_search.py --query "elderly care technology" --n 10 --output result.json

依赖:
  pip install requests

API Key 来源:
  环境变量 PEXELS_API_KEY 或 --apikey 参数
"""

import json
import os
import sys
import argparse
import urllib.request
import urllib.parse


PEXELS_URL = "https://api.pexels.com/v1/search"


def search(query, api_key, per_page=10, orientation=None, color=None, locale="zh-CN"):
    """搜索 Pexels 图库"""
    params = {
        "query": query,
        "per_page": per_page,
        "locale": locale,
    }
    if orientation:
        params["orientation"] = orientation
    if color:
        params["color"] = color

    url = f"{PEXELS_URL}?{urllib.parse.urlencode(params)}"
    headers = {
        "Authorization": api_key,
        "User-Agent": "OpenClaw-ImageGenerator/1.0",
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  Pexels API error: {e.code} {e.reason}", file=sys.stderr)
        return None


def score_image(photo, purpose, platform, brand_keywords):
    """对图片进行评分"""
    score = 0
    reasons = []

    # 关键词匹配（30分）
    combined = f"{photo.get('alt', '')} {photo.get('photographer', '')}".lower()
    matched = [kw for kw in brand_keywords if kw.lower() in combined]
    score += min(30, len(matched) * 15)
    if matched:
        reasons.append(f"品牌关键词匹配: {matched}")

    # 摄影师知名度（简化：有头像+10分）
    if photo.get("photographer_url"):
        score += 10
        reasons.append("来源可追溯")

    # 色彩丰富度（简化：avg_color 存在+10分）
    if photo.get("avg_color"):
        score += 10

    # 平台适配（20分）
    width = photo.get("width", 0)
    height = photo.get("height", 0)
    aspect_ratios = {
        "xiaohongshu": 3/4,
        "douyin": 9/16,
        "wechat": 2.35/1,
    }
    target_ratio = aspect_ratios.get(platform, 1)
    actual_ratio = width / max(height, 1)
    ratio_diff = abs(actual_ratio - target_ratio)
    platform_score = max(0, 20 - int(ratio_diff * 20))
    score += platform_score
    reasons.append(f"平台适配: {platform_score}/20")

    # 美观度基准（20分）
    score += 15
    reasons.append("Pexels 高质量图库")

    risk = "low"
    if platform_score < 10:
        risk = "medium"
        reasons.append("[WARN] 比例差异较大，需裁剪")

    return {
        "score": min(100, score),
        "reasons": reasons,
        "risk": risk,
    }


def main():
    parser = argparse.ArgumentParser(description="Pexels 图库检索")
    parser.add_argument("--query", required=True, help="搜索关键词（英文）")
    parser.add_argument("--n", type=int, default=10, help="返回数量")
    parser.add_argument("--orientation", choices=["landscape", "portrait", "square"], help="图片方向")
    parser.add_argument("--color", help="主色调（如 blue, white）")
    parser.add_argument("--purpose", default="配图", help="图片用途")
    parser.add_argument("--platform", default="xiaohongshu", choices=["xiaohongshu", "douyin", "wechat"])
    parser.add_argument("--brand-keywords", default="medical,healthcare,elderly,care,technology,clean,modern,professional", help="品牌关键词，逗号分隔")
    parser.add_argument("--apikey", help="Pexels API Key（优先用环境变量 PEXELS_API_KEY）")
    parser.add_argument("--output", help="输出 JSON 文件路径")
    parser.add_argument("--min-score", type=int, default=60, help="最低分数阈值")
    args = parser.parse_args()

    api_key = args.apikey or os.environ.get("PEXELS_API_KEY")
    if not api_key:
        print("ERROR: 请设置 PEXELS_API_KEY 环境变量或使用 --apikey 参数", file=sys.stderr)
        sys.exit(1)

    print(f"  Searching Pexels: \"{args.query}\" (platform: {args.platform}, n={args.n})")

    result = search(args.query, api_key, per_page=args.n, orientation=args.orientation, color=args.color)
    if not result:
        sys.exit(1)

    photos = result.get("photos", [])
    print(f"  Found {len(photos)} images (total: {result.get('total_results', 0)})")

    brand_kws = [k.strip() for k in args.brand_keywords.split(",")]

    candidates = []
    for i, photo in enumerate(photos):
        eval_result = score_image(photo, args.purpose, args.platform, brand_kws)
        entry = {
            "rank": i + 1,
            "source": "pexels",
            "photo_id": photo.get("id"),
            "photographer": photo.get("photographer"),
            "photographer_url": photo.get("photographer_url"),
            "url": photo.get("url"),
            "image_urls": photo.get("src", {}),
            "avg_color": photo.get("avg_color"),
            "alt": photo.get("alt"),
            "width": photo.get("width"),
            "height": photo.get("height"),
            "score": eval_result["score"],
            "score_detail": eval_result["reasons"],
            "risk": eval_result["risk"],
        }
        candidates.append(entry)
        print(f"    #{i+1}: score={eval_result['score']} risk={eval_result['risk']} - {photo['photographer']}")

    # 按分数排序
    candidates.sort(key=lambda x: x["score"], reverse=True)

    # 过滤低分
    qualified = [c for c in candidates if c["score"] >= args.min_score]
    print(f"  Qualified (score >= {args.min_score}): {len(qualified)}")

    output_data = {
        "query": args.query,
        "total_results": result.get("total_results", 0),
        "platform": args.platform,
        "min_score": args.min_score,
        "candidates": candidates,
        "qualified": qualified,
        "best": qualified[0] if qualified else None,
    }

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"  Saved: {args.output}")
    else:
        print(json.dumps(output_data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
