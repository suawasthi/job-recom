#!/usr/bin/env python3
"""
CSV Job Import Script
This script imports job data from a CSV file into the database
Half of the jobs will have India city locations
"""

import sys
import os
import csv
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.core.database import SessionLocal, engine, Base
from app.models import user, job, resume  # Import all models to register them
from app.models.job import Job, JobType, JobStatus
from app.models.user import User

# India cities for half of the jobs
INDIA_CITIES = [
    "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai", "Kolkata", 
    "Pune", "Ahmedabad", "Jaipur", "Surat", "Lucknow", "Kanpur", 
    "Nagpur", "Indore", "Thane", "Bhopal", "Visakhapatnam", "Pimpri-Chinchwad",
    "Patna", "Vadodara", "Ghaziabad", "Ludhiana", "Agra", "Nashik",
    "Faridabad", "Meerut", "Rajkot", "Kalyan-Dombivali", "Vasai-Virar",
    "Varanasi", "Srinagar", "Aurangabad", "Navi Mumbai", "Solapur",
    "Vijayawada", "Kolhapur", "Amritsar", "Allahabad", "Ranchi",
    "Howrah", "Coimbatore", "Jabalpur", "Gwalior", "Vijayawada"
]

# Global cities for the other half
GLOBAL_CITIES = [
    "New York", "London", "Tokyo", "Paris", "Sydney", "Toronto", 
    "Berlin", "Amsterdam", "Singapore", "Dubai", "San Francisco", 
    "Los Angeles", "Chicago", "Boston", "Seattle", "Austin", 
    "Vancouver", "Melbourne", "Brisbane", "Perth", "Adelaide",
    "Manchester", "Birmingham", "Leeds", "Liverpool", "Edinburgh",
    "Glasgow", "Cardiff", "Belfast", "Dublin", "Cork", "Galway"
]

def create_sample_user():
    """Create a sample user if none exists"""
    db = SessionLocal()
    try:
        # Check if any user with recruiter role exists
        existing_user = db.query(User).filter(User.role == "RECRUITER").first()
        if existing_user:
            print(f"✅ Found existing recruiter user: {existing_user.email}")
            return existing_user.id
        
        # Create a sample user with recruiter role
        sample_user = User(
            email="admin@example.com",
            username="admin",
            full_name="System Administrator",
            is_active=True,
            is_verified=True,
            user_type="recruiter"
        )
        db.add(sample_user)
        db.commit()
        db.refresh(sample_user)
        print(f"✅ Created sample recruiter user: {sample_user.username}")
        return sample_user.id
        
    except Exception as e:
        print(f"❌ Error creating sample user: {e}")
        db.rollback()
        return None
    finally:
        db.close()

