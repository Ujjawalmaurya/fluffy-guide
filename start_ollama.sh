#!/bin/bash
# Persistent Ollama startup script for SkillBridge AI
# Automatically adapts to RTX 4050 (6GB VRAM) or GTX 1050 (4GB VRAM)

# Source .env if present in backend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -f "$SCRIPT_DIR/.env" ]; then
    export $(grep -E '^(USE_RTX_4050|GPU_PROFILE|OLLAMA_VULKAN)=' "$SCRIPT_DIR/.env" | xargs)
fi

USE_4050_VAL=$(echo "${USE_RTX_4050:-true}" | tr '[:upper:]' '[:lower:]')

export OLLAMA_DEBUG=0
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_KEEP_ALIVE=-1
export OLLAMA_VULKAN=${OLLAMA_VULKAN:-1}

if [ "$USE_4050_VAL" = "false" ] || [ "$USE_4050_VAL" = "0" ] || [ "$GPU_PROFILE" = "1050" ]; then
    echo "[SkillBridge AI] Starting Ollama for GTX 1050 Mobile (4GB VRAM)..."
    echo "  - Flash Attention: DISABLED (unsupported on Pascal Compute 6.1)"
    echo "  - Recommended Model: qwen2.5:1.5b (single resident model)"
    export OLLAMA_FLASH_ATTENTION=0
else
    echo "[SkillBridge AI] Starting Ollama for RTX 4050 Mobile (6GB VRAM)..."
    echo "  - Flash Attention: ENABLED"
    echo "  - Models: qwen3:4b (Reasoning) + qwen2.5:1.5b (Extraction)"
    export OLLAMA_FLASH_ATTENTION=1
fi

ollama serve
