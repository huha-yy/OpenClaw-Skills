#!/bin/bash
# ============================================================
# ComfyUI + SD 模型 一键安装脚本
# ============================================================
# 由 OpenClaw setup-environment skill 调用
# 用法: bash skills/setup-environment/scripts/install_comfyui.sh
# ============================================================

set -e

# -------- 配置 --------
COMFYUI_DIR="${COMFYUI_DIR:-/opt/ComfyUI}"
COMFYUI_PORT="${COMFYUI_PORT:-8188}"
MODEL_URL="https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors"
MODEL_NAME="sd_xl_base_1.0.safetensors"
PYTORCH_INDEX="https://download.pytorch.org/whl/cu121"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "============================================"
echo " ComfyUI + SDXL 一键安装"
echo "============================================"
echo ""

# -------- 1. GPU 检测 --------
echo "[1/6] 检测 GPU..."
if ! command -v nvidia-smi &>/dev/null; then
    echo -e "${RED}✗ nvidia-smi 未找到，请先安装 NVIDIA 驱动${NC}"
    echo "  下载: https://www.nvidia.com/drivers"
    exit 1
fi

GPU_INFO=$(nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>/dev/null | head -1)
if [ -z "$GPU_INFO" ]; then
    echo -e "${RED}✗ 未检测到 NVIDIA GPU${NC}"
    exit 1
fi
echo -e "  ${GREEN}✓${NC} $GPU_INFO"

VRAM_MB=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null | head -1)
if [ "$VRAM_MB" -lt 6000 ]; then
    echo -e "${RED}✗ 显存不足（${VRAM_MB}MB < 6GB），无法运行 SDXL${NC}"
    exit 1
fi

# -------- 2. Python + PyTorch --------
echo ""
echo "[2/6] 检查 Python + PyTorch..."

PYTHON=$(which python3 || which python)
PY_VER=$($PYTHON --version 2>&1)
echo "  Python: $PY_VER"

# 检查 torch 是否有 CUDA
TORCH_CUDA=$($PYTHON -c "import torch; print(torch.cuda.is_available())" 2>/dev/null || echo "False")
if [ "$TORCH_CUDA" = "True" ]; then
    TORCH_VER=$($PYTHON -c "import torch; print(torch.__version__)" 2>/dev/null)
    echo -e "  ${GREEN}✓${NC} PyTorch $TORCH_VER + CUDA"
else
    echo -e "  ${YELLOW}⚠ PyTorch 未安装或无 CUDA，正在安装...${NC}"
    pip install torch torchvision --index-url "$PYTORCH_INDEX"
    TORCH_CUDA=$($PYTHON -c "import torch; print(torch.cuda.is_available())" 2>/dev/null || echo "False")
    if [ "$TORCH_CUDA" != "True" ]; then
        echo -e "${RED}✗ PyTorch CUDA 安装失败${NC}"
        exit 1
    fi
    echo -e "  ${GREEN}✓${NC} PyTorch + CUDA 安装完成"
fi

# -------- 3. 克隆 ComfyUI --------
echo ""
echo "[3/6] 安装 ComfyUI..."

if [ -d "$COMFYUI_DIR" ]; then
    echo "  ComfyUI 目录已存在: $COMFYUI_DIR"
    echo "  如需重新安装请删除该目录后重试"
else
    git clone https://github.com/comfyanonymous/ComfyUI.git "$COMFYUI_DIR"
    echo -e "  ${GREEN}✓${NC} ComfyUI 已克隆到 $COMFYUI_DIR"
fi

cd "$COMFYUI_DIR"
pip install -r requirements.txt -q 2>&1 | tail -1
echo -e "  ${GREEN}✓${NC} Python 依赖安装完成"

# -------- 4. 下载 SDXL 模型 --------
echo ""
echo "[4/6] 下载 SDXL 模型..."

MODEL_DIR="$COMFYUI_DIR/models/checkpoints"
mkdir -p "$MODEL_DIR"

if [ -f "$MODEL_DIR/$MODEL_NAME" ]; then
    MODEL_SIZE=$(du -h "$MODEL_DIR/$MODEL_NAME" | cut -f1)
    echo -e "  ${GREEN}✓${NC} 模型已存在: $MODEL_NAME ($MODEL_SIZE)"
else
    echo "  下载中... (~4GB, 可能需要几分钟)"
    wget -q --show-progress -O "$MODEL_DIR/$MODEL_NAME" "$MODEL_URL" 2>&1 || {
        # wget 可能不支持 --show-progress，用 curl 兜底
        curl -L -o "$MODEL_DIR/$MODEL_NAME" "$MODEL_URL"
    }
    MODEL_SIZE=$(du -h "$MODEL_DIR/$MODEL_NAME" | cut -f1)
    echo -e "  ${GREEN}✓${NC} 模型下载完成: $MODEL_NAME ($MODEL_SIZE)"
fi

# -------- 5. 创建 systemd 服务 --------
echo ""
echo "[5/6] 配置自启动服务..."

SERVICE_FILE="/etc/systemd/system/comfyui.service"

if [ -f "$SERVICE_FILE" ]; then
    echo "  systemd 服务已存在，跳过"
else
    cat > "$SERVICE_FILE" << SERVICEOF
[Unit]
Description=ComfyUI Stable Diffusion Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$COMFYUI_DIR
ExecStart=$PYTHON main.py --listen 127.0.0.1 --port $COMFYUI_PORT
Restart=on-failure
RestartSec=5
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
SERVICEOF

    systemctl daemon-reload
    systemctl enable comfyui
    echo -e "  ${GREEN}✓${NC} systemd 服务已创建"
fi

# -------- 6. 启动并验证 --------
echo ""
echo "[6/6] 启动 ComfyUI 并验证..."

