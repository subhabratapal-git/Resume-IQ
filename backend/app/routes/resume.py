from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
)
from sqlalchemy import func
from sqlalchemy.orm import Session, defer

from app.database import get_db
from app.models.analysis import ResumeAnalysis

from app.models.user import User
from app.routes.auth import get_current_user

from app.services.resume_parser import (
    extract_text_from_docx,
    extract_text_from_pdf,
)

from app.services.text_cleaner import clean_resume_text
from app.services.section_detector import detect_sections
from app.services.skill_extractor import extract_skills
from app.services.job_matcher import match_skills
from app.services.ats_scorer import calculate_ats_score
from app.services.keyword_matcher import calculate_keyword_match
from app.services.structure_scorer import calculate_structure_score
from app.services.education_scorer import calculate_education_score
from app.services.project_scorer import calculate_project_score
from app.services.experience_scorer import calculate_experience_score
from app.services.rate_limiter import analyze_limiter


router = APIRouter()

# Max file size: 5 MB — prevents DoS via large binary uploads
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024

# Max input lengths — prevents oversized payload attacks
MAX_JOB_DESC_LENGTH = 8000
MAX_TARGET_ROLE_LENGTH = 120


async def read_limited_file(file: UploadFile, max_size_bytes: int = MAX_FILE_SIZE_BYTES) -> bytes:
    """
    Reads an uploaded file in chunks up to max_size_bytes.
    Immediately raises 413 if the file exceeds max_size_bytes without reading infinite bytes into RAM.
    """
    chunk_size = 64 * 1024  # 64 KB
    total_bytes = bytearray()

    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total_bytes.extend(chunk)
        if len(total_bytes) > max_size_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"Resume file is too large. Maximum allowed size is {max_size_bytes // (1024 * 1024)} MB.",
            )
    return bytes(total_bytes)


def _verify_file_magic_bytes(file_bytes: bytes, content_type: str) -> bool:
    """
    Verifies the actual file magic bytes match the declared content type.
    Prevents content-type spoofing attacks.
    - PDF files start with: %PDF
    - DOCX files are ZIP archives starting with: PK
    """
    if content_type == "application/pdf":
        return file_bytes[:4] == b"%PDF"

    if content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return file_bytes[:2] == b"PK"

    return False


# =========================================================
# RESUME UPLOAD ROUTE
# =========================================================

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
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

    # Guard: verify magic bytes to prevent content-type spoofing
    if not _verify_file_magic_bytes(file_bytes, file.content_type):
        raise HTTPException(
            status_code=400,
            detail="File content does not match the declared file type.",
        )

    if file.content_type == "application/pdf":
        extracted_text = extract_text_from_pdf(
            file_bytes
        )
    else:
        extracted_text = extract_text_from_docx(
            file_bytes
        )

    if not extracted_text:
        raise HTTPException(
            status_code=400,
            detail="No readable text found in the uploaded resume",
        )

    cleaned_text = clean_resume_text(
        extracted_text
    )

    sections = detect_sections(
        cleaned_text
    )

    skills_text = sections.get(
        "skills",
        ""
    )

    detected_skills = extract_skills(
        skills_text
    )

    # Return only metadata — do NOT expose the full resume text in the response
    return {
        "message": "Resume processed successfully",
        "filename": file.filename,
        "content_type": file.content_type,
        "raw_length": len(extracted_text),
        "cleaned_length": len(cleaned_text),
        "sections": list(sections.keys()),
        "detected_skills": detected_skills,
    }


# =========================================================
# RESUME + JOB DESCRIPTION ANALYSIS ROUTE
# PROTECTED WITH JWT AUTHENTICATION
# =========================================================

