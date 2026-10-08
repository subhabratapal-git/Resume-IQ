

import re


STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "than",
    "to", "of", "in", "on", "at", "for", "from", "by", "with",
    "without", "into", "onto", "over", "under", "between", "among",

    "is", "am", "are", "was", "were", "be", "been", "being",
    "do", "does", "did", "done",
    "have", "has", "had",
    "can", "could", "may", "might", "must", "shall", "should",
    "will", "would",

    "this", "that", "these", "those",
    "it", "its", "they", "them", "their",
    "we", "our", "ours",
    "you", "your", "yours",
    "he", "she", "his", "her",

    "who", "whom", "which", "what", "when", "where", "why", "how",

    "as", "such", "also", "very", "more", "most", "less",
    "some", "any", "all", "each", "every", "both", "either",
    "other", "another",

    "using", "used", "use",
    "including", "include", "includes",
    "working", "work", "worked",
    "knowledge", "understanding",
    "ability", "abilities",
    "skill", "skills",
    "experience", "experienced",

    "looking", "seeking",
    "candidate", "candidates",
    "applicant", "applicants",
    "person", "individual",

    "job", "role", "position",
    "title", "description",
    "responsibility", "responsibilities",
    "requirement", "requirements",
    "qualification", "qualifications",
    "preferred", "required",

    "company", "organization",
    "team", "teams",
    "member", "members",

    "strong", "good", "excellent",
    "motivated", "passionate",
    "responsible",

    "join", "apply", "welcome",
    "freshers", "fresher",

    "development", "develop",
    "developing", "developer",
    "software",

    "build", "building", "built",
    "create", "creating",
    "maintain", "maintaining",
    "test", "testing",
    "write", "writing",

    "clean", "efficient",
    "scalable", "maintainable",

    "related", "field",
    "degree", "bachelor", "master",
    "academic", "personal",

    "year", "years",
    "month", "months",
}


PHRASE_KEYWORDS = [
    "rest apis",
    "rest api",
    "restful api",
    "machine learning",
    "deep learning",
    "natural language processing",
    "computer vision",
    "data structures",
    "data structures and algorithms",
    "object oriented programming",
    "object-oriented programming",
    "computer networks",
    "operating systems",
    "database management system",
    "software development lifecycle",
    "software development life cycle",
    "spring boot",
    "react.js",
    "react js",
    "node.js",
    "node js",
    "express.js",
    "express js",
    "next.js",
    "next js",
    "java swing",
    "jupyter notebook",
    "visual studio code",
    "vs code",
    "scikit-learn",
    "power bi",
    "data analysis",
    "data science",
    "data engineering",
    "feature engineering",
    "cloud computing",
    "version control",
    "problem solving",
    "problem-solving",
    "object detection",
    "image processing",
    "unit testing",
    "integration testing",
    "agile methodology",
    "microservices architecture",
]


TECH_KEYWORDS = {
    # Programming
    "python",
    "java",
    "javascript",
    "typescript",
    "c",
    "c++",
    "c#",
    "go",
    "golang",
    "rust",
    "kotlin",
    "swift",
    "php",
    "ruby",
    "r",

    # Web
    "html",
    "css",
    "react",
    "angular",
    "vue",
    "vite",
    "bootstrap",
    "tailwind",
    "jquery",

    # Backend
    "fastapi",
    "flask",
    "django",
    "spring",
    "express",
    "nestjs",

    # Databases
    "sql",
    "mysql",
    "postgresql",
    "postgres",
    "mongodb",
    "sqlite",
    "oracle",
    "redis",
    "firebase",

    # CS fundamentals
    "dsa",
    "oop",
    "oops",
    "dbms",
    "os",
    "algorithms",
    "networking",

    # ML / AI
    "numpy",
    "pandas",
    "matplotlib",
    "tensorflow",
    "keras",
    "pytorch",
    "opencv",
    "mediapipe",
    "sklearn",
    "nlp",
    "ai",
    "ml",

    # Dev tools
    "git",
    "github",
    "gitlab",
    "docker",
    "kubernetes",
    "jenkins",
    "postman",
    "swagger",
    "linux",

    # Cloud
    "aws",
    "azure",
    "gcp",

    # APIs / architecture
    "api",
    "rest",
    "graphql",
    "microservices",

    # Testing
    "pytest",
    "junit",
    "selenium",

    # Data
    "etl",
    "elt",
    "spark",
    "hadoop",

    # General technical
    "frontend",
    "backend",
    "fullstack",
    "full-stack",
    "debugging",
    "programming",
    "databases",
}


