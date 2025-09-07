#!/usr/bin/env python3
"""
Performance comparison between old and new recommendation systems
"""

import time
import logging
from typing import List, Dict, Any

from main import JobRecommendationSystem as OldSystem
from fast_recommendation_system import FastJobRecommendationSystem as NewSystem
from config.settings import Config

# Configure logging
logging.basicConfig(level=logging.WARNING)  # Reduce logging for cleaner output
logger = logging.getLogger(__name__)


def create_test_data(num_jobs: int = 10) -> tuple:
    """Create test data for performance comparison"""
    
    # Sample candidate data
    candidate_data = {
        'id': 'test_candidate',
        'name': 'John Doe',
        'email': 'john@example.com',
        'skills': ['Python', 'Machine Learning', 'SQL', 'Data Science', 'AWS'],
        'experience_years': 3,
        'current_role': 'Data Scientist',
        'location': 'San Francisco, CA',
        'salary_expectation': 120000.0,
        'remote_preference': 0.7,
        'resume_text': 'Experienced data scientist with expertise in Python, machine learning, and cloud computing. Led multiple ML projects and worked with large datasets.',
        'career_level': 2
    }
    
    # Create multiple jobs
    jobs_data = []
    for i in range(num_jobs):
        jobs_data.append({
            'id': f'job_{i}',
            'job_title': f'Data Scientist {i}',
            'company': f'Tech Company {i}',
            'description': f'We are looking for a data scientist to join our team. This role involves {i+1} years of experience in machine learning and data analysis.',
            'required_skills': ['Python', 'Machine Learning', 'SQL', 'Data Science'],
            'preferred_skills': ['AWS', 'Docker', 'Kubernetes'],
            'min_experience_years': 2,
            'max_experience_years': 5,
            'location': 'San Francisco, CA',
            'remote_work_allowed': 'hybrid',
            'min_salary': 100000.0,
            'max_salary': 150000.0,
            'status': 'active'
        })
    
    return candidate_data, jobs_data


def test_old_system(candidate_data: Dict[str, Any], jobs_data: List[Dict[str, Any]]) -> tuple:
    """Test the old recommendation system"""
    print("🔄 Testing OLD System (Real-time processing)...")
    
    # Initialize old system
    old_system = OldSystem()
    
    # Test timing
    start_time = time.time()
    
    # Get recommendations
    recommendations = old_system.recommend_jobs(candidate_data, jobs_data)
    
    processing_time = time.time() - start_time
    
    return len(recommendations), processing_time


def test_new_system(candidate_data: Dict[str, Any], jobs_data: List[Dict[str, Any]]) -> tuple:
    """Test the new recommendation system"""
    print("🚀 Testing NEW System (Vectorized database)...")
    
    # Initialize new system
    new_system = NewSystem()
    
    # Phase 1: Upload data (one-time cost)
    print("  📝 Uploading data...")
    upload_start = time.time()
    
    # Upload resume
    candidate_id = new_system.upload_resume(candidate_data)
    
    # Post jobs
    job_ids = []
    for job_data in jobs_data:
        job_id = new_system.post_job(job_data)
        job_ids.append(job_id)
    
    upload_time = time.time() - upload_start
    
    # Phase 2: Get recommendations (fast)
    print("  🔍 Getting recommendations...")
    search_start = time.time()
    
    recommendations = new_system.get_job_recommendations(candidate_id, limit=len(jobs_data))
    
    search_time = time.time() - search_start
    
    total_time = upload_time + search_time
    
    return len(recommendations), total_time, upload_time, search_time


def run_performance_comparison():
    """Run comprehensive performance comparison"""
    
    print("🏁 PERFORMANCE COMPARISON: Old vs New System")
    print("=" * 60)
    
    # Test with different dataset sizes
    test_sizes = [5, 10, 20, 50]
    
    results = []
    
    for num_jobs in test_sizes:
        print(f"\n📊 Testing with {num_jobs} jobs:")
        print("-" * 40)
        
        # Create test data
        candidate_data, jobs_data = create_test_data(num_jobs)
        
        # Test old system
        old_count, old_time = test_old_system(candidate_data, jobs_data)
        
        # Test new system
        new_count, new_total_time, upload_time, search_time = test_new_system(candidate_data, jobs_data)
        
        # Calculate improvement
        improvement = ((old_time - new_total_time) / old_time) * 100
        
        results.append({
            'num_jobs': num_jobs,
            'old_time': old_time,
            'new_total_time': new_total_time,
            'upload_time': upload_time,
            'search_time': search_time,
            'improvement': improvement,
            'old_count': old_count,
            'new_count': new_count
        })
        
        print(f"  📈 Results:")
        print(f"    Old System: {old_time:.2f}s ({old_count} matches)")
        print(f"    New System: {new_total_time:.2f}s ({new_count} matches)")
        print(f"      - Upload: {upload_time:.2f}s")
        print(f"      - Search: {search_time:.2f}s")
        print(f"    🚀 Improvement: {improvement:.1f}%")
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 SUMMARY")
    print("=" * 60)
    
    print(f"{'Jobs':<8} {'Old (s)':<10} {'New (s)':<10} {'Upload (s)':<12} {'Search (s)':<12} {'Improvement':<12}")
    print("-" * 70)
    
    for result in results:
        print(f"{result['num_jobs']:<8} {result['old_time']:<10.2f} {result['new_total_time']:<10.2f} "
              f"{result['upload_time']:<12.2f} {result['search_time']:<12.2f} {result['improvement']:<12.1f}%")
    
    # Key insights
    print("\n💡 KEY INSIGHTS:")
    print("• Old system: Processes everything in real-time (slow)")
    print("• New system: Vectorizes once, searches fast")
    print("• Upload time: One-time cost for data preparation")
    print("• Search time: Very fast vector similarity search")
    print("• Improvement: Gets better with more data")


def test_scalability():
    """Test scalability with larger datasets"""
    print("\n🔬 SCALABILITY TEST")
    print("=" * 40)
    
    # Test with larger dataset
    candidate_data, jobs_data = create_test_data(100)
    
    print("Testing NEW system with 100 jobs...")
    
    new_system = NewSystem()
    
    # Upload data
    print("📝 Uploading 100 jobs...")
    start_time = time.time()
    
    candidate_id = new_system.upload_resume(candidate_data)
    
    for job_data in jobs_data:
        new_system.post_job(job_data)
    
    upload_time = time.time() - start_time
    print(f"✅ Upload completed in {upload_time:.2f}s")
    
    # Test multiple searches
    print("🔍 Testing multiple searches...")
    search_times = []
    
    for i in range(5):
        start_time = time.time()
        recommendations = new_system.get_job_recommendations(candidate_id, limit=20)
        search_time = time.time() - start_time
        search_times.append(search_time)
        print(f"  Search {i+1}: {search_time:.3f}s ({len(recommendations)} results)")
    
    avg_search_time = sum(search_times) / len(search_times)
    print(f"\n📊 Average search time: {avg_search_time:.3f}s")
    print(f"📊 System can handle {100/avg_search_time:.0f} searches per second")


if __name__ == "__main__":
    run_performance_comparison()
    test_scalability()
