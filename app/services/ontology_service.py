"""
Ontology and Knowledge Graph Service
Provides structured knowledge about skills, industries, and job relationships
"""

from typing import Dict, List, Any, Set, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import json
import logging

logger = logging.getLogger(__name__)

@dataclass
class SkillNode:
    """Represents a skill in the knowledge graph"""
    name: str
    category: str
    synonyms: List[str]
    related_skills: List[str]
    difficulty_level: int  # 1-5 scale
    industry_relevance: Dict[str, float]  # Industry -> relevance score
    prerequisites: List[str]
    learning_path: List[str]

@dataclass
class IndustryNode:
    """Represents an industry in the knowledge graph"""
    name: str
    key_skills: List[str]
    typical_roles: List[str]
    salary_ranges: Dict[str, Tuple[float, float]]  # Role -> (min, max)
    growth_trends: Dict[str, float]  # Year -> growth rate
    remote_friendly: float  # 0-1 scale

@dataclass
class JobRoleNode:
    """Represents a job role in the knowledge graph"""
    title: str
    industry: str
    required_skills: List[str]
    preferred_skills: List[str]
    experience_level: str
    career_path: List[str]
    salary_range: Tuple[float, float]

class OntologyService:
    """Service for managing job-related knowledge graph and ontology"""
    
    def __init__(self):
        self.skills_graph = {}
        self.industries_graph = {}
        self.roles_graph = {}
        self.skill_relationships = defaultdict(list)
        self.industry_relationships = defaultdict(list)
        
        # Initialize the knowledge base
        self._initialize_skills_ontology()
        self._initialize_industries_ontology()
        self._initialize_roles_ontology()
        self._build_relationships()
    
    def _initialize_skills_ontology(self):
        """Initialize skills knowledge base"""
        self.skills_graph = {
            # Programming Languages
            'python': SkillNode(
                name='Python',
                category='programming',
                synonyms=['py', 'python3', 'python2'],
                related_skills=['django', 'flask', 'pandas', 'numpy', 'scikit-learn'],
                difficulty_level=2,
                industry_relevance={'technology': 0.9, 'finance': 0.7, 'healthcare': 0.6, 'marketing': 0.5},
                prerequisites=['programming fundamentals'],
                learning_path=['python basics', 'data structures', 'libraries', 'frameworks']
            ),
            'javascript': SkillNode(
                name='JavaScript',
                category='programming',
                synonyms=['js', 'ecmascript', 'nodejs'],
                related_skills=['react', 'angular', 'vue', 'node.js', 'express'],
                difficulty_level=2,
                industry_relevance={'technology': 0.9, 'marketing': 0.6, 'finance': 0.4},
                prerequisites=['html', 'css'],
                learning_path=['js basics', 'dom manipulation', 'frameworks', 'backend']
            ),
            'java': SkillNode(
                name='Java',
                category='programming',
                synonyms=['java8', 'java11', 'jdk'],
                related_skills=['spring', 'spring boot', 'hibernate', 'maven', 'gradle'],
                difficulty_level=3,
                industry_relevance={'technology': 0.8, 'finance': 0.7, 'enterprise': 0.9},
                prerequisites=['object-oriented programming'],
                learning_path=['java basics', 'oop', 'collections', 'frameworks']
            ),
            'spring boot': SkillNode(
                name='Spring Boot',
                category='web_backend',
                synonyms=['springboot', 'spring framework'],
                related_skills=['java', 'spring', 'maven', 'gradle', 'hibernate', 'jpa', 'rest api', 'microservices'],
                difficulty_level=4,
                industry_relevance={'technology': 0.8, 'enterprise': 0.9, 'finance': 0.7},
                prerequisites=['java', 'spring'],
                learning_path=['spring basics', 'spring boot', 'rest apis', 'microservices']
            ),
            
            # Web Technologies
            'css': SkillNode(
                name='CSS',
                category='web_frontend',
                synonyms=['cascading style sheets', 'css3'],
                related_skills=['html', 'sass', 'less', 'bootstrap', 'tailwind', 'responsive design', 'flexbox', 'grid'],
                difficulty_level=2,
                industry_relevance={'technology': 0.8, 'marketing': 0.6, 'design': 0.9},
                prerequisites=['html'],
                learning_path=['css basics', 'selectors', 'layout', 'responsive design']
            ),
            'react': SkillNode(
                name='React',
                category='web_frontend',
                synonyms=['reactjs', 'react.js'],
                related_skills=['javascript', 'jsx', 'redux', 'next.js'],
                difficulty_level=3,
                industry_relevance={'technology': 0.9, 'marketing': 0.7, 'startup': 0.8},
                prerequisites=['javascript', 'html', 'css'],
                learning_path=['js fundamentals', 'react basics', 'hooks', 'state management']
            ),
            'node.js': SkillNode(
                name='Node.js',
                category='web',
                synonyms=['nodejs', 'node'],
                related_skills=['javascript', 'express', 'npm', 'mongodb'],
                difficulty_level=3,
                industry_relevance={'technology': 0.8, 'startup': 0.9, 'enterprise': 0.6},
                prerequisites=['javascript', 'backend concepts'],
                learning_path=['js backend', 'express', 'databases', 'deployment']
            ),
            
            # Data Science & AI
            'machine learning': SkillNode(
                name='Machine Learning',
                category='ai_ml',
                synonyms=['ml', 'ai', 'artificial intelligence'],
                related_skills=['python', 'pandas', 'scikit-learn', 'tensorflow', 'pytorch'],
                difficulty_level=4,
                industry_relevance={'technology': 0.9, 'finance': 0.8, 'healthcare': 0.7, 'marketing': 0.6},
                prerequisites=['python', 'statistics', 'linear algebra'],
                learning_path=['statistics', 'python', 'ml algorithms', 'deep learning']
            ),
            'pandas': SkillNode(
                name='Pandas',
                category='data_science',
                synonyms=['pandas library', 'data manipulation'],
                related_skills=['python', 'numpy', 'matplotlib', 'jupyter'],
                difficulty_level=2,
                industry_relevance={'technology': 0.8, 'finance': 0.9, 'healthcare': 0.7, 'marketing': 0.8},
                prerequisites=['python'],
                learning_path=['python basics', 'data structures', 'pandas basics', 'advanced pandas']
            ),
            'data science': SkillNode(
                name='Data Science',
                category='data_science',
                synonyms=['data scientist', 'data analytics', 'data analysis'],
                related_skills=['python', 'pandas', 'numpy', 'matplotlib', 'seaborn', 'scikit-learn', 'jupyter', 'sql', 'statistics'],
                difficulty_level=4,
                industry_relevance={'technology': 0.9, 'finance': 0.9, 'healthcare': 0.8, 'marketing': 0.8, 'consulting': 0.7},
                prerequisites=['python', 'statistics', 'sql'],
                learning_path=['python', 'statistics', 'data manipulation', 'machine learning', 'data visualization']
            ),
            
            # Cloud & DevOps
            'aws': SkillNode(
                name='AWS',
                category='aws_services',
                synonyms=['amazon web services', 'amazon cloud'],
                related_skills=['lambda', 'ec2', 's3', 'rds', 'dynamodb', 'cloudformation', 'cloudwatch', 'iam', 'vpc', 'route53', 'sns', 'sqs', 'api gateway', 'elastic beanstalk', 'ecs', 'eks', 'fargate', 'cloudfront', 'sagemaker', 'redshift', 'elasticsearch', 'kinesis', 'step functions'],
                difficulty_level=4,
                industry_relevance={'technology': 0.9, 'enterprise': 0.8, 'startup': 0.7},
                prerequisites=['cloud concepts', 'linux'],
                learning_path=['cloud basics', 'aws services', 'deployment', 'monitoring']
            ),
            'lambda': SkillNode(
                name='AWS Lambda',
                category='aws_services',
                synonyms=['lambda functions', 'serverless'],
                related_skills=['aws', 'python', 'javascript', 'nodejs', 'api gateway', 'dynamodb', 's3'],
                difficulty_level=4,
                industry_relevance={'technology': 0.8, 'startup': 0.9, 'enterprise': 0.7},
                prerequisites=['aws', 'programming'],
                learning_path=['serverless concepts', 'lambda basics', 'event handling', 'advanced patterns']
            ),
            'ec2': SkillNode(
                name='AWS EC2',
                category='aws_services',
                synonyms=['elastic compute cloud', 'aws instances'],
                related_skills=['aws', 'linux', 'docker', 'terraform', 'cloudformation'],
                difficulty_level=3,
                industry_relevance={'technology': 0.8, 'enterprise': 0.9, 'startup': 0.7},
                prerequisites=['aws', 'linux'],
                learning_path=['ec2 basics', 'instance types', 'networking', 'security groups']
            ),
            'docker': SkillNode(
                name='Docker',
                category='containerization',
                synonyms=['containerization', 'containers'],
                related_skills=['kubernetes', 'containers', 'podman', 'rancher', 'helm', 'deployment', 'ci/cd', 'pipeline', 'devops'],
                difficulty_level=3,
                industry_relevance={'technology': 0.8, 'enterprise': 0.7, 'startup': 0.9},
                prerequisites=['linux', 'networking'],
                learning_path=['containerization', 'docker basics', 'orchestration', 'production']
            ),
            
            # Databases
            'mysql': SkillNode(
                name='MySQL',
                category='databases',
                synonyms=['mysql database', 'mysql server'],
                related_skills=['sql', 'postgresql', 'oracle', 'database design', 'indexing', 'query optimization'],
                difficulty_level=3,
                industry_relevance={'technology': 0.8, 'enterprise': 0.7, 'startup': 0.6},
                prerequisites=['sql', 'database concepts'],
                learning_path=['sql basics', 'mysql administration', 'performance tuning', 'advanced features']
            ),
            'sql': SkillNode(
                name='SQL',
                category='databases',
                synonyms=['structured query language', 'database'],
                related_skills=['mysql', 'postgresql', 'mongodb', 'redis'],
                difficulty_level=2,
                industry_relevance={'technology': 0.8, 'finance': 0.9, 'healthcare': 0.7, 'marketing': 0.6},
                prerequisites=['database concepts'],
                learning_path=['sql basics', 'joins', 'optimization', 'advanced queries']
            ),
            'mongodb': SkillNode(
                name='MongoDB',
                category='database',
                synonyms=['mongo', 'nosql', 'document database'],
                related_skills=['node.js', 'python', 'javascript', 'json'],
                difficulty_level=2,
                industry_relevance={'technology': 0.7, 'startup': 0.8, 'enterprise': 0.5},
                prerequisites=['database concepts'],
                learning_path=['nosql basics', 'mongodb basics', 'aggregation', 'scaling']
            ),
            
            # Development Tools
            'git': SkillNode(
                name='Git',
                category='development_tools',
                synonyms=['version control', 'git version control', 'source control'],
                related_skills=['github', 'gitlab', 'bitbucket', 'command line', 'bash'],
                difficulty_level=2,
                industry_relevance={'technology': 0.9, 'startup': 0.9, 'enterprise': 0.8, 'consulting': 0.7},
                prerequisites=['command line basics'],
                learning_path=['git basics', 'branching', 'merging', 'collaboration', 'advanced git']
            )
        }
    
    def _initialize_industries_ontology(self):
        """Initialize industries knowledge base"""
        self.industries_graph = {
            'technology': IndustryNode(
                name='Technology',
                key_skills=['python', 'javascript', 'react', 'aws', 'docker', 'sql'],
                typical_roles=['software engineer', 'data scientist', 'devops engineer', 'product manager'],
                salary_ranges={
                    'software engineer': (80000, 150000),
                    'data scientist': (90000, 160000),
                    'devops engineer': (85000, 140000),
                    'product manager': (95000, 170000)
                },
                growth_trends={'2023': 0.15, '2024': 0.12, '2025': 0.10},
                remote_friendly=0.8
            ),
            'finance': IndustryNode(
                name='Finance',
                key_skills=[
                    'excel', 'risk management', 'financial modeling',
                    'vba', 'data analysis', 'statistics', 'regression', 'portfolio management',
                    'quantitative analysis', 'compliance', 'accounting', 'power bi', 'tableau'
                ],
                typical_roles=['financial analyst', 'risk analyst', 'quantitative analyst', 'investment banker'],
                salary_ranges={
                    'financial analyst': (70000, 120000),
                    'risk analyst': (75000, 130000),
                    'quantitative analyst': (100000, 180000),
                    'investment banker': (120000, 250000)
                },
                growth_trends={'2023': 0.08, '2024': 0.06, '2025': 0.05},
                remote_friendly=0.4
            ),
            'healthcare': IndustryNode(
                name='Healthcare',
                key_skills=[
                    'data analysis', 'medical knowledge', 'compliance',
                    'clinical research', 'biostatistics', 'electronic health records', 'data visualization',
                    'regulatory affairs', 'public health', 'machine learning', 'r', 'sas'
                ],
                typical_roles=['healthcare analyst', 'clinical data manager', 'health informatics specialist'],
                salary_ranges={
                    'healthcare analyst': (65000, 110000),
                    'clinical data manager': (70000, 120000),
                    'health informatics specialist': (75000, 130000)
                },
                growth_trends={'2023': 0.12, '2024': 0.10, '2025': 0.08},
                remote_friendly=0.3
            ),
            'startup': IndustryNode(
                name='Startup',
                key_skills=['javascript', 'react', 'node.js', 'aws', 'docker', 'python'],
                typical_roles=['full stack developer', 'product manager', 'growth hacker', 'data scientist'],
                salary_ranges={
                    'full stack developer': (70000, 130000),
                    'product manager': (80000, 140000),
                    'growth hacker': (60000, 110000),
                    'data scientist': (80000, 150000)
                },
                growth_trends={'2023': 0.20, '2024': 0.18, '2025': 0.15},
                remote_friendly=0.9
            )
        }
    def _initialize_roles_ontology(self):
        """Initialize job roles knowledge base"""
        self.roles_graph = {
            'software engineer': JobRoleNode(
                title='Software Engineer',
                industry='technology',
                required_skills=['programming', 'data structures', 'algorithms'],
                preferred_skills=['python', 'javascript', 'react', 'aws'],
                experience_level='mid',
                career_path=['junior developer', 'software engineer', 'senior engineer', 'tech lead'],
                salary_range=(80000, 150000)
            ),
            'data scientist': JobRoleNode(
                title='Data Scientist',
                industry='technology',
                required_skills=['python', 'machine learning', 'statistics'],
                preferred_skills=['pandas', 'scikit-learn', 'tensorflow', 'sql'],
                experience_level='mid',
                career_path=['data analyst', 'data scientist', 'senior data scientist', 'data science manager'],
                salary_range=(90000, 160000)
            ),
            'financial analyst': JobRoleNode(
                title='Financial Analyst',
                industry='finance',
                required_skills=['excel', 'financial modeling', 'sql'],
                preferred_skills=['python', 'risk management', 'vba'],
                experience_level='entry',
                career_path=['financial analyst', 'senior analyst', 'associate', 'vice president'],
                salary_range=(70000, 120000)
            )
        }
    
    def _build_relationships(self):
        """Build relationships between skills, industries, and roles"""
        # Build skill relationships
        for skill_name, skill_node in self.skills_graph.items():
            for related_skill in skill_node.related_skills:
                if related_skill in self.skills_graph:
                    self.skill_relationships[skill_name].append(related_skill)
                    self.skill_relationships[related_skill].append(skill_name)
        
        # Build industry relationships
        for industry_name, industry_node in self.industries_graph.items():
            for skill in industry_node.key_skills:
                if skill in self.skills_graph:
                    self.industry_relationships[industry_name].append(skill)
    
    def get_skill_similarity(self, skill1: str, skill2: str) -> float:
        """Calculate similarity between two skills"""
        logger.info(f"Calculating similarity between '{skill1}' and '{skill2}'")
        
        if skill1 == skill2:
            logger.info(f"Exact match: {skill1} == {skill2}")
            return 1.0
        
        skill1_node = self.skills_graph.get(skill1.lower())
        skill2_node = self.skills_graph.get(skill2.lower())
        
        if not skill1_node or not skill2_node:
            logger.info(f"No skill nodes found for '{skill1}' or '{skill2}'")
            return 0.0
        
        # Check if skills are synonyms
        if skill1.lower() in skill2_node.synonyms or skill2.lower() in skill1_node.synonyms:
            logger.info(f"Synonym match: {skill1} <-> {skill2}")
            return 0.9
        
        # Check if skills are directly related
        if skill2.lower() in skill1_node.related_skills or skill1.lower() in skill2_node.related_skills:
            logger.info(f"Related skills match: {skill1} <-> {skill2}")
            return 0.7
        
        # Check if skills are in same category
        if skill1_node.category == skill2_node.category:
            logger.info(f"Same category match: {skill1} ({skill1_node.category}) <-> {skill2} ({skill2_node.category})")
            return 0.5
        
        # Check if skills are connected through relationships
        if skill2.lower() in self.skill_relationships.get(skill1.lower(), []):
            logger.info(f"Relationship match: {skill1} <-> {skill2}")
            return 0.6
        
        logger.info(f"No similarity found between '{skill1}' and '{skill2}'")
        return 0.0
    
    def get_skill_industry_relevance(self, skill: str, industry: str) -> float:
        """Get relevance of a skill to an industry"""
        skill_node = self.skills_graph.get(skill.lower())
        if not skill_node:
            return 0.0
        
        return skill_node.industry_relevance.get(industry.lower(), 0.0)
    
    def get_related_skills(self, skill: str, max_skills: int = 5) -> List[str]:
        """Get related skills for a given skill"""
        skill_node = self.skills_graph.get(skill.lower())
        if not skill_node:
            return []
        
        # Combine related skills and relationship-based skills
        related = set(skill_node.related_skills)
        related.update(self.skill_relationships.get(skill.lower(), []))
        
        return list(related)[:max_skills]
    
    def get_skill_learning_path(self, skill: str) -> List[str]:
        """Get learning path for a skill"""
        skill_node = self.skills_graph.get(skill.lower())
        if not skill_node:
            return []
        
        return skill_node.learning_path
    
    def get_industry_skills(self, industry: str) -> List[str]:
        """Get key skills for an industry"""
        industry_node = self.industries_graph.get(industry.lower())
        if not industry_node:
            return []
        
        return industry_node.key_skills
    
    def get_role_requirements(self, role: str) -> Dict[str, Any]:
        """Get requirements for a job role"""
        role_node = self.roles_graph.get(role.lower())
        if not role_node:
            return {}
        
        return {
            'required_skills': role_node.required_skills,
            'preferred_skills': role_node.preferred_skills,
            'experience_level': role_node.experience_level,
            'career_path': role_node.career_path,
            'salary_range': role_node.salary_range,
            'industry': role_node.industry
        }
    
    def suggest_skill_gaps(self, candidate_skills: List[str], target_role: str) -> List[Dict[str, Any]]:
        """Suggest skills to learn for a target role"""
        role_requirements = self.get_role_requirements(target_role)
        if not role_requirements:
            return []
        
        required_skills = role_requirements['required_skills']
        preferred_skills = role_requirements['preferred_skills']
        
        candidate_skills_lower = [skill.lower() for skill in candidate_skills]
        gaps = []
        
        # Check required skills
        for skill in required_skills:
            if not any(self.get_skill_similarity(skill, candidate_skill) > 0.7 
                      for candidate_skill in candidate_skills_lower):
                gaps.append({
                    'skill': skill,
                    'type': 'required',
                    'priority': 'high',
                    'learning_path': self.get_skill_learning_path(skill)
                })
        
        # Check preferred skills
        for skill in preferred_skills:
            if not any(self.get_skill_similarity(skill, candidate_skill) > 0.7 
                      for candidate_skill in candidate_skills_lower):
                gaps.append({
                    'skill': skill,
                    'type': 'preferred',
                    'priority': 'medium',
                    'learning_path': self.get_skill_learning_path(skill)
                })
        
        return gaps
    
    def get_career_recommendations(self, candidate_skills: List[str], 
                                 current_role: str = None) -> List[Dict[str, Any]]:
        """Get career progression recommendations"""
        recommendations = []
        
        # Find roles that match candidate skills
        for role_name, role_node in self.roles_graph.items():
            match_score = self._calculate_role_match_score(candidate_skills, role_node)
            
            if match_score > 0.6:  # Threshold for recommendations
                recommendations.append({
                    'role': role_name,
                    'match_score': match_score,
                    'industry': role_node.industry,
                    'salary_range': role_node.salary_range,
                    'career_path': role_node.career_path,
                    'skill_gaps': self.suggest_skill_gaps(candidate_skills, role_name)
                })
        
        # Sort by match score
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations[:5]  # Top 5 recommendations
    
    def _calculate_role_match_score(self, candidate_skills: List[str], role_node: JobRoleNode) -> float:
        """Calculate how well candidate skills match a role"""
        candidate_skills_lower = [skill.lower() for skill in candidate_skills]
        
        # Check required skills
        required_matches = 0
        for skill in role_node.required_skills:
            if any(self.get_skill_similarity(skill, candidate_skill) > 0.7 
                  for candidate_skill in candidate_skills_lower):
                required_matches += 1
        
        # Check preferred skills
        preferred_matches = 0
        for skill in role_node.preferred_skills:
            if any(self.get_skill_similarity(skill, candidate_skill) > 0.7 
                  for candidate_skill in candidate_skills_lower):
                preferred_matches += 1
        
        # Calculate weighted score
        required_score = required_matches / len(role_node.required_skills) if role_node.required_skills else 0
        preferred_score = preferred_matches / len(role_node.preferred_skills) if role_node.preferred_skills else 0
        
        return (required_score * 0.7) + (preferred_score * 0.3)
    
    def get_skill_ontology_stats(self) -> Dict[str, Any]:
        """Get statistics about the skill ontology"""
        return {
            'total_skills': len(self.skills_graph),
            'total_industries': len(self.industries_graph),
            'total_roles': len(self.roles_graph),
            'skill_categories': list(set(skill.category for skill in self.skills_graph.values())),
            'industries': list(self.industries_graph.keys()),
            'roles': list(self.roles_graph.keys())
        }

# Singleton instance
ontology_service = OntologyService()