PHRASE_NORMALIZATION = {
    "restful api": "REST API",
    "rest api": "REST API",
    "rest apis": "REST API",

    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "natural language processing": "NLP",

    "data structures and algorithms": "DSA",
    "data structures": "Data Structures",

    "object oriented programming": "OOP",
    "object-oriented programming": "OOP",

    "computer networks": "Computer Networks",
    "operating systems": "Operating Systems",

    "database management system": "DBMS",

    "software development lifecycle": "SDLC",
    "software development life cycle": "SDLC",

    "react js": "React.js",
    "react.js": "React.js",

    "node js": "Node.js",
    "node.js": "Node.js",

    "express js": "Express.js",
    "express.js": "Express.js",

    "next js": "Next.js",
    "next.js": "Next.js",

    "spring boot": "Spring Boot",
    "java swing": "Java Swing",

    "jupyter notebook": "Jupyter Notebook",
    "visual studio code": "VS Code",
    "vs code": "VS Code",

    "scikit-learn": "Scikit-learn",

    "problem solving": "Problem Solving",
    "problem-solving": "Problem Solving",

    "computer vision": "Computer Vision",
    "data analysis": "Data Analysis",
    "data science": "Data Science",
    "data engineering": "Data Engineering",
    "feature engineering": "Feature Engineering",

    "version control": "Version Control",
    "cloud computing": "Cloud Computing",

    "unit testing": "Unit Testing",
    "integration testing": "Integration Testing",

    "microservices architecture": "Microservices",
}


DISPLAY_NAMES = {
    "python": "Python",
    "java": "Java",
    "javascript": "JavaScript",
    "typescript": "TypeScript",

    "c": "C",
    "c++": "C++",
    "c#": "C#",

    "html": "HTML",
    "css": "CSS",

    "react": "React",
    "angular": "Angular",
    "vue": "Vue",
    "vite": "Vite",

    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",

    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "mongodb": "MongoDB",

    "dsa": "DSA",
    "oop": "OOP",
    "oops": "OOPS",
    "dbms": "DBMS",
    "os": "OS",

    "numpy": "NumPy",
    "pandas": "Pandas",
    "matplotlib": "Matplotlib",
    "tensorflow": "TensorFlow",
    "keras": "Keras",
    "pytorch": "PyTorch",
    "opencv": "OpenCV",
    "mediapipe": "MediaPipe",
    "nlp": "NLP",

    "git": "Git",
    "github": "GitHub",
    "gitlab": "GitLab",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "jenkins": "Jenkins",
    "postman": "Postman",
    "swagger": "Swagger",

    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",

    "api": "API",
    "graphql": "GraphQL",

    "frontend": "Frontend",
    "backend": "Backend",
    "debugging": "Debugging",

    "etl": "ETL",
    "elt": "ELT",
    "spark": "Spark",
    "hadoop": "Hadoop",
}


def normalize_text(text: str) -> str:
    text = text.lower()

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def extract_phrase_keywords(text: str) -> tuple[list, str]:
    working_text = normalize_text(text)

    found_phrases = []

    sorted_phrases = sorted(
        PHRASE_KEYWORDS,
        key=len,
        reverse=True
    )

    for phrase in sorted_phrases:

        pattern = rf"(?<!\w){re.escape(phrase)}(?!\w)"

        if re.search(pattern, working_text):

            normalized_name = PHRASE_NORMALIZATION.get(
                phrase,
                phrase.title()
            )

            if normalized_name not in found_phrases:
                found_phrases.append(normalized_name)

            working_text = re.sub(
                pattern,
                " ",
                working_text
            )

    return found_phrases, working_text


