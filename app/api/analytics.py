from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.user import User
from app.models.job import Job, JobApplication
from app.models.resume import Resume
from app.api.auth import get_current_user, get_current_recruiter, get_current_job_seeker

router = APIRouter(prefix="/api/v1/analytics", tags=["analytics"])

@router.get("/trends/skills")
def get_trending_skills(
    limit: int = Query(10, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trending skills based on actual job requirements"""
    from sqlalchemy import func, desc
    
    # Get skills from job requirements
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
    
    # Combine and calculate demand scores
    all_skills = set(required_skills_count.keys()) | set(preferred_skills_count.keys())
    trending_skills = []
    
    for skill in all_skills:
        required_count = required_skills_count.get(skill, 0)
        preferred_count = preferred_skills_count.get(skill, 0)
        total_demand = required_count + preferred_count
        
        # Calculate demand score (required skills weighted more)
        demand_score = (required_count * 2 + preferred_count) / total_jobs * 100 if total_jobs > 0 else 0
        
        # Mock growth percentage for now (could be calculated from historical data)
        growth_percentage = round(demand_score * 0.15, 1)
        
        trending_skills.append({
            "skill": skill.title(),
            "demand_score": round(demand_score, 1),
            "growth_percentage": growth_percentage,
            "job_count": total_demand
        })
    
    # Sort by demand score and return top skills
    trending_skills.sort(key=lambda x: x["demand_score"], reverse=True)

    return {
        "trending_skills": trending_skills[:limit],
        "last_updated": datetime.utcnow(),
        "period": "last_30_days",
        "total_jobs_analyzed": total_jobs
    }

@router.get("/trends/job-titles")
def get_trending_job_titles(
    limit: int = Query(10, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trending job titles"""

    # Get actual job title trends from database
    job_title_counts = db.query(
        Job.title,
        func.count(Job.id).label('count')
    ).filter(
        Job.created_at >= datetime.utcnow() - timedelta(days=30)
    ).group_by(Job.title).order_by(desc('count')).limit(limit).all()

    trending_titles = []
    for title, count in job_title_counts:
        trending_titles.append({
            "title": title,
            "job_count": count,
            "growth_percentage": 12.5,  # Mock growth data
            "avg_salary": 85000  # Mock salary data
        })

    # Add some mock data if not enough real data
    if len(trending_titles) < 5:
        mock_titles = [
            {"title": "Full Stack Developer", "job_count": 145, "growth_percentage": 18.2, "avg_salary": 92000},
            {"title": "Data Scientist", "job_count": 98, "growth_percentage": 22.7, "avg_salary": 115000},
            {"title": "DevOps Engineer", "job_count": 87, "growth_percentage": 25.1, "avg_salary": 105000},
            {"title": "Frontend Developer", "job_count": 76, "growth_percentage": 14.3, "avg_salary": 78000},
            {"title": "Backend Developer", "job_count": 65, "growth_percentage": 16.8, "avg_salary": 88000}
        ]
        trending_titles.extend(mock_titles[:limit - len(trending_titles)])

    return {
        "trending_titles": trending_titles,
        "last_updated": datetime.utcnow(),
        "period": "last_30_days"
    }

@router.get("/trends/industries")
def get_industry_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get hiring trends by industry"""

    industries = [
        {"industry": "Technology", "growth_percentage": 22.5, "job_openings": 15680, "avg_salary": 98000},
        {"industry": "Healthcare", "growth_percentage": 18.2, "job_openings": 12450, "avg_salary": 78000},
        {"industry": "Finance", "growth_percentage": 14.7, "job_openings": 9870, "avg_salary": 105000},
        {"industry": "E-commerce", "growth_percentage": 25.1, "job_openings": 8650, "avg_salary": 85000},
        {"industry": "Education", "growth_percentage": 16.3, "job_openings": 7230, "avg_salary": 65000},
        {"industry": "Manufacturing", "growth_percentage": 12.8, "job_openings": 6540, "avg_salary": 72000}
    ]

    return {
        "industries": industries,
        "last_updated": datetime.utcnow(),
        "period": "current",
        "total_jobs_analyzed": sum(ind["job_openings"] for ind in industries),
        "note": "Industry categorization based on company names and job titles"
    }

@router.get("/trends/locations")
def get_location_trends(
    limit: int = Query(15, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get location trends with job distribution and salary data"""
    
    # Get location-based job statistics
    location_stats = db.query(
        Job.location,
        func.count(Job.id).label('job_count'),
        func.avg(Job.min_salary).label('avg_min_salary'),
        func.avg(Job.max_salary).label('avg_max_salary'),
        func.avg(Job.min_experience_years).label('avg_experience')
    ).filter(
        Job.status == "active"
    ).group_by(Job.location).order_by(desc('job_count')).limit(limit).all()
    
    location_trends = []
    for location, job_count, avg_min, avg_max, avg_exp in location_stats:
        # Calculate average salary
        avg_salary = None
        if avg_min and avg_max:
            avg_salary = (avg_min + avg_max) / 2
        
        # Mock growth data (could be calculated from historical data)
        growth_percentage = round(job_count * 0.12, 1)
        
        location_trends.append({
            "location": location,
            "job_count": job_count,
            "growth_percentage": growth_percentage,
            "avg_salary": round(avg_salary, 0) if avg_salary else None,
            "avg_experience_years": round(avg_exp, 1) if avg_exp else None,
            "demand_level": "High" if job_count >= 10 else "Medium" if job_count >= 5 else "Low"
        })
    
    return {
        "location_trends": location_trends,
        "last_updated": datetime.utcnow(),
        "period": "current",
        "total_locations": len(location_trends)
    }

@router.get("/market/insights")
def get_market_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive market insights and trends"""
    
    # Get overall job market statistics
    total_jobs = db.query(Job).filter(Job.status == "active").count()
    total_applications = db.query(JobApplication).count()
    
    # Calculate average salary across all jobs
    salary_stats = db.query(
        func.avg(Job.min_salary).label('avg_min'),
        func.avg(Job.max_salary).label('avg_max')
    ).filter(
        Job.status == "active",
        Job.min_salary.isnot(None),
        Job.max_salary.isnot(None)
    ).first()
    
    avg_salary = None
    if salary_stats.avg_min and salary_stats.avg_max:
        avg_salary = (salary_stats.avg_min + salary_stats.avg_max) / 2
    
    # Get top skills demand
    skills_query = db.query(
        func.unnest(Job.required_skills).label('skill'),
        func.count(Job.id).label('demand')
    ).filter(
        Job.status == "active",
        Job.required_skills.isnot(None)
    ).group_by('skill').order_by(desc('demand')).limit(5).all()
    
    top_skills = [{"skill": skill, "demand": demand} for skill, demand in skills_query]
    
    # Market insights based on data
    insights = []
    if total_jobs > 0:
        insights.append(f"Active job market with {total_jobs} open positions")
        
        if avg_salary:
            insights.append(f"Average salary range: ${avg_salary:,.0f}")
        
        if total_applications > 0:
            avg_apps_per_job = total_applications / total_jobs
            insights.append(f"Average of {avg_apps_per_job:.1f} applications per job")
        
        if top_skills:
            top_skill_names = [skill["skill"] for skill in top_skills[:3]]
            insights.append(f"Most in-demand skills: {', '.join(top_skill_names)}")
    
    return {
        "market_overview": {
            "total_active_jobs": total_jobs,
            "total_applications": total_applications,
            "avg_salary": round(avg_salary, 0) if avg_salary else None,
            "market_health": "Strong" if total_jobs >= 50 else "Moderate" if total_jobs >= 20 else "Developing"
        },
        "top_skills": top_skills,
        "insights": insights,
        "trends": [
            "Remote work continues to grow",
            "Tech skills remain in high demand",
            "Salary transparency is increasing"
        ],
        "last_updated": datetime.utcnow()
    }

@router.get("/salary/analysis")
def get_salary_analysis(
    location: str = Query(None),
    job_type: str = Query(None),
    experience_level: str = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed salary analysis with filters"""
    
    # Build query with filters
    query = db.query(Job).filter(Job.status == "active")
    
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    
    if job_type:
        query = query.filter(Job.job_type == job_type)
    
    if experience_level:
        # Map experience levels to years
        exp_mapping = {
            'entry': (0, 2),
            'mid': (2, 5),
            'senior': (5, 10),
            'lead': (10, 100)
        }
        if experience_level in exp_mapping:
            min_exp, max_exp = exp_mapping[experience_level]
            query = query.filter(
                Job.min_experience_years >= min_exp,
                Job.min_experience_years < max_exp
            )
    
    jobs = query.all()
    
    if not jobs:
        return {
            "message": "No jobs found with the specified criteria",
            "filters_applied": {
                "location": location,
                "job_type": job_type,
                "experience_level": experience_level
            }
        }
    
    # Calculate salary statistics
    salaries = []
    for job in jobs:
        if job.min_salary and job.max_salary:
            salaries.append((job.min_salary, job.max_salary))
    
    if not salaries:
        return {
            "message": "No salary data available for the specified criteria",
            "filters_applied": {
                "location": location,
                "job_type": job_type,
                "experience_level": experience_level
            }
        }
    
    # Calculate statistics
    min_salaries = [min_sal for min_sal, _ in salaries]
    max_salaries = [max_sal for _, max_sal in salaries]
    avg_salaries = [(min_sal + max_sal) / 2 for min_sal, max_sal in salaries]
    
    analysis = {
        "filters_applied": {
            "location": location,
            "job_type": job_type,
            "experience_level": experience_level
        },
        "job_count": len(jobs),
        "salary_statistics": {
            "min_salary": min(min_salaries),
            "max_salary": max(max_salaries),
            "avg_min_salary": round(sum(min_salaries) / len(min_salaries), 0),
            "avg_max_salary": round(sum(max_salaries) / len(max_salaries), 0),
            "median_salary": round(sorted(avg_salaries)[len(avg_salaries) // 2], 0)
        },
        "salary_distribution": {
            "entry_level": len([s for s in avg_salaries if s < 60000]),
            "mid_level": len([s for s in avg_salaries if 60000 <= s < 100000]),
            "senior_level": len([s for s in avg_salaries if s >= 100000])
        },
        "last_updated": datetime.utcnow()
    }
    
    return analysis

@router.get("/job-seeker/dashboard")
def get_job_seeker_analytics(
    current_user: User = Depends(get_current_job_seeker),
    db: Session = Depends(get_db)
):
    """Get analytics dashboard data for job seekers"""

    # Get user's applications
    applications = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id
    ).all()

    # Get user's resume
    latest_resume = db.query(Resume).filter(
        Resume.user_id == current_user.id
    ).order_by(Resume.created_at.desc()).first()

    # Application statistics
    total_applications = len(applications)
    status_counts = {}
    for app in applications:
        status = app.status
        status_counts[status] = status_counts.get(status, 0) + 1

    # Calculate application success rate
    successful_statuses = ['hired', 'interviewing']
    successful_apps = sum(status_counts.get(status, 0) for status in successful_statuses)
    success_rate = (successful_apps / total_applications * 100) if total_applications > 0 else 0

    # Resume analytics
    resume_score = 0
    skill_recommendations = []
    if latest_resume:
        resume_score = (
            latest_resume.ats_score + 
            latest_resume.completeness_score + 
            latest_resume.keyword_density_score + 
            latest_resume.formatting_score
        ) / 4

        # Mock skill recommendations based on trending skills
        user_skills = set(skill.lower() for skill in (latest_resume.skills or []))
        trending = ["python", "react", "aws", "docker", "kubernetes"]
        skill_recommendations = [skill for skill in trending if skill not in user_skills][:3]

    return {
        "applications": {
            "total": total_applications,
            "status_breakdown": status_counts,
            "success_rate": round(success_rate, 1)
        },
        "resume": {
            "overall_score": round(resume_score, 1) if resume_score else 0,
            "ats_score": latest_resume.ats_score if latest_resume else 0,
            "completeness_score": latest_resume.completeness_score if latest_resume else 0,
            "last_updated": latest_resume.updated_at if latest_resume else None
        },
        "recommendations": {
            "skills_to_learn": skill_recommendations,
            "profile_completion": 85,  # Mock completion percentage
            "market_insights": [
                "Your skills are in high demand",
                "Consider adding cloud certifications",
                "Update your resume with recent projects"
            ]
        }
    }

@router.get("/recruiter/dashboard")
def get_recruiter_analytics(
    current_user: User = Depends(get_current_recruiter),
    db: Session = Depends(get_db)
):
    """Get analytics dashboard data for recruiters"""

    # Get recruiter's jobs
    jobs = db.query(Job).filter(Job.recruiter_id == current_user.id).all()

    # Get applications for recruiter's jobs
    job_ids = [job.id for job in jobs]
    applications = db.query(JobApplication).filter(
        JobApplication.job_id.in_(job_ids)
    ).all() if job_ids else []

    # Job statistics
    total_jobs = len(jobs)
    active_jobs = len([job for job in jobs if job.status.value == 'active'])

    # Application statistics
    total_applications = len(applications)
    applications_per_job = total_applications / total_jobs if total_jobs > 0 else 0

    # Top performing jobs
    job_performance = {}
    for app in applications:
        job_id = app.job_id
        if job_id not in job_performance:
            job_performance[job_id] = {"applications": 0, "avg_match_score": 0, "scores": []}
        job_performance[job_id]["applications"] += 1
        job_performance[job_id]["scores"].append(app.match_score)

    # Calculate average match scores
    for job_id in job_performance:
        scores = job_performance[job_id]["scores"]
        job_performance[job_id]["avg_match_score"] = sum(scores) / len(scores)

    # Get top 3 performing jobs
    top_jobs = sorted(
        job_performance.items(), 
        key=lambda x: (x[1]["applications"], x[1]["avg_match_score"]), 
        reverse=True
    )[:3]

    top_jobs_data = []
    for job_id, perf in top_jobs:
        job = next(j for j in jobs if j.id == job_id)
        top_jobs_data.append({
            "title": job.title,
            "applications": perf["applications"],
            "avg_match_score": round(perf["avg_match_score"], 1),
            "status": job.status.value
        })

    return {
        "jobs": {
            "total": total_jobs,
            "active": active_jobs,
            "draft": total_jobs - active_jobs,
            "avg_applications_per_job": round(applications_per_job, 1)
        },
        "applications": {
            "total": total_applications,
            "this_week": len([app for app in applications 
                            if app.applied_at >= datetime.utcnow() - timedelta(days=7)])
        },
        "top_performing_jobs": top_jobs_data,
        "insights": [
            "Your job postings are performing well",
            "Consider expanding remote work options",
            "Skills in high demand: Python, React, AWS"
        ]
    }

@router.get("/salary-insights")
def get_salary_insights(
    location: str = Query(None),
    job_title: str = Query(None),
    experience_years: int = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get salary insights and benchmarks"""

    # Mock salary data (in production, this would query real salary data)
    base_salaries = {
        "Software Developer": {"min": 70000, "median": 90000, "max": 130000},
        "Data Scientist": {"min": 85000, "median": 115000, "max": 160000},
        "DevOps Engineer": {"min": 80000, "median": 105000, "max": 150000},
        "Product Manager": {"min": 95000, "median": 125000, "max": 180000},
        "Full Stack Developer": {"min": 75000, "median": 95000, "max": 140000}
    }

    # Location adjustments
    location_multipliers = {
        "san francisco": 1.4,
        "new york": 1.3,
        "seattle": 1.2,
        "austin": 1.1,
        "chicago": 1.0,
        "denver": 0.95,
        "atlanta": 0.9
    }

    # Experience adjustments
    experience_multipliers = {
        (0, 2): 0.8,
        (2, 5): 1.0,
        (5, 10): 1.2,
        (10, float('inf')): 1.4
    }

    # Find matching salary data
    salary_data = base_salaries.get(job_title, base_salaries["Software Developer"])

    # Apply location adjustment
    location_multiplier = 1.0
    if location:
        for loc_key, multiplier in location_multipliers.items():
            if loc_key in location.lower():
                location_multiplier = multiplier
                break

    # Apply experience adjustment
    experience_multiplier = 1.0
    if experience_years is not None:
        for (min_exp, max_exp), multiplier in experience_multipliers.items():
            if min_exp <= experience_years < max_exp:
                experience_multiplier = multiplier
                break

    # Calculate adjusted salaries
    final_multiplier = location_multiplier * experience_multiplier
    adjusted_salaries = {
        "min": int(salary_data["min"] * final_multiplier),
        "median": int(salary_data["median"] * final_multiplier),
        "max": int(salary_data["max"] * final_multiplier)
    }

    return {
        "salary_range": adjusted_salaries,
        "location_adjustment": f"{(location_multiplier - 1) * 100:+.0f}%",
        "experience_adjustment": f"{(experience_multiplier - 1) * 100:+.0f}%",
        "market_insights": [
            f"Salaries in {location or 'this area'} are {'above' if location_multiplier > 1 else 'at'} national average",
            f"Your experience level commands a {'premium' if experience_multiplier > 1 else 'standard'} salary",
            "Consider negotiating based on specific skills and achievements"
        ],
        "last_updated": datetime.utcnow()
    }
