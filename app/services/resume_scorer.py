from typing import Dict, List, Any, Tuple
import re
from dataclasses import dataclass

@dataclass
class ScoreBreakdown:
    ats_score: float
    completeness_score: float
    keyword_density_score: float
    formatting_score: float
    overall_score: float

@dataclass
class ResumeFeedback:
    warnings: List[str]
    suggestions: List[str]
    missing_fields: List[str]
    strengths: List[str]

class ResumeScorerService:
    def __init__(self):
        self.critical_fields = ['name', 'email', 'skills', 'work_experience']
        self.important_fields = ['phone', 'education', 'experience_years']
        self.nice_to_have_fields = ['projects']

        # ATS-friendly keywords
        self.action_verbs = [
            'achieved', 'administered', 'analyzed', 'built', 'collaborated',
            'created', 'delivered', 'developed', 'established', 'executed',
            'implemented', 'improved', 'increased', 'led', 'managed',
            'optimized', 'organized', 'planned', 'reduced', 'solved'
        ]

    def calculate_completeness_score(self, parsed_data: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Calculate completeness score based on filled fields"""
        score = 0.0
        missing_fields = []

        # Critical fields (60% of score)
        critical_weight = 0.6 / len(self.critical_fields)
        for field in self.critical_fields:
            field_key = f"parsed_{field}" if field in ['name', 'email'] else field
            if self._is_field_filled(parsed_data.get(field_key)):
                score += critical_weight
            else:
                missing_fields.append(field)

        # Important fields (30% of score)
        important_weight = 0.3 / len(self.important_fields)
        for field in self.important_fields:
            field_key = f"parsed_{field}" if field == 'phone' else field
            if self._is_field_filled(parsed_data.get(field_key)):
                score += important_weight
            else:
                missing_fields.append(field)

        # Nice to have fields (10% of score)
        nice_weight = 0.1 / len(self.nice_to_have_fields)
        for field in self.nice_to_have_fields:
            if self._is_field_filled(parsed_data.get(field)):
                score += nice_weight

        return score, missing_fields

    def calculate_keyword_density_score(self, text: str, skills: List[str]) -> float:
        """Calculate score based on keyword density and action verbs"""
        if not text:
            return 0.0

        text_lower = text.lower()
        score = 0.0

        # Action verbs score (40% of keyword score)
        action_verb_count = sum(1 for verb in self.action_verbs if verb in text_lower)
        action_verb_score = min(action_verb_count / 10.0, 1.0) * 0.4
        score += action_verb_score

        # Skills mentioned score (40% of keyword score)
        if skills:
            skills_mentioned = sum(1 for skill in skills if skill.lower() in text_lower)
            skills_score = min(skills_mentioned / len(skills), 1.0) * 0.4
            score += skills_score

        # Quantifiable achievements (20% of keyword score)
        number_patterns = [
            r'\d+%', r'\$\d+', r'\d+\+', r'\d+k\+?', r'\d+m\+?',
            r'increased.*\d+', r'reduced.*\d+', r'improved.*\d+'
        ]
        quantifiable_count = sum(len(re.findall(pattern, text_lower)) for pattern in number_patterns)
        quantifiable_score = min(quantifiable_count / 5.0, 1.0) * 0.2
        score += quantifiable_score

        return score

    def calculate_formatting_score(self, text: str, parsed_data: Dict[str, Any]) -> float:
        """Calculate formatting score based on structure and readability"""
        score = 0.0

        if not text:
            return 0.0

        # Length check (not too short, not too long)
        word_count = len(text.split())
        if 200 <= word_count <= 1500:
            score += 0.3
        elif 100 <= word_count < 200 or 1500 < word_count <= 2000:
            score += 0.2

        # Section headers (experience, education, skills, etc.)
        section_patterns = [
            r'experience', r'education', r'skills', r'projects',
            r'work history', r'employment', r'qualifications'
        ]
        section_count = sum(1 for pattern in section_patterns if re.search(pattern, text.lower()))
        section_score = min(section_count / 4.0, 1.0) * 0.3
        score += section_score

        # Contact information formatting
        if parsed_data.get('parsed_email') and parsed_data.get('parsed_phone'):
            score += 0.2
        elif parsed_data.get('parsed_email') or parsed_data.get('parsed_phone'):
            score += 0.1

        # Consistent formatting (basic check)
        lines = text.split('\n')
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        if len(non_empty_lines) > 10:  # Sufficient content structure
            score += 0.2

        return min(score, 1.0)

    def calculate_ats_score(self, parsed_data: Dict[str, Any]) -> float:
        """Calculate ATS-friendliness score"""
        score = 0.0

        # Essential contact information
        if parsed_data.get('parsed_email'):
            score += 0.25
        if parsed_data.get('parsed_name'):
            score += 0.15
        if parsed_data.get('parsed_phone'):
            score += 0.1

        # Skills section
        skills = parsed_data.get('skills', [])
        if skills and len(skills) >= 3:
            score += 0.25
        elif skills:
            score += 0.15

        # Work experience
        work_exp = parsed_data.get('work_experience', [])
        if work_exp and len(work_exp) >= 2:
            score += 0.2
        elif work_exp:
            score += 0.1

        # Education
        education = parsed_data.get('education', [])
        if education:
            score += 0.05

        return min(score, 1.0)

    def generate_feedback(self, parsed_data: Dict[str, Any], scores: ScoreBreakdown) -> ResumeFeedback:
        """Generate feedback and suggestions for improvement"""
        warnings = []
        suggestions = []
        missing_fields = []
        strengths = []

        # Check critical missing fields
        if not parsed_data.get('parsed_name'):
            warnings.append("Name is missing or unclear")
            missing_fields.append('name')
        if not parsed_data.get('parsed_email'):
            warnings.append("Email address not found")
            missing_fields.append('email')

        # Skills analysis
        skills = parsed_data.get('skills', [])
        if not skills:
            warnings.append("No technical skills detected")
            suggestions.append("Add a dedicated skills section with relevant technical skills")
            missing_fields.append('skills')
        elif len(skills) < 5:
            suggestions.append(f"Consider adding more skills (currently {len(skills)} detected)")
        else:
            strengths.append(f"Good variety of skills mentioned ({len(skills)} detected)")

        # Experience analysis
        work_exp = parsed_data.get('work_experience', [])
        if not work_exp:
            warnings.append("No work experience detected")
            suggestions.append("Add work experience section with job titles, companies, and dates")
            missing_fields.append('work_experience')
        elif len(work_exp) == 1:
            suggestions.append("Consider adding more work experience entries if available")
        else:
            strengths.append("Multiple work experiences provided")

        # Contact information
        if not parsed_data.get('parsed_phone'):
            suggestions.append("Add phone number for better contact information")

        # Education
        education = parsed_data.get('education', [])
        if not education:
            suggestions.append("Add education information (degree, institution, graduation year)")
            missing_fields.append('education')
        else:
            strengths.append("Education information provided")

        # Score-based suggestions
        if scores.formatting_score < 0.6:
            suggestions.append("Improve resume formatting and structure")
        if scores.keyword_density_score < 0.5:
            suggestions.append("Include more action verbs and quantifiable achievements")
        if scores.ats_score < 0.7:
            suggestions.append("Optimize resume for ATS systems")

        # Positive reinforcement
        if scores.overall_score >= 0.8:
            strengths.append("Overall excellent resume quality")
        elif scores.overall_score >= 0.7:
            strengths.append("Good resume quality with room for improvement")

        return ResumeFeedback(
            warnings=warnings,
            suggestions=suggestions,
            missing_fields=missing_fields,
            strengths=strengths
        )

    def score_resume(self, parsed_data: Dict[str, Any], raw_text: str = "") -> Tuple[ScoreBreakdown, ResumeFeedback]:
        """Main method to score a resume and provide feedback"""
        # Calculate individual scores
        completeness_score, missing_fields = self.calculate_completeness_score(parsed_data)
        keyword_density_score = self.calculate_keyword_density_score(
            raw_text or parsed_data.get('extracted_text', ''), 
            parsed_data.get('skills', [])
        )
        formatting_score = self.calculate_formatting_score(
            raw_text or parsed_data.get('extracted_text', ''), 
            parsed_data
        )
        ats_score = self.calculate_ats_score(parsed_data)

        # Calculate overall score (weighted average)
        overall_score = (
            completeness_score * 0.35 +
            ats_score * 0.25 +
            keyword_density_score * 0.25 +
            formatting_score * 0.15
        )

        scores = ScoreBreakdown(
            ats_score=ats_score,
            completeness_score=completeness_score,
            keyword_density_score=keyword_density_score,
            formatting_score=formatting_score,
            overall_score=overall_score
        )

        feedback = self.generate_feedback(parsed_data, scores)

        return scores, feedback

    def _is_field_filled(self, field_value) -> bool:
        """Check if a field has meaningful content"""
        if field_value is None:
            return False
        if isinstance(field_value, str):
            return bool(field_value.strip())
        if isinstance(field_value, list):
            return bool(field_value)
        if isinstance(field_value, (int, float)):
            return field_value is not None
        return bool(field_value)

# Singleton instance
resume_scorer = ResumeScorerService()
