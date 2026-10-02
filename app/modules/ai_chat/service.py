"""
AI chat service — manages context window, builds system prompt, streams via LLM provider.
Dependency-injected: receives ILLMProvider, so test with MockLLMProvider if needed.
"""
from typing import AsyncGenerator

from app.modules.ai_chat.providers.base import ILLMProvider
from app.modules.ai_chat.providers.ollama_provider import OllamaProvider, get_ollama_instance
from app.modules.ai_chat.providers.jev_provider import JevProvider
from app.modules.ai_chat.repository import ChatRepository
from app.core.logger import get_logger

log = get_logger("AI_CHAT")

SYSTEM_PROMPT_EN = """You are SkillBridge AI, a friendly career guidance assistant for India's workforce. \
User's name is {name}, type is {user_type}, location is {state}. \
Their career interests are {interests}. \
Help them with career advice, skill recommendations, and job search tips. Be concise and practical, engaging and direct.
Respond in English or Hinglish (Hindi + English) based on how the user talks to you.
Use Markdown for structure (e.g., **bold**, lists).
Never include <think> or <thinking> tags in responses. Return only the final answer.
"""

SYSTEM_PROMPT_HI = """आप SkillBridge AI हैं, भारत के कार्यबल के लिए एक मित्रवत करियर मार्गदर्शन सहायक। \
उपयोगकर्ता का नाम {name} है, प्रकार {user_type} है, स्थान {state} है। \
उनके करियर हितों में {interests} शामिल हैं। \
केवल स्पष्ट हिंदी में उत्तर दें। करियर सलाह, कौशल सिफारिशें और नौकरी खोज युक्तियाँ दें। \
संरचना के लिए Markdown का उपयोग करें (जैसे **मोटा अक्षर**, सूचियाँ)।"""

class ChatService:
    def __init__(self, repo: ChatRepository):
        self.repo = repo
        self.provider = get_ollama_instance()
        self.jev = JevProvider()

    def _get_provider(self, language: str) -> ILLMProvider:
        # Semantic Multi-Provider Router: Prefer local Ollama if online; fallback to Gemini
        try:
            from app.modules.ai_chat.providers.gemini import get_gemini_instance
            gemini = get_gemini_instance()
            # If Ollama instance is configured, check if Gemini should be used as primary cloud or fallback
            if gemini.model is not None:
                return gemini
        except Exception:
            pass
        return self.provider

    def _find_matching_grounded_jobs(self, query: str, state: str) -> list[dict]:
        """Deterministic retrieval pre-flight: extracts verified active jobs to prevent hallucination."""
        try:
            from pathlib import Path
            import json
            seed_path = Path(__file__).resolve().parents[3] / "seed_jobs.json"
            if not seed_path.is_file():
                return []
            with open(seed_path, "r", encoding="utf-8") as f:
                jobs = json.load(f)

            q_lower = query.lower()
            state_lower = state.lower()
            matches = []
            for j in jobs:
                title_match = any(w in j.get("title", "").lower() for w in q_lower.split() if len(w) > 3)
                cat_match = j.get("category", "").lower() in q_lower
                skills_match = any(s.lower() in q_lower for s in j.get("required_skills", []))
                loc_match = j.get("location_state", "").lower() == state_lower or j.get("location_city", "").lower() in q_lower

                score = (2 if title_match else 0) + (2 if skills_match else 0) + (1 if loc_match else 0) + (1 if cat_match else 0)
                if score > 0:
                    matches.append((score, j))

            matches.sort(key=lambda x: x[0], reverse=True)
            return [m[1] for m in matches[:3]]
        except Exception:
            return []

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

        # Jev System 1 Guardrail & Triage
        triage = await self.jev.check_chat_guardrails(content)
        if not triage.get("is_safe", True):
            yield "I am here to help you with your career and professional growth. Please let me know how I can support your learning or job search goals."
            return

        if triage.get("is_distress", False):
            yield "It sounds like you are going through a very tough time. Please reach out to trusted friends, family, or professional helpline services. Your well-being comes first."
            return

        intent = triage.get("intent", "career_guidance")
        name = (profile or {}).get("full_name") or user.get("email", "there").split("@")[0].title()
        state = (profile or {}).get("state") or "India"

        # Tier 0 Semantic Fast Path: Instant Greeting with 0 LLM calls (<2ms)
        if intent == "greeting" and len(content.split()) <= 4:
            greeting_text = (
                f"Namaste {name}! I am SkillBridge AI, your career assistant in {state}. "
                "How can I assist your career growth, job search, or skill assessments today?"
                if language != "hi" else
                f"नमस्ते {name}! मैं SkillBridge AI हूँ, {state} में आपका करियर मार्गदर्शन सहायक। "
                "आज मैं आपकी नौकरी खोज, करियर सलाह या कौशल मूल्यांकन में क्या मदद कर सकता हूँ?"
            )
            self.repo.add_message(user_id, "assistant", greeting_text, language)
            yield greeting_text
            return

        history = self.repo.get_history(user_id, limit=11)
        system_prompt = self._build_system_prompt(user, profile, prefs, language)

        # Tier 0 Retrieval Grounding: Inject real database job postings when user asks about jobs
        if intent == "job_search":
            grounded_jobs = self._find_matching_grounded_jobs(content, state)
            if grounded_jobs:
                job_lines = [
                    f"- {j.get('title')} at {j.get('company')} ({j.get('location_city')}, {j.get('location_state')}) | Salary: ₹{j.get('salary_min', 0):,}-₹{j.get('salary_max', 0):,}/mo | Skills: {', '.join(j.get('required_skills', []))}"
                    for j in grounded_jobs
                ]
                system_prompt += (
                    "\n\n[VERIFIED ACTIVE JOB OPENINGS IN DATABASE]:\n"
                    + "\n".join(job_lines)
                    + "\n\nInstruction: Recommend and quote these verified openings directly to the user. Do not invent fake jobs or placeholder companies."
                )

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
