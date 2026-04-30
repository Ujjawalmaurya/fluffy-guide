"""
Ollama Provider — Local LLM implementation using OpenAI-compatible API.
Hardware: GTX 1050 Mobile 6GB VRAM.
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

    async def _rate_limit_check(self):
        """Matches openai_provider interface. No logic needed for local Ollama."""
        pass

    async def complete(self, messages: list[dict], language: str = "en", **kwargs) -> str:
        """
        Match OpenAI interface: return full response string.
        Parameters match exactly for zero-change swap.
        """
        task_config = kwargs.pop("config", kwargs.pop("task_config", None))
        model = kwargs.get("model") or (task_config.model if task_config else llm_config.PRIMARY_MODEL)
        task_name = task_config.task_name if task_config else "generic_complete"
        
        tokens_in = sum(self._estimate_tokens(m.get("content", "")) for m in messages)
        logger.info(f"[LLM] ▶ INFERENCE_START | model={model} | task={task_name} | tokens_in=~{tokens_in}")
        
        start_time = time.time()
        try:
            # Prepare parameters
            task_name = kwargs.pop("task", None) or (task_config.task_name if task_config else "generic_complete")
            
            params = {
                "model": model,
                "messages": messages,
                "temperature": kwargs.get("temperature", task_config.temperature if task_config else 0.7),
                "max_tokens": kwargs.get("max_tokens", task_config.max_tokens if task_config else 512),
                **{k: v for k, v in kwargs.items() if k not in ["model", "temperature", "max_tokens", "task", "config", "task_config"]}
            }
            
            response = await self.client.chat.completions.create(**params)
            content = response.choices[0].message.content or ""
            
            duration = round(time.time() - start_time, 2)
            tokens_out = self._estimate_tokens(content)
            
            logger.info(f"[LLM] ✓ INFERENCE_COMPLETE | model={model} | tokens_out=~{tokens_out} | duration={duration}s")
            if duration > 5:
                logger.warning(f"[LLM] ⚠ SLOW_RESPONSE | duration={duration}s | threshold=5s")
            
            return content
        except Exception as e:
            logger.error(f"[LLM] ✗ INFERENCE_FAILED | model={model} | error={str(e)}")
            raise AppError("OLLAMA_ERROR", f"Ollama call failed: {str(e)}")

    async def stream(self, messages: list[dict], language: str = "en", **kwargs) -> AsyncGenerator[str, None]:
        """
        Match OpenAI interface: yield response tokens.
        Parameters match exactly for zero-change swap.
        """
        task_config = kwargs.pop("config", kwargs.pop("task_config", None))
        model = kwargs.get("model") or (task_config.model if task_config else llm_config.PRIMARY_MODEL)
        task_name = task_config.task_name if task_config else "generic_stream"
        
        tokens_in = sum(self._estimate_tokens(m.get("content", "")) for m in messages)
        logger.info(f"[LLM] ▶ INFERENCE_START | model={model} | task={task_name} | tokens_in=~{tokens_in}")
        
        start_time = time.time()
        full_content = ""
        try:
            task_name = kwargs.pop("task", None) or (task_config.task_name if task_config else "generic_stream")
            
            params = {
                "model": model,
                "messages": messages,
                "temperature": kwargs.get("temperature", task_config.temperature if task_config else 0.7),
                "max_tokens": kwargs.get("max_tokens", task_config.max_tokens if task_config else 512),
                "stream": True,
                **{k: v for k, v in kwargs.items() if k not in ["model", "temperature", "max_tokens", "task", "config", "task_config", "stream"]}
            }
            
            stream = await self.client.chat.completions.create(**params)
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    token = chunk.choices[0].delta.content
                    full_content += token
                    yield token
            
            duration = round(time.time() - start_time, 2)
            tokens_out = self._estimate_tokens(full_content)
            logger.info(f"[LLM] ✓ INFERENCE_COMPLETE | model={model} | tokens_out=~{tokens_out} | duration={duration}s")
            if duration > 5:
                logger.warning(f"[LLM] ⚠ SLOW_RESPONSE | duration={duration}s | threshold=5s")
                
        except Exception as e:
            logger.error(f"[LLM] ✗ INFERENCE_FAILED | model={model} | error={str(e)}")
            raise AppError("OLLAMA_STREAM_ERROR", f"Ollama stream failed: {str(e)}")

    async def complete_json(self, messages: list[dict], **kwargs) -> dict:
        """
        Specialized method for JSON extraction with retries and fence stripping.
        """
        task_config = kwargs.pop("config", None) or kwargs.pop("task_config", None)
        task_name = kwargs.pop("task", None) or (task_config.task_name if task_config else "json_extraction")
        
        # Use a copy of messages to avoid in-place modification
        local_messages = [m.copy() for m in messages]
        
        # Ensure system prompt for JSON
        system_found = False
        for m in local_messages:
            if m["role"] == "system":
                if "Return ONLY raw JSON" not in m["content"]:
                    m["content"] += "\nReturn ONLY raw JSON. No markdown tags. No conversational text."
                system_found = True
                break
        if not system_found:
            local_messages.insert(0, {"role": "system", "content": "Return ONLY raw JSON. No markdown. No explanation."})

        attempts = 0
        max_json_attempts = 3
        
        logger.info(f"[LLM] Entering complete_json | max_attempts={max_json_attempts}")

        while attempts < max_json_attempts:
            attempts += 1
            
            # Smart fallback: 
            # - If attempt 3, try the OTHER model (primary <-> extraction)
            current_model = kwargs.get("model") or (task_config.model if task_config else llm_config.PRIMARY_MODEL)
            
            if attempts == 3:
                fallback_model = llm_config.PRIMARY_MODEL if current_model == llm_config.EXTRACTION_MODEL else llm_config.EXTRACTION_MODEL
                kwargs["model"] = fallback_model
                logger.info(f"[LLM] JSON fallback: switching from {current_model} to {fallback_model}")
            else:
                kwargs["model"] = current_model

            logger.info(f"[LLM] JSON extraction attempt {attempts}/{max_json_attempts} | model={kwargs.get('model')}")
            
            response_text = ""
            try:
                # Use a slightly higher timeout for JSON tasks
                response_text = await self.complete(messages=local_messages, **kwargs)
                
                if not response_text.strip():
                    logger.warning(f"[LLM] Empty response on attempt {attempts}")
                    raise ValueError("Empty response from model")

                # --- ROBUST CLEANING SEQUENCE ---
                clean_text = response_text.strip()
                
                # 1. Aggressive <think> removal
                import re
                if "<think>" in clean_text:
                    if "</think>" in clean_text:
                        clean_text = re.sub(r'<think>.*?</think>', '', clean_text, flags=re.DOTALL).strip()
                    else:
                        clean_text = re.sub(r'<think>.*', '', clean_text, flags=re.DOTALL).strip()

                # 2. Extract from markdown code blocks
                if "```" in clean_text:
                    fences = re.findall(r'```(?:json)?\s*(.*?)```', clean_text, re.DOTALL | re.IGNORECASE)
                    if fences:
                        # Try each fence until one parses
                        for content in fences:
                            content = content.strip()
                            if content.startswith("{") or content.startswith("["):
                                try:
                                    return json.loads(content)
                                except json.JSONDecodeError:
                                    continue
                    
                    # If fences failed or no valid JSON in fences, try to strip fences and continue
                    clean_text = re.sub(r'```(?:json)?', '', clean_text)
                    clean_text = re.sub(r'```', '', clean_text).strip()

                # 3. Locate JSON boundaries
                start_obj = clean_text.find("{")
                start_arr = clean_text.find("[")
                
                start_idx = -1
                if start_obj != -1 and start_arr != -1:
                    start_idx = min(start_obj, start_arr)
                elif start_obj != -1:
                    start_idx = start_obj
                elif start_arr != -1:
                    start_idx = start_arr

                if start_idx != -1:
                    is_obj = (start_obj == start_idx)
                    end_char = "}" if is_obj else "]"
                    end_idx = clean_text.rfind(end_char)
                    
                    if end_idx != -1 and end_idx > start_idx:
                        clean_text = clean_text[start_idx : end_idx + 1]
                
                # 4. Final attempt to parse
                try:
                    return json.loads(clean_text)
                except json.JSONDecodeError:
                    # Strip any non-JSON noise at start/end
                    clean_text = re.sub(r'^[^\{\[]*', '', clean_text)
                    clean_text = re.sub(r'[^\}\]]*$', '', clean_text)
                    return json.loads(clean_text)

            except (json.JSONDecodeError, ValueError, Exception) as e:
                logger.warning(f"[LLM] JSON parse failed on attempt {attempts}: {str(e)}")
                snippet = response_text[:200].replace('\n', ' ')
                logger.debug(f"[LLM] Failed Response Snippet: {snippet}...")
                
                if attempts < max_json_attempts:
                    # Retry with reinforcement
                    # If it was empty, maybe prompt it to actually speak
                    prompt_extension = " Please do not return an empty response." if not response_text.strip() else ""
                    local_messages.append({
                        "role": "user", 
                        "content": f"Your previous response was invalid. {prompt_extension} Please return ONLY the JSON object, starting with {{ or [, and ending with }} or ]. No other text."
                    })
                else:
                    logger.error(f"[LLM] JSON extraction failed after {max_json_attempts} attempts.")
                    logger.error(f"[LLM] FULL FAILED RESPONSE: \n{response_text}")
                    raise AppError("JSON_EXTRACTION_FAILED", "Could not get valid JSON from local LLM.")



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
