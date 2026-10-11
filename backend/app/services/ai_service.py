import os
import re
import json
from google import genai
from dotenv import dotenv_values


def get_genai_key():
    """
    Reads GEMINI_API_KEY directly from the .env file.
    If the key is commented out (#) or removed, returns None immediately,
    even if the uvicorn process had it previously in memory.
    """
    env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
    if os.path.exists(env_path):
        vals = dotenv_values(env_path)
        key = vals.get("GEMINI_API_KEY")
        if key and len(str(key).strip()) > 10:
            return str(key).strip()
        return None

    # Fallback to system env if no .env file exists
    key = os.getenv("GEMINI_API_KEY", "").strip()
    return key if len(key) > 10 else None


def is_gemini_active() -> bool:
    return get_genai_key() is not None

def _call_gemini(prompt: str, api_key: str) -> str:
    """Calls Gemini API using the new google.genai SDK with resilient model fallback."""

    client = genai.Client(api_key=api_key)

    models_to_try = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-flash-latest",
        "gemini-1.5-flash",
        "gemini-pro-latest",
    ]

    last_err = None

    for model_name in models_to_try:

        # Try chat first
        try:
            print(f"[Gemini] Calling model: {model_name} using chat...")

            chat = client.chats.create(model=model_name)
            response = chat.send_message(prompt)

            if response and response.text:
                print(
                    f"[Gemini] Response received successfully "
                    f"from model: {model_name}"
                )

                return response.text.strip()

        except Exception as err:
            print(
                f"[Gemini] Chat call failed for "
                f"{model_name}: {err}"
            )
            last_err = err

        # Fallback to direct generate_content
        try:
            print(
                f"[Gemini] Calling model: {model_name} "
                f"using generate_content..."
            )

            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )

            if response and response.text:
                print(
                    f"[Gemini] Response received successfully "
                    f"from model: {model_name}"
                )

                return response.text.strip()

        except Exception as err:
            print(
                f"[Gemini] generate_content failed for "
                f"{model_name}: {err}"
            )

            last_err = err
            continue

    raise (
        last_err
        if last_err
        else RuntimeError(
            "Gemini content generation returned empty response."
        )
    )

def _extract_summary_from_resume(resume_text: str) -> str:
    """
    Intelligently extracts the candidate's professional summary, career objective,
    or introductory profile statement from the resume text.
    """
    if not resume_text:
        return ""

    # Check for dedicated section headers (summary, objective, profile, etc.)
    summary_pattern = re.compile(
        r"(?:^|\n)\s*(?:career\s+summary|professional\s+summary|executive\s+summary|about\s+me|career\s+objective|objective|profile|summary)\s*[:\-–—]?\s*\n+(.*?)(?=\n\s*(?:technical\s+skills|skills|work\s+experience|professional\s+experience|experience|employment|projects|education|academic|certifications|training|$))",
        re.IGNORECASE | re.DOTALL
    )
    match = summary_pattern.search(resume_text)
    if match:
        extracted = match.group(1).strip()
        cleaned = " ".join([l.strip() for l in extracted.splitlines() if l.strip()])
        if len(cleaned) > 15:
            return cleaned[:350]

    # Fallback: scan introductory lines (skipping contact info and header)
    lines = [l.strip() for l in resume_text.splitlines() if l.strip()]
    candidate_lines = []
    stop_words = ["experience", "education", "skills", "projects", "certifications", "internship"]
    for line in lines[1:6]:
        low = line.lower()
        if any(char in low for char in ["@", "linkedin", "github", "phone", "+91", "+1", ".com"]):
            continue
        if any(sw in low.split() for sw in stop_words):
            break
        if len(line) > 30:
            candidate_lines.append(line)

    if candidate_lines:
        return " ".join(candidate_lines)[:350]

    return ""


def _find_weak_sentences_in_resume(resume_text: str, limit: int = 5) -> list:
    """
    Scans resume for multiple bullet points or sentences that can benefit from
    strong action verbs and quantified impact.
    """
    lines = [l.strip("-*• \t") for l in resume_text.splitlines() if len(l.strip()) > 20]
    found = []

    target_markers = [
        "responsible for", "worked on", "helped with", "helped", "tasked with",
        "assisted with", "assisted", "participated in", "involved in", "built",
        "developed", "implemented", "created", "designed", "maintained"
    ]

    for line in lines:
        if len(found) >= limit:
            break
        # Skip contact/header/education lines
        if any(h in line.lower() for h in ["@", "phone", "linkedin", "github", "http", "university", "college", "school"]):
            continue
        for marker in target_markers:
            if marker in line.lower() and 25 < len(line) < 180 and line not in found:
                found.append(line)
                break

    if not found:
        found.append("Developed and maintained software components, improving system performance.")

    return found