# 如果已在运行，先尝试测试
if curl -s "http://127.0.0.1:$COMFYUI_PORT/system_stats" > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓${NC} ComfyUI 已在运行 (端口 $COMFYUI_PORT)"
else
    systemctl restart comfyui 2>/dev/null || {
        # 如果没有 systemd，直接后台启动
        nohup $PYTHON "$COMFYUI_DIR/main.py" --listen 127.0.0.1 --port "$COMFYUI_PORT" > /var/log/comfyui.log 2>&1 &
    }

    # 等待启动（最多 60 秒）
    echo -n "  等待 ComfyUI 启动"
    for i in $(seq 1 30); do
        if curl -s "http://127.0.0.1:$COMFYUI_PORT/system_stats" > /dev/null 2>&1; then
            echo ""
            echo -e "  ${GREEN}✓${NC} ComfyUI 启动成功 (${i}s)"
            break
        fi
        echo -n "."
        sleep 2
    done

    # 最终检查
    if ! curl -s "http://127.0.0.1:$COMFYUI_PORT/system_stats" > /dev/null 2>&1; then
        echo ""
        echo -e "${RED}✗ ComfyUI 启动超时（60s）${NC}"
        echo "  查看日志: journalctl -u comfyui -n 50"
        echo "  或: tail -50 /var/log/comfyui.log"
        exit 1
    fi
fi

# -------- 测试生图 --------
echo ""
echo "  测试生成一张图片..."

TEST_OUTPUT="/tmp/comfyui_install_test.png"
TEST_POSITIVE="masterpiece, best quality, photorealistic, modern clean office, warm lighting, 8k"
TEST_NEGATIVE="ugly, blurry, low quality, distorted, deformed, watermark, text, signature, person, people, face, hand, finger, human, man, woman, child"

$PYTHON -c "
import json, urllib.request, time, os, sys

COMFYUI_URL = 'http://127.0.0.1:$COMFYUI_PORT'

# 构建工作流
seed = int(time.time() * 1000) % (2**32)
workflow = {
    '1': {'inputs': {'ckpt_name': '$MODEL_NAME'}, 'class_type': 'CheckpointLoaderSimple'},
    '2': {'inputs': {'text': '$TEST_POSITIVE', 'clip': ['1', 1]}, 'class_type': 'CLIPTextEncode'},
    '3': {'inputs': {'text': '$TEST_NEGATIVE', 'clip': ['1', 1]}, 'class_type': 'CLIPTextEncode'},
    '4': {'inputs': {'width': 1024, 'height': 1024, 'batch_size': 1}, 'class_type': 'EmptyLatentImage'},
    '5': {'inputs': {'seed': seed, 'steps': 20, 'cfg': 7.0, 'sampler_name': 'dpmpp_2m', 'scheduler': 'karras', 'denoise': 1.0, 'model': ['1', 0], 'positive': ['2', 0], 'negative': ['3', 0], 'latent_image': ['4', 0]}, 'class_type': 'KSampler'},
    '6': {'inputs': {'samples': ['5', 0], 'vae': ['1', 2]}, 'class_type': 'VAEDecode'},
    '7': {'inputs': {'filename_prefix': 'install_test', 'images': ['6', 0]}, 'class_type': 'SaveImage'},
}

# 提交
data = json.dumps({'prompt': workflow}).encode('utf-8')
req = urllib.request.Request(f'{COMFYUI_URL}/prompt', data=data, headers={'Content-Type': 'application/json'})
with urllib.request.urlopen(req) as resp:
    result = json.loads(resp.read())

prompt_id = result['prompt_id']
print(f'  prompt_id: {prompt_id}')

# 等待完成
for i in range(90):
    time.sleep(2)
    try:
        with urllib.request.urlopen(f'{COMFYUI_URL}/history/{{prompt_id}}') as resp:
            history = json.loads(resp.read())
        if prompt_id in history:
            outputs = history[prompt_id]['outputs']
            break
    except:
        pass
else:
    print('Timeout')
    sys.exit(1)

# 获取图片
for node_id, node_output in outputs.items():
    for img in node_output.get('images', []):
        params = urllib.parse.urlencode({'filename': img['filename'], 'subfolder': img.get('subfolder', ''), 'type': img.get('type', 'output')})
        url = f'{COMFYUI_URL}/view?{{params}}'
        with urllib.request.urlopen(url) as resp:
            with open('$TEST_OUTPUT', 'wb') as f:
                f.write(resp.read())
        print(f'Generated: {{len(resp.read())}} bytes')

print('SUCCESS')
" 2>&1

if [ -f "$TEST_OUTPUT" ]; then
    FILE_SIZE=$(du -h "$TEST_OUTPUT" | cut -f1)
    echo -e "  ${GREEN}✓${NC} 测试生图成功 ($TEST_OUTPUT, $FILE_SIZE)"
    rm -f "$TEST_OUTPUT"
else
    echo -e "${YELLOW}⚠ 测试生图未能完成，但 ComfyUI 服务可能正在加载模型（首次加载需 10-30s）${NC}"
    echo "  可稍后手动测试:"
    echo "  python skills/image-generator/scripts/comfyui_client.py --positive 'test' --output /tmp/"
fi

echo ""
echo "============================================"
echo -e " ${GREEN}安装完成！${NC}"
echo "============================================"
echo ""
echo "  ComfyUI:  http://127.0.0.1:$COMFYUI_PORT"
echo "  模型:     $MODEL_NAME"
echo "  服务:     systemctl status comfyui"
echo "  日志:     journalctl -u comfyui -f"
echo ""
echo "  在 .env 中确保已设置:"
echo "    COMFYUI_URL=http://127.0.0.1:$COMFYUI_PORT"
echo ""
