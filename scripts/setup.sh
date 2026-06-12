#!/bin/bash
# ============================================================
# OpenClaw 内容运营流水线 —— 环境自检脚本
# ============================================================
# 用法: bash scripts/setup.sh
# 功能: 一键检查运行环境是否满足部署要求
# ============================================================

set -e

PASS="✓"
FAIL="✗"
WARN="⚠"

TOTAL=0
PASSED=0
FAILED=0
WARNINGS=0

# 颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo ""
echo "============================================"
echo " OpenClaw 内容运营流水线 - 环境自检"
echo "============================================"
echo ""

# -------- 辅助函数 --------
check() {
    TOTAL=$((TOTAL + 1))
    local label="$1"
    local result="$2"
    local detail="$3"
    case "$result" in
        pass)
            PASSED=$((PASSED + 1))
            echo -e "  ${GREEN}${PASS}${NC} ${label}"
            ;;
        fail)
            FAILED=$((FAILED + 1))
            echo -e "  ${RED}${FAIL}${NC} ${label}"
            if [ -n "$detail" ]; then
                echo -e "    ${RED}→ ${detail}${NC}"
            fi
            ;;
        warn)
            WARNINGS=$((WARNINGS + 1))
            echo -e "  ${YELLOW}${WARN}${NC} ${label}"
            if [ -n "$detail" ]; then
                echo -e "    ${YELLOW}→ ${detail}${NC}"
            fi
            ;;
    esac
}

# -------- 1. Python --------
echo "--- Python ---"
if command -v python3 &>/dev/null; then
    PY_VER=$(python3 --version 2>&1)
    PY_MAJOR=$(python3 -c 'import sys; print(sys.version_info[0])')
    PY_MINOR=$(python3 -c 'import sys; print(sys.version_info[1])')
    if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 8 ]; then
        check "python3 已安装 ($PY_VER)" pass
    else
        check "python3 已安装 ($PY_VER)" warn "建议 Python 3.8+，当前版本可能不兼容"
    fi
else
    check "python3 已安装" fail "请安装 Python 3.8+: https://www.python.org/downloads/"
fi

# -------- 2. OpenClaw CLI --------
echo ""
echo "--- OpenClaw ---"
if command -v openclaw &>/dev/null; then
    OC_VER=$(openclaw --version 2>&1 || echo "unknown")
    check "openclaw CLI 已安装 ($OC_VER)" pass
else
    check "openclaw CLI 已安装" fail "请安装 OpenClaw: npm install -g openclaw"
fi

# -------- 3. Workspace 目录结构 --------
echo ""
echo "--- 目录结构 ---"
if [ -f "skills/hotspot-monitor/SKILL.md" ]; then
    check "workspace 根目录正确（skill 文件存在）" pass
else
    check "workspace 根目录正确" fail "请在项目根目录运行此脚本"
fi

if [ -d "outputs" ]; then
    check "outputs/ 目录存在" pass
else
    check "outputs/ 目录存在" warn "目录不存在，首次运行时会自动创建"
fi

# -------- 4. 环境变量 --------
echo ""
echo "--- 环境变量 ---"
# 支持从 .env 文件读取
if [ -f ".env" ]; then
    set -a; source .env; set +a
    check ".env 文件已配置" pass
else
    check ".env 文件已配置" warn "建议: cp .env.example .env && vim .env"
fi

if [ -n "$FEISHU_APP_ID" ] && [ "$FEISHU_APP_ID" != "cli_xxx" ]; then
    check "FEISHU_APP_ID 已设置" pass
else
    check "FEISHU_APP_ID 已设置" fail "请在 .env 中填写飞书 App ID"
fi

if [ -n "$FEISHU_APP_SECRET" ] && [ "$FEISHU_APP_SECRET" != "xxx" ]; then
    check "FEISHU_APP_SECRET 已设置" pass
else
    check "FEISHU_APP_SECRET 已设置" fail "请在 .env 中填写飞书 App Secret"
fi

if [ -n "$FEISHU_WEBHOOK_URL" ] && [ "$FEISHU_WEBHOOK_URL" != "https://open.feishu.cn/open-apis/bot/v2/hook/xxx" ]; then
    check "FEISHU_WEBHOOK_URL 已设置" pass