def _apply_rule_based_corrections(resume_text: str, ml_errors: dict) -> str:
    """
    Intelligent NLP fallback when Gemini is unavailable.
    Fixes typos, passive words, and standardizes structure.
    """
    corrected = resume_text

    spelling_errors = ml_errors.get("spelling_errors", [])
    for item in spelling_errors:
        word = item.get("word")
        suggestion = item.get("suggestion")
        if word and suggestion:
            def replace_only_lowercase(m):
                matched = m.group(0)
                if matched[0].isupper():
                    return matched
                return suggestion
            corrected = re.sub(rf"\b{re.escape(word)}\b", replace_only_lowercase, corrected)

    replacements = {
        r"\bresponsible for developing scalable\b": "Architected and engineered high-performance",
        r"\bresponsible for developing\b": "Architected and delivered",
        r"\bresponsible for\b": "Spearheaded and executed",
        r"\bworked on\b": "Engineered and maintained",
        r"\bhelped with\b": "Collaborated cross-functionally on",
        r"\btasked with\b": "Orchestrated",
    }
    for pattern, replacement in replacements.items():
        corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)

    return corrected.strip()


def generate_pro_insights(
    resume_text: str,
    job_description: str,
    ats_score: int,
    score_breakdown: dict,
    matched_skills: list,
    missing_skills: list,
    ml_errors: dict,
    target_role: str
) -> dict:
    """
    Generates dynamic AI suggestions and rewrite examples.
    Uses Gemini Flash if API key is available, else uses smart local engine.
    """
    active_key = get_genai_key()
    weak_bullets = _find_weak_sentences_in_resume(resume_text, limit=4)
    original_summary = _extract_summary_from_resume(resume_text)

    # ── Option A: Gemini AI ──────────────────────────────────────────────────
    if active_key:
        try:
            summary_context = original_summary if original_summary else "No explicit professional summary in original resume."
            bullets_formatted = "\n".join([f'- "{b}"' for b in weak_bullets])
            prompt = f"""You are an elite ATS Executive Career Consultant and Resume Architect. Analyze this candidate's resume against the target Job Description.

Candidate ATS Score: {ats_score}/100
Target Role: {target_role}
Missing Critical Skills: {', '.join(missing_skills) if missing_skills else 'None identified'}
Detected Typos / Grammar: {ml_errors.get('spelling_errors', [])}

Original Candidate Summary:
"{summary_context}"

Detected Weak Bullet Points from Resume:
{bullets_formatted}

Candidate Resume Text (Context):
{resume_text[:2500]}

Job Description:
{job_description[:1200]}

INSTRUCTIONS:
1. Provide 5 actionable, expert suggestions on HOW to resolve the candidate's exact resume gaps:
   - If missing critical JD skills: specify exactly where and how to integrate them in projects, skills, or work bullets.
   - If projects lack metrics or JD alignment: give concrete advice on quantifying achievements.
   - If summary or experience needs positioning: give authoritative phrasing tips.
2. CRITICAL CONSTRAINT: Do NOT use the words 'AI', 'machine learning', 'ML', or 'artificial intelligence' anywhere in your text. Formulate suggestions as direct, executive career recommendations.

Generate ONLY a valid JSON object with exactly the following structure (no extra text):
{{
  "suggestions": [
    {{"id": 1, "text": "Specific actionable recommendation to resolve skill gap...", "priority": "High"}},
    {{"id": 2, "text": "Specific keyword or technical implementation tip...", "priority": "High"}},
    {{"id": 3, "text": "Quantified metric or action verb enhancement...", "priority": "Medium"}},
    {{"id": 4, "text": "Project or experience positioning recommendation...", "priority": "Medium"}},
    {{"id": 5, "text": "Certification or modern tooling enhancement...", "priority": "Low"}}
  ],
  "rewrites": [
    {{
      "type": "summary",
      "original": {json.dumps(summary_context)},
      "improved": "Write a compelling, JD-aligned professional summary based on candidate's actual background and target role"
    }},
    {{
      "type": "bullet",
      "original": {json.dumps(weak_bullets[0])},
      "improved": "Rewrite with strong action verbs and quantified impact"
    }}
  ]
}}

IMPORTANT FOR REWRITES:
Provide at least 3 to 5 high-impact rewrites in the "rewrites" array (1 summary rewrite, plus 1 bullet rewrite for each weak bullet point).
"""
            raw = _call_gemini(prompt, active_key)
            if raw.startswith("```"):
                raw = re.sub(r"^```(?:json)?\s*", "", raw)
                raw = re.sub(r"\s*```$", "", raw)
            json_match = re.search(r"\{[\s\S]*\}", raw)
            if json_match:
                raw = json_match.group(0)
            data = json.loads(raw)

            rewrites = data.get("rewrites", [])
            # Guarantee: if original_summary was found, ensure original is never "No summary found"
            if rewrites and len(rewrites) > 0 and original_summary:
                if "no summary" in str(rewrites[0].get("original", "")).lower():
                    rewrites[0]["original"] = original_summary

            return {
                "ai_mode": "AI Mode ON",
                "is_gemini": True,
                "ai_suggestions": data.get("suggestions", []),
                "rewrites": rewrites,
                "categorized_skill_gaps": data.get("skill_gaps", {})
            }
        except Exception as e:
            print(f"Gemini insights call failed ({e}), using local dynamic generator.")

    # ── Option B: Local Dynamic Engine (Offline / No Key) ───────────────────
    spelling_errors = ml_errors.get("spelling_errors", [])
    suggestions = []

    if missing_skills:
        top_miss = ", ".join(missing_skills[:3])
        suggestions.append({"id": 1, "text": f"Integrate missing target keywords: '{top_miss}' into your Skills and Project descriptions to immediately raise keyword match score.", "priority": "High"})
    else:
        suggestions.append({"id": 1, "text": f"Strengthen core {target_role} competencies by highlighting advanced architectural and system design patterns.", "priority": "High"})

    if spelling_errors:
        typo = spelling_errors[0]
        suggestions.append({"id": 2, "text": f"Correct spelling issue: '{typo.get('word')}' -> '{typo.get('suggestion')}'. ATS parsers penalize misspelled keywords heavily.", "priority": "High"})
    else:
        suggestions.append({"id": 2, "text": "Optimize formatting and layout hierarchy to ensure clean, error-free parsing across enterprise ATS platforms.", "priority": "High"})

    suggestions.append({"id": 3, "text": "Quantify achievements in your work history with concrete metrics (e.g. 'improved response times by 35%', 'handled 50K+ requests').", "priority": "Medium"})
    suggestions.append({"id": 4, "text": f"Tailor your Professional Summary to explicitly position yourself as a {target_role} with strong domain expertise.", "priority": "Medium"})
    cert_tools = "Docker, AWS, CI/CD" if "AWS" not in matched_skills else "System Design, Kubernetes"
    suggestions.append({"id": 5, "text": f"Highlight relevant certifications or modern tooling ({cert_tools}) to showcase continuous professional upskilling.", "priority": "Low"})

    summary_orig = original_summary if original_summary else "No summary statement in original CV"
    summary_improved = f"Results-driven {target_role} with proven expertise in building scalable, responsive software solutions. Adept at full lifecycle development, optimizing system performance, and collaborating with cross-functional teams to deliver enterprise-grade applications."

    rewrites_list = [{"type": "summary", "original": summary_orig, "improved": summary_improved}]
    for b in weak_bullets:
        imp = b
        imp = re.sub(r"\bresponsible for developing scalable\b", "Architected and engineered high-performance", imp, flags=re.IGNORECASE)
        imp = re.sub(r"\bresponsible for developing\b", "Architected and delivered", imp, flags=re.IGNORECASE)
        imp = re.sub(r"\bresponsible for\b", "Spearheaded and delivered", imp, flags=re.IGNORECASE)
        imp = re.sub(r"\bworked on\b", "Engineered and optimized core", imp, flags=re.IGNORECASE)
        imp = re.sub(r"\bhelped with\b", "Partnered cross-functionally to execute", imp, flags=re.IGNORECASE)
        imp = re.sub(r"\bdeveloped\b", "Designed and deployed high-performance", imp, flags=re.IGNORECASE)
        imp = re.sub(r"\bbuilt\b", "Architected and delivered", imp, flags=re.IGNORECASE)
        if not any(c.isdigit() for c in imp):
            imp = imp.rstrip(". ") + ", boosting overall system throughput by 30%."
        rewrites_list.append({"type": "bullet", "original": b, "improved": imp})

    return {
        "ai_mode": "AI Mode OFF",
        "is_gemini": False,
        "ai_suggestions": suggestions,
        "rewrites": rewrites_list
    }


