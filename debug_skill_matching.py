#!/usr/bin/env python3
"""
Dynamic Debug skill matching to understand skill matching behavior
"""

import sys
import os
import json

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Configure logging
import logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

class SkillMatchingDebugger:
    """Dynamic skill matching debugger"""
    
    def __init__(self):
        from app.services.job_matcher import job_matcher
        from app.services.ontology_service import ontology_service
        self.job_matcher = job_matcher
        self.ontology_service = ontology_service
    
    def debug_skill_matching(self, candidate_skills, job_required_skills, test_name="Custom Test"):
        """Debug the skill matching process with dynamic inputs"""
        print(f"\n=== {test_name.upper()} ===")
        print(f"Candidate skills: {candidate_skills}")
        print(f"Job required skills: {job_required_skills}")
        print("\n" + "="*50)
        
        # Test the enhanced skill matching
        matches = self.job_matcher._find_enhanced_skill_matches(candidate_skills, job_required_skills)
        
        print(f"\nFinal matches: {matches}")
        
        # Check ontology nodes for each skill
        print(f"\n=== ONTOLOGY NODES ===")
        all_skills = list(set(candidate_skills + job_required_skills))
        for skill in all_skills:
            skill_node = self.ontology_service.skills_graph.get(skill.lower())
            if skill_node:
                print(f"  {skill}: category='{skill_node.category}', related_skills={skill_node.related_skills[:5]}")
            else:
                print(f"  {skill}: NO ONTOLOGY NODE FOUND")
        
        return matches
    
    def test_similarity_matrix(self, skills_list, reference_skill=None):
        """Test similarity between skills"""
        print(f"\n=== SIMILARITY MATRIX ===")
        if reference_skill:
            print(f"Testing similarities with reference skill: {reference_skill}")
            similarities = []
            for skill in skills_list:
                if skill != reference_skill:
                    similarity = self.ontology_service.get_skill_similarity(reference_skill, skill)
                    similarities.append((skill, similarity))
                    print(f"  {reference_skill} <-> {skill}: {similarity}")
            
            # Check threshold
            print(f"\n=== THRESHOLD CHECK (0.7) ===")
            for skill, similarity in similarities:
                if similarity > 0.7:
                    print(f"  WARNING: {skill} has similarity {similarity} > 0.7 with {reference_skill}")
        else:
            # Full matrix
            for i, skill1 in enumerate(skills_list):
                for skill2 in skills_list[i+1:]:
                    similarity = self.ontology_service.get_skill_similarity(skill1, skill2)
                    print(f"  {skill1} <-> {skill2}: {similarity}")
    
    def run_preset_tests(self):
        """Run predefined test scenarios"""
        test_scenarios = [
            {
                "name": "AWS Only Candidate",
                "candidate_skills": ["aws"],
                "job_required_skills": ["spring boot", "css", "mysql", "docker", "python", "java",  "lambda", "s3", "ec2", "rds", "dynamodb", "cloudformation", "cloudwatch", "iam", "vpc", "route53", "sns", "sqs", "api gateway", "elastic beanstalk", "ecs", "eks", "fargate"    ]
            }
           
        ]
        
        for scenario in test_scenarios:
            self.debug_skill_matching(
                scenario["candidate_skills"],
                scenario["job_required_skills"],
                scenario["name"]
            )
            print("\n" + "="*80 + "\n")
    
    def interactive_test(self):
        """Interactive test mode"""
        print("\n=== INTERACTIVE SKILL MATCHING TEST ===")
        
        while True:
            print("\nOptions:")
            print("1. Test skill matching")
            print("2. Test similarity matrix")
            print("3. Run preset tests")
            print("4. Exit")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                candidate_input = input("Enter candidate skills (comma-separated): ").strip()
                job_input = input("Enter job required skills (comma-separated): ").strip()
                test_name = input("Enter test name (optional): ").strip() or "Custom Test"
                
                candidate_skills = [s.strip().lower() for s in candidate_input.split(",") if s.strip()]
                job_required_skills = [s.strip().lower() for s in job_input.split(",") if s.strip()]
                
                self.debug_skill_matching(candidate_skills, job_required_skills, test_name)
                
            elif choice == "2":
                skills_input = input("Enter skills for similarity test (comma-separated): ").strip()
                reference_skill = input("Enter reference skill (optional, for matrix use all skills): ").strip() or None
                
                skills_list = [s.strip().lower() for s in skills_input.split(",") if s.strip()]
                self.test_similarity_matrix(skills_list, reference_skill)
                
            elif choice == "3":
                self.run_preset_tests()
                
            elif choice == "4":
                print("Exiting...")
                break
                
            else:
                print("Invalid choice. Please try again.")

def main():
    """Main function"""
    print("Starting Dynamic Skill Matching Debugger...")
    
    debugger = SkillMatchingDebugger()
    
    # Check if command line arguments are provided
    if len(sys.argv) > 1:
        if sys.argv[1] == "--preset":
            debugger.run_preset_tests()
        elif sys.argv[1] == "--interactive":
            debugger.interactive_test()
        else:
            print("Usage: python debug_skill_matching.py [--preset|--interactive]")
    else:
        # Default: run preset tests
        debugger.run_preset_tests()

if __name__ == "__main__":
    main()