def parse_csv_data(csv_file_path: str) -> List[Dict[str, Any]]:
    """Parse CSV file and return list of job dictionaries"""
    jobs = []
    
    if not os.path.exists(csv_file_path):
        print(f"❌ CSV file not found: {csv_file_path}")
        print("Please ensure the CSV file exists in the current directory.")
        print("Expected schema: job_id,job_title,company,category,location,salary_min,salary_max,experience_required_min,experience_required_max,required_skills,preferred_skills,education_requirement,remote_allowed,job_type,posted_date,application_deadline,urgency")
        return []
    
    try:
        with open(csv_file_path, 'r', encoding='utf-8') as file:
            # Show CSV structure
            first_line = file.readline().strip()
            print(f"📋 CSV header: {first_line}")
            
            # Reset file pointer
            file.seek(0)
            reader = csv.DictReader(file)
            print(f"📊 CSV columns found: {list(reader.fieldnames)}")
            print()
            
            # Validate CSV schema
            if not validate_csv_schema(reader.fieldnames):
                print("❌ CSV schema validation failed. Please check your CSV file format.")
                return []
            
            # Reset file pointer again for data reading
            file.seek(0)
            reader = csv.DictReader(file)
            
            for row in reader:
                # Clean and validate data
                job_data = {
                    'title': row.get('job_title', '').strip(),
                    'company_name': row.get('company', '').strip(),
                    'location': row.get('location', '').strip(),
                    'category': row.get('category', '').strip(),
                    'min_salary': parse_salary(row.get('salary_min', '')),
                    'max_salary': parse_salary(row.get('salary_max', '')),
                    'min_experience_years': parse_experience(row.get('experience_required_min', '')),
                    'max_experience_years': parse_experience(row.get('experience_required_max', '')),
                    'required_skills': parse_skills(row.get('required_skills', '')),
                    'preferred_skills': parse_skills(row.get('preferred_skills', '')),
                    'education_requirements': parse_education(row.get('education_requirement', '')),
                    'remote_work_allowed': parse_remote(row.get('remote_allowed', '')),
                    'job_type': parse_job_type(row.get('job_type', '')),
                    'application_deadline': parse_date(row.get('application_deadline', '')),
                    'urgency': row.get('urgency', 'normal').strip()
                }
                
                # Filter out jobs with empty titles
                if job_data['title']:
                    jobs.append(job_data)
                    
        print(f"✅ Parsed {len(jobs)} jobs from CSV")
        return jobs
        
    except Exception as e:
        print(f"❌ Error parsing CSV: {e}")
        print("Please check the CSV file format and ensure it matches the expected schema.")
        return []

def create_sample_csv():
    """Create a sample CSV file to show the expected format"""
    sample_csv_content = """job_id,job_title,company,category,location,salary_min,salary_max,experience_required_min,experience_required_max,required_skills,preferred_skills,education_requirement,remote_allowed,job_type,posted_date,application_deadline,urgency
1,Senior Software Engineer,TechCorp Solutions,Technology,New York,80000,120000,5,8,"Python,JavaScript,React,Node.js","AWS,Docker,Kubernetes","Bachelor's in Computer Science",Yes,full_time,2024-01-15,2024-02-15,high
2,Data Scientist,Analytics Pro,Data Science,London,90000,130000,3,6,"Python,R,SQL,Machine Learning","TensorFlow,PyTorch,Big Data","Master's in Data Science",Hybrid,full_time,2024-01-16,2024-02-16,normal
3,Product Manager,InnovateTech,Product Management,Bangalore,70000,110000,4,7,"Product Strategy,Agile,User Research","Analytics,Design Thinking,SQL","Bachelor's in Business or Engineering",Yes,full_time,2024-01-17,2024-02-17,high"""
    
    sample_file = "sample_job_recommendation_jobs.csv"
    with open(sample_file, 'w', encoding='utf-8') as f:
        f.write(sample_csv_content)
    
    print(f"✅ Created sample CSV file: {sample_file}")
    print("You can use this as a template for your actual CSV file.")
    return sample_file

def validate_csv_schema(fieldnames):
    """Validate that CSV has the expected columns"""
    expected_columns = [
        'job_id', 'job_title', 'company', 'category', 'location', 
        'salary_min', 'salary_max', 'experience_required_min', 'experience_required_max',
        'required_skills', 'preferred_skills', 'education_requirement', 
        'remote_allowed', 'job_type', 'posted_date', 'application_deadline', 'urgency'
    ]
    
    missing_columns = [col for col in expected_columns if col not in fieldnames]
    extra_columns = [col for col in fieldnames if col not in expected_columns]
    
    if missing_columns:
        print(f"❌ Missing required columns: {missing_columns}")
        return False
    
    if extra_columns:
        print(f"⚠️  Extra columns found (will be ignored): {extra_columns}")
    
    print("✅ CSV schema validation passed!")
    return True

def parse_salary(salary_str: str) -> float:
    """Parse salary string to float"""
    if not salary_str:
        return None
    try:
        # Remove common salary formatting
        cleaned = salary_str.replace('$', '').replace(',', '').replace('k', '000').replace('K', '000')
        return float(cleaned)
    except:
        return None

