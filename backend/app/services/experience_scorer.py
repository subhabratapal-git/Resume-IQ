import re

from app.services.keyword_matcher import extract_keywords


ACTION_WORDS = {
    "developed",
    "implemented",
    "designed",
    "built",
    "created",
    "worked",
    "analyzed",
    "trained",
    "optimized",
    "tested",
    "deployed",
    "automated",
    "managed",
    "maintained",
    "collaborated",
    "integrated",
    "improved",
    "used",
    "utilized",
}


def extract_experience_text(sections: dict) -> str:
    experience_text = sections.get("experience", "").strip()
    training_text = sections.get("training", "").strip()

    if experience_text and training_text:
        return experience_text + "\n" + training_text

    if experience_text:
        return experience_text

    return training_text


def detect_duration(text: str) -> dict:
    year_pattern = r"\b(?:19|20)\d{2}\b"

    month_names = (
        "jan|january|feb|february|mar|march|apr|april|"
        "may|jun|june|jul|july|aug|august|sep|sept|"
        "september|oct|october|nov|november|dec|december"
    )

    month_pattern = rf"\b(?:{month_names})\b"

    years = re.findall(
        year_pattern,
        text,
        re.IGNORECASE
    )

    months = re.findall(
        month_pattern,
        text,
        re.IGNORECASE
    )

    duration_words = re.findall(
        r"\b\d+\s*(?:month|months|year|years|week|weeks)\b",
        text,
        re.IGNORECASE
    )

    duration_found = bool(
        years
        or months
        or duration_words
    )

    return {
        "duration_found": duration_found,
        "years_detected": list(dict.fromkeys(years)),
        "duration_mentions": list(dict.fromkeys(duration_words)),
    }


def calculate_experience_relevance(
    experience_text: str,
    job_description: str
) -> dict:

    experience_keywords = extract_keywords(
        experience_text
    )

    job_keywords = extract_keywords(
        job_description
    )

    experience_lookup = {
        keyword.lower()
        for keyword in experience_keywords
    }

    matched_keywords = []
    missing_keywords = []

    for keyword in job_keywords:

        if keyword.lower() in experience_lookup:
            matched_keywords.append(keyword)

        else:
            missing_keywords.append(keyword)

    if not job_keywords:
        relevance_percentage = 0

    else:
        relevance_percentage = round(
            (
                len(matched_keywords)
                / len(job_keywords)
            ) * 100,
            2
        )

    return {
        "experience_keywords": experience_keywords,
        "matched_job_keywords": matched_keywords,
        "missing_job_keywords": missing_keywords,
        "relevance_percentage": relevance_percentage,
    }


