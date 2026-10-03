"""
grounding.py — Deterministic retrieval pre-flight for grounded job matching.
Extracts verified active jobs from database seed to prevent hallucination.
"""
import json
from pathlib import Path
from typing import List, Dict, Any


def find_matching_grounded_jobs(query: str, state: str) -> List[Dict[str, Any]]:
    """Retrieves verified active jobs matching user query and state."""
    try:
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
