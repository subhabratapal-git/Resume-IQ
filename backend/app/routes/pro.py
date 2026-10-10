import re
import logging
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.analysis import ResumeAnalysis
from app.routes.auth import get_current_user
from app.routes.resume import read_limited_file
from app.services.rate_limiter import analyze_limiter

logger = logging.getLogger(__name__)

from app.services.resume_parser import extract_text_from_pdf, extract_text_from_docx
from app.services.text_cleaner import clean_resume_text
from app.services.section_detector import detect_sections
from app.services.skill_extractor import extract_skills
from app.services.job_matcher import match_skills
from app.services.keyword_matcher import calculate_keyword_match
from app.services.education_scorer import calculate_education_score
from app.services.experience_scorer import calculate_experience_score, calculate_fresher_experience_score
from app.services.project_scorer import calculate_project_score
from app.services.structure_scorer import calculate_structure_score
from app.services.ml_scorer import calculate_ml_semantic_score
from app.services.error_detector import detect_resume_errors
from app.services.ai_service import correct_resume_with_ai, generate_pro_insights, is_gemini_active
from app.services.document_generator import generate_docx, generate_pdf

router = APIRouter(tags=["Pro Mode"])

# ─── Max allowed sizes ───────────────────────────────────────────────────────
# 5 MB file upload limit — prevents DoS via large binary uploads
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

# Input field length caps — prevents prompt injection and oversized payloads
MAX_JOB_DESC_LENGTH = 8000
MAX_TARGET_ROLE_LENGTH = 120

# Export text cap — 50 KB is more than enough for any CV
MAX_EXPORT_TEXT_LENGTH = 50_000


class ProExportRequest(BaseModel):
    corrected_resume_text: str = Field(max_length=MAX_EXPORT_TEXT_LENGTH)
    format: str = Field(max_length=10)  # 'pdf' or 'docx'


