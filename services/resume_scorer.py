import re
from typing import Optional
from models.resume_analysis_models import StructuredProfile, QualityScores

def calculate_quality_scores(
    profile: StructuredProfile,
    raw_text: str,
    target_role: Optional[str] = None
) -> QualityScores:
    """
    Calculates various quality scores for a resume based on the extracted profile and raw text.
    This is entirely rule-based and does not use LLMs.
    """
    
    # 1. ATS Compatibility (0-100)
    ats_score = 100
    ats_issues = []
    
    # Penalties
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
    
    # Pattern for very long lines (suggests tables or columns ATS hates)
    lines = raw_text.split('\n')
    long_lines_count = sum(1 for line in lines if len(line) > 120)
    if long_lines_count > 5:
        ats_score -= 15
        ats_issues.append("Possible table or multi-column layout detected")
        
    ats_score = max(0, ats_score)

    # 2. Quantification Score (0-100)
    total_bullets = 0
    achievement_bullets = 0
    for exp in profile.experiences:
        total_bullets += len(exp.achievements) + len(exp.responsibilities)
        achievement_bullets += len(exp.achievements)
    
    quantification_score = (achievement_bullets / total_bullets * 100) if total_bullets > 0 else 0
    quantification_score = min(100, int(quantification_score))

    # 3. Section Completeness (0-100)
    sections = [
        profile.has_summary_section,
        bool(profile.skills),
        bool(profile.experiences),
        bool(profile.education),
        bool(profile.certifications),
        bool(profile.contact_email or profile.contact_phone),
        profile.has_linkedin
    ]
    missing_sections = []
    if not profile.has_summary_section: missing_sections.append("Summary")
    if not profile.skills: missing_sections.append("Skills")
    if not profile.experiences: missing_sections.append("Experience")
    if not profile.education: missing_sections.append("Education")
    if not profile.certifications: missing_sections.append("Certifications")
    if not (profile.contact_email or profile.contact_phone): missing_sections.append("Contact Info")
    if not profile.has_linkedin: missing_sections.append("LinkedIn")

    section_completeness = int((sum(sections) / len(sections)) * 100)

    # 4. Readability Score (0-100)
    readability_score = 85
    
    # Sentence length penalty (> 25 words)
    # Very rough approximation
    sentences = re.split(r'[.!?]+', raw_text)
    long_sentences = sum(1 for s in sentences if len(s.split()) > 25)
    readability_score -= (long_sentences * 2)
    
    # Passive voice indicators
    passive_indicators = ["was responsible for", "was involved in", "was tasked with", "duties included"]
    for indicator in passive_indicators:
        count = raw_text.lower().count(indicator)
        readability_score -= (count * 3)
        
    readability_score = max(0, min(100, readability_score))

    # 5. Keyword Relevance (0-100, Optional)
    keyword_relevance = None
    if target_role:
        keywords = set(target_role.lower().split())
        # Filter small words
        keywords = {kw for kw in keywords if len(kw) > 3}
        matches = 0
        for kw in keywords:
            if kw in raw_text.lower():
                matches += 1
        
        if keywords:
            keyword_relevance = int((matches / len(keywords)) * 100)
            keyword_relevance = min(100, keyword_relevance)

    # 6. Overall Score (Weighted Average)
    # Weights: ATS (25%), Quantification (30%), Completeness (20%), Readability (25%)
    if keyword_relevance is not None:
        # Blend in keyword relevance at 15%, reducing others
        overall = (
            ats_score * 0.20 +
            quantification_score * 0.25 +
            section_completeness * 0.20 +
            readability_score * 0.20 +
            keyword_relevance * 0.15
        )
    else:
        overall = (
            ats_score * 0.25 +
            quantification_score * 0.30 +
            section_completeness * 0.20 +
            readability_score * 0.25
        )
        
    return QualityScores(
        ats_compatibility=int(ats_score),
        quantification_score=quantification_score,
        section_completeness=section_completeness,
        readability_score=int(readability_score),
        keyword_relevance=keyword_relevance,
        overall=int(overall),
        ats_issues=ats_issues,
        missing_sections=missing_sections
    )
