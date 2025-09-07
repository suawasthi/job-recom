#!/usr/bin/env python3
"""
SkillNer Integration - Uses SkillNer library for advanced skill extraction
"""

import sys
import os
from typing import List, Dict, Any

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

class SkillNerIntegration:
    """Integration with SkillNer library for advanced skill extraction"""
    
    def __init__(self):
        self.skill_extractor = None
        self.nlp = None
        self._initialize_skillner()
    
    def _initialize_skillner(self):
        """Initialize SkillNer"""
        try:
            import spacy
            from spacy.matcher import PhraseMatcher
            from skillNer.general_params import SKILL_DB
            from skillNer.skill_extractor_class import SkillExtractor
            
            print("🔄 Initializing SkillNer...")
            
            # Load spaCy model
            self.nlp = spacy.load("en_core_web_lg")
            
            # Initialize SkillExtractor
            self.skill_extractor = SkillExtractor(self.nlp, SKILL_DB, PhraseMatcher)
            
            print("✅ SkillNer initialized successfully!")
            
        except ImportError as e:
            print(f"❌ SkillNer not installed: {e}")
            print("📦 Install with: pip install skillNer")
            print("📦 Also install: python -m spacy download en_core_web_lg")
        except Exception as e:
            print(f"❌ Error initializing SkillNer: {e}")
    
    def extract_skills(self, text: str) -> List[Dict[str, Any]]:
        """Extract skills using SkillNer"""
        if not self.skill_extractor:
            print("❌ SkillNer not initialized")
            return []
        
        try:
            # Process text
            doc = self.nlp(text)
            annotations = self.skill_extractor.annotate(doc)
            
            # Extract skills
            skills = []
            for skill in annotations.get('results', {}).get('full_matches', []):
                skills.append({
                    'skill': skill.get('doc_node_value', ''),
                    'confidence': skill.get('score', 0.0),
                    'start': skill.get('start', 0),
                    'end': skill.get('end', 0)
                })
            
            return skills
            
        except Exception as e:
            print(f"❌ Error extracting skills: {e}")
            return []
    
    def extract_skills_simple(self, text: str) -> List[str]:
        """Extract skills as simple list"""
        skills_data = self.extract_skills(text)
        return [skill['skill'] for skill in skills_data if skill['skill']]

def test_skillner():
    """Test SkillNer integration"""
    print("🧪 Testing SkillNer Integration...")
    
    skillner = SkillNerIntegration()
    
    if not skillner.skill_extractor:
        print("❌ Cannot test - SkillNer not initialized")
        return
    
    # Test text
    test_text = """
    I am a Python developer with experience in:
    - Python programming
    - Django and Flask web frameworks
    - AWS cloud services (EC2, S3, Lambda)
    - Docker containerization
    - MySQL and PostgreSQL databases
    - Machine learning with scikit-learn
    - Git version control
    """
    
    print(f"📝 Test text: {test_text[:100]}...")
    
    # Extract skills
    skills = skillner.extract_skills_simple(test_text)
    
    print(f"🎯 Extracted skills: {skills}")
    print(f"📊 Total skills found: {len(skills)}")

def main():
    """Main function"""
    print("🚀 Starting SkillNer Integration...")
    test_skillner()

if __name__ == "__main__":
    main()
