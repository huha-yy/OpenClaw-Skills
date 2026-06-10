#!/usr/bin/env python3
"""
ComfyUI API 客户端 —— 提交文生图任务并下载结果。

用法:
  python comfyui_client.py --positive "prompt" --negative "neg" --width 768 --height 512 --output ./images/

依赖:
  pip install requests
"""

import json
import sys
import time
import uuid
import argparse
import urllib.request
import urllib.parse


COMFYUI_URL = "http://127.0.0.1:8188"
TIMEOUT = 300  # 最长等待秒数
CHECK_INTERVAL = 2  # 轮询间隔秒数


def build_workflow(positive, negative, width, height, steps, cfg, seed, checkpoint):
    """用最新 ComfyUI 官方默认文生图工作流"""
    if seed == -1:
        seed = int(time.time() * 1000) % (2**32)

    return {
        "1": {
            "inputs": {"ckpt_name": checkpoint},
            "class_type": "CheckpointLoaderSimple",
        },
        "2": {
            "inputs": {
                "text": positive,
                "clip": ["1", 1],
            },
            "class_type": "CLIPTextEncode",
        },
        "3": {
            "inputs": {
                "text": negative,
                "clip": ["1", 1],
            },
            "class_type": "CLIPTextEncode",
        },
        "4": {
            "inputs": {
                "width": width,
                "height": height,
                "batch_size": 1,
            },
            "class_type": "EmptyLatentImage",
        },
        "5": {
            "inputs": {
                "seed": seed,
                "steps": steps,
                "cfg": cfg,
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
                "denoise": 1.0,
                "model": ["1", 0],
                "positive": ["2", 0],
                "negative": ["3", 0],
                "latent_image": ["4", 0],
            },
            "class_type": "KSampler",
        },
        "6": {
            "inputs": {
                "samples": ["5", 0],
                "vae": ["1", 2],
            },
            "class_type": "VAEDecode",
        },
        "7": {
            "inputs": {
                "filename_prefix": "openclaw-gen",
                "images": ["6", 0],
            },
            "class_type": "SaveImage",
        },
    }


def queue_prompt(workflow):
    """提交工作流到 ComfyUI 队列"""
    data = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def get_history(prompt_id):
    """获取任务执行历史"""
    with urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}") as resp:
        return json.loads(resp.read())


def get_image(filename, subfolder, output_type):
    """下载生成的图片"""
    params = urllib.parse.urlencode(
        {"filename": filename, "subfolder": subfolder, "type": output_type}
    )
    url = f"{COMFYUI_URL}/view?{params}"
    with urllib.request.urlopen(url) as resp:
        return resp.read()


def main():
    parser = argparse.ArgumentParser(description="ComfyUI 文生图客户端")
    parser.add_argument("--positive", required=True, help="正面提示词（英文）")
    parser.add_argument("--negative", default="ugly, blurry, low quality, distorted, deformed, watermark, text, signature, person, people, face, hand, finger, patient, human, nurse, doctor, man, woman, child, messy, dark, scary, cartoon, 3d render", help="负面提示词")
    parser.add_argument("--width", type=int, default=768, help="图片宽度")
    parser.add_argument("--height", type=int, default=512, help="图片高度")
    parser.add_argument("--steps", type=int, default=25, help="采样步数")
    parser.add_argument("--cfg", type=float, default=7.0, help="CFG scale")
    parser.add_argument("--seed", type=int, default=-1, help="随机种子，-1为随机")
    parser.add_argument("--checkpoint", default="v1-5-pruned-emaonly.safetensors", help="模型文件名")
    parser.add_argument("--output", default="./", help="输出目录")
    args = parser.parse_args()

    print(f"  Positive: {args.positive[:80]}...")
    print(f"  Size: {args.width}x{args.height}, Steps: {args.steps}, CFG: {args.cfg}")
    print(f"  Checkpoint: {args.checkpoint}")

    # 1. 构建工作流
    workflow = build_workflow(
        args.positive, args.negative,
        args.width, args.height, args.steps, args.cfg,
        args.seed, args.checkpoint,
    )

    # 2. 提交任务
    print("  Submitting to ComfyUI...")
    try:
        result = queue_prompt(workflow)
    except Exception as e:
        print(f"  ERROR: Cannot connect to ComfyUI at {COMFYUI_URL}")
        print(f"  {e}")
        sys.exit(1)

    prompt_id = result.get("prompt_id")
    if not prompt_id:
        print(f"  ERROR: No prompt_id returned: {result}")
        sys.exit(1)
    print(f"  prompt_id: {prompt_id}")

    # 3. 等待完成
    print("  Waiting for generation...")
    waited = 0
    while waited < TIMEOUT:
        time.sleep(CHECK_INTERVAL)
        waited += CHECK_INTERVAL
        try:
            history = get_history(prompt_id)
        except Exception:
            print(f"  Waiting... ({waited}s)")
            continue

        if prompt_id in history:
            outputs = history[prompt_id]["outputs"]
            break
        print(f"  Waiting... ({waited}s)")
    else:
        print(f"  ERROR: Timeout after {TIMEOUT}s")
        sys.exit(1)

    # 4. 下载图片
    for node_id, node_output in outputs.items():
        images = node_output.get("images", [])
        for img in images:
            filename = img["filename"]
            subfolder = img.get("subfolder", "")
            output_type = img.get("type", "output")

            data = get_image(filename, subfolder, output_type)

            # 保存
            import os
            os.makedirs(args.output, exist_ok=True)
            out_path = os.path.join(args.output, filename)
            with open(out_path, "wb") as f:
                f.write(data)
            print(f"  Saved: {out_path} ({len(data)} bytes)")

    print("Done!")


if __name__ == "__main__":
    main()
