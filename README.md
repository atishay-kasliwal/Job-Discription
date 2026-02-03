# Job Description & Tracker

A comprehensive tool for managing job applications and extracting trending keywords from software and machine learning job descriptions to optimize your resume.

## Features

### Job Tracker 📋
- Store job listings with all relevant details (position, company, salary, location, etc.)
- Search and filter jobs by various criteria
- Export to CSV for easy sharing
- Track H1B sponsorship, work model, and new grad positions

### Resume Builder 📝
- Extracts qualifications from job listings organized by date
- Parses and categorizes skills (Programming Languages, ML Frameworks, Databases, etc.)
- Creates resume-friendly skill tables
- Exports to JSON and CSV formats
- Generates summary of most common skills across all jobs

### Keyword Analyzer 🔍
- Scrapes job descriptions from popular job boards
- Analyzes and extracts trending keywords
- Identifies the most relevant skills and technologies
- Exports results to JSON for easy reference

## Project Structure

- `functions/`: main Python scripts and entrypoints (track jobs, analyze keywords, build resume tables)
- `utils/`: helper modules and shared utility code (to be populated as the project grows)
- `documents/`: non-code assets and data files
  - `documents/sheets/`: raw daily job batches (e.g. `2026-02-03.tsv`)
- `outcome/`: generated output files organized by date
  - `resume_skills.json`: complete resume skills data (all dates)
  - `resume_skills_YYYY-MM-DD.csv`: date-wise CSV files with skills extracted from each day's jobs
  - `count/`: skill frequency counts
    - `skill_counts_YYYY-MM-DD.csv`: date-wise CSV files showing each skill and how many times it appeared
    - `skill_counts_master.csv`: **Master sheet** combining all dates with total counts, categories, and date ranges

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Job Tracker

Track and manage your job applications:

```bash
python job_tracker.py
```

Features:
- **Add jobs**: Store job listings with all details (position title, date, company, salary, location, work model, industry, qualifications, H1B status, etc.)
- **View jobs**: Display jobs in table or detailed format
- **Search jobs**: Filter by company, location, work model, industry, H1B sponsorship, new grad status
- **Export to CSV**: Export all jobs to a CSV file for easy sharing or analysis

Example job fields:
- Position Title
- Date
- Work Model (Hybrid/Remote/On-site)
- Location
- Company
- Salary
- Company Size
- Company Industry (multiple tags)
- Qualifications
- H1B Sponsored (yes/no/not sure)
- Is New Grad (boolean)

### Resume Builder

Extract and organize skills from job qualifications:

```bash
python resume_builder.py
```

Features:
- **Extract skills**: Automatically parses qualifications from all job listings
- **Organize by date**: Groups skills by job posting date
- **Categorize skills**: Organizes into categories (Programming Languages, ML Frameworks, Databases, Cloud Platforms, etc.)
- **Display table**: Shows formatted resume skills table
- **Export formats**: Saves to JSON and CSV for easy use

The resume builder will:
1. Read all job listings from your tracker
2. Extract qualifications from each job (organized by date)
3. Parse and categorize technical skills
4. Display a formatted resume table
5. Save results to `resume_skills.json` and `resume_skills.csv`

### Keyword Analyzer

Extract trending keywords from job descriptions:

```bash
python job_keyword_analyzer.py
```

The script will:
1. Fetch job descriptions for software engineering and ML positions
2. Extract and analyze keywords
3. Display the top trending keywords
4. Save results to `trending_keywords.json`

## Example

Add a sample job:
```bash
python example_add_job.py
```

This will add an example job matching the table format and display it.

## Output

### Job Tracker
- Jobs stored in `job_listings.json`
- Can export to CSV format
- Searchable and filterable

### Keyword Analyzer
Results include:
- Top trending technical keywords
- Keyword frequency counts
- Timestamp of analysis

Use these keywords to optimize your resume and increase your chances of passing ATS (Applicant Tracking Systems)!