def extract_single_keywords(text: str) -> list:
    words = re.findall(
        r"(?<!\w)(?:c\+\+|c#|[a-zA-Z][a-zA-Z0-9.+#-]*)(?!\w)",
        text
    )

    found_keywords = []

    for word in words:
        word_lower = word.lower()

        if word_lower in STOP_WORDS:
            continue

        if word_lower not in TECH_KEYWORDS:
            continue

        display_name = DISPLAY_NAMES.get(
            word_lower,
            word
        )

        if display_name not in found_keywords:
            found_keywords.append(display_name)

    return found_keywords


def extract_keywords(text: str) -> list:
    phrase_keywords, remaining_text = extract_phrase_keywords(text)

    single_keywords = extract_single_keywords(
        remaining_text
    )

    final_keywords = []

    for keyword in phrase_keywords + single_keywords:
        if keyword not in final_keywords:
            final_keywords.append(keyword)

    return final_keywords


def keyword_exists_in_resume(
    keyword: str,
    resume_text: str
) -> bool:

    resume_lower = normalize_text(resume_text)

    keyword_lower = keyword.lower()

    aliases = {
        "rest api": [
            "rest api",
            "restful api",
            "restful services",
        ],

        "oop": [
            "oop",
            "oops",
            "object oriented programming",
            "object-oriented programming",
        ],

        "dsa": [
            "dsa",
            "data structure",
            "data structures",
            "data structure and algorithm",
            "data structures and algorithms",
            "data structure and algorithms",
            "data structures and algorithm",
            "data structures & algorithms",
            "data structure & algorithm",
            "data structures algorithms",
            "algorithms and data structures",
            "algorithms",
        ],

        "data structures and algorithms": [
            "dsa",
            "data structure",
            "data structures",
            "data structure and algorithm",
            "data structures and algorithms",
            "data structures & algorithms",
            "data structure & algorithm",
            "data structures algorithms",
            "algorithms",
        ],

        "data structures": [
            "dsa",
            "data structure",
            "data structures",
            "data structure and algorithm",
            "data structures and algorithms",
            "data structures & algorithms",
        ],

        "nlp": [
            "nlp",
            "natural language processing",
        ],

        "ml": [
            "ml",
            "machine learning",
        ],

        "machine learning": [
            "ml",
            "machine learning",
        ],

        "ai": [
            "ai",
            "artificial intelligence",
        ],

        "artificial intelligence": [
            "ai",
            "artificial intelligence",
        ],

        "ci/cd": [
            "ci/cd",
            "ci cd",
            "cicd",
            "continuous integration",
            "continuous deployment",
        ],

        "sdlc": [
            "sdlc",
            "software development lifecycle",
            "software development life cycle",
        ],

        "react.js": [
            "react.js",
            "react js",
            "react",
        ],

        "node.js": [
            "node.js",
            "node js",
        ],

        "express.js": [
            "express.js",
            "express js",
        ],

        "vs code": [
            "vs code",
            "visual studio code",
        ],

        "scikit-learn": [
            "scikit-learn",
            "sklearn",
        ],

        "problem solving": [
            "problem solving",
            "problem-solving",
        ],
    }

    possible_terms = aliases.get(
        keyword_lower,
        [keyword_lower]
    )

    for term in possible_terms:
        pattern = rf"(?<!\w){re.escape(term)}(?!\w)"

        if re.search(pattern, resume_lower):
            return True

    return False


def calculate_keyword_match(
    resume_text: str,
    job_description: str
) -> dict:

    job_keywords = extract_keywords(
        job_description
    )

    matched_keywords = []
    missing_keywords = []

    for keyword in job_keywords:

        if keyword_exists_in_resume(
            keyword,
            resume_text
        ):
            matched_keywords.append(keyword)

        else:
            missing_keywords.append(keyword)

    total_keywords = len(job_keywords)

    if total_keywords == 0:
        match_percentage = 0

    else:
        match_percentage = round(
            (
                len(matched_keywords)
                / total_keywords
            ) * 100,
            2
        )

    keyword_score = round(
        match_percentage * 0.30,
        2
    )

    return {
        "job_keywords": job_keywords,
        "total_job_keywords": total_keywords,
        "matched_keywords": matched_keywords,
        "missing_keywords": missing_keywords,
        "matched_keyword_count": len(matched_keywords),
        "missing_keyword_count": len(missing_keywords),
        "keyword_match_percentage": match_percentage,
        "keyword_score": keyword_score
    }