@router.post("/analyze")
async def analyze_resume(
    request: Request,
    file: UploadFile = File(...),
    job_description: str = Form(...),
    target_role: str = Form("", max_length=120),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    analyze_limiter.check(request)

    allowed_types = [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are allowed",
        )

    # Truncate to safe length — prevents oversized payload and prompt injection attacks
    job_description = job_description.strip()[:MAX_JOB_DESC_LENGTH]

    if not job_description:
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty",
        )

    # Chunked stream reading prevents memory exhaustion from huge uploads
    file_bytes = await read_limited_file(file, MAX_FILE_SIZE_BYTES)

    # Guard: verify magic bytes to prevent content-type spoofing
    if not _verify_file_magic_bytes(file_bytes, file.content_type):
        raise HTTPException(
            status_code=400,
            detail="File content does not match the declared file type.",
        )

    if file.content_type == "application/pdf":
        extracted_text = extract_text_from_pdf(
            file_bytes
        )
    else:
        extracted_text = extract_text_from_docx(
            file_bytes
        )

    if not extracted_text:
        raise HTTPException(
            status_code=400,
            detail="No readable text found in the uploaded resume",
        )

    cleaned_text = clean_resume_text(
        extracted_text
    )

    sections = detect_sections(
        cleaned_text
    )

    # -----------------------------------------------------
    # EDUCATION ANALYSIS
    # -----------------------------------------------------

    education_result = calculate_education_score(
        sections,
        job_description,
    )

    # -----------------------------------------------------
    # STRUCTURE ANALYSIS
    # -----------------------------------------------------

    structure_result = calculate_structure_score(
        sections
    )

    # -----------------------------------------------------
    # PROJECT ANALYSIS
    # -----------------------------------------------------

    project_result = calculate_project_score(
        sections,
        job_description,
    )

    # -----------------------------------------------------
    # EXPERIENCE ANALYSIS
    # -----------------------------------------------------

    experience_result = calculate_experience_score(
        sections,
        job_description,
    )

    # -----------------------------------------------------
    # SKILL ANALYSIS
    # -----------------------------------------------------

    skills_text = sections.get(
        "skills",
        ""
    )

    resume_skills = extract_skills(
        skills_text
    )

    job_skills = extract_skills(
        job_description
    )

    match_result = match_skills(
        resume_skills,
        job_skills,
    )

    # -----------------------------------------------------
    # KEYWORD ANALYSIS
    # -----------------------------------------------------

    keyword_result = calculate_keyword_match(
        cleaned_text,
        job_description,
    )

    # -----------------------------------------------------
    # FINAL ATS SCORE
    # -----------------------------------------------------

    ats_result = calculate_ats_score(
        match_result[
            "skill_match_percentage"
        ],
        keyword_result[
            "keyword_score"
        ],
        structure_result[
            "structure_score"
        ],
        education_result[
            "education_score"
        ],
        project_result[
            "project_score"
        ],
        experience_result[
            "experience_score"
        ],
    )

    result = {
        "message": "Resume analyzed successfully",

        "filename": file.filename,

        "user": {
            "id": current_user.id,
            "email": current_user.email,
        },

        "resume_skills": resume_skills,
        "job_skills": job_skills,

        "matched_skills": match_result[
            "matched_skills"
        ],

        "missing_skills": match_result[
            "missing_skills"
        ],

        "skill_match_percentage": match_result[
            "skill_match_percentage"
        ],

        "keyword_analysis": keyword_result,

        "structure_analysis": structure_result,

        "education_analysis": education_result,

        "project_analysis": project_result,

        "experience_analysis": experience_result,

        "ats_score_details": ats_result,
    }
    # Keep the existing scoring output intact; save only successful reports.
    # The original file and full job description are not retained.
    record = ResumeAnalysis(
        user_id=current_user.id,
        filename=file.filename or "Resume",
        target_role=target_role.strip(),
        ats_score=ats_result["ats_score"],
        result={key: value for key, value in result.items() if key != "user"},
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    result.update(analysis_id=record.id, analyzed_at=record.created_at.isoformat() + "Z", target_role=record.target_role)
    return result


@router.get("/history")
def analysis_history(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(ResumeAnalysis).filter(ResumeAnalysis.user_id == current_user.id)
    total = query.count()
    best = db.query(func.max(ResumeAnalysis.ats_score)).filter(ResumeAnalysis.user_id == current_user.id).scalar()
    records = query.options(defer(ResumeAnalysis.result)).order_by(ResumeAnalysis.id.desc()).offset(offset).limit(limit).all()
    return {
        "total": total,
        "best_score": best,
        "offset": offset,
        "limit": limit,
        "items": [{
            "id": item.id,
            "filename": item.filename,
            "target_role": item.target_role,
            "ats_score": item.ats_score,
            "created_at": item.created_at.isoformat() + "Z",
            "mode": "normal",
        } for item in records],
    }


@router.get("/history/{analysis_id}")
def saved_analysis(
    analysis_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = db.query(ResumeAnalysis).filter(
        ResumeAnalysis.id == analysis_id,
        ResumeAnalysis.user_id == current_user.id,
    ).first()
    if record is None:
        raise HTTPException(status_code=404, detail="Saved analysis not found")
    return {**record.result, "analysis_id": record.id, "analyzed_at": record.created_at.isoformat() + "Z", "target_role": record.target_role}
