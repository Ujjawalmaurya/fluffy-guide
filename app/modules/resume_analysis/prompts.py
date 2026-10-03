"""
prompts.py — AI synthesis prompts for resume analysis, bullet enhancement, and summary generation.
"""

RESUME_SYNTHESIS_PROMPT = """You are an expert career analyst. Extract structured experience, education, and trajectory from this resume text.
Return ONLY valid JSON matching this schema:
{{
  "experiences": [
    {{
      "company": "Company Name",
      "role": "Job Title",
      "duration_months": 12,
      "seniority_level": "junior|mid|senior|lead|unclear",
      "skills_used": ["Skill1", "Skill2"],
      "responsibilities": ["Task description 1", "Task description 2"],
      "achievements": ["Quantified outcome 1"]
    }}
  ],
  "education": [
    {{
      "degree": "Degree/Diploma Name",
      "institution": "School/University Name",
      "year": 2022,
      "specialization": "Field of Study",
      "is_vocational": false
    }}
  ],
  "career_trajectory": {{
    "direction": "ascending|lateral|descending|unclear",
    "summary": "1-sentence career trajectory overview."
  }},
  "inferred_target_roles": ["Role 1", "Role 2", "Role 3"]
}}
"""

BULLET_IMPROVEMENT_SYSTEM_PROMPT = (
    "You are a resume expert. Improve this weak resume bullet into a strong "
    "achievement-oriented bullet. Add realistic metrics if missing. Keep it under 20 words. "
    "Return ONLY valid JSON: {\"improved\": \"str\", \"reason\": \"str\"}"
)

BATCH_BULLETS_SYSTEM_PROMPT = (
    "You are an ATS resume optimization expert. Improve each of the given weak resume bullets "
    "into strong, action-oriented bullets with realistic metrics where possible. Keep each under 25 words. "
    "Return ONLY a JSON list of objects: [{\"original\": \"...\", \"improved\": \"...\", \"reason\": \"...\"}]"
)
