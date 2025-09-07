#!/usr/bin/env python3
"""
Test Runner for Job Recommendation Algorithm
Executes comprehensive tests for the recommendation system
"""

import sys
import os
import argparse
import time
from typing import List, Dict, Any

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def run_basic_tests():
    """Run basic functionality tests"""
    print("🧪 Running Basic Recommendation Tests...")
    print("=" * 50)
    
    try:
        from tests.test_job_recommendation_algorithm import TestJobRecommendationAlgorithm
        
        test_suite = TestJobRecommendationAlgorithm()
        success = test_suite.run_all_tests()
        
        return success
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed and paths are correct.")
        return False
    except Exception as e:
        print(f"❌ Test execution error: {e}")
        return False

def run_performance_tests():
    """Run performance-focused tests"""
    print("\n⚡ Running Performance Tests...")
    print("=" * 50)
    
    try:
        from services.job_matcher import JobMatcherService
        
        job_matcher = JobMatcherService()
        
        # Create test data
        candidate_data = {
            'skills': ['Python', 'Machine Learning', 'SQL', 'AWS', 'Docker'],
            'experience_years': 4,
            'location': 'San Francisco, CA',
            'salary_expectation': 95000,
            'resume_text': 'Experienced data scientist with ML expertise'
        }
        
        # Generate large job dataset
        large_job_list = []
        for i in range(1000):
            job = {
                'id': f'job_{i:04d}',
                'title': f'Data Scientist {i}',
                'company_name': f'Company {i}',
                'required_skills': ['Python', 'Machine Learning', 'SQL'],
                'preferred_skills': ['AWS', 'Docker'],
                'min_experience_years': 2,
                'max_experience_years': 6,
                'location': 'San Francisco, CA',
                'remote_work_allowed': 'hybrid',
                'min_salary': 80000,
                'max_salary': 120000,
                'status': 'active',
                'description': f'Data scientist position {i} with ML requirements'
            }
            large_job_list.append(job)
        
        # Test performance
        start_time = time.time()
        matches = job_matcher.match_candidate_to_jobs(candidate_data, large_job_list, top_k=20)
        end_time = time.time()
        
        processing_time = end_time - start_time
        jobs_per_second = len(large_job_list) / processing_time
        
        print(f"✅ Processed {len(large_job_list)} jobs in {processing_time:.2f} seconds")
        print(f"✅ Performance: {jobs_per_second:.0f} jobs/second")
        print(f"✅ Returned {len(matches)} top matches")
        
        # Performance benchmarks
        if processing_time < 5.0:
            print("🚀 Excellent performance!")
        elif processing_time < 10.0:
            print("✅ Good performance")
        else:
            print("⚠️  Performance could be improved")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False

def run_accuracy_tests():
    """Run accuracy and correctness tests"""
    print("\n🎯 Running Accuracy Tests...")
    print("=" * 50)
    
    try:
        from services.job_matcher import JobMatcherService
        
        job_matcher = JobMatcherService()
        
        # Test case 1: Perfect match
        candidate_perfect = {
            'skills': ['Python', 'Machine Learning', 'SQL', 'AWS'],
            'experience_years': 4,
            'location': 'San Francisco, CA',
            'salary_expectation': 100000
        }
        
        job_perfect = {
            'id': 'perfect_job',
            'required_skills': ['Python', 'Machine Learning', 'SQL'],
            'preferred_skills': ['AWS'],
            'min_experience_years': 3,
            'max_experience_years': 5,
            'location': 'San Francisco, CA',
            'remote_work_allowed': 'no',
            'min_salary': 90000,
            'max_salary': 110000,
            'status': 'active',
            'description': 'Python ML developer position'
        }
        
        matches = job_matcher.match_candidate_to_jobs(candidate_perfect, [job_perfect])
        
        if matches and matches[0].match_score > 0.8:
            print("✅ Perfect match test passed")
        else:
            print("❌ Perfect match test failed")
            return False
        
        # Test case 2: Poor match
        candidate_poor = {
            'skills': ['JavaScript', 'React'],
            'experience_years': 1,
            'location': 'New York, NY',
            'salary_expectation': 50000
        }
        
        matches = job_matcher.match_candidate_to_jobs(candidate_poor, [job_perfect])
        
        if not matches or matches[0].match_score < 0.3:
            print("✅ Poor match test passed")
        else:
            print("❌ Poor match test failed")
            return False
        
        # Test case 3: Edge case - no skills
        candidate_no_skills = {
            'skills': [],
            'experience_years': 0,
            'location': '',
            'salary_expectation': None
        }
        
        matches = job_matcher.match_candidate_to_jobs(candidate_no_skills, [job_perfect])
        
        if matches and matches[0].match_score >= 0.0:
            print("✅ No skills edge case handled")
        else:
            print("❌ No skills edge case failed")
            return False
        
        print("🎯 All accuracy tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Accuracy test error: {e}")
        return False