def parse_experience(exp_str: str) -> float:
    """Parse experience string to float"""
    if not exp_str:
        return None
    try:
        # Remove common experience formatting
        cleaned = exp_str.replace('years', '').replace('yrs', '').replace('+', '').strip()
        return float(cleaned)
    except:
        return None

def parse_skills(skills_str: str) -> List[str]:
    """Parse skills string to list"""
    if not skills_str:
        return []
    # Split by common delimiters
    skills = skills_str.replace(';', ',').replace('|', ',').split(',')
    return [skill.strip() for skill in skills if skill.strip()]

def parse_education(edu_str: str) -> List[str]:
    """Parse education string to list"""
    if not edu_str:
        return []
    # Split by common delimiters
    education = edu_str.replace(';', ',').replace('|', ',').split(',')
    return [edu.strip() for edu in education if edu.strip()]

def parse_remote(remote_str: str) -> str:
    """Parse remote work string"""
    if not remote_str:
        return 'No'
    remote_lower = remote_str.lower().strip()
    if 'yes' in remote_lower or 'true' in remote_lower:
        return 'Yes'
    elif 'hybrid' in remote_lower:
        return 'Hybrid'
    else:
        return 'No'

def parse_job_type(job_type_str: str) -> str:
    """Parse job type string"""
    if not job_type_str:
        return 'full_time'
    job_type_lower = job_type_str.lower().strip()
    if 'part' in job_type_lower:
        return 'part_time'
    elif 'contract' in job_type_lower:
        return 'contract'
    elif 'freelance' in job_type_lower:
        return 'freelance'
    else:
        return 'full_time'

