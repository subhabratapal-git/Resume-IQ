from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def calculate_ml_semantic_score(resume_text: str, jd_text: str, sections: dict = None) -> dict:
    """
    Calculates a semantic ATS score using TF-IDF and Cosine Similarity.
    Also identifies strong and weak semantic matching areas if sections are provided.
    """
    if not resume_text or not jd_text:
        return {"score": 0.0, "strong_areas": [], "weak_areas": []}

    try:
        # Fit vectorizer once on the full resume + JD corpus so vocabulary is consistent
        all_docs = [resume_text, jd_text]
        if sections:
            all_docs += [c for c in sections.values() if c and len(c.strip()) >= 20]

        vectorizer = TfidfVectorizer(stop_words='english', lowercase=True)
        vectorizer.fit(all_docs)

        # Overall semantic score
        resume_vec = vectorizer.transform([resume_text])
        jd_vec     = vectorizer.transform([jd_text])
        similarity  = cosine_similarity(resume_vec, jd_vec)
        overall_score = float(similarity[0][0]) * 100

        strong_areas = []
        weak_areas = []

        # If sections provided, score them individually for granularity
        if sections:
            for section_name, section_content in sections.items():
                if not section_content or len(section_content.strip()) < 20:
                    continue
                try:
                    sec_vec  = vectorizer.transform([section_content])
                    sec_sim  = cosine_similarity(sec_vec, jd_vec)
                    sec_score = float(sec_sim[0][0]) * 100

                    if sec_score > 60:
                        strong_areas.append(f"{section_name.title()} Section (High Match)")
                    elif sec_score <= 30:
                        weak_areas.append(f"{section_name.title()} Section (Low Match)")
                except Exception:
                    pass

        return {
            "score": round(overall_score, 2),
            "strong_areas": strong_areas,
            "weak_areas": weak_areas
        }
    except Exception as e:
        print(f"Error calculating ML semantic score: {e}")
        return {"score": 0.0, "strong_areas": [], "weak_areas": []}