def run_integration_tests():
    """Run integration tests with real data"""
    print("\n🔗 Running Integration Tests...")
    print("=" * 50)
    
    try:
        from services.job_matcher import JobMatcherService
        
        job_matcher = JobMatcherService()
        
        # Real-world candidate profile
        real_candidate = {
            'id': 'real_candidate_001',
            'name': 'Alex Johnson',
            'skills': ['Python', 'Machine Learning', 'Deep Learning', 'TensorFlow', 'PyTorch', 'SQL', 'AWS', 'Docker', 'Kubernetes'],
            'experience_years': 5,
            'current_role': 'Senior ML Engineer',
            'location': 'Seattle, WA',
            'salary_expectation': 120000,
            'remote_preference': 0.6,
            'resume_text': '''
            Senior Machine Learning Engineer with 5+ years of experience in developing 
            and deploying ML models at scale. Expertise in Python, TensorFlow, PyTorch, 
            and cloud platforms. Strong background in deep learning, computer vision, 
            and natural language processing. Experience with MLOps and model deployment 
            using Docker and Kubernetes.
            ''',
            'work_experience': [
                {
                    'role': 'Senior ML Engineer',
                    'company': 'TechGiant',
                    'duration': '2 years',
                    'description': 'Led ML model development and deployment for recommendation systems'
                },
                {
                    'role': 'ML Engineer',
                    'company': 'StartupAI',
                    'duration': '3 years',
                    'description': 'Developed computer vision models and NLP solutions'
                }
            ],
            'education': [
                {
                    'degree': 'Master of Science',
                    'field': 'Artificial Intelligence',
                    'institution': 'Carnegie Mellon University'
                }
            ]
        }
        
        # Real-world job listings
        real_jobs = [
            {
                'id': 'real_job_001',
                'title': 'Senior Machine Learning Engineer',
                'company_name': 'TechGiant',
                'required_skills': ['Python', 'Machine Learning', 'TensorFlow', 'AWS'],
                'preferred_skills': ['PyTorch', 'Docker', 'Kubernetes', 'MLOps'],
                'min_experience_years': 4,
                'max_experience_years': 7,
                'location': 'Seattle, WA',
                'remote_work_allowed': 'hybrid',
                'min_salary': 110000,
                'max_salary': 150000,
                'status': 'active',
                'description': '''
                We're looking for a Senior Machine Learning Engineer to join our AI team. 
                You'll work on cutting-edge ML models and deploy them at scale. 
                Strong Python, TensorFlow, and cloud experience required.
                '''
            },
            {
                'id': 'real_job_002',
                'title': 'ML Research Scientist',
                'company_name': 'ResearchLab',
                'required_skills': ['Python', 'Deep Learning', 'PyTorch', 'Research'],
                'preferred_skills': ['Computer Vision', 'NLP', 'Publications'],
                'min_experience_years': 3,
                'max_experience_years': 6,
                'location': 'Remote',
                'remote_work_allowed': 'yes',
                'min_salary': 100000,
                'max_salary': 140000,
                'status': 'active',
                'description': '''
                Join our research team as an ML Research Scientist. Focus on deep learning 
                research, computer vision, and NLP. Strong PyTorch and research background required.
                '''
            },
            {
                'id': 'real_job_003',
                'title': 'Data Scientist',
                'company_name': 'FinanceCorp',
                'required_skills': ['Python', 'SQL', 'Statistics', 'Machine Learning'],
                'preferred_skills': ['R', 'Tableau', 'Finance'],
                'min_experience_years': 2,
                'max_experience_years': 5,
                'location': 'New York, NY',
                'remote_work_allowed': 'no',
                'min_salary': 80000,
                'max_salary': 120000,
                'status': 'active',
                'description': '''
                Data Scientist position in financial services. Strong Python, SQL, 
                and statistical analysis skills required. Finance experience preferred.
                '''
            }
        ]
        
        # Run matching
        matches = job_matcher.match_candidate_to_jobs(real_candidate, real_jobs, top_k=3)
        
        print(f"✅ Processed {len(real_jobs)} real-world jobs")
        print(f"✅ Generated {len(matches)} recommendations")
        
        # Analyze results
        for i, match in enumerate(matches, 1):
            print(f"\n#{i} Job: {match.job_id}")
            print(f"   Match Score: {match.match_score:.3f}")
            print(f"   Skill Matches: {len(match.skill_matches)}")
            print(f"   Missing Skills: {len(match.missing_skills)}")
            print(f"   Experience Match: {match.experience_match}")
            print(f"   Location Match: {match.location_match}")
            print(f"   Salary Match: {match.salary_match}")
            if match.match_reasons:
                print(f"   Reasons: {', '.join(match.match_reasons[:2])}")
        
        # Validate results make sense
        if matches and matches[0].match_score > 0.7:
            print("\n🎯 Integration test passed - high-quality matches generated")
            return True
        else:
            print("\n⚠️  Integration test - matches seem low quality")
            return False
        
    except Exception as e:
        print(f"❌ Integration test error: {e}")
        return False

def generate_test_report(results: Dict[str, bool]):
    """Generate a comprehensive test report"""
    print("\n" + "=" * 60)
    print("📊 COMPREHENSIVE TEST REPORT")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    failed_tests = total_tests - passed_tests
    
    print(f"Total Test Suites: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\nDetailed Results:")
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED! The recommendation algorithm is working correctly.")
    else:
        print(f"\n⚠️  {failed_tests} test suite(s) failed. Please review the errors above.")
    
    return failed_tests == 0

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='Run Job Recommendation Algorithm Tests')
    parser.add_argument('--test-type', choices=['all', 'basic', 'performance', 'accuracy', 'integration'], 
                       default='all', help='Type of tests to run')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    print("🚀 Job Recommendation Algorithm Test Suite")
    print("=" * 60)
    
    results = {}
    
    if args.test_type in ['all', 'basic']:
        results['Basic Functionality'] = run_basic_tests()
    
    if args.test_type in ['all', 'performance']:
        results['Performance'] = run_performance_tests()
    
    if args.test_type in ['all', 'accuracy']:
        results['Accuracy'] = run_accuracy_tests()
    
    if args.test_type in ['all', 'integration']:
        results['Integration'] = run_integration_tests()
    
    # Generate final report
    success = generate_test_report(results)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