def parse_date(date_str: str) -> datetime:
    """Parse date string to datetime"""
    if not date_str:
        # Default to 30 days from now
        return datetime.now() + timedelta(days=30)
    
    # Try common date formats
    date_formats = [
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d/%m/%Y',
        '%Y-%m-%d %H:%M:%S',
        '%m/%d/%Y %H:%M:%S'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except:
            continue
    
    # If all formats fail, return default
    return datetime.now() + timedelta(days=30)

def assign_locations(jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Assign India cities to half of the jobs"""
    total_jobs = len(jobs)
    india_jobs_count = total_jobs // 2
    
    # Shuffle jobs to randomize location assignment
    random.shuffle(jobs)
    
    for i, job in enumerate(jobs):
        if i < india_jobs_count:
            # Assign India city
            job['location'] = random.choice(INDIA_CITIES)
            job['currency'] = 'INR'
            # Adjust salary for India market (rough conversion)
            if job.get('min_salary'):
                job['min_salary'] = int(job['min_salary'] * 0.012)  # Rough USD to INR conversion
            if job.get('max_salary'):
                job['max_salary'] = int(job['max_salary'] * 0.012)
        else:
            # Assign global city
            job['location'] = random.choice(GLOBAL_CITIES)
            job['currency'] = 'USD'
    
    print(f"✅ Assigned India cities to {india_jobs_count} jobs")
    print(f"✅ Assigned global cities to {total_jobs - india_jobs_count} jobs")
    return jobs

def import_jobs_to_database(jobs: List[Dict[str, Any]], recruiter_id: int):
    """Import jobs to database"""
    db = SessionLocal()
    imported_count = 0
    
    try:
        for job_data in jobs:
            # Create job object
            job = Job(
                recruiter_id=recruiter_id,
                title=job_data['title'],
                description=f"Job description for {job_data['title']} position at {job_data['company_name']}",
                company_name=job_data['company_name'],
                location=job_data['location'],
                job_type=job_data['job_type'],
                status=JobStatus.ACTIVE,
                required_skills=job_data['required_skills'],
                preferred_skills=job_data['preferred_skills'],
                min_experience_years=job_data['min_experience_years'],
                max_experience_years=job_data['max_experience_years'],
                education_requirements=job_data['education_requirements'],
                min_salary=job_data['min_salary'],
                max_salary=job_data['max_salary'],
                currency=job_data.get('currency', 'USD'),
                remote_work_allowed=job_data['remote_work_allowed'],
                application_deadline=job_data['application_deadline'],
                benefits=["Health Insurance", "Paid Time Off", "Professional Development"]
            )
            
            db.add(job)
            imported_count += 1
        
        db.commit()
        print(f"✅ Successfully imported {imported_count} jobs to database")
        return True
        
    except Exception as e:
        print(f"❌ Error importing jobs: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Main function to run the import process"""
    print("=" * 60)
    print("🚀 CSV Job Import Script")
    print("=" * 60)
    print("This script will:")
    print("2. Assign India city locations to half of the jobs")
    print("3. Assign global city locations to the other half")
    print("4. Import all jobs into the database")
    print("=" * 60)
    
    # CSV file path
    csv_file_path = "C:\\Users\\ADMIN\\Downloads\\job_recommendation_jobs.csv"
    
    # Check if CSV file exists
    if not os.path.exists(csv_file_path):
        print(f"❌ CSV file '{csv_file_path}' not found!")
        print(f"Current working directory: {os.getcwd()}")
        print("Please check the file path and ensure the CSV file exists.")
        print("Expected schema: job_id,job_title,company,category,location,salary_min,salary_max,experience_required_min,experience_required_max,required_skills,preferred_skills,education_requirement,remote_allowed,job_type,posted_date,application_deadline,urgency")
        
        # Offer to create a sample CSV
        print("\n💡 Would you like me to create a sample CSV file to show the expected format?")
        print("This will help you understand the required structure.")
        create_sample_csv()
        return
    
    # Create sample user if none exists
    recruiter_id = create_sample_user()
    if not recruiter_id:
        print("❌ Failed to create sample user. Exiting.")
        return
    
    # Parse CSV data
    print("\n📋 Parsing job data...")
    jobs = parse_csv_data(csv_file_path)
    
    if not jobs:
        print("❌ No jobs to import from CSV. Please ensure the CSV file exists and has valid data.")
        print(f"Expected CSV file: {csv_file_path}")
        print("Expected schema: job_id,job_title,company,category,location,salary_min,salary_max,experience_required_min,experience_required_max,required_skills,preferred_skills,education_requirement,remote_allowed,job_type,posted_date,application_deadline,urgency")
        return
    
    # Assign locations (half India, half global)
    print("\n🌍 Assigning locations...")
    jobs = assign_locations(jobs)
    
    # Import to database
    print("\n💾 Importing jobs to database...")
    success = import_jobs_to_database(jobs, recruiter_id)
    
    if success:
        print("\n🎉 Job import completed successfully!")
        print(f"📊 Total jobs imported: {len(jobs)}")
        print(f"🇮🇳 India location jobs: {len(jobs) // 2}")
        print(f"🌐 Global location jobs: {len(jobs) - len(jobs) // 2}")
    else:
        print("\n💥 Job import failed!")
        return
    
    # Display sample of imported jobs
    print("\n📋 Sample of imported jobs:")
    print("-" * 80)
    for i, job in enumerate(jobs[:5]):  # Show first 5 jobs
        print(f"{i+1}. {job['title']} at {job['company_name']}")
        print(f"   Location: {job['location']} | Salary: {job.get('currency', 'USD')} {job.get('min_salary', 'N/A')}-{job.get('max_salary', 'N/A')}")
        print(f"   Experience: {job.get('min_experience_years', 'N/A')}-{job.get('max_experience_years', 'N/A')} years")
        print(f"   Remote: {job['remote_work_allowed']} | Type: {job['job_type']}")
        print()

if __name__ == "__main__":
    main()
