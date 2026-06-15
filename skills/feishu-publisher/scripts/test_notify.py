#!/usr/bin/env python3
"""飞书群机器人通知测试 —— 通过 webhook 发消息到群聊。"""
import os
import sys
import json
import time
import urllib.request
import urllib.error

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), ".env"))

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def send_webhook(webhook_url, payload):
    """通用 webhook POST。"""
    req = urllib.request.Request(
        webhook_url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"code": e.code, "msg": e.read().decode("utf-8", errors="replace")}


def send_text(webhook_url, text):
    """群机器人发纯文本。"""
    return send_webhook(webhook_url, {
        "msg_type": "text",
        "content": {"text": text},
    })


def send_card(webhook_url, title, content, button_text=None, button_url=None):
    """群机器人发卡片消息。"""
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": title},
            "template": "blue",
        },
        "elements": [
            {"tag": "div", "text": {"tag": "lark_md", "content": content}},
        ],
    }
    if button_text and button_url:
        card["elements"].append({"tag": "hr"})
        card["elements"].append({
            "tag": "action",
            "actions": [{
                "tag": "button",
                "text": {"tag": "plain_text", "content": button_text},
                "type": "primary",
                "url": button_url,
            }],
        })
    return send_webhook(webhook_url, {
        "msg_type": "interactive",
        "card": card,
    })


def main():
    webhook_url = os.environ.get("FEISHU_WEBHOOK_URL", "").strip()
    if not webhook_url:
        print("❌ 请设置环境变量 FEISHU_WEBHOOK_URL")
        print("   飞书群 → 设置 → 群机器人 → 添加自定义机器人 → 复制 webhook URL")
        print("   export FEISHU_WEBHOOK_URL=https://open.feishu.cn/open-apis/bot/v2/hook/xxx")
        sys.exit(1)

    print(f"✅ Webhook URL: {webhook_url[:50]}...")

    # 1. 发一条纯文本
    print("\n--- 发送纯文本消息 ---")
    resp = send_text(webhook_url,
        "🧪 飞书群机器人通知测试 —— 如果你看到这条消息，说明通知通道正常。")
    if resp.get("code") == 0 or resp.get("StatusCode") == 0:
        print("✅ 文本消息发送成功")
    else:
        print(f"❌ 文本消息失败: {resp}")

    # 2. 发一张卡片
    print("\n--- 发送卡片消息 ---")
    resp = send_card(
        webhook_url,
        title="🖼️ 图文编排 + 平台分推测试",
        content="如果你看到这条卡片，说明 **飞书群机器人通知通道正常**。\n\n"
                "新功能：\n"
                "- `article-composer` 图文智能编排\n"
                "- `push_to_feishu.py --platform wechat` 单平台分推\n"
                "- `push_to_feishu.py --platform xhs` 小红书分推\n\n"
                f"测试时间：{time.strftime('%Y-%m-%d %H:%M:%S')}",
    )
    if resp.get("code") == 0 or resp.get("StatusCode") == 0:
        print("✅ 卡片消息发送成功")
    else:
        print(f"❌ 卡片消息失败: {resp}")

    print("\nDone! 去飞书群看看收到没？")


if __name__ == "__main__":
    main()
