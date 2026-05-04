"""
Ollama Provider — Local LLM implementation using OpenAI-compatible API.
Hardware: GTX 1050 Mobile 4GB VRAM.
Models: qwen3:4b (Multilingual), phi4-mini (JSON).
"""
import time
import json
import asyncio
import httpx
from typing import AsyncGenerator, Optional
from openai import AsyncOpenAI
from loguru import logger

from app.core import llm_config
from app.modules.ai_chat.providers.base import ILLMProvider
from app.shared.exceptions import AppError

_instance = None


def get_ollama_instance() -> "OllamaProvider":
    """Singleton factory matching existing pattern."""
    global _instance
    if _instance is None:
        _instance = OllamaProvider()
    return _instance


class OllamaProvider(ILLMProvider):
    def __init__(self):
        self.base_url = llm_config.OLLAMA_BASE_URL
        self.api_key = llm_config.OLLAMA_API_KEY
        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
        logger.info(f"[LLM] OllamaProvider initialized | base_url={self.base_url}")

    def _estimate_tokens(self, text: str) -> int:
        """Rough token estimation (chars/4) for logging."""
        return len(text) // 4

    def _clean_content(self, content: str) -> str:
        """Centralized removal of reasoning/thinking tags."""
        import re
        # Remove <think>...</think> or just <think> if </think> is missing
        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
        content = re.sub(r"<think>.*", "", content, flags=re.DOTALL)
        # Strip other potential reasoning markers
        content = re.sub(r"Thought:.*", "", content, flags=re.DOTALL)
        return content.strip()

    def _prepare_params(self, messages: list[dict], task_config: llm_config.TaskConfig, **kwargs) -> dict:
        """Unified parameter preparation ensuring GPU and context settings."""
        model = kwargs.get("model") or (task_config.model if task_config else llm_config.PRIMARY_MODEL)
        
        # Inject GLOBAL_RULES if not already present
        local_messages = [m.copy() for m in messages]
        system_found = False
        for m in local_messages:
            if m["role"] == "system":
                if "HARD RULES" not in m["content"]:
                    m["content"] = f"{llm_config.GLOBAL_RULES}\n\n{m['content']}"
                system_found = True
                break
        if not system_found:
            local_messages.insert(0, {"role": "system", "content": llm_config.GLOBAL_RULES})

        # Context and prediction limits
        context_window = kwargs.get("context_window") or (task_config.context_window if task_config else llm_config.OLLAMA_PARAMS["num_ctx"])
        max_tokens = kwargs.get("max_tokens") or (task_config.max_tokens if task_config else llm_config.OLLAMA_PARAMS["num_predict"])
        
        # Merge options
        options = llm_config.OLLAMA_PARAMS.copy()
        options.update({
            "num_ctx": context_window,
            "num_predict": max_tokens,
            "temperature": kwargs.get("temperature", task_config.temperature if task_config else options["temperature"]),
            "num_gpu": 999, # Explicitly force GPU layers
            "low_vram": True # Help with GTX 1050
        })
        
        json_mode = kwargs.get("json_mode", False)
        
        return {
            "model": model,
            "messages": local_messages,
            "temperature": options["temperature"],
            "max_tokens": max_tokens,
            "timeout": kwargs.get("timeout", 120.0), # Increased for local GPU patience
            "response_format": {"type": "json_object"} if json_mode else None,
            "extra_body": {
                "options": options,
                "format": "json" if json_mode else None,
                "keep_alive": "10m" # Reduced keep_alive to free VRAM for other tasks
            }
        }

    async def complete(self, messages: list[dict], language: str = "en", **kwargs) -> str:
        task_config = kwargs.pop("config", kwargs.pop("task_config", None))
        task_name = task_config.task_name if task_config else "generic_complete"
        
        params = self._prepare_params(messages, task_config, **kwargs)
        logger.info(f"[LLM] ▶ INFERENCE_START | model={params['model']} | task={task_name}")
        
        start_time = time.time()
        try:
            response = await self.client.chat.completions.create(**params)
            content = response.choices[0].message.content or ""
            content = self._clean_content(content)
            
            duration = round(time.time() - start_time, 2)
            logger.info(f"[LLM] ✓ INFERENCE_COMPLETE | duration={duration}s")
            
            return content
        except Exception as e:
            logger.error(f"[LLM] ✗ INFERENCE_FAILED | error={str(e)}")
            raise AppError("OLLAMA_ERROR", f"Ollama call failed: {str(e)}")

    async def stream(self, messages: list[dict], language: str = "en", **kwargs) -> AsyncGenerator[str, None]:
        task_config = kwargs.pop("config", kwargs.pop("task_config", None))
        task_name = task_config.task_name if task_config else "generic_stream"
        
        params = self._prepare_params(messages, task_config, **kwargs)
        params["stream"] = True
        
        logger.info(f"[LLM] ▶ STREAM_START | model={params['model']} | task={task_name}")
        
        start_time = time.time()
        try:
            stream = await self.client.chat.completions.create(**params)
            buffer = ""
            in_think = False
            
            async for chunk in stream:
                if not chunk.choices or not chunk.choices[0].delta.content:
                    continue
                
                token = chunk.choices[0].delta.content
                buffer += token
                
                if not in_think:
                    # Check for opening tag in buffer
                    if "<think" in buffer.lower():
                        # If we have the closing bracket of the opening tag, enter think mode
                        if ">" in buffer:
                            in_think = True
                            # Remove everything before and including the opening tag
                            idx = buffer.lower().find(">")
                            buffer = buffer[idx+1:]
                        else:
                            # Keep buffering until we see >
                            continue
                    else:
                        # No think tag started, yield and clear buffer
                        yield buffer
                        buffer = ""
                else:
                    # Currently in think mode, wait for closing tag
                    if "</think>" in buffer.lower():
                        in_think = False
                        # Extract content AFTER the closing tag
                        idx = buffer.lower().find("</think>")
                        buffer = buffer[idx+8:]
                        if buffer:
                            yield buffer
                            buffer = ""
                    else:
                        # In think mode, don't yield anything
                        # Keep buffer size manageable
                        if len(buffer) > 200:
                            buffer = buffer[-50:] # Just keep a tail to match </think>
            
            # Yield any remaining non-tag content
            if buffer and not in_think:
                yield buffer

            logger.info(f"[LLM] ✓ STREAM_COMPLETE | duration={round(time.time() - start_time, 2)}s")
        except Exception as e:
            logger.error(f"[LLM] ✗ STREAM_FAILED | error={str(e)}")
            raise AppError("OLLAMA_STREAM_ERROR", str(e))

    async def complete_json(self, messages: list[dict], **kwargs) -> dict:
        task_config = kwargs.pop("config", None) or kwargs.pop("task_config", None)
        task_name = task_config.task_name if task_config else "json_extraction"
        
        # Ensure JSON directive is in system prompt
        local_messages = [m.copy() for m in messages]
        json_directive = "IMPORTANT: Return ONLY raw JSON. No markdown code blocks. No reasoning tags. Start with { or [."
        
        system_found = False
        for m in local_messages:
            if m["role"] == "system":
                m["content"] += f"\n\n{json_directive}"
                system_found = True
                break
        if not system_found:
            local_messages.insert(0, {"role": "system", "content": json_directive})

        attempts = 0
        max_attempts = 3
        last_error = ""
        
        while attempts < max_attempts:
            attempts += 1
            current_model = kwargs.get("model") or (task_config.model if task_config else llm_config.PRIMARY_MODEL)
            
            # Fallback strategy
            if attempts == 2:
                kwargs["model"] = llm_config.EXTRACTION_MODEL
                logger.info(f"[LLM] Retrying JSON with extraction model: {llm_config.EXTRACTION_MODEL}")
            
            try:
                # Force JSON mode for Ollama and PASS CONFIG BACK
                response_text = await self.complete(
                    messages=local_messages, 
                    json_mode=True, 
                    config=task_config,
                    **kwargs
                )
                if not response_text:
                    raise ValueError("Empty response")

                # Clean and isolate JSON
                import re
                text = response_text.strip()
                
                # Remove common markdown clutter
                text = re.sub(r"```json\s*", "", text)
                text = re.sub(r"```\s*", "", text)
                
                # Find the boundaries of the JSON object/array
                start_idx = text.find("{")
                if start_idx == -1: start_idx = text.find("[")
                
                if start_idx != -1:
                    # Truncate text before JSON
                    text = text[start_idx:]
                    
                    # Try to find the last closing brace/bracket
                    end_idx = text.rfind("}")
                    if end_idx == -1: end_idx = text.rfind("]")
                    
                    if end_idx != -1:
                        text = text[:end_idx+1]
                    else:
                        # HEALING: Truncated JSON? Try to close it.
                        # This is a very basic heuristic.
                        open_braces = text.count("{") - text.count("}")
                        if open_braces > 0:
                            text += "}" * open_braces
                
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    # Healing attempt 2: fix common typos
                    # 1. Remove trailing commas in arrays/objects
                    text = re.sub(r",\s*([\]\}])", r"\1", text) 
                    # 2. Quote unquoted keys (simple alphanumeric)
                    text = re.sub(r"([{,]\s*)([a-zA-Z0-9_]+)\s*:", r'\1"\2":', text)
                    # 3. Handle single quotes as double quotes
                    text = text.replace("'", '"') 
                    # 4. Remove ellipsis if model truncated list
                    text = text.replace("...", "")
                    
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError as final_e:
                        logger.warning(f"[LLM] JSON healing failed. Text snippet: {text[:100]}...")
                        raise final_e

            except Exception as e:
                last_error = str(e)
                logger.warning(f"[LLM] JSON attempt {attempts} failed: {last_error}")
                if attempts < max_attempts:
                    # Provide feedback for next attempt
                    local_messages.append({"role": "user", "content": f"ERROR: Your last response was not valid JSON. {last_error}. Return ONLY the corrected JSON object."})
                else:
                    logger.error(f"[LLM] Final JSON failure for task={task_name}. Raw text: {response_text[:200] if 'response_text' in locals() else 'None'}")
                    raise AppError("JSON_EXTRACTION_FAILED", f"Final failure: {last_error}")



    async def is_available(self) -> bool:
        """Health check matching OpenAI provider interface."""
        try:
            await self.client.models.list()
            return True
        except Exception:
            return False

    async def health_check(self) -> dict:
        """Ollama-specific detailed health check."""
        # Ollama API tags endpoint
        url = f"{self.base_url.replace('/v1', '')}/api/tags"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    models = [m["name"] for m in resp.json().get("models", [])]
                    status = "healthy"
                    logger.info(f"[LLM] Health check: {status} | Models found: {len(models)}")
                    return {"status": status, "models": models}
                else:
                    status = "unhealthy"
                    logger.warning(f"[LLM] Health check: {status} | Status code: {resp.status_code}")
                    return {"status": status, "error": f"Status {resp.status_code}"}
        except Exception as e:
            status = "unhealthy"
            logger.error(f"[LLM] Health check: {status} | Error: {str(e)}")
            return {"status": status, "error": str(e)}