else
    check "FEISHU_WEBHOOK_URL 已设置" fail "请在 .env 中填写飞书群机器人 Webhook"
fi

if [ -n "$DEEPSEEK_API_KEY" ] && [ "$DEEPSEEK_API_KEY" != "sk-xxx" ]; then
    check "DEEPSEEK_API_KEY 已设置" pass
else
    check "DEEPSEEK_API_KEY 已设置" fail "请在 .env 中填写 DeepSeek API Key"
fi

if [ -n "$PEXELS_API_KEY" ] && [ "$PEXELS_API_KEY" != "xxx" ]; then
    check "PEXELS_API_KEY 已设置" pass
else
    check "PEXELS_API_KEY 已设置" fail "请在 .env 中填写 Pexels API Key"
fi

if [ -n "$COMFYUI_URL" ]; then
    check "COMFYUI_URL 已设置（AI 生图: 启用）" pass
else
    check "COMFYUI_URL 未设置（AI 生图: 禁用，仅使用 Pexels）" warn "如需 AI 生图，请取消 .env 中 COMFYUI_URL 的注释"
fi

# -------- 5. API 连通性 --------
echo ""
echo "--- API 连通性 ---"

# 飞书
if [ -n "$FEISHU_APP_ID" ] && [ "$FEISHU_APP_ID" != "cli_xxx" ] && [ -n "$FEISHU_APP_SECRET" ] && [ "$FEISHU_APP_SECRET" != "xxx" ]; then
    FEISHU_RESP=$(curl -s -o /dev/null -w "%{http_code}" \
        -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
        -H "Content-Type: application/json" \
        -d "{\"app_id\":\"$FEISHU_APP_ID\",\"app_secret\":\"$FEISHU_APP_SECRET\"}" 2>/dev/null || echo "000")
    if [ "$FEISHU_RESP" = "200" ]; then
        check "飞书 API 连通" pass
    else
        check "飞书 API 连通" fail "HTTP $FEISHU_RESP — 请检查 FEISHU_APP_ID / FEISHU_APP_SECRET"
    fi
else
    check "飞书 API 连通" warn "跳过（凭据未设置）"
fi

# Pexels
if [ -n "$PEXELS_API_KEY" ] && [ "$PEXELS_API_KEY" != "xxx" ]; then
    PEXELS_RESP=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Authorization: $PEXELS_API_KEY" \
        "https://api.pexels.com/v1/search?query=test&per_page=1" 2>/dev/null || echo "000")
    if [ "$PEXELS_RESP" = "200" ]; then
        check "Pexels API 连通" pass
    else
        check "Pexels API 连通" fail "HTTP $PEXELS_RESP — 请检查 PEXELS_API_KEY"
    fi
else
    check "Pexels API 连通" warn "跳过（凭据未设置）"
fi

# ComfyUI (if configured)
if [ -n "$COMFYUI_URL" ]; then
    COMFY_RESP=$(curl -s -o /dev/null -w "%{http_code}" "$COMFYUI_URL/system_stats" 2>/dev/null || echo "000")
    if [ "$COMFY_RESP" = "200" ]; then
        check "ComfyUI 服务连通 ($COMFYUI_URL)" pass
    else
        check "ComfyUI 服务连通 ($COMFYUI_URL)" warn "HTTP $COMFY_RESP — ComfyUI 可能未启动，AI 生图将跳过"
    fi
fi

# -------- 6. 总结 --------
echo ""
echo "============================================"
echo " 检查结果: ${PASSED}${GREEN}通过${NC} / ${FAILED}${RED}失败${NC} / ${WARNINGS}${YELLOW}警告${NC}（共 ${TOTAL} 项）"
echo "============================================"

if [ "$FAILED" -gt 0 ]; then
    echo ""
    echo -e "${RED}请先解决以上 ${FAILED} 项失败项，再继续部署。${NC}"
    echo "详细部署指南: docs/DEPLOYMENT.md"
    exit 1
elif [ "$WARNINGS" -gt 0 ]; then
    echo ""
    echo -e "${YELLOW}有 ${WARNINGS} 项警告，建议处理后再运行流水线。${NC}"
    echo "详细部署指南: docs/DEPLOYMENT.md"
else
    echo ""
    echo -e "${GREEN}环境检查全部通过，可以启动流水线！${NC}"
fi
echo ""
