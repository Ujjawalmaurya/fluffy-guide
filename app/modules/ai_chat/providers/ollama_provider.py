"""
Ollama Provider — Local LLM implementation using OpenAI-compatible API.
Hardware: RTX 4050 6GB VRAM.
Models: qwen3:4b (Reasoning), qwen2.5:1.5b (Extraction).
"""
import time
import json
import asyncio
import httpx
from typing import AsyncIterator, Optional
from openai import AsyncOpenAI
from loguru import logger

from app.core import llm_config
from app.modules.ai_chat.providers.base import ICompletionProvider, IStructuredProvider
from app.shared.exceptions import AppError

_instance = None


def get_ollama_instance() -> "OllamaProvider":
    """Singleton factory matching existing pattern."""
    global _instance
    if _instance is None:
        _instance = OllamaProvider()
    return _instance


class OllamaProvider(ICompletionProvider, IStructuredProvider):
    def __init__(self):
        self.base_url = llm_config.OLLAMA_BASE_URL
        self.api_key = llm_config.OLLAMA_API_KEY
        self.client = AsyncOpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
            max_retries=0
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

    def _prepare_params(self, prompt: str | list[dict], system_prompt: str = None, task_config: llm_config.TaskConfig = None, **kwargs) -> dict:
        """Unified parameter preparation ensuring GPU and context settings."""
        # Convert prompt to messages list
        if isinstance(prompt, list):
            messages = [m.copy() for m in prompt]
            if system_prompt:
                system_found = False
                for m in messages:
                    if m["role"] == "system":
                        m["content"] = f"{system_prompt}\n\n{m['content']}"
                        system_found = True
                        break
                if not system_found:
                    messages.insert(0, {"role": "system", "content": system_prompt})
        else:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": str(prompt)})

        # Select model based on tier (Reasoning vs Extraction) if not specified
        json_mode = kwargs.get("json_mode", False)
        default_model = llm_config.EXTRACTION_MODEL if json_mode else llm_config.REASONING_MODEL
        model = kwargs.get("model") or (task_config.model if task_config else default_model)
        
        # Inject task-appropriate rules if not already present
        system_found = False
        is_chat = task_config and task_config.task_name == "career_guidance_chat"
        rules = llm_config.CHAT_RULES if is_chat else llm_config.EXTRACTION_RULES
        rule_marker = "STYLE:" if is_chat else "HARD RULES"

        for m in messages:
            if m["role"] == "system":
                if rule_marker not in m["content"]:
                    m["content"] = f"{rules}\n\n{m['content']}"
                system_found = True
                break
        if not system_found:
            messages.insert(0, {"role": "system", "content": rules})

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
            # "low_vram": True # Help with RTX 4050
        })
        
        extra_body = {
            "options": options,
            "keep_alive": "60m" # Keep both models resident in VRAM to avoid thrashing
        }
        if json_mode:
            extra_body["format"] = "json"

        return {
            "model": model,
            "messages": messages,
            "temperature": options["temperature"],
            "max_tokens": max_tokens,
            "timeout": kwargs.get("timeout", 120.0), # Increased for local GPU patience
            "response_format": {"type": "json_object"} if json_mode else None,
            "extra_body": extra_body
        }

    async def complete(self, prompt: str | list[dict], system_prompt: str = None, **kwargs) -> str:
        task_config = kwargs.pop("config", kwargs.pop("task_config", None))
        task_name = task_config.task_name if task_config else "generic_complete"
        
        params = self._prepare_params(prompt, system_prompt, task_config, **kwargs)
        logger.info(f"[LLM] ▶ INFERENCE_START | model={params['model']} | task={task_name}")
        
        start_time = time.time()
        try:
            response = await self.client.chat.completions.create(**params)
            message = response.choices[0].message
            content = message.content or ""
            content = self._clean_content(content)
            
            # Extract reasoning/thinking tokens if present
            reasoning = getattr(message, "reasoning", None) or getattr(message, "reasoning_content", None) or ""
            if reasoning and not kwargs.get("json_mode"):
                reasoning = reasoning.strip()
                if reasoning:
                    if content:
                        content = f"<details><summary>Thinking Process</summary>\n\n{reasoning}\n\n</details>\n\n{content}"
                    else:
                        content = f"<details><summary>Thinking Process</summary>\n\n{reasoning}\n\n</details>"
            
            duration = round(time.time() - start_time, 2)
            logger.info(f"[LLM] ✓ INFERENCE_COMPLETE | duration={duration}s")
            
            return content
        except Exception as e:
            logger.error(f"[LLM] ✗ INFERENCE_FAILED | error={str(e)}")
            raise AppError("OLLAMA_ERROR", f"Ollama call failed: {str(e)}")

    async def stream(self, prompt: str | list[dict], system_prompt: str = None, **kwargs) -> AsyncIterator[str]:
        task_config = kwargs.pop("config", kwargs.pop("task_config", None))
        task_name = task_config.task_name if task_config else "generic_stream"
        
        params = self._prepare_params(prompt, system_prompt, task_config, **kwargs)
        params["stream"] = True
        
        logger.info(f"[LLM] ▶ STREAM_START | model={params['model']} | task={task_name}")
        
        start_time = time.time()
        try:
            stream = await self.client.chat.completions.create(**params)
            in_think = False
            has_think_header = False
            
            async for chunk in stream:
                if not chunk.choices:
                    continue
                
                delta = chunk.choices[0].delta
                content = getattr(delta, "content", None) or ""
                reasoning = getattr(delta, "reasoning", None) or getattr(delta, "reasoning_content", None) or ""
                
                # Stream reasoning tokens inside a details block
                if reasoning:
                    if not has_think_header:
                        yield "<details><summary>Thinking Process</summary>\n\n"
                        has_think_header = True
                        in_think = True
                    yield reasoning
                
                # Stream content tokens, closing details block first if still in think mode
                if content:
                    if in_think:
                        yield "\n\n</details>\n\n"
                        in_think = False
                    yield content
            
            # Close details tag if stream ended and it was left open
            if in_think:
                yield "\n\n</details>"

            logger.info(f"[LLM] ✓ STREAM_COMPLETE | duration={round(time.time() - start_time, 2)}s")
        except Exception as e:
            logger.error(f"[LLM] ✗ STREAM_FAILED | error={str(e)}")
            raise AppError("OLLAMA_STREAM_ERROR", str(e))

    async def complete_json(self, prompt: str | list[dict] = None, schema = None, system_prompt: str = None, **kwargs) -> dict:
        if prompt is None and "messages" in kwargs:
            prompt = kwargs.pop("messages")
        if prompt is None:
            raise ValueError("OllamaProvider.complete_json() requires either 'prompt' or 'messages' argument")

        task_config = kwargs.pop("config", None) or kwargs.pop("task_config", None)
        task_name = task_config.task_name if task_config else "json_extraction"
        
        # Ensure JSON directive is in system prompt
        json_directive = "IMPORTANT: Return ONLY raw JSON. No markdown code blocks. No reasoning tags. Start with { or [."
        
        # Handle formatting of local messages
        if isinstance(prompt, list):
            local_messages = [m.copy() for m in prompt]
            system_found = False
            for m in local_messages:
                if m["role"] == "system":
                    m["content"] += f"\n\n{json_directive}"
                    system_found = True
                    break
            if not system_found:
                local_messages.insert(0, {"role": "system", "content": json_directive})
        else:
            local_messages = []
            sys_content = f"{system_prompt}\n\n{json_directive}" if system_prompt else json_directive
            local_messages.append({"role": "system", "content": sys_content})
            local_messages.append({"role": "user", "content": str(prompt)})

        attempts = 0
        max_attempts = 3
        last_error = ""
        response_text = ""
        
        from app.shared.llm_json_utils import clean_and_extract_json_text, parse_healed_json

        while attempts < max_attempts:
            attempts += 1
            current_model = kwargs.get("model") or (task_config.model if task_config else llm_config.EXTRACTION_MODEL)
            
            try:
                # Force JSON mode for Ollama
                response_text = await self.complete(
                    prompt=local_messages, 
                    config=task_config,
                    model=current_model,
                    json_mode=True,
                    **kwargs
                )
                if not response_text:
                    raise ValueError("Empty response")

                # Clean and isolate JSON
                cleaned_text = clean_and_extract_json_text(response_text)
                parsed_data = parse_healed_json(cleaned_text)

                # Schema validation & Pydantic healing if schema provided
                if schema:
                    # Check if schema is StructuredProfile and run normalize_ai_output if so
                    if schema.__name__ == "StructuredProfile":
                        try:
                            from services.resume_extractor import normalize_ai_output
                            parsed_data = normalize_ai_output(parsed_data)
                        except Exception as ne:
                            logger.warning(f"[LLM] Failed to run StructuredProfile normalize_ai_output: {ne}")
                    
                    try:
                        validated = schema.model_validate(parsed_data)
                        return validated.model_dump()
                    except Exception as ve:
                        logger.warning(f"[LLM] Schema validation failed for {schema.__name__}: {ve}. Returning healed dict.")
                        return parsed_data
                else:
                    return parsed_data

            except Exception as e:
                last_error = str(e)
                logger.warning(f"[LLM] JSON attempt {attempts} failed: {last_error}")
                if "timed out" in last_error.lower() or "timeout" in last_error.lower():
                    logger.error(f"[LLM] Timeout detected during task={task_name}. Failing fast without retry.")
                    raise AppError("JSON_EXTRACTION_TIMEOUT", f"Ollama request timed out: {last_error}")
                if attempts < max_attempts:
                    local_messages.append({"role": "user", "content": f"ERROR: Your last response was not valid JSON. {last_error}. Return ONLY the corrected JSON object."})
                else:
                    logger.error(f"[LLM] Final JSON failure for task={task_name}. Raw text: {response_text[:200] if response_text else 'None'}")
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
