from typing import List, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

# Set up logging
logger = logging.getLogger(__name__)

from app.core.database import get_db
from app.models.user import User
from app.models.job import Job, JobApplication
from app.models.resume import Resume
from app.models.user_preferences import UserJobPreferences, JobComparison, JobComparisonItem
from app.schemas.job import (
    Job as JobSchema, 
    JobCreate, 
    JobUpdate, 
    JobRecommendation,
    JobApplicationCreate,
    JobApplication as JobApplicationSchema,
    JobSearchFilters
)
from app.schemas.user_preferences import (
    JobFeedbackRequest,
    JobBookmarkRequest,
    JobHideRequest,
    JobComparisonRequest,
    UserJobPreferencesResponse,
    JobComparisonResponse,
    JobComparisonDetailResponse
)
from app.api.auth import get_current_recruiter, get_current_job_seeker, get_current_user
from app.services.job_matcher import job_matcher

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])

@router.post("/", response_model=JobSchema)
def create_job(
    job_data: JobCreate,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Create a new job posting"""
    db_job = Job(
        recruiter_id=current_user.id,
        title=job_data.title,
        description=job_data.description,
        company_name=job_data.company_name,
        location=job_data.location,
        job_type=job_data.job_type,
        required_skills=job_data.required_skills,
        preferred_skills=job_data.preferred_skills,
        min_experience_years=job_data.min_experience_years,
        max_experience_years=job_data.max_experience_years,
        education_requirements=job_data.education_requirements,
        min_salary=job_data.min_salary,
        max_salary=job_data.max_salary,
        currency=job_data.currency,
        benefits=job_data.benefits,
        remote_work_allowed=job_data.remote_work_allowed,
        application_deadline=job_data.application_deadline
    )

    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    return JobSchema.from_orm(db_job)

@router.get("/", response_model=List[JobSchema])
def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    location: Optional[str] = Query(None),
    job_type: Optional[str] = Query(None),
    min_salary: Optional[float] = Query(None),
    max_salary: Optional[float] = Query(None),
    skills: Optional[str] = Query(None),  # Comma-separated skills
    experience_years: Optional[float] = Query(None),
    remote_work: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List jobs with advanced filtering and search"""
    query = db.query(Job).filter(Job.status == "active")

    # Apply filters
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    if job_type:
        query = query.filter(Job.job_type == job_type)

    if min_salary:
        query = query.filter(
            or_(Job.min_salary >= min_salary, Job.max_salary >= min_salary)
        )

    if max_salary:
        query = query.filter(
            or_(Job.max_salary <= max_salary, Job.min_salary <= max_salary)
        )

    if skills:
        skill_list = [skill.strip().lower() for skill in skills.split(",")]
        for skill in skill_list:
            query = query.filter(
                or_(
                    Job.required_skills.contains([skill]),
                    Job.preferred_skills.contains([skill])
                )
            )

    if experience_years:
        query = query.filter(
            and_(
                Job.min_experience_years <= experience_years,
                Job.max_experience_years >= experience_years
            )
        )

    if remote_work:
        query = query.filter(Job.remote_work_allowed.ilike(f"%{remote_work}%"))

    if company:
        query = query.filter(Job.company_name.ilike(f"%{company}%"))

    # Order by most recent first
    query = query.order_by(Job.created_at.desc())

    jobs = query.offset(skip).limit(limit).all()
    return [JobSchema.from_orm(job) for job in jobs]

@router.post("/search", response_model=List[JobSchema])
def search_jobs(
    filters: JobSearchFilters,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, le=100),
    sort_by: str = Query("relevance", regex="^(relevance|salary|date|experience)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Advanced job search with filters and sorting"""
    query = db.query(Job).filter(Job.status == "active")

    # Apply filters
    if filters.location:
        query = query.filter(Job.location.ilike(f"%{filters.location}%"))

    if filters.job_type:
        query = query.filter(Job.job_type == filters.job_type)

    if filters.min_salary:
        query = query.filter(
            or_(Job.min_salary >= filters.min_salary, Job.max_salary >= filters.min_salary)
        )

    if filters.max_salary:
        query = query.filter(
            or_(Job.max_salary <= filters.max_salary, Job.min_salary <= filters.max_salary)
        )

    if filters.remote_work_allowed:
        query = query.filter(Job.remote_work_allowed.ilike(f"%{filters.remote_work_allowed}%"))

    if filters.skills:
        for skill in filters.skills:
            query = query.filter(
                or_(
                    Job.required_skills.contains([skill.lower()]),
                    Job.preferred_skills.contains([skill.lower()])
                )
            )

    if filters.experience_years:
        query = query.filter(
            and_(
                Job.min_experience_years <= filters.experience_years,
                Job.max_experience_years >= filters.experience_years
            )
        )

    # Apply sorting
    if sort_by == "salary":
        query = query.order_by(Job.max_salary.desc())
    elif sort_by == "date":
        query = query.order_by(Job.created_at.desc())
    elif sort_by == "experience":
        query = query.order_by(Job.min_experience_years.asc())
    else:  # relevance - default sorting
        query = query.order_by(Job.created_at.desc())

    jobs = query.offset(skip).limit(limit).all()
    return [JobSchema.from_orm(job) for job in jobs]

@router.get("/search/quick", response_model=List[JobSchema])
@router.post("/search/quick", response_model=List[JobSchema])
def quick_search_jobs(
    q: str = Query(..., description="Search query for job title, company, or skills"),
    location: Optional[str] = Query(None),
    limit: int = Query(20, le=50),
    db: Session = Depends(get_db)
):
    """Quick search across job titles, companies, and skills"""
    query = db.query(Job).filter(Job.status == "ACTIVE")
    
    # Simple search across multiple fields
    # Search across multiple fields
    if q and q.strip():
        search_term = f"%{q.strip()}%"
        print(f"Search term: '{q}' -> search_term: '{search_term}'")
        
        # Debug: Check what the query looks like before filter
        print(f"Jobs before search filter: {query.count()}")
        
        query = query.filter(
            or_(
                Job.title.ilike(search_term),
                Job.company_name.ilike(search_term),
                Job.description.ilike(search_term),
                Job.location.ilike(search_term),
                # Also search in skills arrays
                Job.required_skills.contains([q.lower()]),
                Job.preferred_skills.contains([q.lower()])
            )
        )
        
        # Debug: Check what the query looks like after filter
        print(f"Jobs after search filter: {query.count()}")
    else:
        print(f"No search term provided or empty: '{q}'")
    
    
    query = query.order_by(Job.created_at.desc())
    
    # Debug logging
    print(f'Search query: {q}')
    print(f'Limit parameter: {limit}')
    print(f'Total active jobs: {db.query(Job).filter(Job.status == "ACTIVE").count()}')
    print(f'Total matching jobs before limit: {query.count()}')
    
    # Show a few sample jobs to debug
    sample_jobs = db.query(Job).filter(Job.status == "ACTIVE").limit(3).all()
    print("Sample job titles:")
    for job in sample_jobs:
        print(f"- {job.title}")
        print(f"  Company: {job.company_name}")
        print(f"  Location: {job.location}")
        print(f"  Description preview: {job.description[:100]}...")
    
    jobs = query.limit(limit).all()
    print(f'Jobs returned after limit: {len(jobs)}')
    
    return jobs

@router.get("/recommendations", response_model=List[JobRecommendation])
def get_job_recommendations(
    current_user: User = Depends(get_current_job_seeker),
    limit: int = Query(50, le=50),
    location: Optional[str] = Query(None),
    skills: Optional[str] = Query(None),
    experience_years: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    """Get personalized job recommendations for the current user""" 
    logger.info("=== JOB RECOMMENDATIONS API CALLED ===")
    logger.info(f"User ID: {current_user.id}")
    logger.info(f"Limit: {limit}")
    logger.info(f"Location filter: {location}")
    logger.info(f"Skills filter: {skills}")
    logger.info(f"Experience filter: {experience_years}")

    resume = db.query(Resume).filter(
        Resume.user_id == current_user.id
    ).order_by(Resume.created_at.desc()).first()


    if not resume:
        logger.info("No resume found for user, returning recent active jobs")
        # If no resume, return recent active jobs
        jobs = db.query(Job).filter(
            Job.status == "active"
        ).order_by(Job.created_at.desc()).limit(limit).all()
        
        return [
            JobRecommendation(
                job=JobSchema.from_orm(job),
                match_score=0.5,
                match_reasons=["No resume available for personalized matching"],
                skill_matches=[],
                missing_skills=job.required_skills or []
            )
            for job in jobs
        ]
    
    logger.info(f"Found resume for user: {resume.id}")
    logger.info(f"Resume skills: {resume.skills}")
    logger.info(f"Resume experience: {resume.experience_years}")
    logger.info(f"Resume text length: {len(resume.extracted_text or '')}")
    
    # Prepare candidate data for matching with resume text
    candidate_data = {
        "skills": resume.skills or [],
        "experience_years": resume.experience_years or 0,
        "location": current_user.location,
        "salary_expectation": None,
        "resume_text": resume.extracted_text or ""  # Add resume text for NLP processing
    }
    logger.info(f"Prepared candidate data: {candidate_data}")
    
    # Build job query with filters
    job_query = db.query(Job).filter(Job.status == "active")
    logger.info("Building job query with filters")
    
    if location:
        job_query = job_query.filter(Job.location.ilike(f"%{location}%"))
        logger.info(f"Applied location filter: {location}")
    
    if skills:
        skill_list = [skill.strip().lower() for skill in skills.split(",")]
        logger.info(f"Applied skills filter: {skill_list}")
        for skill in skill_list:
            job_query = job_query.filter(
                or_(
                    Job.required_skills.contains([skill]),
                    Job.preferred_skills.contains([skill])
                )
            )
    
    if experience_years is not None:
        job_query = job_query.filter(
            Job.min_experience_years <= experience_years,
            Job.max_experience_years >= experience_years
        )
        logger.info(f"Applied experience filter: {experience_years}")
    
    # Get jobs and apply matching
    jobs = job_query.limit(limit * 2).all()  # Get more jobs for better matching
    logger.info(f"Found {len(jobs)} jobs from database")
    
    if not jobs:
        logger.info("No jobs found, returning empty list")
        return []
    
    # Convert jobs to dict format for matching
    job_data_list = []
    for job in jobs:
        job_data_list.append({
            "id": job.id,
            "required_skills": job.required_skills or [],
            "preferred_skills": job.preferred_skills or [],
            "min_experience_years": job.min_experience_years,
            "max_experience_years": job.max_experience_years,
            "location": job.location,
            "remote_work_allowed": job.remote_work_allowed,
            "min_salary": job.min_salary,
            "max_salary": job.max_salary,
            "description": job.description,
            "status": "active"
        })
    

    logger.info(f"Converted {len(job_data_list)} jobs to dict format")
    logger.info("Calling job matcher service...")
    
    # Get matches using job matcher service
    try:
        matches = job_matcher.match_candidate_to_jobs(candidate_data, job_data_list, top_k=limit)
        logger.info(f"Job matcher returned {len(matches)} matches")
    except Exception as e:
        logger.error(f"Job matcher failed: {e}")
        logger.info("Falling back to simple matching")
        # Fallback to simple matching if job matcher fails
        matches = []
        for job in jobs[:limit]:
            # Simple skill-based matching
            user_skills = set(skill.lower() for skill in (resume.skills or []))
            required_skills = set(skill.lower() for skill in (job.required_skills or []))
            preferred_skills = set(skill.lower() for skill in (job.preferred_skills or []))
            
            matching_skills = user_skills.intersection(required_skills.union(preferred_skills))
            total_skills = len(required_skills.union(preferred_skills))
            
            if total_skills > 0:
                match_score = len(matching_skills) / total_skills
            else:
                match_score = 0.5
            
            matches.append({
                "job_id": job.id,
                "match_score": match_score,
                "matching_skills": list(matching_skills),
                "missing_skills": list(required_skills - user_skills),
                "match_reasons": [f"Skill match: {len(matching_skills)}/{len(required_skills.union(preferred_skills))}"],
                "skill_matches": list(matching_skills)
            })
    
    logger.info("Creating job recommendations...")
    # Create recommendations
    recommendations = []
    for match in matches:
        job_id = match.get("job_id") if isinstance(match, dict) else match.job_id
        match_score = match.get("match_score") if isinstance(match, dict) else match.match_score
        matching_skills = match.get("matching_skills", []) if isinstance(match, dict) else getattr(match, 'matching_skills', [])
        missing_skills = match.get("missing_skills", []) if isinstance(match, dict) else getattr(match, 'missing_skills', [])
        match_reasons = match.get("match_reasons", []) if isinstance(match, dict) else getattr(match, 'match_reasons', [])
        skill_matches = match.get("skill_matches", []) if isinstance(match, dict) else getattr(match, 'skill_matches', [])
        
        # Find the job object
        job = next((j for j in jobs if j.id == job_id), None)
        if job:
            recommendations.append(
                JobRecommendation(
                    job=JobSchema.from_orm(job),
                    match_score=match_score,
                    match_reasons=match_reasons,
                    skill_matches=skill_matches,
                    missing_skills=missing_skills
                )
            )
    
    logger.info(f"Created {len(recommendations)} recommendations")
    logger.info(f"Top 3 match scores: {[f'{r.match_score:.3f}' for r in recommendations[:3]]}")
    
    # Sort by match score and return top recommendations
    recommendations.sort(key=lambda x: x.match_score, reverse=True)
    return recommendations[:limit]

@router.get("/stats/overview")
def get_job_stats_overview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overview statistics for jobs"""
    from sqlalchemy import func, desc
    
    total_jobs = db.query(Job).filter(Job.status == "active").count()
    
    # Location distribution
    location_stats = db.query(
        Job.location,
        func.count(Job.id).label('count')
    ).filter(Job.status == "active").group_by(Job.location).order_by(desc('count')).limit(10).all()
    
    # Job type distribution
    job_type_stats = db.query(
        Job.job_type,
        func.count(Job.id).label('count')
    ).filter(Job.status == "active").group_by(Job.job_type).all()
    
    # Salary ranges
    salary_stats = db.query(
        func.avg(Job.min_salary).label('avg_min_salary'),
        func.avg(Job.max_salary).label('avg_max_salary'),
        func.min(Job.min_salary).label('min_salary'),
        func.max(Job.max_salary).label('max_salary')
    ).filter(Job.status == "active").first()
    
    return {
        "total_active_jobs": total_jobs,
        "location_distribution": [{"location": loc, "count": count} for loc, count in location_stats],
        "job_type_distribution": [{"type": jt, "count": count} for jt, count in job_type_stats],
        "salary_statistics": {
            "average_min_salary": float(salary_stats.avg_min_salary) if salary_stats.avg_min_salary else 0,
            "average_max_salary": float(salary_stats.avg_max_salary) if salary_stats.avg_max_salary else 0,
            "min_salary": float(salary_stats.min_salary) if salary_stats.min_salary else 0,
            "max_salary": float(salary_stats.max_salary) if salary_stats.max_salary else 0
        }
    }

@router.get("/stats/skills")
def get_skills_statistics(
    limit: int = Query(20, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get skills statistics from job requirements"""
    # Count required skills
    required_skills_count = {}
    preferred_skills_count = {}
    
    jobs = db.query(Job).filter(Job.status == "active").all()
    total_jobs = len(jobs)
    
    for job in jobs:
        if job.required_skills:
            for skill in job.required_skills:
                skill_lower = skill.lower()
                required_skills_count[skill_lower] = required_skills_count.get(skill_lower, 0) + 1
        
        if job.preferred_skills:
            for skill in job.preferred_skills:
                skill_lower = skill.lower()
                preferred_skills_count[skill_lower] = preferred_skills_count.get(skill_lower, 0) + 1
    
    # Combine and sort by total demand
    all_skills = set(required_skills_count.keys()) | set(preferred_skills_count.keys())
    skills_stats = []
    
    for skill in all_skills:
        required_count = required_skills_count.get(skill, 0)
        preferred_count = preferred_skills_count.get(skill, 0)
        total_demand = required_count + preferred_count
        
        skills_stats.append({
            "skill": skill,
            "required_count": required_count,
            "preferred_count": preferred_count,
            "total_demand": total_demand,
            "demand_score": (required_count * 2 + preferred_count) / total_jobs * 100 if total_jobs > 0 else 0
        })
    
    # Sort by total demand and return top skills
    skills_stats.sort(key=lambda x: x["total_demand"], reverse=True)
    return skills_stats[:limit]

@router.get("/my-jobs", response_model=List[JobSchema])
def get_my_jobs(
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Get jobs posted by current recruiter"""
    jobs = db.query(Job).filter(Job.recruiter_id == current_user.id).all()
    return [JobSchema.from_orm(job) for job in jobs]

@router.get("/{job_id}", response_model=JobSchema)
def get_job(
    job_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get specific job details"""
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    return JobSchema.from_orm(job)

@router.put("/{job_id}", response_model=JobSchema)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Update job posting"""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.recruiter_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    # Update fields
    update_data = job_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)

    return JobSchema.from_orm(job)

@router.delete("/{job_id}")
def delete_job(
    job_id: int,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Delete job posting"""
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.recruiter_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    db.delete(job)
    db.commit()

    return {"message": "Job deleted successfully"}

@router.post("/{job_id}/apply", response_model=JobApplicationSchema)
def apply_to_job(
    job_id: int,
    application_data: JobApplicationCreate,
    current_user: User = Depends(get_current_job_seeker),
    db: Session = Depends(get_db)
):
    """Apply to a job"""
    # Check if job exists and is active
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.status == "ACTIVE"
    ).one()

    print(f"Job: {len(job)}")

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found or not active"
        )

    # Check if resume exists and belongs to user
    resume = db.query(Resume).filter(
        Resume.id == application_data.resume_id,
        Resume.user_id == current_user.id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    # Check if already applied
    existing_application = db.query(JobApplication).filter(
        JobApplication.job_id == job_id,
        JobApplication.user_id == current_user.id
    ).first()

    if existing_application:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already applied to this job"
        )

    # Calculate match score with resume text
    candidate_data = {
        "skills": resume.skills or [],
        "experience_years": resume.experience_years,
        "location": current_user.location,
        "salary_expectation": None,
        "resume_text": resume.extracted_text or ""  # Add resume text for NLP processing
    }

    job_data = {
        "id": job.id,
        "required_skills": job.required_skills or [],
        "preferred_skills": job.preferred_skills or [],
        "min_experience_years": job.min_experience_years,
        "max_experience_years": job.max_experience_years,
        "location": job.location,
        "remote_work_allowed": job.remote_work_allowed,
        "min_salary": job.min_salary,
        "max_salary": job.max_salary,
        "description": job.description,
        "status": "active"
    }

    matches = job_matcher.match_candidate_to_jobs(candidate_data, [job_data], top_k=1)
    match_score = matches[0].match_score if matches else 0.5

    # Create application
    application = JobApplication(
        job_id=job_id,
        user_id=current_user.id,
        resume_id=application_data.resume_id,
        cover_letter=application_data.cover_letter,
        match_score=match_score
    )

    db.add(application)
    db.commit()
    db.refresh(application)

    return JobApplicationSchema.from_orm(application)

@router.get("/applications/my-applications", response_model=List[JobApplicationSchema])
def get_my_applications(
    current_user: User = Depends(get_current_job_seeker),
    db: Session = Depends(get_db)
):
    """Get job applications by current user"""
    applications = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id
    ).order_by(JobApplication.applied_at.desc()).all()

    return [JobApplicationSchema.from_orm(app) for app in applications]

@router.get("/{job_id}/applications", response_model=List[JobApplicationSchema])
def get_job_applications(
    job_id: int,
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Get applications for a specific job (recruiter only)"""
    # Verify job belongs to current recruiter
    job = db.query(Job).filter(
        Job.id == job_id,
        Job.recruiter_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    applications = db.query(JobApplication).filter(
        JobApplication.job_id == job_id
    ).order_by(JobApplication.match_score.desc()).all()

    return [JobApplicationSchema.from_orm(app) for app in applications]

# =============================================================================
# JOB PREFERENCES ENDPOINTS
# =============================================================================

@router.post("/feedback", response_model=UserJobPreferencesResponse)
def provide_job_feedback(
    feedback_data: JobFeedbackRequest,
    current_user: User = Depends(get_current_job_seeker),
    db: Session = Depends(get_db)
):
    """Provide feedback for a job (relevant, not_relevant, maybe_later)"""
    
    # Check if job exists
    job = db.query(Job).filter(Job.id == feedback_data.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get or create user job preferences
    preferences = db.query(UserJobPreferences).filter(
        UserJobPreferences.user_id == current_user.id,
        UserJobPreferences.job_id == feedback_data.job_id
    ).first()
    
    if not preferences:
        preferences = UserJobPreferences(
            user_id=current_user.id,
            job_id=feedback_data.job_id
        )
        db.add(preferences)
    
    # Update feedback based on type
    if feedback_data.feedback_type == "relevant":
        preferences.is_relevant = True
        preferences.is_maybe_later = False
    elif feedback_data.feedback_type == "not_relevant":
        preferences.is_relevant = False
        preferences.is_maybe_later = False
    elif feedback_data.feedback_type == "maybe_later":
        preferences.is_maybe_later = True
        preferences.is_relevant = None  # Reset relevant status
    
    if feedback_data.notes:
        preferences.feedback_notes = feedback_data.notes
    
    db.commit()
    db.refresh(preferences)
    
    return UserJobPreferencesResponse.from_orm(preferences)

@router.post("/bookmark", response_model=UserJobPreferencesResponse)
def toggle_job_bookmark(
    bookmark_data: JobBookmarkRequest,
    current_user: User = Depends(get_current_job_seeker),
    db: Session = Depends(get_db)
):
    """Bookmark or unbookmark a job"""
    
    # Check if job exists
    job = db.query(Job).filter(Job.id == bookmark_data.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get or create user job preferences
    preferences = db.query(UserJobPreferences).filter(
        UserJobPreferences.user_id == current_user.id,
        UserJobPreferences.job_id == bookmark_data.job_id
    ).first()
    
    if not preferences:
        preferences = UserJobPreferences(
            user_id=current_user.id,
            job_id=bookmark_data.job_id
        )
        db.add(preferences)
    
    preferences.is_bookmarked = bookmark_data.is_bookmarked
    db.commit()
    db.refresh(preferences)
    
    return UserJobPreferencesResponse.from_orm(preferences)

@router.post("/hide", response_model=UserJobPreferencesResponse)
def toggle_job_visibility(
    hide_data: JobHideRequest,
    current_user: User = Depends(get_current_job_seeker),
    db: Session = Depends(get_db)
):
    """Hide or show a job"""
    
    # Check if job exists
    job = db.query(Job).filter(Job.id == hide_data.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    # Get or create user job preferences
    preferences = db.query(UserJobPreferences).filter(
        UserJobPreferences.user_id == current_user.id,
        UserJobPreferences.job_id == hide_data.job_id
    ).first()
    
    if not preferences:
        preferences = UserJobPreferences(
            user_id=current_user.id,
            job_id=hide_data.job_id
        )
        db.add(preferences)
    
    preferences.is_hidden = hide_data.is_hidden
    db.commit()
    db.refresh(preferences)
    
    return UserJobPreferencesResponse.from_orm(preferences)

@router.get("/preferences", response_model=List[UserJobPreferencesResponse])
def get_user_job_preferences(
    current_user: User = Depends(get_current_job_seeker),
    db: Session = Depends(get_db)
):
    """Get all job preferences for the current user"""
    
    preferences = db.query(UserJobPreferences).filter(
        UserJobPreferences.user_id == current_user.id
    ).all()
    
    return [UserJobPreferencesResponse.from_orm(pref) for pref in preferences]

@router.get("/bookmarked", response_model=List[JobSchema])
def get_bookmarked_jobs(
    current_user: User = Depends(get_current_job_seeker),
    db: Session = Depends(get_db)
):
    """Get all bookmarked jobs for the current user"""
    
    bookmarked_preferences = db.query(UserJobPreferences).filter(
        UserJobPreferences.user_id == current_user.id,
        UserJobPreferences.is_bookmarked == True
    ).all()
    
    job_ids = [pref.job_id for pref in bookmarked_preferences]
    jobs = db.query(Job).filter(Job.id.in_(job_ids)).all()
    
    return [JobSchema.from_orm(job) for job in jobs]

@router.get("/hidden", response_model=List[JobSchema])
def get_hidden_jobs(
    current_user: User = Depends(get_current_job_seeker),
    db: Session = Depends(get_db)
):
    """Get all hidden jobs for the current user"""
    
    hidden_preferences = db.query(UserJobPreferences).filter(
        UserJobPreferences.user_id == current_user.id,
        UserJobPreferences.is_hidden == True
    ).all()
    
    job_ids = [pref.job_id for pref in hidden_preferences]
    jobs = db.query(Job).filter(Job.id.in_(job_ids)).all()
    
    return [JobSchema.from_orm(job) for job in jobs]

# =============================================================================
# JOB COMPARISON ENDPOINTS
# =============================================================================

@router.post("/compare", response_model=JobComparisonResponse)
def create_job_comparison(
    comparison_data: JobComparisonRequest,
    current_user: User = Depends(get_current_job_seeker),
    db: Session = Depends(get_db)
):
    """Create a new job comparison"""
    
    # Validate that all jobs exist
    jobs = db.query(Job).filter(Job.id.in_(comparison_data.job_ids)).all()
    if len(jobs) != len(comparison_data.job_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="One or more jobs not found"
        )
    
    # Create comparison
    comparison = JobComparison(
        user_id=current_user.id,
        comparison_name=comparison_data.comparison_name
    )
    db.add(comparison)
    db.flush()  # Get the ID
    
    # Add jobs to comparison
    for job_id in comparison_data.job_ids:
        comparison_item = JobComparisonItem(
            comparison_id=comparison.id,
            job_id=job_id
        )
        db.add(comparison_item)
    
    db.commit()
    db.refresh(comparison)
    
    return JobComparisonResponse(
        id=comparison.id,
        user_id=comparison.user_id,
        comparison_name=comparison.comparison_name,
        created_at=comparison.created_at,
        job_count=len(comparison_data.job_ids)
    )

@router.get("/compare", response_model=List[JobComparisonResponse])
def get_user_comparisons(
    current_user: User = Depends(get_current_job_seeker),
    db: Session = Depends(get_db)
):
    """Get all job comparisons for the current user"""
    
    comparisons = db.query(JobComparison).filter(
        JobComparison.user_id == current_user.id
    ).all()
    
    result = []
    for comparison in comparisons:
        job_count = db.query(JobComparisonItem).filter(
            JobComparisonItem.comparison_id == comparison.id
        ).count()
        
        result.append(JobComparisonResponse(
            id=comparison.id,
            user_id=comparison.user_id,
            comparison_name=comparison.comparison_name,
            created_at=comparison.created_at,
            job_count=job_count
        ))
    
    return result

@router.get("/compare/{comparison_id}", response_model=JobComparisonDetailResponse)
def get_comparison_details(
    comparison_id: int,
    current_user: User = Depends(get_current_job_seeker),
    db: Session = Depends(get_db)
):
    """Get detailed comparison with job information"""
    
    # Check if comparison exists and belongs to user
    comparison = db.query(JobComparison).filter(
        JobComparison.id == comparison_id,
        JobComparison.user_id == current_user.id
    ).first()
    
    if not comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comparison not found"
        )
    
    # Get comparison items with job details
    comparison_items = db.query(JobComparisonItem).filter(
        JobComparisonItem.comparison_id == comparison_id
    ).all()
    
    jobs = []
    for item in comparison_items:
        job = db.query(Job).filter(Job.id == item.job_id).first()
        if job:
            jobs.append(JobSchema.from_orm(job).dict())
    
    return JobComparisonDetailResponse(
        id=comparison.id,
        user_id=comparison.user_id,
        comparison_name=comparison.comparison_name,
        created_at=comparison.created_at,
        jobs=jobs
    )

@router.delete("/compare/{comparison_id}")
def delete_comparison(
    comparison_id: int,
    current_user: User = Depends(get_current_job_seeker),
    db: Session = Depends(get_db)
):
    """Delete a job comparison"""
    
    # Check if comparison exists and belongs to user
    comparison = db.query(JobComparison).filter(
        JobComparison.id == comparison_id,
        JobComparison.user_id == current_user.id
    ).first()
    
    if not comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comparison not found"
        )
    
    # Delete comparison items first
    db.query(JobComparisonItem).filter(
        JobComparisonItem.comparison_id == comparison_id
    ).delete()
    
    # Delete comparison
    db.delete(comparison)
    db.commit()
    
    return {"message": "Comparison deleted successfully"}
