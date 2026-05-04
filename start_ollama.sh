#!/bin/bash
# Persistent Ollama startup script for SkillBridge AI
# Optimized for GTX 1050 (4GB VRAM) with Vulkan

export OLLAMA_VULKAN=1
export OLLAMA_DEBUG=0
export OLLAMA_MAX_LOADED_MODELS=1
export OLLAMA_NUM_PARALLEL=1
export OLLAMA_FLASH_ATTENTION=1
export OLLAMA_KEEP_ALIVE=-1

echo "[SkillBridge AI] Starting Ollama with GPU acceleration (Vulkan)..."
ollama serve