def calculate_experience_score(
    sections: dict,
    job_description: str
) -> dict:

    experience_text = extract_experience_text(
        sections
    )

    if not experience_text:
        return {
            "experience_score": 0,
            "experience_strength": "missing",
            "details": [],
            "issues": [
                "Experience or training section not found"
            ],
            "experience_analysis": {
                "relevance_percentage": 0,
                "matched_job_keywords": []
            }
        }

    score = 0
    details = []
    issues = []

    # -----------------------------------------
    # 1. Experience/training section = 3 marks
    # -----------------------------------------

    score += 3

    details.append(
        "Experience or training section found"
    )

    # -----------------------------------------
    # 2. Sufficient description = 2 marks
    # -----------------------------------------

    word_count = len(
        re.findall(
            r"\b\w+\b",
            experience_text
        )
    )

    if word_count >= 60:
        score += 2

        details.append(
            "Experience contains sufficient description"
        )

    elif word_count >= 25:
        score += 1

        details.append(
            "Experience contains some description"
        )

        issues.append(
            "Experience description is limited"
        )

    else:
        issues.append(
            "Experience description is too short"
        )

    # -----------------------------------------
    # 3. Duration evidence = 2 marks
    # -----------------------------------------

    duration_result = detect_duration(
        experience_text
    )

    if duration_result["duration_found"]:
        score += 2

        details.append(
            "Experience duration found"
        )

    else:
        issues.append(
            "Experience duration not clearly mentioned"
        )

    # -----------------------------------------
    # 4. Technical evidence = 2 marks
    # -----------------------------------------

    experience_keywords = extract_keywords(
        experience_text
    )

    technical_keyword_count = len(
        experience_keywords
    )

    if technical_keyword_count >= 5:
        score += 2

        details.append(
            "Strong technical evidence found in experience"
        )

    elif technical_keyword_count >= 2:
        score += 1

        details.append(
            "Some technical evidence found in experience"
        )

        issues.append(
            "Experience contains limited technical detail"
        )

    else:
        issues.append(
            "Experience lacks clear technical evidence"
        )

    # -----------------------------------------
    # 5. Action / responsibility evidence = 2 marks
    # -----------------------------------------

    experience_lower = experience_text.lower()

    detected_actions = []

    for action in ACTION_WORDS:

        pattern = rf"\b{re.escape(action)}\b"

        if re.search(
            pattern,
            experience_lower
        ):
            detected_actions.append(action)

    if len(detected_actions) >= 3:
        score += 2

        details.append(
            "Strong responsibility and action evidence found"
        )

    elif detected_actions:
        score += 1

        details.append(
            "Some responsibility evidence found"
        )

        issues.append(
            "Experience could show more responsibility evidence"
        )

    else:
        issues.append(
            "Experience does not clearly describe responsibilities"
        )

    # -----------------------------------------
    # 6. JD relevance = maximum 4 marks
    # -----------------------------------------

    relevance_result = calculate_experience_relevance(
        experience_text,
        job_description
    )

    relevance = relevance_result[
        "relevance_percentage"
    ]

    if relevance >= 60:
        relevance_score = 4

    elif relevance >= 40:
        relevance_score = 3

    elif relevance >= 20:
        relevance_score = 2

    elif relevance > 0:
        relevance_score = 1

    else:
        relevance_score = 0

    score += relevance_score

    if relevance_score == 0:
        issues.append(
            "Experience shows little relevance to the job description"
        )

    elif relevance_score == 1:
        issues.append(
            "Experience has low relevance to the job description"
        )

    elif relevance_score == 2:
        details.append(
            "Experience has some relevance to the job description"
        )

    elif relevance_score == 3:
        details.append(
            "Experience has good relevance to the job description"
        )

    else:
        details.append(
            "Experience has strong relevance to the job description"
        )

    # -----------------------------------------
    # Final score
    # -----------------------------------------

    score = min(score, 15)

    if score >= 13:
        strength = "excellent"

    elif score >= 10:
        strength = "good"

    elif score >= 7:
        strength = "average"

    else:
        strength = "weak"

    return {
        "experience_score": score,
        "experience_strength": strength,
        "word_count": word_count,
        "technical_keyword_count": technical_keyword_count,
        "detected_actions": detected_actions,
        "duration_analysis": duration_result,
        "details": details,
        "issues": issues,
        "experience_analysis": relevance_result,
    }


