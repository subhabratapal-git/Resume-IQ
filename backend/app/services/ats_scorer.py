def calculate_ats_score(
    skill_match_percentage: float,
    keyword_score: float,
    structure_score: float,
    education_score: float,
    project_score: float,
    experience_score: float
) -> dict:

    skill_score = round(
        skill_match_percentage * 0.30,
        2
    )

    total_score = (
        skill_score
        + keyword_score
        + education_score
        + project_score
        + experience_score
        + structure_score
    )

    return {
        "skill_score": skill_score,
        "keyword_score": keyword_score,
        "education_score": education_score,
        "project_score": project_score,
        "experience_score": experience_score,
        "structure_score": structure_score,
        "ats_score": round(min(total_score, 100), 2)
    }
    
    
    