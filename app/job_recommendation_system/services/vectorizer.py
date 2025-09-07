"""
Vectorization service for consistent embedding pipeline
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False
    print("Warning: FAISS not available. Using fallback similarity search.")
import pickle
import os
from datetime import datetime

from config.settings import Config
from data.embeddings import SkillEmbeddings

logger = logging.getLogger(__name__)


class VectorizationService:
    """Consistent vectorization service with FAISS vector search"""
    
    def __init__(self, config: Config):
        self.config = config
        self.embeddings = SkillEmbeddings(config)
        
        # FAISS index for fast similarity search
        self.job_index = None
        self.resume_index = None
        self.job_ids = []  # Keep track of job IDs in index
        self.resume_ids = []  # Keep track of resume IDs in index
        
        # Fallback storage for embeddings
        self.job_embeddings = []  # Store embeddings for fallback search
        self.resume_embeddings = []  # Store embeddings for fallback search
        
        # Initialize FAISS indices
        self._initialize_faiss_indices()
        
        logger.info("VectorizationService initialized")
    
    def _initialize_faiss_indices(self):
        """Initialize FAISS indices for fast similarity search"""
        dimension = self.config.embedding_dimension
        
        if FAISS_AVAILABLE:
            # Use simple index for now (works well for smaller datasets)
            self.job_index = faiss.IndexFlatIP(dimension)
            self.resume_index = faiss.IndexFlatIP(dimension)
            logger.info(f"FAISS indices initialized - Job index: {type(self.job_index)}, Resume index: {type(self.resume_index)}")
        else:
            # Fallback: store embeddings in memory
            self.job_index = None
            self.resume_index = None
            logger.info("Using fallback similarity search (no FAISS)")
    
    def _create_consistent_text(self, data: Dict[str, Any], data_type: str) -> str:
        """
        Create consistent text representation for embedding
        
        Args:
            data: Job or resume data
            data_type: 'job' or 'resume'
            
        Returns:
            Consistent text string for embedding
        """
        if data_type == 'job':
            # Consistent job text: title + company + required_skills + preferred_skills + description
            title = data.get('job_title', '')
            company = data.get('company', '')
            required_skills = ' '.join(data.get('required_skills', []))
            preferred_skills = ' '.join(data.get('preferred_skills', []))
            description = data.get('description', '')
            
            # Structured format for consistency
            text_parts = [
                f"Job Title: {title}",
                f"Company: {company}",
                f"Required Skills: {required_skills}",
                f"Preferred Skills: {preferred_skills}",
                f"Description: {description}"
            ]
            
        elif data_type == 'resume':
            # Consistent resume text: name + current_role + skills + experience + description
            name = data.get('name', '')
            current_role = data.get('current_role', '')
            skills = ' '.join(data.get('skills', []))
            experience_years = str(data.get('experience_years', 0))
            resume_text = data.get('resume_text', '')
            
            # Structured format for consistency
            text_parts = [
                f"Name: {name}",
                f"Current Role: {current_role}",
                f"Skills: {skills}",
                f"Experience: {experience_years} years",
                f"Description: {resume_text}"
            ]
        
        else:
            raise ValueError(f"Invalid data_type: {data_type}")
        
        # Join with consistent separator
        return " | ".join(text_parts)
    
    def vectorize_job_description(self, job_data: Dict[str, Any]) -> 'JobVector':
        """
        Vectorize job description with consistent pipeline
        
        Args:
            job_data: Job description data
            
        Returns:
            JobVector object
        """
        try:
            # Create consistent text representation
            job_text = self._create_consistent_text(job_data, 'job')
            
            # Generate embedding using consistent pipeline
            job_embedding = self.embeddings.get_text_embedding(job_text)
            
            # Create JobVector object
            from models.database import JobVector
            job_vector = JobVector(
                job_id=job_data.get('id', f"job_{datetime.now().timestamp()}"),
                title=job_data.get('job_title', ''),
                company=job_data.get('company', ''),
                location=job_data.get('location', ''),
                title_embedding=job_embedding,  # Use consistent embedding
                description_embedding=job_embedding,  # Same embedding for consistency
                skills_embedding=job_embedding,  # Same embedding for consistency
                required_skills=job_data.get('required_skills', []),
                preferred_skills=job_data.get('preferred_skills', []),
                min_experience_years=job_data.get('min_experience_years', 0),
                max_experience_years=job_data.get('max_experience_years', 10),
                min_salary=job_data.get('min_salary', 0.0),
                max_salary=job_data.get('max_salary', 0.0),
                remote_work_allowed=job_data.get('remote_work_allowed', 'no'),
                status=job_data.get('status', 'active')
            )
            
            # Add to FAISS index for fast search
            self._add_to_job_index(job_vector)
            
            logger.info(f"Job vectorized successfully: {job_vector.job_id}")
            return job_vector
            
        except Exception as e:
            logger.error(f"Error vectorizing job: {e}")
            raise
    
    def vectorize_resume(self, candidate_data: Dict[str, Any]) -> 'ResumeVector':
        """
        Vectorize resume with consistent pipeline
        
        Args:
            candidate_data: Candidate resume data
            
        Returns:
            ResumeVector object
        """
        try:
            # Create consistent text representation
            resume_text = self._create_consistent_text(candidate_data, 'resume')
            
            # Generate embedding using consistent pipeline
            resume_embedding = self.embeddings.get_text_embedding(resume_text)
            
            # Create ResumeVector object
            from models.database import ResumeVector
            resume_vector = ResumeVector(
                candidate_id=candidate_data.get('id', f"candidate_{datetime.now().timestamp()}"),
                name=candidate_data.get('name', ''),
                email=candidate_data.get('email', ''),
                resume_embedding=resume_embedding,  # Use consistent embedding
                skills_embedding=resume_embedding,  # Same embedding for consistency
                experience_embedding=resume_embedding,  # Same embedding for consistency
                skills=candidate_data.get('skills', []),
                experience_years=candidate_data.get('experience_years', 0),
                current_role=candidate_data.get('current_role', ''),
                location=candidate_data.get('location', ''),
                salary_expectation=candidate_data.get('salary_expectation', 0.0),
                remote_preference=candidate_data.get('remote_preference', 0.0)
            )
            
            # Add to FAISS index for fast search
            self._add_to_resume_index(resume_vector)
            
            logger.info(f"Resume vectorized successfully: {resume_vector.candidate_id}")
            return resume_vector
            
        except Exception as e:
            logger.error(f"Error vectorizing resume: {e}")
            raise
    
    def _add_to_job_index(self, job_vector: 'JobVector'):
        """Add job vector to FAISS index or fallback storage"""
        try:
            if FAISS_AVAILABLE and self.job_index is not None:
                # Reshape embedding for FAISS (1, dimension)
                embedding = job_vector.description_embedding.reshape(1, -1).astype('float32')
                
                # Add to index
                self.job_index.add(embedding)
                self.job_ids.append(job_vector.job_id)
                
                logger.debug(f"Added job {job_vector.job_id} to FAISS index")
            else:
                # Fallback: store embedding in memory
                self.job_embeddings.append(job_vector.description_embedding)
                self.job_ids.append(job_vector.job_id)
                
                logger.debug(f"Added job {job_vector.job_id} to fallback storage")
            
        except Exception as e:
            logger.error(f"Error adding job to index: {e}")
            # Fallback: store embedding in memory
            self.job_embeddings.append(job_vector.description_embedding)
            self.job_ids.append(job_vector.job_id)
    
    def _add_to_resume_index(self, resume_vector: 'ResumeVector'):
        """Add resume vector to FAISS index or fallback storage"""
        try:
            if FAISS_AVAILABLE and self.resume_index is not None:
                # Reshape embedding for FAISS (1, dimension)
                embedding = resume_vector.resume_embedding.reshape(1, -1).astype('float32')
                
                # Add to index
                self.resume_index.add(embedding)
                self.resume_ids.append(resume_vector.candidate_id)
                
                logger.debug(f"Added resume {resume_vector.candidate_id} to FAISS index")
            else:
                # Fallback: store embedding in memory
                self.resume_embeddings.append(resume_vector.resume_embedding)
                self.resume_ids.append(resume_vector.candidate_id)
                
                logger.debug(f"Added resume {resume_vector.candidate_id} to fallback storage")
            
        except Exception as e:
            logger.error(f"Error adding resume to index: {e}")
            # Fallback: store embedding in memory
            self.resume_embeddings.append(resume_vector.resume_embedding)
            self.resume_ids.append(resume_vector.candidate_id)
    
    def search_similar_jobs_faiss(self, query_embedding: np.ndarray, limit: int = 10) -> List[tuple]:
        """
        Fast similarity search using FAISS or fallback
        
        Args:
            query_embedding: Query embedding
            limit: Maximum number of results
            
        Returns:
            List of (job_id, similarity_score) tuples
        """
        try:
            if FAISS_AVAILABLE and self.job_index is not None:
                # Reshape query embedding for FAISS
                query = query_embedding.reshape(1, -1).astype('float32')
                
                # Search FAISS index
                similarities, indices = self.job_index.search(query, min(limit, len(self.job_ids)))
                
                # Convert to results
                results = []
                for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                    if idx < len(self.job_ids):  # Valid index
                        job_id = self.job_ids[idx]
                        results.append((job_id, float(similarity)))
                
                logger.debug(f"FAISS job search returned {len(results)} results")
                return results
            else:
                # Fallback: manual similarity search
                return self._fallback_job_search(query_embedding, limit)
            
        except Exception as e:
            logger.error(f"Error in job search: {e}")
            # Fallback: manual similarity search
            return self._fallback_job_search(query_embedding, limit)
    
    def _fallback_job_search(self, query_embedding: np.ndarray, limit: int = 10) -> List[tuple]:
        """Fallback similarity search using manual cosine similarity"""
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            
            results = []
            for i, job_embedding in enumerate(self.job_embeddings):
                similarity = cosine_similarity([query_embedding], [job_embedding])[0][0]
                job_id = self.job_ids[i]
                results.append((job_id, float(similarity)))
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error in fallback job search: {e}")
            return []
    
    def search_similar_resumes_faiss(self, query_embedding: np.ndarray, limit: int = 10) -> List[tuple]:
        """
        Fast similarity search using FAISS or fallback
        
        Args:
            query_embedding: Query embedding
            limit: Maximum number of results
            
        Returns:
            List of (candidate_id, similarity_score) tuples
        """
        try:
            if FAISS_AVAILABLE and self.resume_index is not None:
                # Reshape query embedding for FAISS
                query = query_embedding.reshape(1, -1).astype('float32')
                
                # Search FAISS index
                similarities, indices = self.resume_index.search(query, min(limit, len(self.resume_ids)))
                
                # Convert to results
                results = []
                for i, (similarity, idx) in enumerate(zip(similarities[0], indices[0])):
                    if idx < len(self.resume_ids):  # Valid index
                        candidate_id = self.resume_ids[idx]
                        results.append((candidate_id, float(similarity)))
                
                logger.debug(f"FAISS resume search returned {len(results)} results")
                return results
            else:
                # Fallback: manual similarity search
                return self._fallback_resume_search(query_embedding, limit)
            
        except Exception as e:
            logger.error(f"Error in resume search: {e}")
            # Fallback: manual similarity search
            return self._fallback_resume_search(query_embedding, limit)
    
    def _fallback_resume_search(self, query_embedding: np.ndarray, limit: int = 10) -> List[tuple]:
        """Fallback similarity search using manual cosine similarity"""
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            
            results = []
            for i, resume_embedding in enumerate(self.resume_embeddings):
                similarity = cosine_similarity([query_embedding], [resume_embedding])[0][0]
                candidate_id = self.resume_ids[i]
                results.append((candidate_id, float(similarity)))
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"Error in fallback resume search: {e}")
            return []
    
    def batch_vectorize_jobs(self, jobs_data: List[Dict[str, Any]]) -> List['JobVector']:
        """
        Vectorize multiple job descriptions efficiently
        
        Args:
            jobs_data: List of job description data
            
        Returns:
            List of JobVector objects
        """
        job_vectors = []
        
        # Pre-load the embedding model once
        if self.embeddings.text_model is None:
            self.embeddings._load_text_model()
        
        logger.info(f"Starting batch vectorization of {len(jobs_data)} jobs")
        
        for i, job_data in enumerate(jobs_data):
            try:
                job_vector = self.vectorize_job_description(job_data)
                job_vectors.append(job_vector)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"Vectorized {i + 1}/{len(jobs_data)} jobs")
                    
            except Exception as e:
                logger.error(f"Error vectorizing job {i}: {e}")
                continue
        
        logger.info(f"Batch vectorization completed: {len(job_vectors)} jobs processed")
        return job_vectors
    
    def save_indices(self, filepath: str):
        """Save FAISS indices to disk"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Save FAISS indices
            faiss.write_index(self.job_index, f"{filepath}_jobs.faiss")
            faiss.write_index(self.resume_index, f"{filepath}_resumes.faiss")
            
            # Save ID mappings
            with open(f"{filepath}_ids.pkl", 'wb') as f:
                pickle.dump({
                    'job_ids': self.job_ids,
                    'resume_ids': self.resume_ids
                }, f)
            
            logger.info(f"FAISS indices saved to {filepath}")
            
        except Exception as e:
            logger.error(f"Error saving FAISS indices: {e}")
    
    def load_indices(self, filepath: str):
        """Load FAISS indices from disk"""
        try:
            # Load FAISS indices
            self.job_index = faiss.read_index(f"{filepath}_jobs.faiss")
            self.resume_index = faiss.read_index(f"{filepath}_resumes.faiss")
            
            # Load ID mappings
            with open(f"{filepath}_ids.pkl", 'rb') as f:
                id_data = pickle.load(f)
                self.job_ids = id_data['job_ids']
                self.resume_ids = id_data['resume_ids']
            
            logger.info(f"FAISS indices loaded from {filepath}")
            
        except Exception as e:
            logger.error(f"Error loading FAISS indices: {e}")
    
    def get_vectorization_stats(self) -> Dict[str, Any]:
        """Get vectorization statistics"""
        stats = {
            'embedding_cache': self.embeddings.get_cache_stats(),
            'embedding_model': self.config.embedding_model,
            'embedding_dimension': self.config.embedding_dimension,
            'faiss_job_index_size': len(self.job_ids),
            'faiss_resume_index_size': len(self.resume_ids),
        }
        
        if FAISS_AVAILABLE and self.job_index is not None:
            stats['faiss_job_index_type'] = type(self.job_index).__name__
            stats['faiss_resume_index_type'] = type(self.resume_index).__name__
        else:
            stats['faiss_job_index_type'] = 'Fallback'
            stats['faiss_resume_index_type'] = 'Fallback'
        
        return stats
