from typing import List, Dict, Any, Tuple
import math
import re
import logging
from collections import Counter
from dataclasses import dataclass
from app.services.nlp_service import nlp_service
from app.services.ontology_service import ontology_service
from app.services.weight_calculator import weight_calculator

# Set up logging
logger = logging.getLogger(__name__)

@dataclass
class JobMatch:
    job_id: int
    match_score: float
    skill_matches: List[str]
    missing_skills: List[str]
    match_reasons: List[str]
    experience_match: bool
    location_match: bool
    salary_match: bool

class JobMatcherService:
    def __init__(self):
        # Minimal English stopword list to avoid heavy dependencies
        self.stop_words = {
            'a', 'an', 'the', 'and', 'or', 'but', 'if', 'while', 'with', 'for', 'to', 'of', 'in', 'on', 'at',
            'by', 'from', 'as', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'this', 'that', 'these', 'those',
            'it', 'its', 'he', 'she', 'they', 'them', 'we', 'you', 'your', 'i', 'me', 'my', 'our', 'us'
        }

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into alphanumeric tokens, lowercased and stopword-filtered."""
        text_lower = text.lower()
        tokens = re.findall(r"[a-z0-9]+", text_lower)
        return [t for t in tokens if t not in self.stop_words and len(t) > 1]

    def _generate_ngrams(self, tokens: List[str], n: int) -> List[str]:
        if n == 1:
            return tokens
        ngrams: List[str] = []
        for i in range(len(tokens) - n + 1):
            ngrams.append(" ".join(tokens[i:i + n]))
        return ngrams

    def _build_document_terms(self, text: str) -> List[str]:
        tokens = self._tokenize(text)
        unigrams = tokens
        bigrams = self._generate_ngrams(tokens, 2)
        terms = unigrams + bigrams
        # Cap features to roughly match previous vectorizer behavior
        return terms[:1000]

    def _tfidf_vectors(self, documents: List[str]) -> List[Dict[str, float]]:
        """Compute simple TF-IDF vectors for a small corpus without external deps."""
        doc_terms: List[List[str]] = [self._build_document_terms(doc) for doc in documents]
        term_frequencies: List[Counter] = [Counter(terms) for terms in doc_terms]

        # Document frequency
        df_counter: Counter = Counter()
        for terms in doc_terms:
            df_counter.update(set(terms))

        num_docs = len(documents)
        vectors: List[Dict[str, float]] = []
        for tf in term_frequencies:
            vector: Dict[str, float] = {}
            for term, count in tf.items():
                # Smooth IDF
                df = df_counter.get(term, 0)
                idf = math.log((1 + num_docs) / (1 + df)) + 1.0
                # Raw term frequency; could use log-normalization, but keep simple
                tf_value = 1.0 + math.log(count)
                vector[term] = tf_value * idf
            # L2 normalize
            norm = math.sqrt(sum(v * v for v in vector.values())) or 1.0
            for term in list(vector.keys()):
                vector[term] /= norm
            vectors.append(vector)
        return vectors

    def _cosine_similarity(self, v1: Dict[str, float], v2: Dict[str, float]) -> float:
        if not v1 or not v2:
            return 0.0
        # Iterate over the smaller vector for efficiency
        if len(v1) > len(v2):
            v1, v2 = v2, v1
        dot = 0.0
        for term, w1 in v1.items():
            w2 = v2.get(term)
            if w2 is not None:
                dot += w1 * w2
        # Vectors are already normalized
        return max(0.0, min(1.0, dot))

    def calculate_skill_match_score(self, candidate_skills: List[str], required_skills: List[str], 
                                  preferred_skills: List[str] = None, resume_text: str = "", 
                                  use_enhanced_matching: bool = True) -> Tuple[float, List[str], List[str]]:
        """Calculate skill match score - simple or enhanced matching"""
        if not candidate_skills or not required_skills:
            return 0.0, [], required_skills or []

        if use_enhanced_matching:
            return self._calculate_enhanced_skill_match_score(candidate_skills, required_skills, preferred_skills, resume_text)
        else:
            return self._calculate_simple_skill_match_score(candidate_skills, required_skills, preferred_skills)

    def _calculate_simple_skill_match_score(self, candidate_skills: List[str], required_skills: List[str], 
                                          preferred_skills: List[str] = None) -> Tuple[float, List[str], List[str]]:
        """Simple lowercase skill matching"""
        # Normalize skills to lowercase for comparison
        candidate_skills_lower = [skill.lower().strip() for skill in candidate_skills]
        required_skills_lower = [skill.lower().strip() for skill in required_skills]
        preferred_skills_lower = [skill.lower().strip() for skill in (preferred_skills or [])]

        # Simple exact match
        required_matches = [skill for skill in required_skills_lower if skill in candidate_skills_lower]
        preferred_matches = [skill for skill in preferred_skills_lower if skill in candidate_skills_lower]

        # Find missing skills
        missing_required = [skill for skill in required_skills_lower if skill not in required_matches]

        # Calculate score
        required_match_ratio = len(required_matches) / len(required_skills_lower) if required_skills_lower else 0
        preferred_match_ratio = len(preferred_matches) / len(preferred_skills_lower) if preferred_skills_lower else 0

        # Weighted score: 80% for required skills, 20% for preferred skills
        skill_score = (required_match_ratio * 0.8) + (preferred_match_ratio * 0.2)

        all_matches = list(set(required_matches + preferred_matches))

        return skill_score, all_matches, missing_required

    def _calculate_enhanced_skill_match_score(self, candidate_skills: List[str], required_skills: List[str], 
                                            preferred_skills: List[str] = None, resume_text: str = "") -> Tuple[float, List[str], List[str]]:
        """Enhanced skill match score 7using NLP capabilities (OPTIONAL - for future use)"""
        # Skills are already extracted and passed in candidate_skills
        enhanced_candidate_skills = set(candidate_skills)

        # Normalize skills to lowercase for comparison
        candidate_skills_lower = [skill.lower() for skill in enhanced_candidate_skills]
        required_skills_lower = [skill.lower() for skill in required_skills]
        preferred_skills_lower = [skill.lower() for skill in (preferred_skills or [])]

        # Enhanced matching with skill categories and synonyms
        required_matches = self._find_enhanced_skill_matches(candidate_skills_lower, required_skills_lower)
        preferred_matches = self._find_enhanced_skill_matches(candidate_skills_lower, preferred_skills_lower)

        # Find missing skills
        missing_required = [skill for skill in required_skills_lower 
                          if skill not in [match.lower() for match in required_matches]]

        # Calculate score with enhanced matching
        required_match_ratio = len(required_matches) / len(required_skills_lower) if required_skills_lower else 0
        preferred_match_ratio = len(preferred_matches) / len(preferred_skills_lower) if preferred_skills_lower else 0

        # Weighted score: 80% for required skills, 20% for preferred skills
        skill_score = (required_match_ratio * 0.8) + (preferred_match_ratio * 0.2)

        all_matches = list(set(required_matches + preferred_matches))  

        return skill_score, all_matches, missing_required

    def _find_enhanced_skill_matches(self, candidate_skills: List[str], job_skills: List[str]) -> List[str]:
        """Enhanced skill matching using ontology and NLP service (OPTIONAL - for future use)"""
        # Normalize skills for case-insensitive matching
        normalized_candidate_skills = [skill.lower().strip() for skill in candidate_skills]
        normalized_job_skills = [skill.lower().strip() for skill in job_skills]
        
        matches = []
        
        for i, job_skill in enumerate(job_skills):
            normalized_job_skill = normalized_job_skills[i]
            
            # Direct match (case-insensitive)
            if normalized_job_skill in normalized_candidate_skills:
                # Find the original candidate skill that matches
                for j, candidate_skill in enumerate(candidate_skills):
                    if normalized_candidate_skills[j] == normalized_job_skill:
                        matches.append(candidate_skill)
                        break
                continue
            
            # Ontology-based matching (using normalized skills)
            best_match = None
            best_similarity = 0.0
            
            for j, candidate_skill in enumerate(candidate_skills):
                normalized_candidate_skill = normalized_candidate_skills[j]
                similarity = ontology_service.get_skill_similarity(normalized_job_skill, normalized_candidate_skill)
                if similarity > best_similarity and similarity > 0.7:  # Higher threshold for ontology match
                    best_similarity = similarity
                    best_match = candidate_skill
            
            if best_match:
                matches.append(best_match)
                continue
            
            # Category-based matching using ontology service (fallback)
            # Only match within the same category to prevent false positives
            job_skill_node = ontology_service.skills_graph.get(normalized_job_skill)
            if job_skill_node:
                job_skill_category = job_skill_node.category
                
                # Only match if candidate has skills in the same category
                category_matches = []
                for j, candidate_skill in enumerate(candidate_skills):
                    normalized_candidate_skill = normalized_candidate_skills[j]
                    candidate_skill_node = ontology_service.skills_graph.get(normalized_candidate_skill)
                    if candidate_skill_node and candidate_skill_node.category == job_skill_category:
                        category_matches.append(candidate_skill)
                
                if category_matches:
                    # Only add the first match to avoid duplicates
                    matches.append(category_matches[0])
        
        return list(set(matches))

    def calculate_experience_match_score(self, candidate_experience: float, 
                                       min_experience: float = None, 
                                       max_experience: float = None,
                                       resume_text: str = "") -> Tuple[float, bool]:
        """Calculate enhanced experience match score using NLP"""
        # Use NLP to extract experience if not provided
        if candidate_experience is None and resume_text and nlp_service.nlp:
            extracted_experience = nlp_service.extract_experience_years(resume_text)
            if extracted_experience is not None:
                candidate_experience = extracted_experience

        if candidate_experience is None:
            return 0.5, False  # Neutral score if experience not provided

        if min_experience is None and max_experience is None:
            return 1.0, True  # No experience requirements

        if min_experience is not None and max_experience is not None:
            if min_experience <= candidate_experience <= max_experience:
                return 1.0, True
            elif candidate_experience < min_experience:
                # Penalize less for being under-experienced
                diff = min_experience - candidate_experience
                score = max(0.0, 1.0 - (diff * 0.2))
                return score, False
            else:  # Over-experienced
                diff = candidate_experience - max_experience
                score = max(0.7, 1.0 - (diff * 0.1))  # Less penalty for being over-qualified
                return score, candidate_experience <= max_experience + 2

        if min_experience is not None:
            if candidate_experience >= min_experience:
                return 1.0, True
            else:
                diff = min_experience - candidate_experience
                score = max(0.0, 1.0 - (diff * 0.2))
                return score, False

        return 1.0, True

    def calculate_location_match_score(self, candidate_location: str, job_location: str, 
                                     remote_allowed: str = "No") -> Tuple[float, bool]:
        """Calculate location compatibility score"""
        if not candidate_location or not job_location:
            return 0.5, False

        # Remote work handling
        if remote_allowed.lower() in ["yes", "fully remote", "remote"]:
            return 1.0, True

        candidate_location_lower = candidate_location.lower()
        job_location_lower = job_location.lower()

        # Exact match
        if candidate_location_lower == job_location_lower:
            return 1.0, True

        # City match (extract city from "City, State" format)
        candidate_parts = candidate_location_lower.split(',')
        job_parts = job_location_lower.split(',')

        if len(candidate_parts) > 0 and len(job_parts) > 0:
            candidate_city = candidate_parts[0].strip()
            job_city = job_parts[0].strip()

            if candidate_city == job_city:
                return 0.9, True

        # Partial match (state level)
        if len(candidate_parts) > 1 and len(job_parts) > 1:
            candidate_state = candidate_parts[1].strip()
            job_state = job_parts[1].strip()

            if candidate_state == job_state:
                return 0.6, True

        # Hybrid work gets moderate score
        if remote_allowed.lower() in ["hybrid", "partial remote"]:
            return 0.7, True

        return 0.2, False

    def calculate_semantic_similarity(self, candidate_profile: str, job_description: str) -> float:
        """Calculate semantic similarity using TF-IDF and cosine similarity"""
        if not candidate_profile or not job_description:
            return 0.0

        try:
            corpus = [candidate_profile, job_description]
            v1, v2 = self._tfidf_vectors(corpus)
            return float(self._cosine_similarity(v1, v2))
        except Exception as e:
            print(f"Error calculating semantic similarity: {e}")
            return 0.0

    def calculate_semantic_similarity_enhanced(self, resume_text: str, job_description: str) -> float:
        """Enhanced semantic similarity using spaCy embeddings"""
        if not resume_text or not job_description:
            return 0.0
        
        try:
            if nlp_service.nlp:
                # Use spaCy for better semantic understanding
                doc1 = nlp_service.nlp(resume_text)
                doc2 = nlp_service.nlp(job_description)
                
                # Calculate similarity using spaCy's built-in similarity
                similarity = doc1.similarity(doc2)
                
                # Also calculate entity-based similarity
                entity_similarity = self._calculate_entity_similarity(doc1, doc2)
                
                # Combine both similarities
                combined_similarity = (similarity * 0.7) + (entity_similarity * 0.3)
                
                return float(combined_similarity)
            else:
                # Fallback to TF-IDF if spaCy not available
                return self.calculate_semantic_similarity(resume_text, job_description)
        except Exception as e:
            print(f"Error calculating enhanced semantic similarity: {e}")
            return 0.0

    def _calculate_entity_similarity(self, doc1, doc2) -> float:
        """Calculate similarity based on named entities"""
        entities1 = set([ent.text.lower() for ent in doc1.ents])
        entities2 = set([ent.text.lower() for ent in doc2.ents])
        
        if not entities1 or not entities2:
            return 0.0
        
        # Calculate Jaccard similarity for entities
        intersection = len(entities1.intersection(entities2))
        union = len(entities1.union(entities2))
        
        return intersection / union if union > 0 else 0.0

    def calculate_education_match_score(self, candidate_education: List[Dict[str, Any]], 
                                      job_requirements: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Match education requirements using NLP"""
        if not candidate_education or not job_requirements:
            return 0.5, []  # Neutral score if no data
        
        try:
            # Extract education requirements from job description using NLP
            required_education = self._extract_education_requirements(job_requirements)
            
            if not required_education:
                return 1.0, []  # No education requirements
            
            matches = []
            total_score = 0.0
            
            for req in required_education:
                best_match_score = 0.0
                best_match = None
                
                for edu in candidate_education:
                    match_score = self._calculate_education_similarity(edu, req)
                    if match_score > best_match_score:
                        best_match_score = match_score
                        best_match = edu
                
                if best_match and best_match_score > 0.6:
                    matches.append(f"{best_match.get('degree', '')} matches {req.get('degree', '')}")
                    total_score += best_match_score
            
            avg_score = total_score / len(required_education) if required_education else 0.0
            return avg_score, matches
            
        except Exception as e:
            print(f"Error calculating education match: {e}")
            return 0.5, []

    def calculate_work_experience_relevance(self, candidate_experience: List[Dict[str, Any]], 
                                          job_description: str) -> Tuple[float, List[str]]:
        """Analyze work experience relevance using NLP"""
        if not candidate_experience or not job_description:
            return 0.5, []
        
        try:
            if not nlp_service.nlp:
                return 0.5, []  # Fallback if spaCy not available
            
            job_doc = nlp_service.nlp(job_description)
            relevant_experiences = []
            total_relevance = 0.0
            
            for exp in candidate_experience:
                # Create experience text
                exp_text = f"{exp.get('role', '')} {exp.get('company', '')} {exp.get('description', '')}"
                exp_doc = nlp_service.nlp(exp_text)
                
                # Calculate relevance using semantic similarity
                relevance = exp_doc.similarity(job_doc)
                
                if relevance > 0.3:  # Threshold for relevance
                    relevant_experiences.append(f"{exp.get('role', '')} at {exp.get('company', '')} (relevance: {relevance:.2f})")
                    total_relevance += relevance
            
            avg_relevance = total_relevance / len(candidate_experience) if candidate_experience else 0.0
            return avg_relevance, relevant_experiences
            
        except Exception as e:
            print(f"Error calculating work experience relevance: {e}")
            return 0.5, []

    def extract_job_requirements_from_description(self, job_description: str) -> Dict[str, Any]:
        """Extract requirements from job description using NLP"""
        if not job_description or not nlp_service.nlp:
            return {}
        
        try:
            doc = nlp_service.nlp(job_description)
            
            # Extract skills mentioned in job description
            extracted_skills = nlp_service.extract_skills(job_description)
            
            # Extract experience requirements
            experience_years = nlp_service.extract_experience_years(job_description)
            
            # Extract education requirements
            education_requirements = self._extract_education_requirements_from_text(job_description)
            
            # Extract location information
            locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
            
            # Extract company information
            organizations = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
            
            # Extract key phrases and requirements
            key_phrases = self._extract_key_phrases(doc)
            
            return {
                'extracted_skills': extracted_skills,
                'experience_years': experience_years,
                'education_requirements': education_requirements,
                'locations': locations,
                'organizations': organizations,
                'key_phrases': key_phrases,
                'requirements_section': self._extract_requirements_section(job_description)
            }
            
        except Exception as e:
            print(f"Error extracting job requirements: {e}")
            return {}

    def _extract_education_requirements(self, job_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract education requirements from job data"""
        education_reqs = []
        
        # Check if education requirements are explicitly provided
        if 'education_requirements' in job_requirements:
            for req in job_requirements['education_requirements']:
                education_reqs.append({
                    'degree': req.get('degree', ''),
                    'field': req.get('field', ''),
                    'required': req.get('required', True)
                })
        
        return education_reqs

    def _calculate_education_similarity(self, candidate_edu: Dict[str, Any], 
                                      required_edu: Dict[str, Any]) -> float:
        """Calculate similarity between candidate and required education"""
        candidate_degree = candidate_edu.get('degree', '').lower()
        required_degree = required_edu.get('degree', '').lower()
        
        # Exact match
        if candidate_degree == required_degree:
            return 1.0
        
        # Degree level matching
        degree_levels = {
            'phd': 4, 'doctorate': 4, 'ph.d': 4,
            'master': 3, 'mba': 3, 'ms': 3, 'ma': 3,
            'bachelor': 2, 'bs': 2, 'ba': 2, 'btech': 2,
            'associate': 1, 'diploma': 1, 'certificate': 1
        }
        
        candidate_level = 0
        required_level = 0
        
        for degree, level in degree_levels.items():
            if degree in candidate_degree:
                candidate_level = max(candidate_level, level)
            if degree in required_degree:
                required_level = max(required_level, level)
        
        if candidate_level >= required_level:
            return 0.8  # Higher or equal level
        else:
            return 0.3  # Lower level

    def _extract_education_requirements_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Extract education requirements from job description text"""
        education_reqs = []
        
        # Common education patterns
        patterns = [
            r'(bachelor|master|phd|doctorate|associate)\s+(of\s+)?(\w+\s*){1,3}',
            r'(b\.?s\.?|m\.?s\.?|ph\.?d\.?|m\.?b\.?a\.?)\s*(?:in\s+)?(\w+\s*){1,3}',
            r'degree\s+in\s+(\w+\s*){1,3}',
            r'(\w+)\s+degree\s+required'
        ]
        
        import re
        for pattern in patterns:
            matches = re.findall(pattern, text.lower(), re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    degree = ' '.join([part for part in match if part.strip()])
                else:
                    degree = match
                
                education_reqs.append({
                    'degree': degree.title(),
                    'required': True
                })
        
        return education_reqs

    def _extract_key_phrases(self, doc) -> List[str]:
        """Extract key phrases from job description"""
        key_phrases = []
        
        # Extract noun phrases
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) >= 2:  # Multi-word phrases
                key_phrases.append(chunk.text)
        
        # Extract important adjectives and nouns
        important_words = []
        for token in doc:
            if (token.pos_ in ['NOUN', 'ADJ'] and 
                not token.is_stop and 
                not token.is_punct and 
                len(token.text) > 3):
                important_words.append(token.text)
        
        return key_phrases[:10] + important_words[:10]  # Top 20 phrases/words

    def _extract_requirements_section(self, job_description: str) -> str:
        """Extract the requirements section from job description"""
        lines = job_description.split('\n')
        requirements_section = []
        in_requirements = False
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Start of requirements section
            if any(keyword in line_lower for keyword in ['requirements', 'qualifications', 'must have', 'should have']):
                in_requirements = True
                continue
            
            # End of requirements section
            if in_requirements and any(keyword in line_lower for keyword in ['responsibilities', 'duties', 'benefits', 'compensation']):
                break
            
            if in_requirements and line.strip():
                requirements_section.append(line.strip())
        
        return '\n'.join(requirements_section)

    def calculate_salary_match_score(self, candidate_expectation: float = None,
                                   job_min_salary: float = None,
                                   job_max_salary: float = None) -> Tuple[float, bool]:
        """Calculate salary compatibility score"""
        if candidate_expectation is None or (job_min_salary is None and job_max_salary is None):
            return 1.0, True  # No salary constraints

        if job_min_salary is not None and job_max_salary is not None:
            job_mid_salary = (job_min_salary + job_max_salary) / 2

            if job_min_salary <= candidate_expectation <= job_max_salary:
                return 1.0, True
            elif candidate_expectation < job_min_salary:
                # Candidate expects less than offered (good for employer)
                return 1.0, True
            else:
                # Candidate expects more than offered
                diff_ratio = (candidate_expectation - job_max_salary) / job_max_salary
                score = max(0.0, 1.0 - (diff_ratio * 2))
                return score, False

        return 1.0, True

    def match_candidate_to_jobs(self, candidate_data: Dict[str, Any], 
                              jobs: List[Dict[str, Any]], 
                              top_k: int = 10) -> List[JobMatch]:
        """
        Match a candidate to jobs and return ranked recommendations

        Args:
            candidate_data: Dictionary containing candidate information
            jobs: List of job dictionaries
            top_k: Number of top matches to return

        Returns:
            List of JobMatch objects sorted by match score
        """
        matches = []

        # Extract candidate information
        candidate_skills = candidate_data.get('skills', [])
        candidate_experience = candidate_data.get('experience_years')
        candidate_location = candidate_data.get('location', '')
        candidate_salary_expectation = candidate_data.get('salary_expectation')
        resume_text = candidate_data.get('resume_text', '')

        # Create candidate profile text for semantic similarity
        candidate_profile = self._create_candidate_profile_text(candidate_data)
        
        # Extract skills from resume text ONCE (expensive NLP operation)
        enhanced_candidate_skills = set(candidate_skills)
        if resume_text and nlp_service.nlp:
            extracted_skills = nlp_service.extract_skills(resume_text)
            enhanced_candidate_skills.update(extracted_skills)
            logger.warning(f"Extracted {len(extracted_skills)} additional skills from resume")

        for i, job in enumerate(jobs):
            try:
                # Skip inactive jobs
                if job.get('status', '').lower() != 'active':
                    continue

                # Calculate individual match components (using pre-extracted skills)
                skill_score, skill_matches, missing_skills = self.calculate_skill_match_score(
                    list(enhanced_candidate_skills),  # Use pre-extracted skills
                    job.get('required_skills', []),
                    job.get('preferred_skills', []),
                    "",  # No need to pass resume_text since skills are already extracted
                    use_enhanced_matching=True
                )

                experience_score, experience_match = self.calculate_experience_match_score(
                    candidate_experience,
                    job.get('min_experience_years'),
                    job.get('max_experience_years'),
                    resume_text
                )

                location_score, location_match = self.calculate_location_match_score(
                    candidate_location,
                    job.get('location', ''),
                    job.get('remote_work_allowed', 'No')
                )

                salary_score, salary_match = self.calculate_salary_match_score(
                    candidate_salary_expectation,
                    job.get('min_salary'),
                    job.get('max_salary')
                )

                # Enhanced semantic similarity using spaCy and ontology
                semantic_score = self.calculate_semantic_similarity_enhanced(
                    resume_text,
                    job.get('description', '')
                )

                # Calculate dynamic weights based on context
                dynamic_weights = weight_calculator.calculate_optimal_weights(
                    user_profile=candidate_data,
                    job_data=job,
                    market_context=None  # Could be passed from API
                )
                
                # Calculate weighted overall match score using dynamic weights
                overall_score = (
                    skill_score * dynamic_weights.skill_weight +
                    experience_score * dynamic_weights.experience_weight +
                    location_score * dynamic_weights.location_weight +
                    semantic_score * dynamic_weights.semantic_weight +
                    salary_score * dynamic_weights.salary_weight +
                    0.5 * dynamic_weights.market_demand_weight +  # Placeholder for market demand
                    0.5 * dynamic_weights.career_growth_weight    # Placeholder for career growth
                )

                # Generate match reasons
                match_reasons = self._generate_match_reasons(
                    skill_score, experience_match, location_match, 
                    salary_match, len(skill_matches), semantic_score
                )

                job_match = JobMatch(
                    job_id=job.get('id'),
                    match_score=overall_score,
                    skill_matches=skill_matches,
                    missing_skills=missing_skills,
                    match_reasons=match_reasons,
                    experience_match=experience_match,
                    location_match=location_match,
                    salary_match=salary_match
                )

                matches.append(job_match)
                logger.info(f"Added job match with score: {overall_score}")

            except Exception as e:
                logger.error(f"Error matching job {job.get('id')}: {e}")
                continue

        # Sort by match score and return top K
        matches.sort(key=lambda x: x.match_score, reverse=True)
        
        logger.info(f"\n=== JOB MATCHING COMPLETED ===")
        logger.info(f"Total matches generated: {len(matches)}")
        logger.info(f"Top 5 match scores: {[f'{m.job_id}: {m.match_score:.3f}' for m in matches[:5]]}")
        
        return matches[:top_k]

    def _create_candidate_profile_text(self, candidate_data: Dict[str, Any]) -> str:
        """Create a text representation of candidate profile for semantic matching"""
        profile_parts = []

        if candidate_data.get('skills'):
            profile_parts.append(f"Skills: {', '.join(candidate_data['skills'])}")

        if candidate_data.get('work_experience'):
            work_exp_texts = []
            for exp in candidate_data['work_experience']:
                exp_text = f"{exp.get('role', '')} at {exp.get('company', '')} - {exp.get('description', '')}"
                work_exp_texts.append(exp_text)
            profile_parts.append(f"Experience: {' '.join(work_exp_texts)}")

        if candidate_data.get('education'):
            edu_texts = [f"{edu.get('degree', '')} from {edu.get('institution', '')}" 
                        for edu in candidate_data['education']]
            profile_parts.append(f"Education: {' '.join(edu_texts)}")

        return ' '.join(profile_parts)

    def _generate_match_reasons(self, skill_score: float, experience_match: bool, 
                              location_match: bool, salary_match: bool, 
                              skill_match_count: int, semantic_score: float) -> List[str]:
        """Generate human-readable match reasons"""
        reasons = []

        if skill_score >= 0.8:
            reasons.append(f"Excellent skills match ({skill_match_count} matching skills)")
        elif skill_score >= 0.6:
            reasons.append(f"Good skills alignment ({skill_match_count} matching skills)")
        elif skill_score >= 0.4:
            reasons.append(f"Moderate skills match ({skill_match_count} matching skills)")

        if experience_match:
            reasons.append("Experience level matches requirements")

        if location_match:
            reasons.append("Location compatible")

        if salary_match:
            reasons.append("Salary expectations aligned")

        if semantic_score >= 0.3:
            reasons.append("Strong job description alignment")

        if not reasons:
            reasons.append("Basic compatibility found")

        return reasons

# Singleton instance
job_matcher = JobMatcherService()
