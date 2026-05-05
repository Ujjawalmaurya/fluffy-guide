# Gap Analysis AI Pipeline
from typing import List, Dict, Optional
import asyncio

class GapAnalysisAIPipeline:
    def __init__(self, model_name: str = "qwen2.5:0.5b"):
        self.model_name = model_name
        self.MAX_RETRIES = 2
        self.RETRY_DELAY = 1

    async def analyze_learnability(self, gaps: List[str]) -> Dict[str, float]:
        """
        Estimate learnability_weeks for each gap using LLM.
        Returns a dict mapping skill_name to weeks (float).
        """
        # 1. Prompt construction (pre-processed structured data)
        # 2. Call LLM (Ollama)
        # 3. Strip <think> tags
        # 4. Pydantic healing / JSON extraction
        # 5. Return safe defaults if failure
        
        # Stub implementation
        return {skill: 2.0 for skill in gaps}

    async def generate_mentorship_message(self, top_gap: str) -> str:
        """
        Generate a motivating message for the user's primary gap.
        """
        return f"Focusing on {top_gap} will significantly boost your career prospects."