def detect_fresher_duration_months(text: str) -> float:
    """
    Detects duration in months from experience, internship, or project descriptions.
    Supports direct mentions ('3 months', '6-month internship') and month-year ranges.
    """
    if not text:
        return 0.0

    max_months = 0.0

    # 1. Direct month mentions like '3 months', '6 month', '2.5 months', '4-month'
    month_matches = re.findall(r"\b(\d+(?:\.\d+)?)\s*(?:-|–|\s)?\s*(?:months?|mths?|mo)\b", text, re.IGNORECASE)
    for m in month_matches:
        try:
            val = float(m)
            if 0.5 <= val <= 36:
                max_months = max(max_months, val)
        except ValueError:
            pass

    # 2. Week mentions like '8 weeks' -> weeks / 4.0
    week_matches = re.findall(r"\b(\d+)\s*(?:weeks?|wks?)\b", text, re.IGNORECASE)
    for w in week_matches:
        try:
            val = float(w) / 4.0
            if 0.5 <= val <= 24:
                max_months = max(max_months, val)
        except ValueError:
            pass

    # 3. Keyword hints
    if re.search(r"\b(?:summer\s+internship|winter\s+internship)\b", text, re.IGNORECASE):
        max_months = max(max_months, 2.0)
    if re.search(r"\b(?:six\s+months?|6\s+months?)\s+(?:industrial\s+training|internship)\b", text, re.IGNORECASE):
        max_months = max(max_months, 6.0)

    # 4. Date ranges like 'Jan 2024 - Mar 2024' or 'June - August 2023'
    MONTH_MAP = {
        "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
        "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
        "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10, "october": 10,
        "nov": 11, "november": 11, "dec": 12, "december": 12
    }
    range_pattern = r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december)\b(?:\s+\d{4})?\s*(?:-|–|to)\s*\b(jan|feb|mar|apr|may|jun|jul|aug|sep|sept|oct|nov|dec|january|february|march|april|june|july|august|september|october|november|december)\b(?:\s+(\d{4}))?"
    for m1, m2, y in re.findall(range_pattern, text, re.IGNORECASE):
        idx1 = MONTH_MAP.get(m1.lower(), 1)
        idx2 = MONTH_MAP.get(m2.lower(), 1)
        diff = idx2 - idx1 + 1 if idx2 >= idx1 else (12 - idx1 + idx2 + 1)
        if 1 <= diff <= 12:
            max_months = max(max_months, float(diff))

    return max_months


def calculate_fresher_experience_score(
    sections: dict,
    resume_skills: list,
    job_description: str
) -> dict:
    """
    Specialized scoring for Freshers:
    If technical skills exist on the CV, score scales based on internship/training duration:
      - 1 to 2 months: 50%
      - 2 to 3 months: 60%
      - 3 to 4 months: 70%
      - 4 to 6 months+: 80%
    """
    exp_text = extract_experience_text(sections)
    proj_text = sections.get("projects", "")
    full_search_text = f"{exp_text}\n{proj_text}"

    has_tech_skills = bool(resume_skills and len(resume_skills) > 0)
    detected_months = detect_fresher_duration_months(full_search_text)

    details = []
    issues = []

    if has_tech_skills:
        details.append(f"Verified technical skills profile ({len(resume_skills)} core competencies identified).")

        if detected_months >= 4.0:
            percentage = 80
            details.append(f"Internship / training duration ({round(detected_months, 1)} months) satisfies entry-level industry benchmark (80%).")
        elif detected_months >= 3.0:
            percentage = 70
            details.append(f"Hands-on internship / project duration detected: {round(detected_months, 1)} months (70%).")
            issues.append("Extending hands-on internship or project duration to 4–6 months will increase your rating to 80%.")
        elif detected_months >= 2.0:
            percentage = 60
            details.append(f"Found {round(detected_months, 1)} months internship / training experience (60%).")
            issues.append("Target at least 3–6 months of hands-on internship experience to unlock higher ATS placement.")
        elif detected_months >= 1.0:
            percentage = 50
            details.append(f"Found {round(detected_months, 1)} month practical learning / internship experience (50%).")
            issues.append("Highlighting 3+ months of structured internship or technical training will raise your score to 70%+.")
        else:
            # Technical skills present, but no explicit duration mentioned
            percentage = 50
            details.append("Technical skills validated across profile (50% entry-level baseline).")
            issues.append("Specify clear duration for your internships, training, or capstone projects (e.g., '3 months', 'June–August') to unlock 70–80%.")
    else:
        percentage = 35
        issues.append("No technical skills or practical internship duration found on resume.")

    score = round((percentage / 100.0) * 15.0, 1)

    return {
        "experience_score": score,
        "percentage": percentage,
        "experience_strength": "good" if percentage >= 70 else "average" if percentage >= 50 else "weak",
        "detected_months": detected_months,
        "has_tech_skills": has_tech_skills,
        "details": details,
        "issues": issues,
        "experience_analysis": {
            "relevance_percentage": percentage,
            "matched_job_keywords": resume_skills[:6] if resume_skills else []
        }
    }

