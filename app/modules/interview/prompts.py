"""
prompts.py — Prompts and fallback questions for mock interviews.
"""

QUESTION_PROMPT = """You are an expert HR interviewer for the Indian job market.
Generate {count} interview questions for the role: {role}.
Questions should be practical, behavioural, and appropriate for a candidate with skills: {skills}.
Return JSON only:
{{"questions": [{{"id": 1, "question": "...", "type": "behavioural/technical/situational"}}]}}"""

SCORE_PROMPT = """You are an expert interviewer scoring a mock interview answer.
Role: {role}
Question: {question}
Candidate Answer: {answer}

Score from 1-10 and provide brief feedback. Return JSON only:
{{"score": 7, "feedback": "...", "keywords_matched": ["...", "..."], "improvement": "one improvement tip"}}"""

REPORT_PROMPT = """You are an expert HR consultant. Summarize this mock interview performance.
Role: {role}
Questions and Scores:
{qa_summary}

Provide a comprehensive report. Return JSON only:
{{"overall_score": 7.5, "grade": "B+", "strengths": ["...", "..."], "areas_to_improve": ["...", "..."],
"recommendation": "Ready for interviews / Needs more preparation", "summary": "..."}}"""


def get_default_questions(role: str, count: int) -> list[dict]:
    """Fallback questions when LLM is unavailable."""
    return [
        {"id": 1, "question": f"Can you describe your experience and core projects related to {role}?", "type": "technical"},
        {"id": 2, "question": "Tell me about a time you faced a difficult problem on a deadline. How did you resolve it?", "type": "behavioural"},
        {"id": 3, "question": f"Which tools and technologies do you rely on most when executing {role} tasks?", "type": "technical"},
        {"id": 4, "question": "How do you handle disagreement with a colleague or manager regarding technical implementation?", "type": "situational"},
        {"id": 5, "question": "Where do you see yourself professionally in the next two to three years?", "type": "behavioural"}
    ][:count]