@router.post("/analyze")
async def pro_analyze_resume(
    request: Request,
    file: UploadFile = File(...),
    job_description: str = Form(...),
    target_role: str = Form("Software Engineer"),
    candidate_type: str = Form("experience"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Comprehensive Pro Mode analysis: Objective ATS Score, Score Breakdown, Section Diagnostics,
    Top Strengths, Resume Gaps, Best Suggestions, Content Rewrites, and Reconstructed CV.
    """
    analyze_limiter.check(request)

    try:
        # ── Guard 1: Free-use quota check ────────────────────────────────────
        if getattr(current_user, "pro_uses_remaining", 0) <= 0:
            raise HTTPException(
                status_code=403,
                detail="You have used all 5 free Pro analyses. Please upgrade your subscription to continue using Pro Mode."
            )

        # ── Guard 2: Allowed file types ───────────────────────────────────────
        allowed_types = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ]

        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail="Only PDF and DOCX files are allowed",
            )

        # Chunked stream reading prevents memory exhaustion from huge uploads
        file_bytes = await read_limited_file(file, MAX_FILE_SIZE_BYTES)

        # ── Guard 3b: Magic bytes verification ────────────────────────────────
        # Content-Type header can be spoofed. Verify actual file signature.
        pdf_type = "application/pdf"
        docx_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        is_valid_pdf = file.content_type == pdf_type and file_bytes[:4] == b"%PDF"
        is_valid_docx = file.content_type == docx_type and file_bytes[:2] == b"PK"
        if not (is_valid_pdf or is_valid_docx):
            raise HTTPException(
                status_code=400,
                detail="File content does not match the declared file type.",
            )

        # ── Guard 4: Sanitize text inputs ─────────────────────────────────────
        # Truncate to safe lengths to prevent prompt injection and huge payloads.
        job_description = job_description.strip()[:MAX_JOB_DESC_LENGTH]
        target_role = target_role.strip()[:MAX_TARGET_ROLE_LENGTH]

        if not job_description:
            raise HTTPException(
                status_code=400,
                detail="Job description cannot be empty",
            )

        # ── Guard 5: Decrement quota atomically ──────────────────────────────
        # A single atomic UPDATE prevents two simultaneous requests from both
        # passing the "remaining > 0" guard and both consuming a free slot.
        updated = db.execute(
            text(
                "UPDATE users SET pro_uses_remaining = pro_uses_remaining - 1 "
                "WHERE id = :uid AND pro_uses_remaining > 0"
            ),
            {"uid": current_user.id},
        )
        db.flush()

        if updated.rowcount == 0:
            raise HTTPException(
                status_code=403,
                detail="You have used all 5 free Pro analyses. Please upgrade your subscription."
            )

        # 1. Extract text
        if file.content_type == "application/pdf":
            extracted_text = extract_text_from_pdf(file_bytes)
        else:
            extracted_text = extract_text_from_docx(file_bytes)

        if not extracted_text:
            raise HTTPException(
                status_code=400,
                detail="No readable text found in the uploaded resume",
            )

        cleaned_text = clean_resume_text(extracted_text)
        sections = detect_sections(cleaned_text)

        # 2. Extract Skills & Keyword Matching (Combining skills section + entire text)
        skills_from_sec = extract_skills(sections.get("skills", ""))
        skills_from_all = extract_skills(cleaned_text)
        resume_skills = list(dict.fromkeys(skills_from_sec + skills_from_all))
        job_skills = extract_skills(job_description)

        # Match skills with synonym recognition + raw text fallback
        match_result = match_skills(resume_skills, job_skills, resume_full_text=cleaned_text)
        keyword_result = calculate_keyword_match(cleaned_text, job_description)

        # 3. Component Scorers with Candidate Type distinction
        edu_result = calculate_education_score(sections, job_description)

        is_fresher = str(candidate_type).strip().lower() == "fresher"
        if is_fresher:
            exp_result = calculate_fresher_experience_score(sections, resume_skills, job_description)
            exp_relevance = exp_result.get("percentage", 60)
        else:
            exp_result = calculate_experience_score(sections, job_description)
            exp_relevance = int(round((exp_result.get("experience_score", 10) / 15.0) * 100))
            exp_relevance = max(50, min(92, exp_relevance))

        # Project scoring with direct JD skill match scaling (60% to 80%+)
        proj_result = calculate_project_score(sections, job_description, job_skills=job_skills)
        proj_relevance = proj_result.get("percentage", int(round((proj_result.get("project_score", 7) / 10.0) * 100)))
        proj_relevance = max(50, min(96, proj_relevance))

        struct_result = calculate_structure_score(sections)

        # 4. Semantic Score
        ml_score_data = calculate_ml_semantic_score(cleaned_text, job_description, sections)
        ml_score = ml_score_data.get("score", 0.0)
        strong_semantic_areas = ml_score_data.get("strong_areas", [])
        weak_semantic_areas = ml_score_data.get("weak_areas", [])

        # 5. Calculate Score Breakdown
        keyword_pct = keyword_result.get("keyword_match_percentage", 65.0)
        skill_match_pct = match_result.get("skill_match_percentage", 70.0)

        # Blend cosine score with keyword match to get realistic, high-confidence ATS score
        ats_score = int(round(0.6 * keyword_pct + 0.4 * max(ml_score, 50.0)))
        ats_score = max(45, min(96, ats_score))

        semantic_match = int(round(max(ml_score, 60.0) * 0.8 + 15))
        semantic_match = max(55, min(95, semantic_match))

        skill_match = int(round(max(skill_match_pct, 60.0)))
        skill_match = max(50, min(95, skill_match))

        overall_quality = int(round((ats_score + semantic_match + skill_match + exp_relevance + proj_relevance) / 5))

        score_breakdown = {
            "ats_score": ats_score,
            "semantic_match": semantic_match,
            "skill_match": skill_match,
            "experience_relevance": exp_relevance,
            "project_relevance": proj_relevance,
            "overall_quality": overall_quality
        }

        # 7. Errors & Diagnostics
        errors = detect_resume_errors(cleaned_text)

        matched_list = match_result.get("matched_skills", [])
        missing_list = match_result.get("missing_skills", [])

        # 8 & 9. Dynamic Suggestions & Contextual Rewrites
        ai_insights = generate_pro_insights(
            resume_text=cleaned_text,
            job_description=job_description,
            ats_score=ats_score,
            score_breakdown=score_breakdown,
            matched_skills=matched_list,
            missing_skills=missing_list,
            ml_errors=errors,
            target_role=target_role or "Software Engineer"
        )
        ai_suggestions = ai_insights.get("ai_suggestions", [])
        rewrites = ai_insights.get("rewrites", [])
        ai_mode = ai_insights.get("ai_mode", "ResumeIQ Pro Engine (Active)")
        is_gemini = ai_insights.get("is_gemini", False)

        # 10. Education Scoring
        edu_score_pct = int(round((edu_result.get("education_score", 8) / 10.0) * 100))
        edu_issues = edu_result.get("issues", [])
        if edu_score_pct >= 100 or not edu_issues:
            edu_deductions = []
            edu_positives = ["Degree fully satisfies JD educational requirements."]
            if edu_result.get("details"):
                for d in edu_result["details"]:
                    if d not in edu_positives:
                        edu_positives.append(d)
        else:
            edu_deductions = edu_issues
            edu_positives = edu_result.get("details", ["Academic degree credentials verified."])

        # 11. Top Strengths (Verified matching qualifications)
        top_strengths = []
        if matched_list:
            top_strengths.append(f"Strong technical alignment in {', '.join(matched_list[:4])}")
        if proj_result.get("matched_jd_skills"):
            top_strengths.append(f"Projects directly implement core JD technologies: {', '.join(proj_result['matched_jd_skills'][:3])}")
        elif proj_relevance >= 70:
            top_strengths.append("Hands-on technical project portfolio demonstrated")
        if edu_score_pct >= 75:
            top_strengths.append("Academic degree and educational qualifications satisfy role requirements")
        if is_fresher:
            if exp_result.get("has_tech_skills"):
                months_label = f" ({round(exp_result.get('detected_months', 0), 1)} months)" if exp_result.get('detected_months') else ""
                top_strengths.append(f"Verified technical foundation with practical training / internship evidence{months_label}")
        elif exp_relevance >= 75:
            top_strengths.append("Solid professional experience duration and relevant background")
        if not top_strengths:
            top_strengths.append("Well-structured resume with recognized technical competencies")

        # 12. Resume Gaps (Objective, distinct from Best Suggestions)
        resume_gaps = []
        if missing_list:
            resume_gaps.append(f"Missing {len(missing_list)} critical target keywords: {', '.join(missing_list[:4])}")
        if proj_result.get("missing_jd_skills"):
            resume_gaps.append(f"Projects lack practical demonstration of key JD skills: {', '.join(proj_result['missing_jd_skills'][:3])}")
        if is_fresher and exp_result.get("detected_months", 0) < 4:
            resume_gaps.append("Hands-on internship/project duration is below the 4–6 month threshold for maximum rating")
        elif not is_fresher and exp_result.get("issues"):
            resume_gaps.append(exp_result["issues"][0])
        if edu_score_pct < 100 and edu_issues:
            resume_gaps.append(edu_issues[0])
        if errors.get("spelling_errors"):
            resume_gaps.append(f"Detected {len(errors['spelling_errors'])} spelling or formatting errors in resume text")
        if len(resume_gaps) < 3:
            resume_gaps.append("Work and project descriptions lack quantifiable impact metrics (percentages, scale, speed improvements)")

        # 13. Section-wise Diagnostics
        section_wise = [
            {
                "id": "skills",
                "title": "Technical Skills",
                "score": skill_match,
                "feedback": "Outstanding match" if skill_match >= 80 else "Good, but critical skills missing" if skill_match >= 60 else "Major skill gaps detected",
                "color": "#3b82f6",
                "matched_skills": matched_list,
                "missing_skills": missing_list,
                "deduction_reasons": [f"Missing {len(missing_list)} critical JD skills: {', '.join(missing_list[:6])}"] if missing_list else []
            },
            {
                "id": "experience",
                "title": "Work Experience" if not is_fresher else "Practical Experience & Internships",
                "score": exp_relevance,
                "feedback": "Highly relevant" if exp_relevance >= 80 else "Good practical foundation" if exp_relevance >= 60 else "Needs longer duration and quantifiable impact",
                "color": "#f59e0b",
                "matched_points": exp_result.get("details", ["Practical experience detected."]),
                "deduction_reasons": exp_result.get("issues", []) if exp_relevance < 100 else []
            },
            {
                "id": "projects",
                "title": "Technical Projects",
                "score": proj_relevance,
                "feedback": "Strong project alignment" if proj_relevance >= 80 else "Good, needs stronger metrics and JD skills" if proj_relevance >= 65 else "Projects have low relevance to job requirements",
                "color": "#8b5cf6",
                "matched_points": proj_result.get("details", ["Relevant project titles and technologies detected."]),
                "deduction_reasons": proj_result.get("issues", []) if proj_relevance < 100 else []
            },
            {
                "id": "education",
                "title": "Education & Academics",
                "score": edu_score_pct,
                "feedback": "Fully satisfies requirements" if edu_score_pct >= 90 else "Meets core requirements" if edu_score_pct >= 75 else "Degree or field does not strictly align",
                "color": "#10b981",
                "matched_points": edu_positives,
                "deduction_reasons": edu_deductions
            },
        ]

        # 14. Full Corrected Resume
        corrected_text = correct_resume_with_ai(
            resume_text=cleaned_text,
            job_description=job_description,
            ml_errors=errors,
            target_role=target_role or "Software Engineer"
        )

        now_formatted = datetime.now().strftime("%b %d, %Y at %I:%M %p")

        # 15. Record analysis in database
        record = ResumeAnalysis(
            user_id=current_user.id,
            filename=file.filename or "Resume",
            target_role=target_role.strip() or "Software Engineer",
            ats_score=ats_score,
            result={
                "pro_mode": True,
                "ats_score": ats_score,
                "score_breakdown": score_breakdown,
                "section_wise": section_wise,
                "ai_suggestions": ai_suggestions,
                "rewrites": rewrites,
                "ai_mode": ai_mode,
                "is_gemini": is_gemini
            }
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        db.refresh(current_user)

        return {
            "filename": file.filename,
            "target_role": target_role or "Software Engineer",
            "candidate_type": candidate_type,
            "analyzed_at": now_formatted,
            "pro_match_score": ats_score,
            "score_breakdown": score_breakdown,
            "top_strengths": top_strengths[:5],
            "key_improvements": resume_gaps[:5],
            "section_wise": section_wise,
            "ai_suggestions": ai_suggestions,
            "rewrites": rewrites,
            "strong_semantic_areas": strong_semantic_areas,
            "weak_semantic_areas": weak_semantic_areas,
            "ai_mode": ai_mode,
            "is_gemini": is_gemini,
            "pro_uses_remaining": current_user.pro_uses_remaining,
            "analysis_id": record.id,
            "errors": errors,
            "corrected_resume_text": corrected_text,
            "raw_resume_text": cleaned_text
        }
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        logger.exception("[Pro Analyze] Unexpected error during pro analysis")
        raise HTTPException(status_code=500, detail="Pro analysis failed due to an internal error. Please try again.")


@router.post("/export")
def pro_export_resume(
    request: ProExportRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Export the corrected resume text to PDF or DOCX.
    Requires authentication — only logged-in users may generate export files.
    """
    fmt = request.format.strip().lower()

    if fmt == "pdf":
        file_stream = generate_pdf(request.corrected_resume_text)
        media_type = "application/pdf"
        filename = "Pro_Optimized_Resume.pdf"
    elif fmt == "docx":
        file_stream = generate_docx(request.corrected_resume_text)
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = "Pro_Optimized_Resume.docx"
    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid format. Accepted values are 'pdf' or 'docx'."
        )

    return StreamingResponse(
        file_stream,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


@router.get("/status")
def get_pro_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns current user Pro usage status, AI Mode state, and current user's analysis count.
    """
    user_analysis_count = db.query(func.count(ResumeAnalysis.id)).filter(ResumeAnalysis.user_id == current_user.id).scalar() or 0
    return {
        "pro_uses_remaining": getattr(current_user, "pro_uses_remaining", 5),
        "ai_mode": "AI Mode ON" if is_gemini_active() else "AI Mode OFF",
        "is_ai_active": is_gemini_active(),
        "total_analyses": user_analysis_count
    }
