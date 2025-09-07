from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.resume import Resume
from app.schemas.resume import (
    Resume as ResumeSchema, 
    ResumeAnalysis, 
    ResumeUpdate, 
    ResumeScore,
    ResumeFeedback,
    ParsedData
)
from app.api.auth import get_current_job_seeker, get_current_user
from app.services.resume_parser import resume_parser
from app.services.resume_scorer import resume_scorer
from app.utils.file_handler import file_handler
from app.utils.validators import ResumeDataValidator

router = APIRouter(prefix="/api/v1/resumes", tags=["resumes"])

@router.post("/upload", response_model=ResumeAnalysis)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_job_seeker),
    db: Session = Depends(get_db)
):
    """Upload and parse a resume"""

    # Read file content
    file_content = await file.read()

    # Validate file
    is_valid, error_msg = file_handler.validate_file(file.filename, len(file_content))
    if not is_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg)

    try:
        # Save file to disk
        file_path, safe_filename = file_handler.save_uploaded_file(
            file_content, file.filename, current_user.id
        )

        # Parse resume
        parsed_data = await resume_parser.parse_resume(file_content, file.filename)

        # Validate parsed data
        validation_result = ResumeDataValidator.validate_parsed_resume_data(parsed_data)

        # Calculate scores and feedback
        scores, feedback = resume_scorer.score_resume(parsed_data)

        # Delete existing resumes for this user (keep only latest)
        existing_resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
        for existing_resume in existing_resumes:
            file_handler.delete_file(existing_resume.file_path)
            db.delete(existing_resume)

        # Create new resume record
        db_resume = Resume(
            user_id=current_user.id,
            original_filename=file.filename,
            file_path=file_path,
            extracted_text=parsed_data.get("extracted_text"),
            parsed_name=parsed_data.get("parsed_name"),
            parsed_email=parsed_data.get("parsed_email"),
            parsed_phone=parsed_data.get("parsed_phone"),
            skills=parsed_data.get("skills"),
            experience_years=parsed_data.get("experience_years"),
            education=parsed_data.get("education"),
            work_experience=parsed_data.get("work_experience"),
            projects=parsed_data.get("projects"),
            ats_score=scores.ats_score,
            completeness_score=scores.completeness_score,
            keyword_density_score=scores.keyword_density_score,
            formatting_score=scores.formatting_score,
            warnings=[warning for warning in feedback.warnings],
            suggestions=[suggestion for suggestion in feedback.suggestions]
        )

        db.add(db_resume)
        db.commit()
        db.refresh(db_resume)

        return ResumeAnalysis(
            resume=ResumeSchema.from_orm(db_resume),
            score=ResumeScore(
                ats_score=scores.ats_score,
                completeness_score=scores.completeness_score,
                keyword_density_score=scores.keyword_density_score,
                formatting_score=scores.formatting_score,
                overall_score=scores.overall_score
            ),
            feedback=ResumeFeedback(
                warnings=feedback.warnings,
                suggestions=feedback.suggestions,
                missing_fields=feedback.missing_fields
            ),
            parsed_data=ParsedData(
                name=parsed_data.get("parsed_name"),
                email=parsed_data.get("parsed_email"),
                phone=parsed_data.get("parsed_phone"),
                skills=parsed_data.get("skills"),
                experience_years=parsed_data.get("experience_years"),
                education=parsed_data.get("education"),
                work_experience=parsed_data.get("work_experience"),
                projects=parsed_data.get("projects")
            )
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing resume: {str(e)}"
        )

@router.get("/", response_model=List[ResumeSchema])
def get_user_resumes(
    current_user: User = Depends(get_current_job_seeker),
    db: Session = Depends(get_db)
):
    """Get all resumes for the current user"""
    resumes = db.query(Resume).filter(Resume.user_id == current_user.id).all()
    return [ResumeSchema.from_orm(resume) for resume in resumes]

