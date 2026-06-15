#!/usr/bin/env python3
"""
图片生产执行层 —— 读取 LLM 生成的 image_plan.json，自动执行：
  策略一 Pexels 搜索 → 评分 → 下载合格图
  策略二 ComfyUI 生图（Pexels 不合格时兜底）

用法:
  python run_image_pipeline.py --plan outputs/topic/images/image_plan.json
"""

import json
import os
import sys
import time
import argparse
import subprocess
import urllib.request

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), ".env"))

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

# 强制人物屏蔽词 —— 小模型容易画出畸形手/脸，代码层兜底确保不被 LLM 遗漏
MANDATORY_NEGATIVE = (
    "person, people, face, hand, finger, human, man, woman, child, "
    "patient, nurse, doctor, portrait, crowd, family"
)


def run_pexels(query, platform, orientation, n, min_score, output_dir):
    """调用 pexels_search.py"""
    api_key = os.environ.get("PEXELS_API_KEY", "")
    out_file = os.path.join(output_dir, "pexels_tmp.json")

    cmd = [
        sys.executable,
        os.path.join(SCRIPTS_DIR, "pexels_search.py"),
        "--query", query,
        "--platform", platform,
        "--orientation", orientation,
        "--n", str(n),
        "--min-score", str(min_score),
        "--output", out_file,
    ]
    if api_key:
        cmd.extend(["--apikey", api_key])

    print(f"    Pexels: \"{query}\"")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if result.returncode != 0:
        print(f"    Pexels ERROR: {result.stderr[-200:]}")
        return None

    with open(out_file, "r", encoding="utf-8") as f:
        return json.load(f)


def download_pexels_image(photo, output_dir, filename):
    """下载 Pexels 图片"""
    url = photo["image_urls"].get("large2x") or photo["image_urls"].get("large")
    if not url:
        return None

    out_path = os.path.join(output_dir, filename)
    api_key = os.environ.get("PEXELS_API_KEY", "")
    headers = {"User-Agent": "OpenClaw-ImagePipeline/1.0"}
    if api_key:
        headers["Authorization"] = api_key
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            with open(out_path, "wb") as f:
                f.write(resp.read())
        return out_path
    except Exception as e:
        print(f"    Download failed: {e}")
        return None


def run_comfyui(positive, negative, width, height, steps, cfg, output_dir):
    """调用 comfyui_client.py"""
    # 强制合入人物屏蔽词（小模型可能遗漏，代码层兜底）
    llm_neg_words = set(w.strip() for w in negative.split(",") if w.strip())
    mandatory_words = set(w.strip() for w in MANDATORY_NEGATIVE.split(",") if w.strip())
    merged_negative = ", ".join(sorted(llm_neg_words | mandatory_words))

    cmd = [
        sys.executable,
        os.path.join(SCRIPTS_DIR, "comfyui_client.py"),
        "--positive", positive,
        "--negative", merged_negative,
        "--width", str(width),
        "--height", str(height),
        "--steps", str(steps),
        "--cfg", str(cfg),
        "--output", output_dir,
    ]
    print(f"    ComfyUI: generating...")
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env)
    if result.returncode != 0:
        print(f"    ComfyUI stderr: {result.stderr[-300:]}")
        print(f"    ComfyUI stdout: {result.stdout[-300:]}")
        return None

    # 从 stdout 提取保存的文件名
    for line in result.stdout.split("\n"):
        if "Saved:" in line:
            return line.split("Saved:")[1].strip()
    return None


def main():
    parser = argparse.ArgumentParser(description="图片生产执行层")
    parser.add_argument("--plan", required=True, help="image_plan.json 路径")
    args = parser.parse_args()

    # 读取方案
    with open(args.plan, "r", encoding="utf-8") as f:
        plan = json.load(f)

    topic = plan.get("topic", "unknown")
    platform = plan.get("platform", "wechat")
    threshold = plan.get("min_score_threshold", 50)
    images = plan.get("images", [])

    output_dir = os.path.dirname(args.plan) or "."
    os.makedirs(output_dir, exist_ok=True)

    print(f"  Topic: {topic} | Platform: {platform} | Images: {len(images)}")
    print(f"  Threshold: {threshold} | Output: {output_dir}")
    print()

    results = []
    pexels_used = 0
    comfyui_used = 0

    for img in images:
        img_id = img["image_id"]
        purpose = img.get("purpose", "未知")
        print(f"[Image {img_id}] {purpose}")

        entry = {
            "image_id": img_id,
            "purpose": purpose,
            "source": None,
            "file": None,
            "pexels_score": None,
            "photographer": None,
        }

        # 策略一：Pexels
        pexels_result = run_pexels(
            query=img["pexels_query"],
            platform=img.get("platform", platform),
            orientation=img.get("pexels_orientation", "landscape"),
            n=5,
            min_score=threshold,
            output_dir=output_dir,
        )

        if pexels_result and pexels_result.get("best"):
            best = pexels_result["best"]
            score = best["score"]
            entry["pexels_score"] = score

            if score >= threshold:
                # Pexels 合格，下载
                filename = f"img{img_id:02d}_{purpose}_pexels.jpg"
                path = download_pexels_image(best, output_dir, filename)
                if path:
                    entry["source"] = "pexels"
                    entry["file"] = path
                    entry["photographer"] = best.get("photographer")
                    pexels_used += 1
                    print(f"    -> Pexels (score={score}) by {best.get('photographer')}")

        # 策略二：ComfyUI 兜底
        if entry["source"] is None:
            path = run_comfyui(
                positive=img["sd_positive"],
                negative=img["sd_negative"],
                width=768,
                height=512,
                steps=img.get("sd_steps", 25),
                cfg=img.get("sd_cfg", 7.0),
                output_dir=output_dir,
            )
            if path:
                entry["source"] = "comfyui"
                entry["file"] = path
                comfyui_used += 1
                print(f"    -> ComfyUI: {os.path.basename(path)}")
            else:
                entry["source"] = "failed"
                print(f"    -> FAILED")

        results.append(entry)
        print()

    # 写结果摘要
    summary = {
        "topic": topic,
        "platform": platform,
        "threshold": threshold,
        "total": len(images),
        "pexels_used": pexels_used,
        "comfyui_used": comfyui_used,
        "results": results,
    }

    summary_path = os.path.join(output_dir, "pipeline_result.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"  Done: {pexels_used} Pexels + {comfyui_used} ComfyUI = {len(images)} total")
    print(f"  Summary: {summary_path}")


if __name__ == "__main__":
    main()
