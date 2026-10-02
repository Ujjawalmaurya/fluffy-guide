"""
scorer.py — Rule-based resume scoring engine (ATS, quantification, completeness, readability, relevance).
Zero-LLM: runs synchronously in milliseconds with deterministic scoring logic.
"""
import re
from typing import Optional, List
from app.modules.resume_analysis.schemas import StructuredProfile, QualityScores


def _calculate_ats_score(profile: StructuredProfile, raw_text: str) -> tuple[int, List[str]]:
    ats_score = 100
    ats_issues: List[str] = []

    if profile.has_photo_mentioned:
        ats_score -= 10
        ats_issues.append("Photo detected (often filtered by ATS in some regions)")
    if not profile.contact_email:
        ats_score -= 10
        ats_issues.append("Missing contact email")
    if not profile.skills:
        ats_score -= 10
        ats_issues.append("Missing skills section")
    if not profile.experiences:
        ats_score -= 20
        ats_issues.append("Experience section absent or unreadable")
    if profile.has_caste_religion_info:
        ats_score -= 10
        ats_issues.append("Sensitive info detected (caste/religion)")

    lines = raw_text.split("\n")
    long_lines_count = sum(1 for line in lines if len(line) > 120)
    if long_lines_count > 5:
        ats_score -= 15
        ats_issues.append("Possible table or multi-column layout detected")

    return max(0, ats_score), ats_issues


def _calculate_quantification_score(profile: StructuredProfile) -> int:
    total_bullets = 0
    achievement_bullets = 0
    for exp in profile.experiences:
        total_bullets += len(exp.achievements) + len(exp.responsibilities)
        achievement_bullets += len(exp.achievements)

    if total_bullets == 0:
        return 0
    return min(100, int((achievement_bullets / total_bullets) * 100))


def _calculate_section_completeness(profile: StructuredProfile) -> tuple[int, List[str]]:
    sections = [
        profile.has_summary_section,
        bool(profile.skills),
        bool(profile.experiences),
        bool(profile.education),
        bool(profile.certifications),
        bool(profile.contact_email or profile.contact_phone),
        profile.has_linkedin,
    ]
    missing_sections: List[str] = []
    if not profile.has_summary_section:
        missing_sections.append("Summary")
    if not profile.skills:
        missing_sections.append("Skills")
    if not profile.experiences:
        missing_sections.append("Experience")
    if not profile.education:
        missing_sections.append("Education")
    if not profile.certifications:
        missing_sections.append("Certifications")
    if not (profile.contact_email or profile.contact_phone):
        missing_sections.append("Contact Info")
    if not profile.has_linkedin:
        missing_sections.append("LinkedIn")

    completeness = int((sum(sections) / len(sections)) * 100)
    return completeness, missing_sections


def _calculate_readability_score(raw_text: str) -> int:
    readability_score = 85
    sentences = re.split(r"[.!?]+", raw_text)
    long_sentences = sum(1 for s in sentences if len(s.split()) > 25)
    readability_score -= long_sentences * 2

    passive_indicators = ["was responsible for", "was involved in", "was tasked with", "duties included"]
    for indicator in passive_indicators:
        count = raw_text.lower().count(indicator)
        readability_score -= count * 3

    return max(0, min(100, readability_score))


def _calculate_keyword_relevance(raw_text: str, target_roles: Optional[List[str]]) -> Optional[int]:
    if not target_roles:
        return None

    role_scores = []
    raw_lower = raw_text.lower()
    for role in target_roles:
        keywords = {kw for kw in role.lower().split() if len(kw) > 3}
        if not keywords:
            continue
        matches = sum(1 for kw in keywords if kw in raw_lower)
        role_scores.append(int((matches / len(keywords)) * 100))

    if not role_scores:
        return None
    return min(100, max(role_scores))


def calculate_quality_scores(
    profile: StructuredProfile,
    raw_text: str,
    target_roles: Optional[List[str]] = None,
) -> QualityScores:
    """
    Calculates various quality scores for a resume based on the extracted profile and raw text.
    Entirely rule-based: runs deterministically without LLM calls.
    """
    ats_score, ats_issues = _calculate_ats_score(profile, raw_text)
    quantification_score = _calculate_quantification_score(profile)
    section_completeness, missing_sections = _calculate_section_completeness(profile)
    readability_score = _calculate_readability_score(raw_text)
    keyword_relevance = _calculate_keyword_relevance(raw_text, target_roles)

    if keyword_relevance is not None:
        overall = (
            ats_score * 0.20
            + quantification_score * 0.25
            + section_completeness * 0.20
            + readability_score * 0.20
            + keyword_relevance * 0.15
        )
    else:
        overall = (
            ats_score * 0.25
            + quantification_score * 0.30
            + section_completeness * 0.20
            + readability_score * 0.25
        )

    return QualityScores(
        ats_compatibility=int(ats_score),
        quantification_score=quantification_score,
        section_completeness=section_completeness,
        readability_score=int(readability_score),
        keyword_relevance=keyword_relevance,
        overall=int(overall),
        ats_issues=ats_issues,
        missing_sections=missing_sections,
    )
