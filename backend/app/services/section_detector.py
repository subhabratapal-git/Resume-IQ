import re


SECTION_ALIASES = {
    "summary": [
        "summary",
        "career summary",
        "professional summary",
        "profile",
        "objective",
        "career objective",
    ],

    "education": [
        "education",
        "academic background",
        "academic qualifications",
        "educational qualifications",
    ],

    "skills": [
        "skills",
        "technical skills",
        "key skills",
        "core skills",
    ],

    "experience": [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "internship experience",
    ],

    "training": [
        "training",
        "technical training",
        "industrial training",
        "technical training & certifications",
        "training & certifications",
        "internship",
        "internships",
    ],

    "projects": [
        "projects",
        "academic projects",
        "personal projects",
        "technical projects",
    ],

    "certifications": [
        "certifications",
        "certificates",
        "certification",
        "courses",
        "licenses & certifications",
    ],
}


def normalize_heading(text: str) -> str:
    text = text.strip().lower()

    text = re.sub(r"[:\-–—]+$", "", text)

    text = re.sub(r"\s+", " ", text)

    return text


def get_section_name(line: str):
    normalized_line = normalize_heading(line)

    for section_name, aliases in SECTION_ALIASES.items():
        if normalized_line in aliases:
            return section_name

    return None


def detect_sections(text: str) -> dict:
    sections = {}

    current_section = "header"
    sections[current_section] = []

    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        if not line:
            continue

        detected_section = get_section_name(line)

        if detected_section:
            current_section = detected_section

            if current_section not in sections:
                sections[current_section] = []

            continue

        sections[current_section].append(line)

    final_sections = {}

    for section_name, content in sections.items():
        joined_text = "\n".join(content).strip()

        if joined_text:
            final_sections[section_name] = joined_text

    return final_sections


