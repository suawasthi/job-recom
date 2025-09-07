try:
    import spacy as _spacy
except Exception:
    _spacy = None
import re
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Set up logging
logger = logging.getLogger(__name__)

@dataclass
class ExtractedInfo:
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = None
    experience_years: Optional[float] = None
    education: List[Dict[str, Any]] = None
    work_experience: List[Dict[str, Any]] = None
    projects: List[Dict[str, Any]] = None

class NLPService:
    def __init__(self):
        # Load spaCy model (requires: python -m spacy download en_core_web_sm)
        if _spacy is not None:
            try:
                self.nlp = _spacy.load("en_core_web_sm")
            except OSError:
                print("Warning: spaCy model not found. Run: python -m spacy download en_core_web_sm")
                self.nlp = None
        else:
            self.nlp = None

        # Skill keywords database - More specific and accurate categories
        
        self.technical_skills = {
            'python': [
                'flask', 'fastapi', 'django', 'pandas', 'numpy',
                'scikit-learn', 'matplotlib', 'tensorflow', 'pytorch'
            ],
            'javascript': [
                'react', 'vue', 'nodejs', 'express', 'jquery',
                'next.js', 'nuxt.js', 'angular', 'svelte'
            ],
            'typescript': [
                'angular', 'nestjs', 'react', 'next.js'
            ],
            'java': [
                'spring', 'spring boot', 'hibernate', 'maven',
                'gradle', 'jakarta ee'
            ],
            'c#': [
                'asp.net', 'dotnet', 'entity framework', 'xamarin'
            ],
            'c++': [
                'qt', 'boost', 'opengl', 'ue4'
            ],
            'c': [
                'embedded systems', 'linux kernel', 'microcontrollers'
            ],
            'go': [
                'gin', 'echo', 'fiber', 'go-kit'
            ],
            'php': [
                'laravel', 'symfony', 'wordpress', 'drupal'
            ],
            'ruby': [
                'rails', 'sinatra'
            ],
            'kotlin': [
                'android', 'spring boot', 'ktor'
            ],
            'scala': [
                'akka', 'play', 'spark'
            ],
            'swift': [
                'ios', 'xcode', 'swiftui'
            ],
            'dart': [
                'flutter'
            ],
            'r': [
                'ggplot2', 'dplyr', 'shiny'
            ],
            'perl': [
                'moose', 'catalyst', 'dbi'
            ],
            'lua': [
                'love2d', 'openresty'
            ],
            'haskell': [
                'stack', 'yesod'
            ],
            'elixir': [
                'phoenix', 'nerves'
            ],
            'clojure': [
                'leiningen', 'ring', 're-frame'
            ],
            'objective-c': [
                'ios', 'xcode', 'cocoa'
            ],
            'bash': [
                'shell scripting', 'linux'
            ],
            'shell': [
                'shell scripting', 'linux'
            ],
            'powershell': [
                'windows server', 'active directory'
            ],
            'matlab': [
                'simulink'
            ],
            'assembly': [
                'x86', 'arm', 'embedded'
            ],
            'fortran': [
                'numerical computing'
            ],
            'groovy': ['gradle', 'jenkins'],
            'f#': [
                '.net', 'functional programming'
            ],  
            'web_frontend': ['html', 'css', 'react', 'angular', 'vue', 'svelte', 'jquery', 'bootstrap', 'tailwind', 'sass', 'less'],
            'web_backend': ['nodejs', 'express', 'django', 'flask', 'fastapi', 'spring boot', 'spring', 'laravel', 'rails', 'asp.net'],
            'databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'sqlite', 'oracle', 'cassandra', 'dynamodb'],
            'aws_services': ['aws', 'lambda', 'ec2', 's3', 'rds', 'dynamodb', 'cloudformation', 'cloudwatch', 'iam', 'vpc', 'route53', 'sns', 'sqs', 'api gateway', 'elastic beanstalk', 'ecs', 'eks', 'fargate'],
            'cloud_platforms': ['azure', 'gcp', 'google cloud', 'ibm cloud', 'oracle cloud'],
            'containerization': ['docker', 'kubernetes', 'containers', 'podman', 'rancher', 'helm'],
            'devops_deployment': ['terraform', 'ansible', 'jenkins', 'gitlab ci', 'github actions', 'azure devops', 'circleci', 'travis ci', 'deployment', 'ci/cd', 'pipeline'],
            'ml_ai': ['machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'keras', 'opencv', 'nlp', 'computer vision'],
            'development_tools': ['git', 'jira', 'confluence', 'postman', 'swagger', 'figma', 'photoshop', 'vscode', 'intellij', 'eclipse', 'vim', 'emacs'],
            'testing': ['jest', 'mocha', 'junit', 'pytest', 'selenium', 'cypress', 'testng', 'rspec', 'testing', 'qa', 'automation']
}

    def extract_contact_info(self, text: str) -> Dict[str, Optional[str]]:
        """Extract name, email, and phone from resume text"""
        # Email extraction
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        email = emails[0] if emails else None

        # Phone extraction
        phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        phones = re.findall(phone_pattern, text)
        phone = ''.join(phones[0]) if phones else None

        # Name extraction using spaCy
        name = None
        if self.nlp:
            doc = self.nlp(text[:500])  # Process first 500 chars
            persons = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
            if persons:
                name = persons[0]

        # Fallback name extraction from first line
        if not name:
            lines = text.strip().split('\n')
            first_line = lines[0].strip()
            if len(first_line.split()) <= 4 and not any(char.isdigit() for char in first_line):
                name = first_line

        return {"name": name, "email": email, "phone": phone}

    def extract_skills(self, text: str) -> List[str]:
        """Extract technical skills from resume text with improved filtering"""
        logger.info(f"Extracting skills from text: {text[:200]}...")
        text_lower = text.lower()
        found_skills = set()

        # Split text into sections to avoid extracting skills from job descriptions
        sections = self._split_resume_sections(text_lower)
        
        # Only extract skills from relevant sections (skip job descriptions, work experience details)
        relevant_sections = []
        for section in sections:
            if not self._is_job_description_section(section):
                relevant_sections.append(section)
        
        logger.info(f"Found {len(relevant_sections)} relevant sections out of {len(sections)} total sections")
        
        # Search for skills in relevant sections only
        for section in relevant_sections:
            for category, skills in self.technical_skills.items():
                for skill in skills:
                    if skill.lower() in section:
                        logger.info(f"Found skill '{skill}' in relevant section")
                        found_skills.add(skill.title())

        logger.info(f"Extracted skills: {list(found_skills)}")
        return list(found_skills)
    
    def _split_resume_sections(self, text: str) -> List[str]:
        """Split resume text into logical sections"""
        # Common section headers
        section_headers = [
            'skills', 'technical skills', 'technologies', 'programming languages',
            'experience', 'work experience', 'employment', 'professional experience',
            'education', 'projects', 'summary', 'objective', 'profile'
        ]
        
        sections = []
        lines = text.split('\n')
        current_section = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this line is a section header
            is_header = any(header in line for header in section_headers)
            
            if is_header and current_section:
                sections.append(' '.join(current_section))
                current_section = [line]
            else:
                current_section.append(line)
        
        # Add the last section
        if current_section:
            sections.append(' '.join(current_section))
            
        return sections
    
    def _is_job_description_section(self, section: str) -> bool:
        """Check if a section contains job descriptions rather than personal skills"""
        job_description_indicators = [
            'responsibilities', 'duties', 'requirements', 'qualifications',
            'looking for', 'seeking', 'candidate should', 'must have',
            'job description', 'role description', 'position requires',
            'about the role', 'key responsibilities', 'what you will do'
        ]
        
        return any(indicator in section for indicator in job_description_indicators)

    def extract_experience_years(self, text: str) -> Optional[float]:
        """Extract years of experience from resume text"""
        # Patterns for experience
        patterns = [
            r'(\d+)\+?\s+years?\s+of\s+experience',
            r'(\d+)\+?\s+years?\s+experience',
            r'experience\s*:?\s*(\d+)\+?\s+years?',
            r'(\d+)\+?\s*yr?s?\s+exp',
        ]

        text_lower = text.lower()
        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                return float(matches[0])

        return None

    def extract_education(self, text: str) -> List[Dict[str, Any]]:
        """Extract education information from resume text"""
        education_list = []

        # Common degree patterns
        degree_patterns = [
            r'(bachelor|master|phd|doctorate|associate)\s+(of\s+)?(\w+\s*){1,3}',
            r'(b\.?s\.?|m\.?s\.?|ph\.?d\.?|m\.?b\.?a\.?)\s*(?:in\s+)?(\w+\s*){1,3}',
        ]

        # University patterns
        university_patterns = [
            r'(university\s+of\s+\w+|\w+\s+university)',
            r'(\w+\s+college|college\s+of\s+\w+)',
            r'(\w+\s+institute|institute\s+of\s+\w+)',
        ]

        text_lower = text.lower()

        for pattern in degree_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                degree = ' '.join([part for part in match if part.strip()])
                education_list.append({"degree": degree.title(), "institution": "", "year": ""})

        return education_list[:3]  # Return top 3 matches

    def extract_work_experience(self, text: str) -> List[Dict[str, Any]]:
        """Extract work experience from resume text"""
        experience_list = []

        # Look for date patterns (years)
        date_pattern = r'(20\d{2}|19\d{2})\s*[-–]\s*(20\d{2}|19\d{2}|present|current)'
        date_matches = re.findall(date_pattern, text.lower())

        # Look for job title patterns
        title_patterns = [
            r'(?:^|\n)([A-Z][^\n]{10,60})(?=\n|$)',  # Capitalized lines
        ]

        if date_matches:
            for i, (start_year, end_year) in enumerate(date_matches[:3]):
                experience_list.append({
                    "company": f"Company {i+1}",
                    "role": f"Position {i+1}",
                    "duration": f"{start_year} - {end_year}",
                    "description": "Work experience details extracted from resume"
                })

        return experience_list

    def extract_all_info(self, text: str) -> ExtractedInfo:
        """Extract all information from resume text"""
        logger.info(f"extract_all_info called with text length: {len(text)}")
        logger.info(f"First 500 chars of text: {text[:500]}")
        
        contact_info = self.extract_contact_info(text)
        skills = self.extract_skills(text)
        experience_years = self.extract_experience_years(text)
        education = self.extract_education(text)
        work_experience = self.extract_work_experience(text)

        logger.info(f"Final extracted skills: {skills}")
        
        return ExtractedInfo(
            name=contact_info["name"],
            email=contact_info["email"],
            phone=contact_info["phone"],
            skills=skills,
            experience_years=experience_years,
            education=education,
            work_experience=work_experience,
            projects=[]  # Could be extended
        )

# Singleton instance
nlp_service = NLPService()
