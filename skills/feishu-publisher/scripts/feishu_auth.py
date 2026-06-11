#!/usr/bin/env python3
"""
飞书 Token 管理 —— 获取/缓存/自动刷新 tenant_access_token。

用法:
  from feishu_auth import FeishuAuth
  auth = FeishuAuth()
  token = auth.get_token()  # 自动处理缓存和刷新

环境变量:
  FEISHU_APP_ID     飞书应用 App ID
  FEISHU_APP_SECRET 飞书应用 App Secret
"""

import os
import sys
import time
import urllib.request
import urllib.error
import json

# Windows 终端强制 UTF-8
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TOKEN_URL = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
TOKEN_TTL = 7200         # 2 小时
REFRESH_MARGIN = 1800    # 剩余 < 30 分钟时刷新


class FeishuAuth:
    """飞书 tenant_access_token 管理器，自动获取/缓存/刷新。"""

    def __init__(self, app_id=None, app_secret=None):
        self._app_id = app_id or os.environ.get("FEISHU_APP_ID", "")
        self._app_secret = app_secret or os.environ.get("FEISHU_APP_SECRET", "")
        self._token = None
        self._expires_at = 0.0

    def _fetch_token(self):
        """从飞书 API 获取新 token。"""
        if not self._app_id or not self._app_secret:
            raise RuntimeError(
                "缺少飞书凭据。请设置环境变量 FEISHU_APP_ID 和 FEISHU_APP_SECRET"
            )

        body = json.dumps({
            "app_id": self._app_id,
            "app_secret": self._app_secret,
        }).encode("utf-8")

        req = urllib.request.Request(
            TOKEN_URL,
            data=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"获取飞书 token 失败: HTTP {e.code} — {body}")

        if data.get("code") != 0:
            raise RuntimeError(
                f"获取飞书 token 失败: code={data.get('code')} msg={data.get('msg')}"
            )

        self._token = data["tenant_access_token"]
        # 用服务器返回的 expire 或默认 7200 秒
        expire_seconds = data.get("expire", TOKEN_TTL)
        self._expires_at = time.time() + expire_seconds

        return self._token

    def get_token(self):
        """获取有效 token，必要时自动刷新。"""
        if self._token is None:
            return self._fetch_token()

        remaining = self._expires_at - time.time()
        if remaining < REFRESH_MARGIN:
            return self._fetch_token()

        return self._token

    @property
    def app_id(self):
        return self._app_id


# 模块级单例
_auth_instance = None


def get_auth():
    """获取模块级 FeishuAuth 单例。"""
    global _auth_instance
    if _auth_instance is None:
        _auth_instance = FeishuAuth()
    return _auth_instance


if __name__ == "__main__":
    # 简单自检
    try:
        auth = FeishuAuth()
        token = auth.get_token()
        print(f"Token OK: {token[:16]}... (app_id={auth.app_id})")
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
