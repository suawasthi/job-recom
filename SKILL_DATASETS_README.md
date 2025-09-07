# 🚀 Skill Datasets Integration

This directory contains tools to fetch, integrate, and use various skill databases to improve the job recommendation system.

## 📁 Files Overview

### Core Files
- **`skill_datasets_fetcher.py`** - Downloads skill datasets from various sources
- **`skill_integrator.py`** - Integrates fetched skills with existing ontology
- **`run_skill_fetcher.py`** - Simple script to run the fetcher
- **`skillner_integration.py`** - Integration with SkillNer library

### Test Files
- **`debug_skill_matching.py`** - Dynamic skill matching debugger
- **`simple_skill_test.py`** - Simple skill extraction test
- **`test_category_matching.py`** - Category-based matching test

## 🎯 Available Skill Databases

### 1. O*NET Database (US Department of Labor)
- **Source**: https://www.onetcenter.org/
- **Content**: Comprehensive skills, knowledge, abilities, and occupations
- **Size**: ~2,000+ skills
- **Format**: Excel files
- **Update**: Quarterly

### 2. ESCO Skills Database (European Commission)
- **Source**: https://ec.europa.eu/esco/
- **Content**: European skills, competences, and qualifications
- **Size**: ~13,000+ skills
- **Format**: JSON API
- **Update**: Regular

### 3. GitHub Skills Data
- **Source**: GitHub API
- **Content**: Trending repositories and programming languages
- **Size**: Dynamic
- **Format**: JSON API
- **Update**: Real-time

### 4. Stack Overflow Survey Data
- **Source**: Stack Overflow Developer Survey
- **Content**: Developer skills and technologies
- **Size**: ~70,000+ responses
- **Format**: CSV/ZIP
- **Update**: Annual

## 🚀 Quick Start

### 1. Fetch All Skill Datasets
```bash
python run_skill_fetcher.py
```

### 2. Test SkillNer Integration
```bash
python skillner_integration.py
```

### 3. Debug Skill Matching
```bash
python debug_skill_matching.py --interactive
```

## 📦 Installation Requirements

### For SkillNer Integration
```bash
pip install skillNer
python -m spacy download en_core_web_lg
```

### For Data Processing
```bash
pip install pandas requests openpyxl
```

## 🔧 Usage Examples

### Fetch Specific Dataset
```python
from skill_datasets_fetcher import SkillDatasetsFetcher

fetcher = SkillDatasetsFetcher()

# Fetch only O*NET data
onet_data = fetcher.fetch_onet_database()

# Fetch only ESCO data
esco_data = fetcher.fetch_esco_skills()
```

### Integrate with Ontology
```python
from skill_integrator import SkillIntegrator
from app.services.ontology_service import ontology_service

integrator = SkillIntegrator()
integrator.integrate_with_ontology(ontology_service)
```

### Use SkillNer for Extraction
```python
from skillner_integration import SkillNerIntegration

skillner = SkillNerIntegration()
skills = skillner.extract_skills_simple("I know Python, AWS, and Docker")
print(skills)  # ['Python', 'AWS', 'Docker']
```

## 📊 Expected Results

### After Running Fetcher
- **O*NET Skills**: ~2,000+ skills
- **ESCO Skills**: ~13,000+ skills
- **Merged Skills**: ~15,000+ unique skills
- **Data Directory**: `skill_datasets/`

### After Integration
- **Enhanced Ontology**: More comprehensive skill coverage
- **Better Matching**: Improved skill similarity calculations
- **Reduced False Positives**: More accurate job recommendations

## 🎯 Benefits

1. **Comprehensive Coverage**: Access to thousands of skills from multiple sources
2. **Standardized Skills**: Consistent skill naming and categorization
3. **Better Matching**: Improved skill similarity calculations
4. **Reduced Manual Work**: Automated skill database updates
5. **Industry Standards**: Based on official government and industry databases

## 🔍 Debugging

### Test Skill Matching
```bash
python debug_skill_matching.py --preset
```

### Interactive Testing
```bash
python debug_skill_matching.py --interactive
```

### Check Ontology Coverage
```python
from app.services.ontology_service import ontology_service
print(f"Total skills in ontology: {len(ontology_service.skills_graph)}")
```

## 📈 Performance Impact

- **Initial Fetch**: ~5-10 minutes (one-time)
- **Integration**: ~1-2 minutes
- **Runtime Impact**: Minimal (skills are cached)
- **Memory Usage**: ~50-100MB additional

## 🛠️ Troubleshooting

### Common Issues

1. **SkillNer Import Error**
   ```bash
   pip install skillNer
   python -m spacy download en_core_web_lg
   ```

2. **Network Timeout**
   - Check internet connection
   - Retry with longer timeout

3. **File Permission Error**
   - Ensure write permissions to `skill_datasets/` directory

4. **Memory Issues**
   - Process datasets in smaller chunks
   - Use streaming for large files

## 🔄 Updates

### Automatic Updates
- Run `python run_skill_fetcher.py` periodically
- Datasets are updated regularly by their sources

### Manual Updates
- Check source websites for new versions
- Update URLs in `skill_datasets_fetcher.py` if needed

## 📝 Notes

- **Data Quality**: O*NET and ESCO are government-maintained, high-quality sources
- **Coverage**: ESCO has better international coverage, O*NET has better US coverage
- **Integration**: Skills are merged intelligently to avoid duplicates
- **Caching**: Results are cached to avoid repeated API calls

## 🎉 Success Metrics

After integration, you should see:
- ✅ More accurate skill matching
- ✅ Reduced false positives
- ✅ Better job recommendations
- ✅ Comprehensive skill coverage
- ✅ Improved user experience
