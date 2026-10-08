import re

TECH_SYNONYMS = {
    # DSA & Algorithms
    "dsa": "dsa",
    "data structure": "dsa",
    "data structures": "dsa",
    "data structure and algorithm": "dsa",
    "data structures and algorithms": "dsa",
    "data structure and algorithms": "dsa",
    "data structures and algorithm": "dsa",
    "data structures & algorithms": "dsa",
    "data structure & algorithm": "dsa",
    "data structures algorithms": "dsa",
    "algorithms and data structures": "dsa",
    "algorithms": "dsa",

    # OOP / Systems
    "oop": "oops",
    "oops": "oops",
    "object oriented programming": "oops",
    "object-oriented programming": "oops",
    "object oriented programming systems": "oops",

    # DBMS / RDBMS
    "dbms": "dbms",
    "rdbms": "dbms",
    "database management system": "dbms",
    "database management systems": "dbms",
    "relational database management system": "dbms",

    # OS
    "os": "os",
    "operating system": "os",
    "operating systems": "os",

    # AI / ML
    "ml": "machine learning",
    "machine learning": "machine learning",
    "dl": "deep learning",
    "deep learning": "deep learning",
    "ai": "artificial intelligence",
    "artificial intelligence": "artificial intelligence",
    "nlp": "natural language processing",
    "natural language processing": "natural language processing",
    "cv": "computer vision",
    "computer vision": "computer vision",

    # Web & Frameworks
    "react": "react",
    "react.js": "react",
    "reactjs": "react",
    "node": "node",
    "node.js": "node",
    "nodejs": "node",
    "express": "express",
    "express.js": "express",
    "expressjs": "express",
    "vue": "vue",
    "vue.js": "vue",
    "vuejs": "vue",
    "next": "nextjs",
    "next.js": "nextjs",
    "nextjs": "nextjs",
    "angular": "angular",
    "angular.js": "angular",
    "angularjs": "angular",

    # Languages
    "js": "javascript",
    "javascript": "javascript",
    "ts": "typescript",
    "typescript": "typescript",
    "py": "python",
    "python": "python",

    # Cloud & DevOps
    "aws": "aws",
    "amazon web services": "aws",
    "gcp": "gcp",
    "google cloud": "gcp",
    "google cloud platform": "gcp",
    "azure": "azure",
    "microsoft azure": "azure",
    "k8s": "kubernetes",
    "kubernetes": "kubernetes",
    "ci/cd": "ci/cd",
    "ci cd": "ci/cd",
    "cicd": "ci/cd",
    "continuous integration": "ci/cd",
    "continuous deployment": "ci/cd",
    "continuous delivery": "ci/cd",

    # Databases
    "postgres": "postgresql",
    "postgresql": "postgresql",
    "psql": "postgresql",
    "mongo": "mongodb",
    "mongodb": "mongodb",

    # APIs & Architecture
    "rest api": "rest api",
    "rest apis": "rest api",
    "restful api": "rest api",
    "restful apis": "rest api",
    "restful web services": "rest api",
    "system design": "system design",
    "distributed systems": "system design",
    "software architecture": "system design",
}

# Inverted mapping to check all alias variations in raw text
ALIASES_BY_CANONICAL = {}
for alias, canonical in TECH_SYNONYMS.items():
    ALIASES_BY_CANONICAL.setdefault(canonical, set()).add(alias)


def normalize_skill(skill: str) -> str:
    """
    Normalizes a skill name using a comprehensive tech synonym dictionary.
    E.g. 'Data Structures & Algorithms' -> 'dsa', 'React.js' -> 'react'.
    """
    s = skill.lower().strip()
    return TECH_SYNONYMS.get(s, s)


def match_skills(resume_skills: list, job_skills: list, resume_full_text: str = "") -> dict:
    """
    Matches candidate skills with job description requirements.
    Understands tech synonyms (e.g. DSA == Data Structures and Algorithms).
    Also scans full resume text as a second check to ensure 100% accuracy.
    """
    resume_set = {normalize_skill(skill) for skill in resume_skills}
    resume_lower = (resume_full_text or "").lower()

    matched = []
    missing = []

    for skill in job_skills:
        canonical = normalize_skill(skill)

        # 1. Direct normalized match in extracted skills
        if canonical in resume_set:
            matched.append(skill)
            continue

        # 2. Search all alias variations in full resume text
        found_in_text = False
        aliases = ALIASES_BY_CANONICAL.get(canonical, [skill.lower()])
        for alias in aliases:
            pattern = rf"(?<![a-zA-Z0-9]){re.escape(alias)}(?![a-zA-Z0-9])"
            if re.search(pattern, resume_lower):
                matched.append(skill)
                found_in_text = True
                break

        if not found_in_text:
            missing.append(skill)

    if len(job_skills) == 0:
        match_percentage = 0
    else:
        match_percentage = round((len(matched) / len(job_skills)) * 100, 2)

    return {
        "matched_skills": matched,
        "missing_skills": missing,
        "skill_match_percentage": match_percentage
    }