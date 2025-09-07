#!/usr/bin/env python3
"""
Skill Integrator - Integrates fetched skill datasets with existing ontology
"""

import json
import os
import sys
from typing import Dict, List, Any

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

class SkillIntegrator:
    """Integrates external skill datasets with existing ontology"""
    
    def __init__(self, data_dir: str = "skill_datasets"):
        self.data_dir = data_dir
        self.merged_skills_file = os.path.join(data_dir, "merged_skills.json")
    
    def load_merged_skills(self) -> Dict[str, Any]:
        """Load merged skills from file"""
        if not os.path.exists(self.merged_skills_file):
            print(f"❌ Merged skills file not found: {self.merged_skills_file}")
            print("Please run skill_datasets_fetcher.py first")
            return {}
        
        with open(self.merged_skills_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def integrate_with_ontology(self, ontology_service):
        """Integrate fetched skills with existing ontology"""
        print("🔄 Integrating fetched skills with existing ontology...")
        
        merged_skills = self.load_merged_skills()
        if not merged_skills:
            return
        
        # Add missing skills to ontology
        added_count = 0
        for skill_name, skill_data in merged_skills.items():
            if skill_name not in ontology_service.skills_graph:
                # Create new skill node
                from app.services.ontology_service import SkillNode
                
                skill_node = SkillNode(
                    name=skill_name.title(),
                    category=skill_data.get('category', 'general'),
                    synonyms=[],
                    related_skills=[],
                    difficulty_level=3,
                    industry_relevance={'technology': 0.5},
                    prerequisites=[],
                    learning_path=[]
                )
                
                ontology_service.skills_graph[skill_name] = skill_node
                added_count += 1
        
        print(f"✅ Added {added_count} new skills to ontology")
        print(f"Total skills in ontology: {len(ontology_service.skills_graph)}")

def main():
    """Main function"""
    integrator = SkillIntegrator()
    
    # Load existing ontology
    from app.services.ontology_service import ontology_service
    
    print("🚀 Starting Skill Integration...")
    integrator.integrate_with_ontology(ontology_service)
    print("✅ Integration completed!")

if __name__ == "__main__":
    main()
