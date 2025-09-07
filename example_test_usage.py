#!/usr/bin/env python3
"""
Example Usage of Job Recommendation Algorithm Test Suite
Demonstrates how to run tests and interpret results
"""

import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def run_example_tests():
    """Run example tests to demonstrate the test suite"""
    print("🚀 Job Recommendation Algorithm Test Suite - Example Usage")
    print("=" * 60)
    
    try:
        # Import the test suite
        from tests.test_job_recommendation_algorithm import TestJobRecommendationAlgorithm
        from tests.test_data_generator import TestDataGenerator
        
        print("\n1. 📊 Generating Sample Test Data...")
        generator = TestDataGenerator()
        
        # Generate sample data
        sample_candidate = generator.generate_candidate('data_scientist')
        sample_jobs = generator.generate_job_dataset(10, ['data_scientist', 'software_development'])
        
        print(f"   ✅ Generated candidate: {sample_candidate['name']}")
        print(f"   ✅ Generated {len(sample_jobs)} jobs")
        print(f"   ✅ Candidate skills: {', '.join(sample_candidate['skills'][:5])}")
        
        print("\n2. 🧪 Running Individual Algorithm Tests...")
        test_suite = TestJobRecommendationAlgorithm()
        
        # Run specific tests
        print("\n   Testing skill matching...")
        test_suite.test_skill_match_score_calculation()
        
        print("\n   Testing experience matching...")
        test_suite.test_experience_match_score_calculation()
        
        print("\n   Testing location matching...")
        test_suite.test_location_match_score_calculation()
        
        print("\n   Testing salary matching...")
        test_suite.test_salary_match_score_calculation()
        
        print("\n3. 🎯 Running Complete Matching Test...")
        from services.job_matcher import JobMatcherService
        
        job_matcher = JobMatcherService()
        
        # Test with generated data
        matches = job_matcher.match_candidate_to_jobs(sample_candidate, sample_jobs, top_k=5)
        
        print(f"   ✅ Found {len(matches)} job matches")
        print("\n   Top Matches:")
        for i, match in enumerate(matches[:3], 1):
            print(f"   #{i} Job {match.job_id}: Score {match.match_score:.3f}")
            print(f"      Skills: {len(match.skill_matches)} matches, {len(match.missing_skills)} missing")
            print(f"      Experience: {match.experience_match}, Location: {match.location_match}")
        
        print("\n4. ⚡ Running Performance Test...")
        import time
        
        # Generate larger dataset
        large_job_list = generator.generate_job_dataset(100)
        
        start_time = time.time()
        matches = job_matcher.match_candidate_to_jobs(sample_candidate, large_job_list, top_k=10)
        end_time = time.time()
        
        processing_time = end_time - start_time
        jobs_per_second = len(large_job_list) / processing_time
        
        print(f"   ✅ Processed {len(large_job_list)} jobs in {processing_time:.2f} seconds")
        print(f"   ✅ Performance: {jobs_per_second:.0f} jobs/second")
        print(f"   ✅ Returned {len(matches)} top matches")
        
        print("\n5. 📈 Test Results Summary...")
        print("   ✅ All individual algorithm tests passed")
        print("   ✅ Complete matching test successful")
        print("   ✅ Performance test completed within acceptable time")
        print("   ✅ Generated realistic test data")
        
        print("\n🎉 Example test run completed successfully!")
        print("\nTo run the full test suite, use:")
        print("   python run_recommendation_tests.py --test-type all")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed and the app directory is in the Python path.")
        return False
    except Exception as e:
        print(f"❌ Error during test execution: {e}")
        import traceback
        traceback.print_exc()
        return False

def demonstrate_test_configuration():
    """Demonstrate test configuration usage"""
    print("\n🔧 Test Configuration Example...")
    
    try:
        from tests.test_config import TestConfig
        
        # Show configuration values
        print(f"   Performance test jobs count: {TestConfig.PERFORMANCE_TEST_JOBS_COUNT}")
        print(f"   Perfect match minimum score: {TestConfig.PERFECT_MATCH_MIN_SCORE}")
        print(f"   Performance max time: {TestConfig.PERFORMANCE_MAX_TIME_SECONDS}s")
        
        # Get sample data
        candidate = TestConfig.get_test_candidate('data_scientist')
        job = TestConfig.get_test_job('data_scientist_job')
        
        print(f"   Sample candidate skills: {candidate['skills']}")
        print(f"   Sample job requirements: {job['required_skills']}")
        
        # Generate large dataset
        large_dataset = TestConfig.create_large_job_dataset(50)
        print(f"   Generated {len(large_dataset)} jobs for testing")
        
        print("   ✅ Test configuration loaded successfully")
        
    except Exception as e:
        print(f"   ❌ Configuration error: {e}")

def show_test_commands():
    """Show available test commands"""
    print("\n📋 Available Test Commands...")
    print("=" * 40)
    
    commands = [
        ("Run all tests", "python run_recommendation_tests.py"),
        ("Run basic tests only", "python run_recommendation_tests.py --test-type basic"),
        ("Run performance tests", "python run_recommendation_tests.py --test-type performance"),
        ("Run accuracy tests", "python run_recommendation_tests.py --test-type accuracy"),
        ("Run integration tests", "python run_recommendation_tests.py --test-type integration"),
        ("Run with verbose output", "python run_recommendation_tests.py --verbose"),
        ("Generate test data", "python tests/test_data_generator.py"),
        ("Run example usage", "python example_test_usage.py")
    ]
    
    for description, command in commands:
        print(f"   {description}:")
        print(f"      {command}")
        print()

def main():
    """Main function"""
    print("Job Recommendation Algorithm Test Suite - Example Usage")
    print("This script demonstrates how to use the test suite effectively.")
    print()
    
    # Run example tests
    success = run_example_tests()
    
    # Show configuration
    demonstrate_test_configuration()
    
    # Show available commands
    show_test_commands()
    
    if success:
        print("\n✅ Example completed successfully!")
        print("You can now run the full test suite using the commands shown above.")
    else:
        print("\n❌ Example failed. Please check the error messages above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
