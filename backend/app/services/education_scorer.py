import re


DEGREE_LEVELS = {
    "phd": 5,
    "doctorate": 5,

    "master": 4,
    "masters": 4,
    "m.tech": 4,
    "mtech": 4,
    "m.sc": 4,
    "msc": 4,
    "mba": 4,

    "bachelor": 3,
    "bachelors": 3,
    "b.tech": 3,
    "btech": 3,
    "b.e": 3,
    "be": 3,
    "b.sc": 3,
    "bsc": 3,
    "bca": 3,

    "diploma": 2,

    "higher secondary": 1,
    "12th": 1,
    "10+2": 1,

    "secondary": 0,
    "10th": 0
}


FIELD_KEYWORDS = [
    "computer science",
    "computer engineering",
    "information technology",
    "software engineering",
    "data science",
    "artificial intelligence",
    "electronics",
    "electrical",
    "mechanical",
    "civil"
]


def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def detect_degree_levels(text: str) -> list:
    text = normalize_text(text)

    found_levels = []

    for degree, level in DEGREE_LEVELS.items():
        pattern = rf"(?<!\w){re.escape(degree)}(?!\w)"

        if re.search(pattern, text):
            found_levels.append(
                {
                    "degree": degree,
                    "level": level
                }
            )

    return found_levels


def get_highest_degree_level(text: str) -> int:
    degrees = detect_degree_levels(text)

    if not degrees:
        return -1

    return max(item["level"] for item in degrees)


def detect_field_match(
    education_text: str,
    job_description: str
) -> dict:

    education_lower = normalize_text(education_text)
    jd_lower = normalize_text(job_description)

    resume_fields = []
    required_fields = []
    excluded_fields = []

    # Detect fields in resume
    for field in FIELD_KEYWORDS:
        if field in education_lower:
            resume_fields.append(field)

    # Split JD into sentences
    sentences = re.split(
        r"[.\n;]+",
        jd_lower
    )

    exclusion_phrases = [
        "not considered equivalent",
        "not accepted",
        "not eligible",
        "not considered",
        "not allowed",
        "will not be considered",
        "excluding",
        "except"
    ]

    requirement_phrases = [
        "required",
        "requirement",
        "must have",
        "must hold",
        "degree in",
        "qualification",
        "qualifications"
    ]

    # Analyze each sentence separately
    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        sentence_fields = []

        for field in FIELD_KEYWORDS:
            if field in sentence:
                sentence_fields.append(field)

        if not sentence_fields:
            continue

        is_exclusion_sentence = any(
            phrase in sentence
            for phrase in exclusion_phrases
        )

        if is_exclusion_sentence:
            for field in sentence_fields:
                if field not in excluded_fields:
                    excluded_fields.append(field)

            continue

        is_requirement_sentence = any(
            phrase in sentence
            for phrase in requirement_phrases
        )

        if is_requirement_sentence:
            for field in sentence_fields:
                if field not in required_fields:
                    required_fields.append(field)

    # Remove accidentally conflicting fields
    required_fields = [
        field
        for field in required_fields
        if field not in excluded_fields
    ]

    # If JD mentions no specific field requirement
    if not required_fields and not excluded_fields:
        return {
            "field_required": False,
            "field_match": True,
            "required_fields": [],
            "excluded_fields": [],
            "resume_fields": resume_fields
        }

    # Resume contains explicitly excluded field
    excluded_match = any(
        field in resume_fields
        for field in excluded_fields
    )

    # Resume contains accepted/required field
    required_match = any(
        field in resume_fields
        for field in required_fields
    )

    # If the candidate has an explicitly excluded field,
    # the field requirement must fail.
    if excluded_match:
        field_match = False

    # If specific required fields exist,
    # at least one must match.
    elif required_fields:
        field_match = required_match

    else:
        field_match = True

    return {
        "field_required": bool(required_fields or excluded_fields),
        "field_match": field_match,
        "required_fields": required_fields,
        "excluded_fields": excluded_fields,
        "resume_fields": resume_fields
    }
    
    
    
