import re
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, validator, EmailStr

class EmailValidator:
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

class PhoneValidator:
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Validate phone number format"""
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)

        # Check if it's a valid US phone number (10 or 11 digits)
        return len(digits) in [10, 11]

    @staticmethod
    def format_phone(phone: str) -> str:
        """Format phone number to standard format"""
        digits = re.sub(r'\D', '', phone)

        if len(digits) == 10:
            return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == '1':
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            return phone  # Return as-is if can't format

class PasswordValidator:
    @staticmethod
    def is_strong_password(password: str) -> tuple[bool, List[str]]:
        """
        Validate password strength

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        if len(password) < 8:
            issues.append("Password must be at least 8 characters long")

        if not re.search(r'[A-Z]', password):
            issues.append("Password must contain at least one uppercase letter")

        if not re.search(r'[a-z]', password):
            issues.append("Password must contain at least one lowercase letter")

        if not re.search(r'\d', password):
            issues.append("Password must contain at least one digit")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            issues.append("Password must contain at least one special character")

        return len(issues) == 0, issues

class SkillsValidator:
    COMMON_SKILLS = {
        'programming': [
            'Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust',
            'Ruby', 'PHP', 'Swift', 'Kotlin', 'Scala', 'R', 'MATLAB'
        ],
        'web': [
            'HTML', 'CSS', 'React', 'Angular', 'Vue.js', 'Node.js', 'Express.js',
            'Django', 'Flask', 'FastAPI', 'Spring', 'Laravel', 'Ruby on Rails'
        ],
        'databases': [
            'SQL', 'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
            'SQLite', 'Oracle', 'SQL Server', 'Cassandra'
        ],
        'cloud': [
            'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Terraform',
            'Jenkins', 'GitLab CI', 'GitHub Actions'
        ],
        'ml_ai': [
            'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch',
            'Scikit-learn', 'Pandas', 'NumPy', 'OpenCV', 'NLP'
        ]
    }

    @classmethod
    def get_all_common_skills(cls) -> List[str]:
        """Get all common skills as a flat list"""
        all_skills = []
        for category in cls.COMMON_SKILLS.values():
            all_skills.extend(category)
        return all_skills

    @classmethod
    def validate_skills(cls, skills: List[str]) -> Dict[str, Any]:
        """Validate and categorize skills"""
        if not skills:
            return {'valid': True, 'recognized_skills': [], 'unknown_skills': []}

        common_skills = [skill.lower() for skill in cls.get_all_common_skills()]
        recognized = []
        unknown = []

        for skill in skills:
            if skill.lower() in common_skills:
                recognized.append(skill)
            else:
                unknown.append(skill)

        return {
            'valid': True,
            'recognized_skills': recognized,
            'unknown_skills': unknown,
            'total_count': len(skills),
            'recognized_count': len(recognized)
        }

class ExperienceValidator:
    @staticmethod
    def validate_experience_years(years: float) -> tuple[bool, str]:
        """Validate years of experience"""
        if years is None:
            return True, ""

        if years < 0:
            return False, "Experience years cannot be negative"

        if years > 50:
            return False, "Experience years seems too high (>50 years)"

        return True, ""

class ResumeDataValidator:
    @staticmethod
    def validate_parsed_resume_data(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive validation of parsed resume data

        Returns:
            Dictionary with validation results and suggestions
        """
        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'suggestions': []
        }

        # Validate email
        email = data.get('parsed_email')
        if email and not EmailValidator.is_valid_email(email):
            validation_result['errors'].append(f"Invalid email format: {email}")
            validation_result['is_valid'] = False

        # Validate phone
        phone = data.get('parsed_phone')
        if phone and not PhoneValidator.is_valid_phone(phone):
            validation_result['warnings'].append(f"Phone number format may be incorrect: {phone}")

        # Validate skills
        skills = data.get('skills', [])
        skills_validation = SkillsValidator.validate_skills(skills)
        if skills_validation['unknown_skills']:
            validation_result['suggestions'].append(
                f"Some skills may not be recognized: {', '.join(skills_validation['unknown_skills'][:3])}"
            )

        # Validate experience
        exp_years = data.get('experience_years')
        exp_valid, exp_error = ExperienceValidator.validate_experience_years(exp_years)
        if not exp_valid:
            validation_result['errors'].append(exp_error)
            validation_result['is_valid'] = False

        # Check for critical missing fields
        critical_fields = ['parsed_name', 'parsed_email', 'skills']
        for field in critical_fields:
            if not data.get(field):
                validation_result['warnings'].append(f"Missing critical field: {field}")

        return validation_result