def correct_resume_with_ai(
    resume_text: str,
    job_description: str,
    ml_errors: dict,
    target_role: str = "Software Engineer"
) -> str:
    """
    Uses Gemini AI to reconstruct the candidate's resume into a proper,
    ATS-optimized executive CV.
    - Preserves exact candidate identity, real company names, colleges, degrees, dates.
    - Maintains the user's CV structure and sections.
    - Corrects all typos, spelling/grammar errors, and weak bullet points.
    - Aligns skills and bullet impact with the target job description.
    """
    active_key = get_genai_key()
    if not active_key:
        return _apply_rule_based_corrections(resume_text, ml_errors)

    try:
        prompt = f"""You are an elite ATS Executive Resume Writer and Career Architect.
Reconstruct the candidate's resume into a pristine, professionally formatted, ATS-compliant CV tailored for the target role: "{target_role}" and the provided Job Description.

CORE PRINCIPLES — STRICT COMPLIANCE REQUIRED:
1. PRESERVE CANDIDATE IDENTITY & REAL FACTS:
   - Retain the candidate's real name, contact details (email, phone, location, LinkedIn/GitHub links).
   - Retain all actual company names, educational institutions, degrees/majors, and employment dates.
   - NEVER hallucinate fake companies, fake degrees, or non-existent work experience.

2. MAINTAIN THE ORIGINAL CV STRUCTURE:
   - Keep the structural flow of the candidate's resume intact:
     HEADER (Name & Contact)
     PROFESSIONAL SUMMARY
     TECHNICAL SKILLS
     EXPERIENCE / WORK HISTORY
     PROJECTS
     EDUCATION
     CERTIFICATIONS / ACHIEVEMENTS (if present in original)

3. FIX ALL WEAKNESSES, ERRORS, & PASSIVE PHRASING:
   - Fix all spelling mistakes, grammatical errors, and typos (including detected ML errors: {ml_errors.get('spelling_errors', [])}).
   - Transform weak, passive bullet points (e.g., "responsible for...", "worked on...", "helped with...") into commanding, accomplishment-focused bullets using strong action verbs (e.g., "Architected", "Spearheaded", "Engineered", "Optimized", "Delivered") with quantifiable outcomes and metrics where suitable.
   - Enhance the Professional Summary into a concise 3-4 sentence powerhouse tailored to {target_role} and aligned with the Job Description.
   - Organize Technical Skills cleanly into categorized lines (e.g., Languages, Frameworks, Tools, Databases) so ATS systems can easily parse them.

4. CLEAN RESUME OUTPUT FORMATTING:
   - Use standard UPPERCASE section headings: SUMMARY, SKILLS, EXPERIENCE, PROJECTS, EDUCATION.
   - Use clean bullet markers ("• ") for all achievement and project points.
   - Leave a blank line between sections for clean document rendering and PDF/Word export.
   - Output ONLY the finished resume text. Do NOT include introductory remarks, commentary, explanations, or markdown code fences (```).

--- TARGET ROLE ---
{target_role}

--- JOB DESCRIPTION ---
{job_description}

--- ORIGINAL CANDIDATE RESUME ---
{resume_text}
"""
        result = _call_gemini(prompt, active_key)
        if result:
            cleaned_result = re.sub(r"^```(?:markdown|text)?\s*", "", result.strip())
            cleaned_result = re.sub(r"\s*```$", "", cleaned_result).strip()
            return cleaned_result
        return _apply_rule_based_corrections(resume_text, ml_errors)
    except Exception as e:
        print(f"AI correction API call failed ({e}), falling back to NLP rule-based engine.")
        return _apply_rule_based_corrections(resume_text, ml_errors)
