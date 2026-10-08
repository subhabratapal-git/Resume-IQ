import re

# Comprehensive list of technical skills and acronyms
# Note: Longer multi-word phrases MUST come before smaller substrings
SKILL_KEYWORDS = [
    # Data Structures & Algorithms variations
    "Data Structures and Algorithms",
    "Data Structures & Algorithms",
    "Data Structure and Algorithm",
    "Data Structure & Algorithm",
    "Data Structure and Algorithms",
    "Data Structures Algorithms",
    "Algorithms and Data Structures",
    "Data Structures",
    "Algorithms",

    # OOP / Systems / Core CS
    "Object Oriented Programming Systems",
    "Object Oriented Programming",
    "Object-Oriented Programming",
    "Database Management Systems",
    "Database Management System",
    "Relational Database Management System",
    "Operating Systems",
    "Operating System",
    "Computer Networks",
    "System Design",
    "Distributed Systems",
    "Microservices Architecture",
    "Microservices",
    "Software Architecture",

    # AI / ML / Data Science
    "Natural Language Processing",
    "Artificial Intelligence",
    "Machine Learning",
    "Deep Learning",
    "Computer Vision",
    "Scikit-learn",
    "Jupyter Notebook",
    "TensorFlow",
    "PyTorch",
    "MediaPipe",
    "PyAutoGUI",
    "Matplotlib",
    "OpenCV",
    "Pandas",
    "NumPy",
    "Keras",

    # Cloud & DevOps & CI/CD
    "Continuous Integration / Continuous Deployment",
    "Continuous Integration",
    "Continuous Deployment",
    "Continuous Delivery",
    "Amazon Web Services",
    "Google Cloud Platform",
    "Google Cloud",
    "Microsoft Azure",
    "Kubernetes",
    "Docker",
    "CI/CD",
    "CI CD",
    "AWS",
    "GCP",
    "Azure",
    "K8s",

    # APIs & Web Development
    "RESTful Web Services",
    "RESTful APIs",
    "RESTful API",
    "REST APIs",
    "REST API",
    "GraphQL",
    "Spring Boot",
    "Java Swing",
    "Express.js",
    "React.js",
    "Next.js",
    "Node.js",
    "Vue.js",
    "Angular.js",
    "FastAPI",
    "Django",
    "Flask",
    "Redux",
    "React",
    "Express",
    "Node",
    "Next",
    "Vue",

    # Databases
    "PostgreSQL",
    "MongoDB",
    "MySQL",
    "SQLite",
    "Redis",

    # Languages
    "JavaScript",
    "TypeScript",
    "Python",
    "Java",
    "HTML5",
    "CSS3",
    "HTML",
    "CSS",
    "SQL",
    "C++",
    "C#",
    "C",

    # Acronyms (Word boundary protected)
    "DSA",
    "OOPS",
    "OOP",
    "DBMS",
    "RDBMS",
    "OS",
    "ML",
    "DL",
    "AI",
    "NLP",
    "CV",

    # Tools
    "VS Code",
    "GitHub",
    "Git",
]


def extract_skills(skills_text: str) -> list:
    """
    Extracts all recognized technical skills from text, preserving multi-word skills
    and avoiding greedy substring over-matching.
    """
    if not skills_text:
        return []

    detected_skills = []
    working_text = skills_text

    for skill in SKILL_KEYWORDS:
        pattern = re.escape(skill)
        # Match with word boundaries, supporting special characters like C++, CI/CD, React.js
        regex_pattern = rf"(?<![\w\.\+#]){pattern}(?![\w\.\+#])"

        match = re.search(regex_pattern, working_text, re.IGNORECASE)
        if match:
            # Add canonical display name
            detected_skills.append(skill)
            # Remove from working text to prevent smaller subsets matching again
            working_text = re.sub(regex_pattern, " ", working_text, flags=re.IGNORECASE)

    return detected_skills