@router.get("/{resume_id}", response_model=ResumeAnalysis)
def get_resume(
    resume_id: int,
    current_user: User = Depends(get_current_job_seeker),
    db: Session = Depends(get_db)
):
    """Get specific resume with analysis"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    return ResumeAnalysis(
        resume=ResumeSchema.from_orm(resume),
        score=ResumeScore(
            ats_score=resume.ats_score,
            completeness_score=resume.completeness_score,
            keyword_density_score=resume.keyword_density_score,
            formatting_score=resume.formatting_score,
            overall_score=(resume.ats_score + resume.completeness_score + 
                          resume.keyword_density_score + resume.formatting_score) / 4
        ),
        feedback=ResumeFeedback(
            warnings=resume.warnings or [],
            suggestions=resume.suggestions or [],
            missing_fields=[]
        ),
        parsed_data=ParsedData(
            name=resume.parsed_name,
            email=resume.parsed_email,
            phone=resume.parsed_phone,
            skills=resume.skills,
            experience_years=resume.experience_years,
            education=resume.education,
            work_experience=resume.work_experience,
            projects=resume.projects
        )
    )

@router.put("/{resume_id}", response_model=ResumeSchema)
def update_resume(
    resume_id: int,
    parsed_data: ResumeUpdate,
    current_user: User = Depends(get_current_job_seeker),
    db: Session = Depends(get_db)
):
    """Update resume with edited information"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()

    print("update data", parsed_data)
    
    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    # Update fields
    update_data = parsed_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == 'name':
            setattr(resume, 'parsed_name', value)
        elif field == 'email':
            setattr(resume, 'parsed_email', value)
        elif field == 'phone':
            setattr(resume, 'parsed_phone', value)
        else:
            setattr(resume, field, value)

    # Recalculate scores with updated data
    parsed_data = {
        "parsed_name": resume.parsed_name,
        "parsed_email": resume.parsed_email,
        "parsed_phone": resume.parsed_phone,
        "skills": resume.skills,
        "experience_years": resume.experience_years,
        "education": resume.education,
        "work_experience": resume.work_experience,
        "projects": resume.projects,
        "extracted_text": resume.extracted_text
    }

    scores, feedback = resume_scorer.score_resume(parsed_data)

    # Update scores
    resume.ats_score = scores.ats_score
    resume.completeness_score = scores.completeness_score
    resume.keyword_density_score = scores.keyword_density_score
    resume.formatting_score = scores.formatting_score
    resume.warnings = feedback.warnings
    resume.suggestions = feedback.suggestions

    print("resume data", resume)

    db.commit()
    db.refresh(resume)

    return ResumeSchema.from_orm(resume)

@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    current_user: User = Depends(get_current_job_seeker),
    db: Session = Depends(get_db)
):
    """Delete a resume"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    # Delete file from disk
    file_handler.delete_file(resume.file_path)

    # Delete from database
    db.delete(resume)
    db.commit()

    return {"message": "Resume deleted successfully"}

@router.post("/{resume_id}/reanalyze", response_model=ResumeAnalysis)
def reanalyze_resume(
    resume_id: int,
    current_user: User = Depends(get_current_job_seeker),
    db: Session = Depends(get_db)
):
    """Reanalyze resume with latest algorithms"""
    resume = db.query(Resume).filter(
        Resume.id == resume_id,
        Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    # Prepare data for reanalysis
    parsed_data = {
        "parsed_name": resume.parsed_name,
        "parsed_email": resume.parsed_email,
        "parsed_phone": resume.parsed_phone,
        "skills": resume.skills,
        "experience_years": resume.experience_years,
        "education": resume.education,
        "work_experience": resume.work_experience,
        "projects": resume.projects,
        "extracted_text": resume.extracted_text
    }

    # Recalculate scores and feedback
    scores, feedback = resume_scorer.score_resume(parsed_data)

    # Update resume
    resume.ats_score = scores.ats_score
    resume.completeness_score = scores.completeness_score
    resume.keyword_density_score = scores.keyword_density_score
    resume.formatting_score = scores.formatting_score
    resume.warnings = feedback.warnings
    resume.suggestions = feedback.suggestions

    db.commit()
    db.refresh(resume)

    return ResumeAnalysis(
        resume=ResumeSchema.from_orm(resume),
        score=ResumeScore(
            ats_score=scores.ats_score,
            completeness_score=scores.completeness_score,
            keyword_density_score=scores.keyword_density_score,
            formatting_score=scores.formatting_score,
            overall_score=scores.overall_score
        ),
        feedback=ResumeFeedback(
            warnings=feedback.warnings,
            suggestions=feedback.suggestions,
            missing_fields=feedback.missing_fields
        ),
        parsed_data=ParsedData(
            name=resume.parsed_name,
            email=resume.parsed_email,
            phone=resume.parsed_phone,
            skills=resume.skills,
            experience_years=resume.experience_years,
            education=resume.education,
            work_experience=resume.work_experience,
            projects=resume.projects
        )
    )
