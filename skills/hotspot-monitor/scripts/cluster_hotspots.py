#!/usr/bin/env python3
"""
热点去重聚类 —— 按标题相似度、URL、关键词重叠度合并重复热点。

用法:
  python cluster_hotspots.py --input hotspots_raw.json --output hotspots_dedup.json
输入:
  标准化的热点列表 JSON（来自 RSS/API 拉取）
输出:
  去重 + 打上 cluster_id + duplicate_of 标记的热点列表
"""

import json
import sys
import argparse
import re
from urllib.parse import urlparse


def normalize_title(title):
    """标准化标题用于比较：去标点、转小写、去多余空格"""
    if not title:
        return ""
    title = re.sub(r"[^\w\s]", " ", title)
    title = re.sub(r"\s+", " ", title).strip().lower()
    return title


def extract_keywords(title, summary=""):
    """从标题+摘要提取关键词集合"""
    text = f"{title} {summary}"
    # 简单分词：2字以上中文词 + 3字母以上英文词
    words = set()
    # 中文词
    chinese_words = re.findall(r"[\u4e00-\u9fff]{2,}", text)
    words.update(chinese_words)
    # 英文词
    english_words = re.findall(r"[a-zA-Z]{3,}", text)
    words.update(w.lower() for w in english_words)
    return words


def url_domain(url):
    """提取域名，用于判断同源"""
    try:
        return urlparse(url).netloc
    except Exception:
        return url or ""


def title_overlap_ratio(a_title, b_title):
    """计算两个标题的字符级重叠率（简单Jaccard）"""
    a_words = set(normalize_title(a_title).split())
    b_words = set(normalize_title(b_title).split())
    if not a_words or not b_words:
        return 0.0
    intersection = a_words & b_words
    union = a_words | b_words
    return len(intersection) / len(union)


def keyword_overlap_ratio(a_kw, b_kw):
    """计算关键词重叠率"""
    if not a_kw or not b_kw:
        return 0.0
    intersection = a_kw & b_kw
    union = a_kw | b_kw
    return len(intersection) / len(union)


def cluster_hotspots(hotspots, title_threshold=0.45, keyword_threshold=0.50):
    """
    聚类去重：
    1. 标题Jaccard相似度 > title_threshold → 视为重复
    2. same URL domain + keyword overlap > keyword_threshold → 视为重复
    3. 同一cluster内保留最早出现的作为主热点，其余标记为 duplicate_of
    """
    clusters = []  # list of clusters, each cluster is list of (index, hotspot)

    for i, hs in enumerate(hotspots):
        hs_title = hs.get("title", "")
        hs_url = hs.get("url", "")
        hs_domain = url_domain(hs_url)
        hs_kw = extract_keywords(hs_title, hs.get("summary", ""))
        matched = False

        for cluster in clusters:
            for _, rep in cluster:
                rep_title = rep.get("title", "")
                rep_url = rep.get("url", "")
                rep_domain = url_domain(rep_url)
                rep_kw = extract_keywords(rep_title, rep.get("summary", ""))

                # 规则1: 标题词级Jaccard过高
                if title_overlap_ratio(hs_title, rep_title) >= title_threshold:
                    cluster.append((i, hs))
                    matched = True
                    break

                # 规则2: 同域名 + 关键词重叠
                if hs_domain == rep_domain and hs_domain:
                    if keyword_overlap_ratio(hs_kw, rep_kw) >= keyword_threshold:
                        cluster.append((i, hs))
                        matched = True
                        break

            if matched:
                break

        if not matched:
            clusters.append([(i, hs)])

    # 构建去重结果
    deduped = []
    seen_dup = set()

    for cluster in clusters:
        # 第一个作为主热点
        _, primary = cluster[0]
        primary["cluster_id"] = f"c{len(deduped):03d}"
        primary["duplicate_of"] = None
        primary["raw_sources"] = len(cluster)
        deduped.append(primary)

        # 其余标记为重复
        for _, dup in cluster[1:]:
            dup_idx = dup.get("hotspot_id", id(dup))
            if dup_idx not in seen_dup:
                dup["duplicate_of"] = primary.get("hotspot_id")
                dup["cluster_id"] = primary["cluster_id"]
                dup["raw_sources"] = len(cluster)
                seen_dup.add(dup_idx)

    return deduped


def main():
    parser = argparse.ArgumentParser(description="热点去重聚类")
    parser.add_argument("--input", required=True, help="输入 JSON 文件路径（标准化热点列表）")
    parser.add_argument("--output", required=True, help="输出去重后的 JSON 文件路径")
    parser.add_argument("--title-threshold", type=float, default=0.45,
                        help="标题Jaccard相似度阈值（默认0.45）")
    parser.add_argument("--keyword-threshold", type=float, default=0.50,
                        help="关键词重叠阈值（默认0.50）")
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 支持 {"hotspots": [...]} 或直接 [...] 格式
    if isinstance(data, dict) and "hotspots" in data:
        hotspots = data["hotspots"]
        wrapper = data
    elif isinstance(data, list):
        hotspots = data
        wrapper = {}
    else:
        print(f"ERROR: 期望 JSON list 或带 hotspots 字段的 dict，实际: {type(data)}", file=sys.stderr)
        sys.exit(1)

    original_count = len(hotspots)
    deduped = cluster_hotspots(hotspots, args.title_threshold, args.keyword_threshold)
    deduped_count = len(deduped)

    # 输出
    output = {
        "dedup_time": wrapper.get("monitor_time", ""),
        "original_count": original_count,
        "deduped_count": deduped_count,
        "duplicates_removed": original_count - deduped_count,
        "hotspots": deduped,
    }

    # 把同cluster的重复项追加到末尾（供人工核查）
    duplicates = [h for h in hotspots if h.get("duplicate_of")]
    if duplicates:
        output["duplicates_appendix"] = duplicates

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"  {original_count} -> {deduped_count} hotspots ({original_count - deduped_count} duplicates merged)")
    print(f"  Output: {args.output}")


if __name__ == "__main__":
    main()
