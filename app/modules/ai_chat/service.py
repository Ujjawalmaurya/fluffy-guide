"""
AI chat service — manages context window, builds system prompt, streams via LLM provider.
Dependency-injected: receives ILLMProvider, so test with MockLLMProvider if needed.
"""
from typing import AsyncGenerator

from app.modules.ai_chat.providers.base import ILLMProvider
from app.modules.ai_chat.providers.gemini import GeminiProvider
from app.modules.ai_chat.repository import ChatRepository
from app.core.logger import get_logger

log = get_logger("AI_CHAT")

SYSTEM_PROMPT_EN = """You are SkillBridge AI, a friendly career guidance assistant for India's workforce. \
User's name is {name}, type is {user_type}, location is {state}. \
Their career interests are {interests}. \
Help them with career advice, skill recommendations, and job search tips. Be concise and practical, little bit engaging.
Respond in English or Hinglish (Hindi + English) based on how the user talks to you.
Use Markdown for structure (e.g., **bold**, lists).
Never include <think> or <thinking> tags in responses. Return only the final answer.
"""

SYSTEM_PROMPT_HI = """आप SkillBridge AI हैं, भारत के कार्यबल के लिए एक मित्रवत करियर मार्गदर्शन सहायक। \
उपयोगकर्ता का नाम {name} है, प्रकार {user_type} है, स्थान {state} है। \
उनके करियर हितों में {interests} शामिल हैं। \
केवल शुद्ध और स्पष्ट हिंदी में उत्तर दें (Strictly respond in proper Hindi only). करियर सलाह, कौशल सिफारिशें और नौकरी खोज युक्तियाँ दें। प्रोत्साहित करें। \
संरचना के लिए Markdown का उपयोग करें (जैसे **मोटा अक्षर**, सूचियाँ)।"""


class ChatService:
    def __init__(self, repo: ChatRepository):
        self.repo = repo
        self.provider = GeminiProvider()

    def _get_provider(self, language: str) -> ILLMProvider:
        return self.provider

    def _build_system_prompt(self, user: dict, profile: dict | None, prefs: dict | None, language: str) -> str:
        name = (profile or {}).get("full_name") or user.get("email", "User")
        user_type = user.get("user_type", "individual_youth")
        
        # Defensive access: database might have NULLs
        state = (profile or {}).get("state") or "India"
        
        raw_interests = (prefs or {}).get("career_interests")
        if isinstance(raw_interests, list):
            interests = ", ".join(raw_interests)
        else:
            interests = "various fields"

        template = SYSTEM_PROMPT_HI if language == "hi" else SYSTEM_PROMPT_EN
        return template.format(name=name, user_type=user_type, state=state, interests=interests)

    def _merge_consecutive_roles(self, messages: list[dict]) -> list[dict]:
        """Ensures roles alternate (user, assistant, user...). Merges consecutive identical roles."""
        if not messages:
            return []
        
        merged = []
        for msg in messages:
            if merged and merged[-1]["role"] == msg["role"]:
                # Append content with newline
                merged[-1]["content"] += "\n" + msg["content"]
            else:
                merged.append({"role": msg["role"], "content": msg["content"]})
        return merged

    async def stream_message(
        self,
        user_id: str,
        content: str,
        language: str,
        user: dict,
        profile: dict | None,
        prefs: dict | None,
    ) -> AsyncGenerator[str, None]:
        # Save user message
        self.repo.add_message(user_id, "user", content, language)

        history = self.repo.get_history(user_id, limit=11)
        system_prompt = self._build_system_prompt(user, profile, prefs, language)

        raw_messages = [{"role": "system", "content": system_prompt}]
        raw_messages += [{"role": m["role"], "content": m["content"]} for m in history]
        
        # Sarvam AI requirement: First message after system MUST be 'user'.
        # If history starts with 'assistant', we drop it to maintain valid sequence.
        while len(raw_messages) > 1 and raw_messages[1]["role"] == "assistant":
            raw_messages.pop(1)

        messages = self._merge_consecutive_roles(raw_messages)

        log.info(f"Chat message for user={user_id}, lang={language}")

        # Stream + collect response
        full_response = []
        
        # Robust filtering state
        in_reasoning = False
        buffer = ""

        provider = self._get_provider(language)
        async for token in provider.stream(messages, language):
            buffer += token
            
            # Simple state-based filter for <think> blocks
            while True:
                if not in_reasoning:
                    if "<think" in buffer.lower():
                        # Start of reasoning block detected
                        start_idx = buffer.lower().find("<think")
                        # Yield everything before the tag
                        pre_content = buffer[:start_idx]
                        if pre_content:
                            full_response.append(pre_content)
                            yield pre_content
                        
                        buffer = buffer[start_idx:]
                        in_reasoning = True
                        continue
                    else:
                        # No reasoning start in buffer, yield it
                        # Careful: if buffer has partial "<thi", wait for more tokens
                        if any(buffer.lower().startswith(s) for s in ["<", "<t", "<th", "<thi", "<thin", "<think"]):
                            break # Wait for full tag or mismatch
                        
                        if buffer:
                            full_response.append(buffer)
                            yield buffer
                            buffer = ""
                        break
                else:
                    if "</think>" in buffer.lower():
                        # End of reasoning block found
                        end_idx = buffer.lower().find("</think>") + len("</think>")
                        buffer = buffer[end_idx:]
                        in_reasoning = False
                        continue
                    else:
                        # Still in reasoning, swallow the buffer
                        # but keep a small end-segment in case tag is split
                        if len(buffer) > 10:
                            buffer = buffer[-10:] # Keep potential closing tag fragment
                        break

        # Yield any remaining non-reasoning buffer
        if not in_reasoning and buffer:
            full_response.append(buffer)
            yield buffer

        # Save assistant response
        if full_response:
            self.repo.add_message(user_id, "assistant", "".join(full_response), language)

    def get_history(self, user_id: str) -> list[dict]:
        return self.repo.get_history(user_id, limit=50)

    def clear_history(self, user_id: str):
        self.repo.clear_history(user_id)
