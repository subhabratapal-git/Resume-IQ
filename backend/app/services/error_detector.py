from spellchecker import SpellChecker
import re

def detect_resume_errors(resume_text: str) -> dict:
    """
    Analyzes resume text for REAL spelling mistakes only.
    
    Rules to NEVER flag:
    - Proper nouns: words starting with a Capital letter (names, companies, places, universities)
    - All-uppercase words: acronyms (SQL, API, CGPA, etc.)
    - Known tech vocab
    - Words 3 characters or shorter
    - Email addresses, URLs, phone numbers
    """
    if not resume_text:
        return {"spelling_errors": [], "grammar_suggestions": [], "error_count": 0}

    spell = SpellChecker()

    # ── Extensive tech + domain whitelist (all lowercase for comparison) ──
    tech_whitelist = {
        # Programming languages
        "python", "java", "javascript", "typescript", "kotlin", "swift", "golang",
        "rust", "scala", "perl", "ruby", "php", "dart",
        # Frameworks & Libraries
        "react", "reactjs", "nextjs", "vuejs", "angularjs", "angular", "redux",
        "svelte", "django", "flask", "fastapi", "spring", "springboot", "laravel",
        "express", "nodejs", "nuxtjs", "nestjs", "tensorflow", "pytorch", "keras",
        "sklearn", "scikit", "pandas", "numpy", "matplotlib", "opencv", "scipy",
        # Databases
        "sql", "nosql", "mysql", "postgresql", "postgres", "mongodb", "redis",
        "elasticsearch", "cassandra", "sqlite", "dynamodb", "neo4j", "firebase",
        # Cloud & DevOps
        "aws", "gcp", "azure", "docker", "kubernetes", "k8s", "jenkins", "terraform",
        "ansible", "github", "gitlab", "bitbucket", "nginx", "apache", "linux",
        "ubuntu", "debian", "ci", "cd", "devops", "mlops", "dataops",
        # Web & APIs
        "api", "apis", "rest", "restful", "graphql", "grpc", "oauth", "jwt",
        "html", "css", "sass", "scss", "tailwind", "bootstrap", "webpack",
        "vite", "babel", "npm", "yarn", "json", "xml", "csv", "yaml",
        # CS Concepts
        "dsa", "oops", "oop", "dbms", "os", "cn", "lld", "hld", "microservices",
        "ui", "ux", "git", "agile", "scrum", "jira", "kanban",
        # Degrees & Academic
        "btech", "mtech", "bca", "mca", "bsc", "msc", "phd", "gpa", "cgpa",
        "resume", "curriculum", "vitae",
        # Others
        "ai", "ml", "nlp", "llm", "rag", "gen", "genai", "fullstack",
        "frontend", "backend", "qa", "dev", "sdk", "ide",
        # Common resume verbs that spellcheck may not know
        "spearheaded", "architected", "onboarded", "upskilled",
    }

    spelling_errors = []
    grammar_suggestions = []

    # ── Step 1: Remove emails, URLs, phone numbers before checking ──
    cleaned_for_spell = re.sub(r'\S+@\S+', '', resume_text)          # emails
    cleaned_for_spell = re.sub(r'https?://\S+', '', cleaned_for_spell) # URLs
    cleaned_for_spell = re.sub(r'[\+\d][\d\s\-\(\)]{7,}', '', cleaned_for_spell)  # phones

    # ── Step 2: Extract only purely lowercase words (not proper nouns, not ALL-CAPS) ──
    # We ONLY check words that:
    #   1. Are entirely lowercase (meaning they are not proper nouns or acronyms)
    #   2. Are longer than 3 characters
    #   3. Are not in our whitelist
    all_words = re.findall(r'\b[a-z]{4,}\b', cleaned_for_spell)  # lowercase-only words, min 4 chars
    candidate_words = [w for w in set(all_words) if w not in tech_whitelist]

    misspelled = spell.unknown(candidate_words)

    for word in misspelled:
        correction = spell.correction(word)
        # Only flag if:
        # - correction is different from the word
        # - correction is not None
        # - the edit distance looks like a real typo (not a completely different word)
        if (
            correction
            and correction.lower() != word.lower()
            and len(correction) > 2
            # Ensure the correction is reasonably close (not replacing 'dockr' with 'dock' etc.)
            and abs(len(correction) - len(word)) <= 3
        ):
            spelling_errors.append({
                "word": word,
                "suggestion": correction
            })

    # ── Step 3: Sentence Structure Analysis (regex-only, no NLTK) ──
    raw_sentences = re.split(r'(?<=[.!?\n])\s+', resume_text)
    for sent in raw_sentences:
        clean_sent = sent.strip()
        words_in_sent = re.findall(r'\b\w+\b', clean_sent)

        # Fragmented: 1-2 word "sentences" that look like bullet stubs
        if 1 <= len(words_in_sent) <= 2 and len(clean_sent) > 3:
            if (
                not clean_sent.endswith(":")      # Skip section headers "Experience:"
                and not clean_sent.isupper()      # Skip "SKILLS"
                and not re.match(r'^[A-Z]', clean_sent)  # Skip proper noun stubs
                and not re.match(r'^[\d\+\-]', clean_sent)  # Skip phone/years
            ):
                grammar_suggestions.append({
                    "issue": "Fragmented or incomplete sentence.",
                    "sentence": clean_sent
                })

        # Run-on: extremely long sentences
        elif len(words_in_sent) > 50:
            grammar_suggestions.append({
                "issue": "Run-on sentence — consider splitting for ATS readability.",
                "sentence": clean_sent[:90] + "..."
            })

    return {
        "spelling_errors": spelling_errors[:12],     # cap at 12 for clean UI
        "grammar_suggestions": grammar_suggestions[:8],
        "error_count": len(spelling_errors) + len(grammar_suggestions)
    }
