#!/usr/bin/env python3
"""
Skill Datasets Fetcher - Downloads and integrates various skill databases
"""

import requests
import pandas as pd
import json
import os
import sys
from typing import Dict, List, Any, Optional
import logging

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SkillDatasetsFetcher:
    """Fetches and integrates various skill datasets"""
    
    def __init__(self, data_dir: str = "skill_datasets"):
        self.data_dir = data_dir
        self.ensure_data_dir()
        
    def ensure_data_dir(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"Created data directory: {self.data_dir}")
    
    def fetch_onet_database(self) -> Dict[str, Any]:
        """Fetch O*NET database (most comprehensive skills database)"""
        logger.info("Fetching O*NET database...")
        
        # O*NET database URLs (these are the actual download links)
        onet_urls = {
            'skills': 'https://www.onetcenter.org/database/2024.3/db_28_3_excel/Skills.xlsx',
            'knowledge': 'https://www.onetcenter.org/database/2024.3/db_28_3_excel/Knowledge.xlsx',
            'abilities': 'https://www.onetcenter.org/database/2024.3/db_28_3_excel/Abilities.xlsx',
            'occupations': 'https://www.onetcenter.org/database/2024.3/db_28_3_excel/Occupation Data.xlsx'
        }
        
        onet_data = {}
        
        for data_type, url in onet_urls.items():
            try:
                logger.info(f"Downloading {data_type} from O*NET...")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # Save to file
                file_path = os.path.join(self.data_dir, f"onet_{data_type}.xlsx")
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                # Load into pandas
                df = pd.read_excel(file_path)
                onet_data[data_type] = df
                logger.info(f"Successfully downloaded {data_type}: {len(df)} records")
                
            except Exception as e:
                logger.error(f"Failed to download {data_type}: {e}")
        
        return onet_data
    
    def fetch_stackoverflow_survey(self) -> Dict[str, Any]:
        """Fetch Stack Overflow Developer Survey data"""
        logger.info("Fetching Stack Overflow Developer Survey...")
        
        # Stack Overflow survey URLs (2023 data)
        so_urls = {
            'survey_results': 'https://info.stackoverflowsolutions.com/rs/719-EMH-566/images/stack-overflow-developer-survey-2023.zip'
        }
        
        so_data = {}
        
        for data_type, url in so_urls.items():
            try:
                logger.info(f"Downloading {data_type} from Stack Overflow...")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # Save to file
                file_path = os.path.join(self.data_dir, f"stackoverflow_{data_type}.zip")
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Successfully downloaded {data_type}")
                
            except Exception as e:
                logger.error(f"Failed to download {data_type}: {e}")
        
        return so_data
    
    def fetch_esco_skills(self) -> Dict[str, Any]:
        """Fetch ESCO (European Skills, Competences, Qualifications and Occupations) database"""
        logger.info("Fetching ESCO skills database...")
        
        # ESCO API endpoints
        esco_urls = {
            'skills': 'https://ec.europa.eu/esco/api/resource/skill?language=en&type=http://data.europa.eu/esco/model#Skill',
            'occupations': 'https://ec.europa.eu/esco/api/resource/occupation?language=en'
        }
        
        esco_data = {}
        
        for data_type, url in esco_urls.items():
            try:
                logger.info(f"Downloading {data_type} from ESCO...")
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                esco_data[data_type] = data
                
                # Save to file
                file_path = os.path.join(self.data_dir, f"esco_{data_type}.json")
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Successfully downloaded {data_type}: {len(data.get('_embedded', {}).get('items', []))} records")
                
            except Exception as e:
                logger.error(f"Failed to download {data_type}: {e}")
        
        return esco_data
    
    def fetch_github_skills(self) -> Dict[str, Any]:
        """Fetch GitHub skills from trending repositories and languages"""
        logger.info("Fetching GitHub skills data...")
        
        # GitHub API endpoints
        github_urls = {
            'trending_repos': 'https://api.github.com/search/repositories?q=stars:>1000&sort=stars&order=desc&per_page=100',
            'languages': 'https://api.github.com/languages'
        }
        
        github_data = {}
        
        for data_type, url in github_urls.items():
            try:
                logger.info(f"Downloading {data_type} from GitHub...")
                headers = {'Accept': 'application/vnd.github.v3+json'}
                response = requests.get(url, headers=headers, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                github_data[data_type] = data
                
                # Save to file
                file_path = os.path.join(self.data_dir, f"github_{data_type}.json")
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Successfully downloaded {data_type}")
                
            except Exception as e:
                logger.error(f"Failed to download {data_type}: {e}")
        
        return github_data
    
    def process_onet_skills(self, onet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process O*NET skills data into our format"""
        logger.info("Processing O*NET skills data...")
        
        if 'skills' not in onet_data:
            logger.error("No skills data found in O*NET data")
            return {}
        
        skills_df = onet_data['skills']
        processed_skills = {}
        
        for _, row in skills_df.iterrows():
            skill_name = row.get('Element Name', '').lower().strip()
            skill_id = row.get('Element ID', '')
            skill_category = row.get('Domain', '')
            skill_description = row.get('Description', '')
            
            if skill_name:
                processed_skills[skill_name] = {
                    'id': skill_id,
                    'category': skill_category,
                    'description': skill_description,
                    'source': 'onet'
                }
        
        logger.info(f"Processed {len(processed_skills)} skills from O*NET")
        return processed_skills
    
    def process_esco_skills(self, esco_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process ESCO skills data into our format"""
        logger.info("Processing ESCO skills data...")
        
        if 'skills' not in esco_data:
            logger.error("No skills data found in ESCO data")
            return {}
        
        skills_data = esco_data['skills']
        processed_skills = {}
        
        items = skills_data.get('_embedded', {}).get('items', [])
        
        for item in items:
            skill_name = item.get('preferredLabel', '').lower().strip()
            skill_id = item.get('uri', '')
            skill_description = item.get('description', '')
            
            if skill_name:
                processed_skills[skill_name] = {
                    'id': skill_id,
                    'category': 'esco',
                    'description': skill_description,
                    'source': 'esco'
                }
        
        logger.info(f"Processed {len(processed_skills)} skills from ESCO")
        return processed_skills
    
    def merge_skill_databases(self, *skill_databases) -> Dict[str, Any]:
        """Merge multiple skill databases"""
        logger.info("Merging skill databases...")
        
        merged_skills = {}
        
        for db_name, skills in skill_databases:
            for skill_name, skill_data in skills.items():
                if skill_name in merged_skills:
                    # Merge data from multiple sources
                    merged_skills[skill_name]['sources'].append(skill_data['source'])
                    merged_skills[skill_name]['descriptions'].append(skill_data['description'])
                else:
                    merged_skills[skill_name] = {
                        'id': skill_data.get('id', ''),
                        'category': skill_data.get('category', ''),
                        'sources': [skill_data['source']],
                        'descriptions': [skill_data['description']],
                        'source': skill_data['source']
                    }
        
        logger.info(f"Merged {len(merged_skills)} unique skills from all databases")
        return merged_skills
    
    def save_merged_skills(self, merged_skills: Dict[str, Any], filename: str = "merged_skills.json"):
        """Save merged skills to file"""
        file_path = os.path.join(self.data_dir, filename)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(merged_skills, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved merged skills to {file_path}")
    
    def fetch_all_datasets(self) -> Dict[str, Any]:
        """Fetch all available skill datasets"""
        logger.info("Starting to fetch all skill datasets...")
        
        all_data = {}
        
        # Fetch O*NET database
        try:
            onet_data = self.fetch_onet_database()
            all_data['onet'] = onet_data
        except Exception as e:
            logger.error(f"Failed to fetch O*NET data: {e}")
        
        # Fetch ESCO skills
        try:
            esco_data = self.fetch_esco_skills()
            all_data['esco'] = esco_data
        except Exception as e:
            logger.error(f"Failed to fetch ESCO data: {e}")
        
        # Fetch GitHub data
        try:
            github_data = self.fetch_github_skills()
            all_data['github'] = github_data
        except Exception as e:
            logger.error(f"Failed to fetch GitHub data: {e}")
        
        # Process and merge skills
        skill_databases = []
        
        if 'onet' in all_data:
            onet_skills = self.process_onet_skills(all_data['onet'])
            skill_databases.append(('onet', onet_skills))
        
        if 'esco' in all_data:
            esco_skills = self.process_esco_skills(all_data['esco'])
            skill_databases.append(('esco', esco_skills))
        
        if skill_databases:
            merged_skills = self.merge_skill_databases(*skill_databases)
            self.save_merged_skills(merged_skills)
            all_data['merged_skills'] = merged_skills
        
        logger.info("Completed fetching all skill datasets")
        return all_data

def main():
    """Main function to fetch all datasets"""
    fetcher = SkillDatasetsFetcher()
    
    print("🚀 Starting Skill Datasets Fetcher...")
    print("This will download and process various skill databases:")
    print("- O*NET Database (US Department of Labor)")
    print("- ESCO Skills Database (European Commission)")
    print("- GitHub Skills Data")
    print("- Stack Overflow Survey Data")
    print("\n" + "="*60)
    
    # Fetch all datasets
    all_data = fetcher.fetch_all_datasets()
    
    print("\n✅ Completed fetching skill datasets!")
    print(f"Data saved to: {fetcher.data_dir}")
    
    # Show summary
    if 'merged_skills' in all_data:
        print(f"Total unique skills: {len(all_data['merged_skills'])}")
    
    return all_data

if __name__ == "__main__":
    main()
