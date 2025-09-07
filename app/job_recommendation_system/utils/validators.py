"""
Data validation utilities
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def validate_candidate_data(candidate_data: Dict[str, Any]) -> bool:
    """
    Validate candidate data structure
    
    Args:
        candidate_data: Candidate data dictionary
        
    Returns:
        True if valid, raises ValueError if invalid
    """
    required_fields = ['id', 'name', 'email']
    
    for field in required_fields:
        if field not in candidate_data:
            raise ValueError(f"Missing required field: {field}")
        
        if not candidate_data[field]:
            raise ValueError(f"Required field cannot be empty: {field}")
    
    # Validate email format
    email = candidate_data.get('email', '')
    if '@' not in email:
        raise ValueError("Invalid email format")
    
    # Validate skills
    skills = candidate_data.get('skills', [])
    if not isinstance(skills, list):
        raise ValueError("Skills must be a list")
    
    # Validate experience
    experience = candidate_data.get('experience_years', 0)
    if not isinstance(experience, (int, float)) or experience < 0:
        raise ValueError("Experience years must be a non-negative number")
    
    # Validate salary expectation
    salary = candidate_data.get('salary_expectation', 0)
    if not isinstance(salary, (int, float)) or salary < 0:
        raise ValueError("Salary expectation must be a non-negative number")
    
    # Validate remote preference
    remote_pref = candidate_data.get('remote_preference', 0.5)
    if not isinstance(remote_pref, (int, float)) or not 0 <= remote_pref <= 1:
        raise ValueError("Remote preference must be between 0 and 1")
    
    return True


def validate_job_data(job_data: Dict[str, Any]) -> bool:
    """
    Validate job data structure
    
    Args:
        job_data: Job data dictionary
        
    Returns:
        True if valid, raises ValueError if invalid
    """
    required_fields = ['id', 'job_title', 'company']
    
    for field in required_fields:
        if field not in job_data:
            raise ValueError(f"Missing required field: {field}")
        
        if not job_data[field]:
            raise ValueError(f"Required field cannot be empty: {field}")
    
    # Validate skills
    required_skills = job_data.get('required_skills', [])
    if not isinstance(required_skills, list):
        raise ValueError("Required skills must be a list")
    
    preferred_skills = job_data.get('preferred_skills', [])
    if not isinstance(preferred_skills, list):
        raise ValueError("Preferred skills must be a list")
    
    # Validate experience requirements
    min_exp = job_data.get('min_experience_years', 0)
    max_exp = job_data.get('max_experience_years', 10)
    
    if not isinstance(min_exp, int) or min_exp < 0:
        raise ValueError("Min experience years must be a non-negative integer")
    
    if not isinstance(max_exp, int) or max_exp < 0:
        raise ValueError("Max experience years must be a non-negative integer")
    
    if min_exp > max_exp:
        raise ValueError("Min experience cannot be greater than max experience")
    
    # Validate salary
    min_salary = job_data.get('min_salary', 0)
    max_salary = job_data.get('max_salary', 0)
    
    if not isinstance(min_salary, (int, float)) or min_salary < 0:
        raise ValueError("Min salary must be a non-negative number")
    
    if not isinstance(max_salary, (int, float)) or max_salary < 0:
        raise ValueError("Max salary must be a non-negative number")
    
    if min_salary > max_salary:
        raise ValueError("Min salary cannot be greater than max salary")
    
    # Validate remote work policy
    remote_policy = job_data.get('remote_work_allowed', 'no')
    valid_policies = ['no', 'hybrid', 'yes', 'remote', 'fully remote']
    if remote_policy.lower() not in valid_policies:
        raise ValueError(f"Remote work policy must be one of: {valid_policies}")
    
    # Validate status
    status = job_data.get('status', 'active')
    valid_statuses = ['active', 'closed', 'draft', 'expired']
    if status.lower() not in valid_statuses:
        raise ValueError(f"Status must be one of: {valid_statuses}")
    
    return True


def validate_match_data(match_data: Dict[str, Any]) -> bool:
    """
    Validate job match data structure
    
    Args:
        match_data: Match data dictionary
        
    Returns:
        True if valid, raises ValueError if invalid
    """
    required_fields = ['job_id', 'candidate_id', 'match_score']
    
    for field in required_fields:
        if field not in match_data:
            raise ValueError(f"Missing required field: {field}")
    
    # Validate match score
    match_score = match_data.get('match_score', 0)
    if not isinstance(match_score, (int, float)) or not 0 <= match_score <= 1:
        raise ValueError("Match score must be between 0 and 1")
    
    # Validate confidence score
    confidence_score = match_data.get('confidence_score', 0)
    if not isinstance(confidence_score, (int, float)) or not 0 <= confidence_score <= 1:
        raise ValueError("Confidence score must be between 0 and 1")
    
    return True


def sanitize_input_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize input data to prevent injection attacks
    
    Args:
        data: Input data dictionary
        
    Returns:
        Sanitized data dictionary
    """
    sanitized = {}
    
    for key, value in data.items():
        if isinstance(value, str):
            # Remove potentially dangerous characters
            sanitized_value = value.strip()
            sanitized_value = sanitized_value.replace('<', '&lt;').replace('>', '&gt;')
            sanitized[key] = sanitized_value
        elif isinstance(value, list):
            # Sanitize list items
            sanitized[key] = [str(item).strip() for item in value if item]
        else:
            sanitized[key] = value
    
    return sanitized


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration data
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if valid, raises ValueError if invalid
    """
    # Validate weights
    weight_fields = [
        'skill_weight', 'experience_weight', 'location_weight',
        'career_growth_weight', 'salary_weight', 'market_demand_weight'
    ]
    
    total_weight = 0
    for field in weight_fields:
        weight = config.get(field, 0)
        if not isinstance(weight, (int, float)) or weight < 0:
            raise ValueError(f"Invalid weight for {field}: {weight}")
        total_weight += weight
    
    # Weights should sum to approximately 1.0
    if abs(total_weight - 1.0) > 0.1:
        raise ValueError(f"Weights should sum to 1.0, got: {total_weight}")
    
    # Validate thresholds
    thresholds = ['min_match_score', 'min_confidence_score']
    for threshold in thresholds:
        value = config.get(threshold, 0)
        if not isinstance(value, (int, float)) or not 0 <= value <= 1:
            raise ValueError(f"Invalid threshold for {threshold}: {value}")
    
    # Validate max results
    max_results = config.get('max_results', 20)
    if not isinstance(max_results, int) or max_results <= 0:
        raise ValueError(f"Invalid max_results: {max_results}")
    
    return True
