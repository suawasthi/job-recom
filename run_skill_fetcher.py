#!/usr/bin/env python3
"""
Run Skill Datasets Fetcher
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def main():
    """Main function"""
    print("🚀 Starting Skill Datasets Fetcher...")
    
    try:
        from skill_datasets_fetcher import SkillDatasetsFetcher
        
        fetcher = SkillDatasetsFetcher()
        all_data = fetcher.fetch_all_datasets()
        
        print("\n✅ Successfully fetched skill datasets!")
        print(f"📁 Data saved to: {fetcher.data_dir}")
        
        # Show summary
        if 'merged_skills' in all_data:
            print(f"📊 Total unique skills: {len(all_data['merged_skills'])}")
        
        # Ask if user wants to integrate
        integrate = input("\n🔄 Do you want to integrate these skills with the existing ontology? (y/n): ").strip().lower()
        
        if integrate == 'y':
            from skill_integrator import SkillIntegrator
            integrator = SkillIntegrator()
            
            from app.services.ontology_service import ontology_service
            integrator.integrate_with_ontology(ontology_service)
            
            print("✅ Integration completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
