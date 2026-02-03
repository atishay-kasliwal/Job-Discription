#!/usr/bin/env python3
"""
Job Description Keyword Analyzer
Extracts trending keywords from software and ML job descriptions
"""

import requests
from bs4 import BeautifulSoup
import re
from collections import Counter
import json
from datetime import datetime
import time
from typing import List, Dict, Set
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    try:
        nltk.download('punkt_tab', quiet=True)
    except:
        try:
            nltk.download('punkt', quiet=True)
        except:
            pass

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


class JobKeywordAnalyzer:
    """Analyzes job descriptions to extract trending keywords"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        # Common technical keywords to look for
        self.tech_keywords = {
            # Programming Languages
            'python', 'java', 'javascript', 'typescript', 'c++', 'c#', 'go', 'rust', 
            'kotlin', 'swift', 'scala', 'ruby', 'php', 'r', 'matlab',
            # ML/AI Frameworks
            'tensorflow', 'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy',
            'jupyter', 'mlflow', 'huggingface', 'transformers', 'opencv',
            # Cloud & DevOps
            'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'ci/cd',
            'terraform', 'ansible', 'git', 'github', 'gitlab',
            # Databases
            'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
            'cassandra', 'dynamodb', 'snowflake',
            # Web Frameworks
            'react', 'angular', 'vue', 'node.js', 'django', 'flask', 'fastapi',
            'spring', 'express', 'next.js', 'nuxt',
            # Big Data & Tools
            'spark', 'hadoop', 'kafka', 'airflow', 'databricks', 'snowflake',
            # ML Concepts
            'machine learning', 'deep learning', 'neural networks', 'nlp',
            'computer vision', 'reinforcement learning', 'llm', 'gpt',
            'transformer', 'bert', 'cnn', 'rnn', 'lstm',
            # Software Engineering
            'agile', 'scrum', 'microservices', 'rest api', 'graphql',
            'test-driven development', 'tdd', 'code review', 'pair programming'
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Remove special characters but keep spaces
        text = re.sub(r'[^\w\s-]', ' ', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.lower().strip()
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from job description"""
        text = self.clean_text(text)
        words = word_tokenize(text)
        
        # Filter out stop words and short words
        keywords = [
            word for word in words 
            if word not in self.stop_words and len(word) > 2
        ]
        
        # Also check for multi-word phrases
        phrases = []
        words_lower = text.lower()
        for keyword in self.tech_keywords:
            if keyword in words_lower:
                phrases.append(keyword)
        
        return keywords + phrases
    
    def analyze_job_descriptions(self, descriptions: List[str]) -> Dict:
        """Analyze multiple job descriptions and return keyword frequencies"""
        all_keywords = []
        
        for desc in descriptions:
            keywords = self.extract_keywords(desc)
            all_keywords.extend(keywords)
        
        # Count keyword frequencies
        keyword_counts = Counter(all_keywords)
        
        # Filter to only include tech-related keywords
        # Exclude common non-technical words
        exclude_words = {'experience', 'knowledge', 'strong', 'required', 'must', 
                        'have', 'with', 'and', 'the', 'for', 'are', 'will', 'this',
                        'that', 'from', 'their', 'would', 'should', 'could', 'more',
                        'than', 'other', 'some', 'such', 'these', 'those', 'about',
                        'into', 'through', 'during', 'including', 'familiarity',
                        'understanding', 'proficiency', 'expertise', 'skills',
                        'ability', 'candidate', 'position', 'role', 'team', 'work',
                        'looking', 'seeking', 'hiring', 'join', 'develop', 'build',
                        'create', 'design', 'implement', 'manage', 'lead', 'support'}
        
        tech_keyword_counts = {
            kw: count for kw, count in keyword_counts.items()
            if (kw.lower() not in exclude_words and 
                (any(tech in kw.lower() or kw.lower() in tech 
                     for tech in self.tech_keywords) or 
                 (len(kw) > 4 and kw.lower() not in self.stop_words)))
        }
        
        return {
            'total_jobs': len(descriptions),
            'keyword_counts': dict(keyword_counts.most_common(100)),
            'tech_keywords': dict(sorted(tech_keyword_counts.items(), 
                                        key=lambda x: x[1], reverse=True)[:50]),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_trending_keywords(self, analysis: Dict, top_n: int = 30) -> List[tuple]:
        """Get top N trending keywords"""
        tech_keywords = analysis.get('tech_keywords', {})
        return sorted(tech_keywords.items(), key=lambda x: x[1], reverse=True)[:top_n]


class JobScraper:
    """Scrapes job descriptions from various job boards"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
    
    def scrape_indeed(self, query: str, location: str = "", max_results: int = 20) -> List[str]:
        """
        Scrape job descriptions from Indeed
        Note: Indeed has anti-scraping measures, this is a basic implementation
        For production use, consider using Indeed's official API or Selenium
        """
        descriptions = []
        base_url = "https://www.indeed.com/jobs"
        
        try:
            params = {
                'q': query,
                'l': location,
                'start': 0
            }
            
            response = requests.get(base_url, params=params, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                # Try multiple selectors as Indeed changes their structure
                job_cards = soup.find_all(['div', 'a'], class_=lambda x: x and ('job' in x.lower() or 'result' in x.lower()))
                
                for card in job_cards[:max_results]:
                    # Look for job description snippets
                    desc_elem = card.find(['div', 'span'], class_=lambda x: x and ('snippet' in x.lower() or 'summary' in x.lower()))
                    if desc_elem:
                        text = desc_elem.get_text(strip=True)
                        if len(text) > 50:  # Filter out very short snippets
                            descriptions.append(text)
            
            time.sleep(2)  # Be respectful with requests
            
        except Exception as e:
            print(f"  ⚠️  Error scraping Indeed: {e}")
        
        return descriptions
    
    def scrape_github_jobs(self, query: str, max_results: int = 20) -> List[str]:
        """
        Scrape from GitHub Jobs (if available) or similar tech-focused boards
        """
        descriptions = []
        # GitHub Jobs API endpoint (if available)
        # Note: GitHub Jobs was discontinued, but we can try alternatives
        return descriptions
    
    def get_real_job_descriptions(self, query: str, max_results: int = 20) -> List[str]:
        """
        Attempts to get real job descriptions from multiple sources
        Falls back to sample data if scraping fails
        """
        descriptions = []
        
        print(f"    Trying Indeed...")
        indeed_descriptions = self.scrape_indeed(query, max_results=max_results)
        descriptions.extend(indeed_descriptions)
        
        if len(descriptions) < 5:
            print(f"    ⚠️  Limited results from scraping. Using enhanced samples...")
            # Use more realistic sample descriptions
            descriptions.extend(self.scrape_sample_descriptions(query))
        
        return descriptions[:max_results]
    
    def scrape_sample_descriptions(self, query: str) -> List[str]:
        """
        Returns realistic sample job descriptions based on current market trends
        These are based on common patterns in real job postings
        """
        samples = [
            f"""
            {query.title()} - We are seeking a talented {query} with strong experience in Python, 
            machine learning, and data science. The ideal candidate will have hands-on experience 
            with TensorFlow, PyTorch, and scikit-learn. Must be proficient in pandas, numpy, and 
            have experience with deep learning and neural networks. Experience with AWS cloud services, 
            Docker containers, and Kubernetes orchestration is highly preferred. Knowledge of 
            natural language processing (NLP), computer vision, and large language models (LLMs) 
            including GPT and transformer architectures is a plus.
            """,
            f"""
            Senior {query.title()} - Join our innovative team to develop cutting-edge ML solutions 
            and AI products. Required skills include Python programming, scikit-learn, pandas, 
            numpy, and Jupyter notebooks. Experience with NLP, computer vision, reinforcement 
            learning, and LLM fine-tuning. Strong knowledge of React, Node.js, REST APIs, and 
            GraphQL. Familiarity with CI/CD pipelines, Git version control, GitHub Actions, 
            and agile/scrum methodologies. Experience with microservices architecture, test-driven 
            development (TDD), and code reviews.
            """,
            f"""
            {query.title()} Specialist - We need a proficient professional in machine learning 
            and data science. Required: Python, R, SQL, PostgreSQL, MongoDB, Redis. Experience 
            with Apache Spark, Hadoop, Airflow workflow orchestration, and Databricks. Cloud 
            experience with AWS (S3, EC2, Lambda), Azure, or Google Cloud Platform (GCP). 
            Knowledge of microservices architecture, containerization with Docker, and 
            orchestration with Kubernetes. Experience with Terraform infrastructure as code.
            """,
            f"""
            {query.title()} Engineer - Looking for an experienced engineer with expertise in 
            Python, Java, JavaScript, TypeScript, and Go. Strong background in machine learning, 
            deep learning, and AI model development. Experience with TensorFlow, PyTorch, Keras, 
            and MLflow for model tracking. Knowledge of computer vision, OpenCV, and image 
            processing. Familiarity with big data tools like Spark, Kafka, and Elasticsearch. 
            Experience with cloud platforms (AWS, Azure, GCP) and DevOps tools (Jenkins, 
            Ansible, Terraform). Understanding of software engineering best practices including 
            code reviews, pair programming, and agile development.
            """,
            f"""
            {query.title()} Developer - We're hiring a developer with strong ML/AI background. 
            Skills required: Python, scikit-learn, pandas, numpy, matplotlib. Experience with 
            neural networks, CNNs, RNNs, LSTMs, and transformer models. Knowledge of Hugging 
            Face transformers library and model fine-tuning. Experience with data pipelines, 
            ETL processes, and data warehousing (Snowflake). Proficiency in SQL and NoSQL 
            databases. Cloud experience with AWS services. Familiarity with React frontend 
            development and Node.js backend services.
            """,
            f"""
            {query.title()} - Seeking a professional with machine learning and software engineering 
            expertise. Must have: Python, TensorFlow, PyTorch, scikit-learn. Experience with 
            natural language processing, computer vision, and reinforcement learning. Knowledge 
            of LLMs, GPT models, BERT, and transformer architectures. Strong programming skills 
            in Python, Java, or C++. Experience with cloud computing (AWS, Azure), Docker, 
            Kubernetes, and CI/CD pipelines. Database knowledge: PostgreSQL, MongoDB, Redis. 
            Understanding of microservices, REST APIs, and GraphQL.
            """
        ]
        return samples


def main():
    """Main function to run the keyword analyzer"""
    print("🔍 Job Description Keyword Analyzer")
    print("=" * 50)
    
    # Initialize components
    scraper = JobScraper()
    analyzer = JobKeywordAnalyzer()
    
    # Search queries
    queries = [
        "software engineer",
        "machine learning engineer",
        "data scientist",
        "ML engineer"
    ]
    
    all_descriptions = []
    
    print("\n📥 Fetching job descriptions...")
    for query in queries:
        print(f"  Searching for: {query}")
        # Try to get real job descriptions, falls back to samples if needed
        descriptions = scraper.get_real_job_descriptions(query, max_results=15)
        all_descriptions.extend(descriptions)
        print(f"    Found {len(descriptions)} job descriptions")
    
    if not all_descriptions:
        print("⚠️  No job descriptions found. Using sample data...")
        all_descriptions = scraper.scrape_sample_descriptions("software engineer")
    
    print(f"\n📊 Analyzing {len(all_descriptions)} job descriptions...")
    
    # Analyze keywords
    analysis = analyzer.analyze_job_descriptions(all_descriptions)
    
    # Get trending keywords
    trending = analyzer.get_trending_keywords(analysis, top_n=30)
    
    # Display results
    print("\n" + "=" * 50)
    print("🔥 TOP TRENDING KEYWORDS FOR YOUR RESUME")
    print("=" * 50)
    print(f"\nBased on {analysis['total_jobs']} job descriptions analyzed\n")
    
    for i, (keyword, count) in enumerate(trending, 1):
        bar = "█" * min(count, 20)
        print(f"{i:2d}. {keyword:30s} [{count:3d}] {bar}")
    
    # Save results to JSON
    output_file = "trending_keywords.json"
    with open(output_file, 'w') as f:
        json.dump({
            'analysis': analysis,
            'trending_keywords': trending,
            'generated_at': datetime.now().isoformat()
        }, f, indent=2)
    
    print(f"\n💾 Results saved to {output_file}")
    print("\n✨ Use these keywords to optimize your resume!")


if __name__ == "__main__":
    main()
