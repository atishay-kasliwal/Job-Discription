#!/usr/bin/env python3
"""
Resume Builder - Extract qualifications from job listings and create resume tables
"""

import json
import re
from datetime import datetime
from typing import List, Dict, Set
from collections import defaultdict, Counter
from pathlib import Path
from job_tracker import JobTracker, JobListing
from job_keyword_analyzer import JobKeywordAnalyzer


class ResumeBuilder:
    """Builds resume tables from job listing qualifications"""
    
    def __init__(self):
        self.tracker = JobTracker()
        self.keyword_analyzer = JobKeywordAnalyzer()
        
        # Categories for organizing skills
        self.skill_categories = {
            'programming_languages': {
                'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'cpp', 'go', 'golang',
                'rust', 'kotlin', 'swift', 'scala', 'ruby', 'php', 'r', 'matlab', 'sql',
                'html', 'css', 'bash', 'shell', 'powershell'
            },
            'ml_frameworks': {
                'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'scikit', 'sklearn',
                'pandas', 'numpy', 'jupyter', 'mlflow', 'huggingface', 'transformers',
                'opencv', 'xgboost', 'lightgbm', 'catboost'
            },
            'databases': {
                'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
                'cassandra', 'dynamodb', 'snowflake', 'oracle', 'sqlite', 'neo4j'
            },
            'cloud_platforms': {
                'aws', 'amazon web services', 'azure', 'gcp', 'google cloud',
                'kubernetes', 'docker', 'terraform', 'ansible', 'jenkins'
            },
            'web_frameworks': {
                'react', 'angular', 'vue', 'node.js', 'nodejs', 'django', 'flask',
                'fastapi', 'spring', 'express', 'next.js', 'nuxt', 'laravel'
            },
            'big_data_tools': {
                'spark', 'hadoop', 'kafka', 'airflow', 'databricks', 'snowflake',
                'presto', 'hive', 'storm'
            },
            'ml_concepts': {
                'machine learning', 'deep learning', 'neural networks', 'nlp',
                'natural language processing', 'computer vision', 'reinforcement learning',
                'llm', 'large language models', 'gpt', 'transformer', 'bert', 'cnn',
                'rnn', 'lstm', 'gan', 'svm', 'random forest', 'gradient boosting'
            },
            'software_engineering': {
                'agile', 'scrum', 'microservices', 'rest api', 'graphql', 'api',
                'test-driven development', 'tdd', 'code review', 'pair programming',
                'ci/cd', 'devops', 'git', 'github', 'gitlab', 'jira', 'confluence'
            },
            'education': {
                'bs', 'bachelor', 'master', 'ms', 'phd', 'doctorate', 'degree',
                'computer science', 'engineering', 'mathematics', 'statistics',
                'data science', 'machine learning'
            }
        }
    
    def extract_skills_from_qualifications(self, qualifications: str) -> Dict[str, Set[str]]:
        """Extract skills from qualifications text and categorize them"""
        text = qualifications.lower()
        found_skills = defaultdict(set)
        
        # Exclude common non-technical words
        exclude_words = {
            'experience', 'knowledge', 'strong', 'required', 'must', 'have', 'with',
            'and', 'the', 'for', 'are', 'will', 'this', 'that', 'from', 'their',
            'would', 'should', 'could', 'more', 'than', 'other', 'some', 'such',
            'these', 'those', 'about', 'into', 'through', 'during', 'including',
            'familiarity', 'understanding', 'proficiency', 'expertise', 'skills',
            'ability', 'candidate', 'position', 'role', 'team', 'work', 'looking',
            'seeking', 'hiring', 'join', 'develop', 'build', 'create', 'design',
            'implement', 'manage', 'lead', 'support', 'related', 'field', 'years'
        }
        
        # Check each category - prioritize exact matches
        for category, keywords in self.skill_categories.items():
            for keyword in keywords:
                # Use word boundaries for better matching
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, text):
                    # Normalize the keyword (use the canonical form from our list)
                    found_skills[category].add(keyword)
        
        # Extract additional technical terms using patterns
        # Look for common tech patterns: X.js, X++, X#, etc.
        tech_patterns = [
            r'\b([a-z]+\.js|node\.js|next\.js)\b',  # .js frameworks
            r'\b([a-z]+\+\+)\b',  # C++, etc.
            r'\b([a-z]+#)\b',  # C#, F#, etc.
            r'\b(api|rest api|graphql)\b',  # API types
            r'\b(ci/cd|tdd|nlp|llm|gpt|bert|cnn|rnn|lstm|gan|svm)\b',  # Acronyms
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match[0] else match[1]
                if match and match.lower() not in exclude_words:
                    # Try to categorize
                    categorized = False
                    for category, keywords in self.skill_categories.items():
                        if match.lower() in keywords or any(kw in match.lower() for kw in keywords):
                            found_skills[category].add(match.lower())
                            categorized = True
                            break
                    if not categorized:
                        found_skills['other_technologies'].add(match.lower())
        
        # Filter out excluded words from results
        for category in list(found_skills.keys()):
            found_skills[category] = {
                skill for skill in found_skills[category]
                if skill.lower() not in exclude_words and len(skill) > 1
            }
            # Remove empty categories
            if not found_skills[category]:
                del found_skills[category]
        
        return dict(found_skills)
    
    def build_resume_table(self) -> Dict:
        """Build resume table from all job listings, organized by date"""
        jobs = self.tracker.get_all_jobs()
        
        if not jobs:
            return {
                'error': 'No jobs found. Please add job listings first.',
                'resume_data': {},
                'summary': {}
            }
        
        # Group jobs by date
        jobs_by_date = defaultdict(list)
        for job in jobs:
            jobs_by_date[job.date].append(job)
        
        # Extract skills from each job's qualifications
        resume_data = {}
        all_skills_by_category = defaultdict(Counter)
        
        for date, job_list in sorted(jobs_by_date.items()):
            date_skills = defaultdict(set)
            
            for job in job_list:
                skills = self.extract_skills_from_qualifications(job.qualifications)
                
                # Merge skills for this date
                for category, skill_set in skills.items():
                    date_skills[category].update(skill_set)
                    # Also track globally
                    for skill in skill_set:
                        all_skills_by_category[category][skill] += 1
            
            # Convert sets to sorted lists for JSON serialization
            resume_data[date] = {
                category: sorted(list(skills))
                for category, skills in date_skills.items()
            }
            resume_data[date]['_jobs'] = [
                {
                    'position_title': job.position_title,
                    'company': job.company,
                    'industry': job.company_industry
                }
                for job in job_list
            ]
        
        # Create summary with most common skills across all dates
        summary = {
            category: [skill for skill, count in skills.most_common(20)]
            for category, skills in all_skills_by_category.items()
        }
        
        return {
            'resume_data': resume_data,
            'summary': summary,
            'total_jobs': len(jobs),
            'dates_analyzed': sorted(jobs_by_date.keys()),
            'generated_at': datetime.now().isoformat()
        }
    
    def display_resume_table(self, resume_data: Dict = None):
        """Display resume table in a formatted way"""
        if resume_data is None:
            result = self.build_resume_table()
            if 'error' in result:
                print(f"\n❌ {result['error']}")
                return
            resume_data = result['resume_data']
            summary = result['summary']
        else:
            result = self.build_resume_table()
            summary = result['summary']
        
        print("\n" + "=" * 100)
        print("📋 RESUME SKILLS TABLE (Organized by Date)")
        print("=" * 100)
        
        category_names = {
            'programming_languages': 'Programming Languages',
            'ml_frameworks': 'ML/AI Frameworks',
            'databases': 'Databases',
            'cloud_platforms': 'Cloud Platforms & DevOps',
            'web_frameworks': 'Web Frameworks',
            'big_data_tools': 'Big Data Tools',
            'ml_concepts': 'ML Concepts & Domains',
            'software_engineering': 'Software Engineering Practices',
            'education': 'Education Requirements',
            'other_technologies': 'Other Technologies'
        }
        
        for date in sorted(resume_data.keys()):
            print(f"\n📅 Date: {date}")
            print("-" * 100)
            
            jobs_info = resume_data[date].get('_jobs', [])
            if jobs_info:
                print(f"Jobs found: {len(jobs_info)}")
                for job in jobs_info:
                    print(f"  • {job['position_title']} at {job['company']}")
            
            print("\nSkills extracted:")
            
            for category, skills in resume_data[date].items():
                if category == '_jobs' or not skills:
                    continue
                
                display_name = category_names.get(category, category.replace('_', ' ').title())
                print(f"\n  {display_name}:")
                print(f"    {', '.join(skills)}")
        
        # Display summary
        print("\n" + "=" * 100)
        print("📊 SUMMARY - Most Common Skills Across All Dates")
        print("=" * 100)
        
        for category, skills in summary.items():
            if skills:
                display_name = category_names.get(category, category.replace('_', ' ').title())
                print(f"\n{display_name}:")
                print(f"  {', '.join(skills[:15])}")  # Show top 15
    
    def save_resume_table(self, filename: str = "resume_skills.json"):
        """Save resume table to JSON file"""
        result = self.build_resume_table()
        
        if 'error' in result:
            print(f"\n❌ {result['error']}")
            return False
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n✅ Resume table saved to {filename}")
            print(f"   - Analyzed {result['total_jobs']} jobs")
            print(f"   - Dates: {', '.join(result['dates_analyzed'])}")
            return True
        except Exception as e:
            print(f"\n❌ Error saving resume table: {e}")
            return False
    
    def export_resume_csv(self, filename: str = "resume_skills.csv"):
        """Export resume skills to CSV format"""
        result = self.build_resume_table()
        
        if 'error' in result:
            print(f"\n❌ {result['error']}")
            return False
        
        import csv
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow(['Date', 'Category', 'Skills', 'Job Titles', 'Companies'])
                
                # Write data
                for date in sorted(result['resume_data'].keys()):
                    date_data = result['resume_data'][date]
                    jobs_info = date_data.get('_jobs', [])
                    job_titles = '; '.join([j['position_title'] for j in jobs_info])
                    companies = '; '.join([j['company'] for j in jobs_info])
                    
                    for category, skills in date_data.items():
                        if category == '_jobs' or not skills:
                            continue
                        writer.writerow([
                            date,
                            category.replace('_', ' ').title(),
                            ', '.join(skills),
                            job_titles,
                            companies
                        ])
            
            print(f"\n✅ Resume skills exported to {filename}")
            return True
        except Exception as e:
            print(f"\n❌ Error exporting to CSV: {e}")
            return False


def main():
    """Main function"""
    builder = ResumeBuilder()
    
    print("\n" + "=" * 100)
    print("📝 Resume Builder - Extract Skills from Job Qualifications")
    print("=" * 100)
    
    print("\nOptions:")
    print("1. Display resume table")
    print("2. Save resume table to JSON")
    print("3. Export resume table to CSV")
    print("4. All of the above")
    
    choice = input("\nSelect an option (1-4): ").strip()
    
    if choice == '1':
        builder.display_resume_table()
    elif choice == '2':
        builder.save_resume_table()
    elif choice == '3':
        builder.export_resume_csv()
    elif choice == '4':
        builder.display_resume_table()
        builder.save_resume_table()
        builder.export_resume_csv()
    else:
        print("\n❌ Invalid option")


if __name__ == "__main__":
    main()
