import re

from app.services.keyword_matcher import extract_keywords


TECHNICAL_ACTION_WORDS = {
    "developed",
    "develop",
    "built",
    "implemented",
    "designed",
    "created",
    "integrated",
    "trained",
    "optimized",
    "deployed",
    "tested",
    "analyzed",
    "processed",
    "automated",
    "used",
    "utilized",
}


from app.services.skill_extractor import extract_skills


def calculate_project_relevance(
    project_text: str,
    job_description: str,
    job_skills: list = None
) -> dict:

    project_keywords = extract_keywords(project_text)
    job_keywords = extract_keywords(job_description)

    # If job_skills not provided, extract from job_description
    if not job_skills:
        job_skills = extract_skills(job_description)

    project_lower = project_text.lower()
    project_lookup = {keyword.lower() for keyword in project_keywords}

    # Match JD skills in project text
    matched_skills = []
    missing_skills = []

    for skill in (job_skills or []):
        sk_low = skill.lower()
        # Direct word boundary or text match
        pattern = rf"\b{re.escape(sk_low)}\b"
        if re.search(pattern, project_lower) or sk_low in project_lookup:
            matched_skills.append(skill)
        else:
            missing_skills.append(skill)

    # Also compute general keyword match
    matched_keywords = []
    missing_keywords = []
    for keyword in job_keywords:
        if keyword.lower() in project_lookup:
            matched_keywords.append(keyword)
        else:
            missing_keywords.append(keyword)

    if job_skills and len(job_skills) > 0:
        skill_alignment_pct = round((len(matched_skills) / len(job_skills)) * 100, 2)
    elif job_keywords and len(job_keywords) > 0:
        skill_alignment_pct = round((len(matched_keywords) / len(job_keywords)) * 100, 2)
    else:
        skill_alignment_pct = 50.0

    return {
        "project_keywords": project_keywords,
        "matched_job_keywords": matched_keywords,
        "missing_job_keywords": missing_keywords,
        "matched_jd_skills": matched_skills,
        "missing_jd_skills": missing_skills,
        "skill_alignment_pct": skill_alignment_pct,
        "relevance_percentage": skill_alignment_pct
    }


def calculate_project_score(
    sections: dict,
    job_description: str,
    job_skills: list = None
) -> dict:

    project_text = sections.get(
        "projects",
        ""
    ).strip()

    if not project_text:
        return {
            "project_score": 0,
            "project_strength": "missing",
            "issues": [
                "Projects section not found"
            ],
            "project_analysis": {
                "relevance_percentage": 0,
                "matched_job_keywords": []
            }
        }

    score = 0
    issues = []
    details = []

    # -----------------------------------------
    # 1. Projects section present = 2 marks
    # -----------------------------------------

    score += 2

    details.append(
        "Projects section found"
    )

    # -----------------------------------------
    # 2. Sufficient project content = 1 mark
    # -----------------------------------------

    word_count = len(
        re.findall(
            r"\b\w+\b",
            project_text
        )
    )

    if word_count >= 40:
        score += 1

        details.append(
            "Projects contain sufficient description"
        )

    else:
        issues.append(
            "Project descriptions are too short"
        )

    # -----------------------------------------
    # 3. Technical evidence = 2 marks
    # -----------------------------------------

    project_keywords = extract_keywords(
        project_text
    )

    technical_keyword_count = len(
        project_keywords
    )

    if technical_keyword_count >= 5:
        score += 2

        details.append(
            "Strong technical evidence found in projects"
        )

    elif technical_keyword_count >= 2:
        score += 1

        details.append(
            "Some technical evidence found in projects"
        )

        issues.append(
            "Projects contain limited technical detail"
        )

    else:
        issues.append(
            "Projects lack clear technical evidence"
        )

    # -----------------------------------------
    # 4. Implementation/action evidence = 1 mark
    # -----------------------------------------

    project_lower = project_text.lower()

    detected_actions = []

    for action in TECHNICAL_ACTION_WORDS:

        pattern = rf"\b{re.escape(action)}\b"

        if re.search(
            pattern,
            project_lower
        ):
            detected_actions.append(
                action
            )

    if detected_actions:
        score += 1

        details.append(
            "Implementation evidence found"
        )

    else:
        issues.append(
            "Projects do not clearly describe implementation work"
        )

    # -----------------------------------------
    # 5. Measurable result = 1 mark
    # -----------------------------------------

    measurable_pattern = (
        r"\b\d+(?:\.\d+)?\s*%"
        r"|\b\d+(?:\.\d+)?x\b"
        r"|\b\d+\+\b"
        r"|\baccuracy\b"
        r"|\bprecision\b"
        r"|\brecall\b"
        r"|\bf1(?:-score)?\b"
        r"|\blatency\b"
        r"|\bperformance\b"
    )

    measurable_result_found = bool(
        re.search(
            measurable_pattern,
            project_text,
            re.IGNORECASE
        )
    )

    if measurable_result_found:
        score += 1

        details.append(
            "Measurable project result found"
        )

    else:
        issues.append(
            "No measurable project outcome found"
        )

    # -----------------------------------------
    # 6. JD skill relevance = dynamic 60% to 80%+ scaling
    # -----------------------------------------

    relevance_result = calculate_project_relevance(
        project_text,
        job_description,
        job_skills=job_skills
    )

    matched_jd_skills = relevance_result.get("matched_jd_skills", [])
    missing_jd_skills = relevance_result.get("missing_jd_skills", [])
    skill_alignment_pct = relevance_result.get("skill_alignment_pct", 0)

    # Dynamic scaling based on user requirements:
    # Strong match with JD skills -> 80% - 90%+
    # Low / moderate match -> 60%
    if len(matched_jd_skills) >= 3 or skill_alignment_pct >= 45:
        percentage = 85
        details.append(
            f"Projects strongly demonstrate core JD technologies: {', '.join(matched_jd_skills[:4])} (85%)."
        )
    elif len(matched_jd_skills) >= 1 or skill_alignment_pct >= 20:
        percentage = 70
        details.append(
            f"Projects demonstrate {len(matched_jd_skills)} target JD skills: {', '.join(matched_jd_skills[:3])} (70%)."
        )
        if missing_jd_skills:
            issues.append(
                f"Projects lack demonstration of key JD technologies: {', '.join(missing_jd_skills[:3])}."
            )
    else:
        percentage = 60
        issues.append(
            f"Projects show low alignment with required JD skills ({', '.join(missing_jd_skills[:4]) if missing_jd_skills else 'tech stack'}). Target at least 2 JD skills in project descriptions to reach 80%."
        )

    # Map percentage to 10-point scale
    score = round((percentage / 100.0) * 10.0, 1)

    if percentage >= 80:
        strength = "excellent"
    elif percentage >= 70:
        strength = "good"
    elif percentage >= 50:
        strength = "average"
    else:
        strength = "weak"

    return {
        "project_score": score,
        "percentage": percentage,
        "project_strength": strength,
        "word_count": word_count,
        "technical_keyword_count": technical_keyword_count,
        "detected_actions": detected_actions,
        "measurable_result_found": measurable_result_found,
        "matched_jd_skills": matched_jd_skills,
        "missing_jd_skills": missing_jd_skills,
        "details": details,
        "issues": issues,
        "project_analysis": relevance_result
    }
