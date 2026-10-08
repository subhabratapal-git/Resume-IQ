def calculate_structure_score(sections: dict) -> dict:

    score = 0
    found_sections = []
    missing_sections = []

    # Summary
    if "summary" in sections and sections["summary"].strip():
        score += 1
        found_sections.append("summary")
    else:
        missing_sections.append("summary")

    # Education
    if "education" in sections and sections["education"].strip():
        score += 1
        found_sections.append("education")
    else:
        missing_sections.append("education")

    # Skills
    if "skills" in sections and sections["skills"].strip():
        score += 1
        found_sections.append("skills")
    else:
        missing_sections.append("skills")

    # Projects
    if "projects" in sections and sections["projects"].strip():
        score += 1
        found_sections.append("projects")
    else:
        missing_sections.append("projects")

    # Experience or Training
    if (
        ("experience" in sections and sections["experience"].strip())
        or
        ("training" in sections and sections["training"].strip())
    ):
        score += 1
        found_sections.append("experience_or_training")
    else:
        missing_sections.append("experience_or_training")

    return {
        "structure_score": score,
        "found_sections": found_sections,
        "missing_sections": missing_sections
    }
    
    
    
    
    
    