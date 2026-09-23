import re

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'(?:\+?91[\s\-]?)?(?:0)?[6-9]\d{4}[\s\-]?\d{5}\b|(?:\+?91[\s\-]?)?[6-9]\d{9}\b')
LINKEDIN_REGEX = re.compile(r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_\-\.]+')
GITHUB_REGEX = re.compile(r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_\-\.]+')

SECTION_HEADERS = {
    "summary": re.compile(r'^(?:professional\s+summary|summary|profile|about\s+me|career\s+objective)\b', re.IGNORECASE | re.MULTILINE),
    "experience": re.compile(r'^(?:work\s+experience|professional\s+experience|experience|employment\s+history|internships?)\b', re.IGNORECASE | re.MULTILINE),
    "education": re.compile(r'^(?:education|academic\s+qualifications|academics|qualifications)\b', re.IGNORECASE | re.MULTILINE),
    "skills": re.compile(r'^(?:technical\s+skills|skills|core\s+competencies|key\s+skills|tools\s+&\s+technologies|technical\s+proficiency)\b', re.IGNORECASE | re.MULTILINE),
    "projects": re.compile(r'^(?:projects|key\s+projects|academic\s+projects|personal\s+projects)\b', re.IGNORECASE | re.MULTILINE),
    "certifications": re.compile(r'^(?:certifications|certificates|licenses\s+&\s+certifications)\b', re.IGNORECASE | re.MULTILINE),
    "achievements": re.compile(r'^(?:achievements|honors\s+&\s+awards|awards|accomplishments)\b', re.IGNORECASE | re.MULTILINE),
}


def extract_contact_info(text: str, links: list[str] = None) -> dict:
    """Extract candidate contact details and online profiles from text and extracted URLs."""
    all_content = f"{text}\n" + "\n".join(links or [])

    emails = EMAIL_REGEX.findall(all_content)
    phones = PHONE_REGEX.findall(all_content)
    linkedin = LINKEDIN_REGEX.findall(all_content)
    github = GITHUB_REGEX.findall(all_content)

    portfolio_candidates = []
    for link in (links or []):
        lower = link.lower()
        if not any(d in lower for d in ["linkedin.com", "github.com", "mailto:", "tessdata", "google.com"]):
            portfolio_candidates.append(link)

    return {
        "email": emails[0] if emails else None,
        "phone": phones[0] if phones else None,
        "linkedin": linkedin[0] if linkedin else None,
        "github": github[0] if github else None,
        "portfolio": portfolio_candidates[0] if portfolio_candidates else None
    }


def segment_sections(text: str) -> dict[str, str]:
    """Segment resume into canonical sections using boundary detection."""
    lines = text.split("\n")
    sections: dict[str, list[str]] = {"header": []}
    current_section = "header"

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        matched_section = None
        for sec_name, pattern in SECTION_HEADERS.items():
            if pattern.match(stripped) and len(stripped) < 45:
                matched_section = sec_name
                break

        if matched_section:
            current_section = matched_section
            if current_section not in sections:
                sections[current_section] = []
        else:
            sections[current_section].append(stripped)

    return {k: "\n".join(v) for k, v in sections.items() if v}