def detect_education_requirement(
    job_description: str
) -> dict:

    jd_lower = normalize_text(job_description)

    detected = detect_degree_levels(jd_lower)

    if not detected:
        return {
            "qualification_required": False,
            "minimum_degree_level": None,
            "detected_requirements": []
        }

    levels = [
        item["level"]
        for item in detected
    ]

    minimum_level = min(levels)

    return {
        "qualification_required": True,
        "minimum_degree_level": minimum_level,
        "detected_requirements": detected
    }


def calculate_resume_education_quality(
    education_text: str
) -> dict:

    if not education_text.strip():
        return {
            "quality_score": 0,
            "details": []
        }

    score = 0
    details = []

    # Education section exists
    score += 1
    details.append("Education section found")

    # Degree found
    degree_level = get_highest_degree_level(
        education_text
    )

    if degree_level >= 0:
        score += 1
        details.append("Degree information found")

    # Institution
    if re.search(
        r"\b(university|college|institute|school|academy|polytechnic|vidyamandir)\b",
        education_text,
        re.IGNORECASE
    ):
        score += 1
        details.append("Institution information found")

    # Academic performance
    if re.search(
        r"\b(cgpa|gpa|marks?|percentage)\b|%",
        education_text,
        re.IGNORECASE
    ):
        score += 1
        details.append("Academic performance found")

    # Timeline
    if re.search(
        r"\b(?:19|20)\d{2}\b",
        education_text
    ):
        score += 1
        details.append("Education timeline found")

    return {
        "quality_score": min(score, 5),
        "details": details
    }


def calculate_qualification_match(
    education_text: str,
    job_description: str
) -> dict:

    jd_requirement = detect_education_requirement(
        job_description
    )

    resume_level = get_highest_degree_level(
        education_text
    )

    field_result = detect_field_match(
        education_text,
        job_description
    )

    # No qualification mentioned in JD
    if not jd_requirement["qualification_required"]:

        return {
            "qualification_score": 5,
            "qualification_match": True,
            "reason": "No specific qualification requirement found in job description",
            "resume_degree_level": resume_level,
            "required_degree_level": None,
            "field_analysis": field_result
        }

    required_level = jd_requirement[
        "minimum_degree_level"
    ]

    degree_match = (
        resume_level >= 0 and resume_level >= required_level
    )

    field_match = field_result["field_match"]

    if degree_match and field_match:
        score = 5
        reason = "Resume qualification matches job requirement"

    elif degree_match and not field_match:
        score = 3
        reason = "Degree level matches but field of study does not fully match"

    elif not degree_match and field_match:
        score = 2
        reason = "Field matches but degree level is below job requirement"

    else:
        score = 0
        reason = "Resume qualification does not match job requirement"

    return {
        "qualification_score": score,
        "qualification_match": degree_match and field_match,
        "reason": reason,
        "resume_degree_level": resume_level,
        "required_degree_level": required_level,
        "detected_job_requirements": jd_requirement[
            "detected_requirements"
        ],
        "field_analysis": field_result
    }


def calculate_education_score(
    sections: dict,
    job_description: str
) -> dict:

    education_text = sections.get(
        "education",
        ""
    ).strip()

    if not education_text:
        return {
            "education_score": 0,
            "resume_quality": {
                "quality_score": 0,
                "details": []
            },
            "qualification_analysis": {
                "qualification_score": 0,
                "qualification_match": False,
                "reason": "Education section not found"
            }
        }

    quality_result = calculate_resume_education_quality(
        education_text
    )

    qualification_result = calculate_qualification_match(
        education_text,
        job_description
    )

    total_score = (
        quality_result["quality_score"]
        + qualification_result["qualification_score"]
    )

    return {
        "education_score": min(total_score, 10),
        "resume_quality": quality_result,
        "qualification_analysis": qualification_result
    }
