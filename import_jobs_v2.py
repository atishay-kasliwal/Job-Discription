#!/usr/bin/env python3
"""
Import jobs from text file - simpler approach
"""

from job_tracker import JobTracker, JobListing
import re

def parse_jobs_from_file(file_path: str):
    """Parse jobs from the text file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    jobs = []
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip empty lines
        if not line:
            i += 1
            continue
        
        # A new job starts with a position title (not starting with number, tab, or quote)
        # Pattern: Title, then tab, then date (YYYY-MM-DD)
        if '\t' in line and re.match(r'^\d{4}-\d{2}-\d{2}', line.split('\t')[1] if len(line.split('\t')) > 1 else ''):
            # This looks like a job start
            job_data = extract_job(lines, i)
            if job_data:
                jobs.append(job_data)
                i = job_data.get('_end_line', i + 1)
            else:
                i += 1
        else:
            i += 1
    
    return jobs

def extract_job(lines, start_idx):
    """Extract a single job starting at start_idx"""
    # First line has: title \t date \t url \t work_model \t location \t company \t salary \t size \t industry \t "qualifications...
    first_line = lines[start_idx]
    parts = first_line.split('\t')
    
    if len(parts) < 9:
        return None
    
    job = {
        'position_title': parts[0].strip(),
        'date': parts[1].strip(),
        'apply_url': parts[2].strip() if len(parts) > 2 else '',
        'work_model': parts[3].strip() if len(parts) > 3 else '',
        'location': parts[4].strip() if len(parts) > 4 else '',
        'company': parts[5].strip() if len(parts) > 5 else '',
        'salary': parts[6].strip() if len(parts) > 6 else '',
        'company_size': parts[7].strip() if len(parts) > 7 else '',
        'company_industry': parts[8].strip() if len(parts) > 8 else '',
    }
    
    # Qualifications start after industry (9th field, index 8)
    # Split by tab and get everything after industry
    all_parts = first_line.split('\t')
    if len(all_parts) < 9:
        return None
    
    # Everything from index 9 onwards is qualifications + h1b + new_grad
    quals_and_rest = '\t'.join(all_parts[9:])
    
    # Check if qualifications start with quote (multi-line)
    if quals_and_rest.startswith('"'):
        # Multi-line qualifications
        quals_lines = [quals_and_rest[1:]]  # Remove opening quote
        i = start_idx + 1
        
        # Collect lines until we find closing quote
        while i < len(lines):
            line = lines[i]
            if '"' in line:
                # Found closing quote
                quote_pos = line.find('"')
                quals_lines.append(line[:quote_pos])
                quals_text = '\n'.join(quals_lines)
                
                # After quote, we have: \t h1b \t new_grad
                after_quote = line[quote_pos+1:].strip()
                if after_quote.startswith('\t'):
                    remaining = after_quote.split('\t')
                    job['h1b_sponsored'] = remaining[1].strip().lower() if len(remaining) > 1 else 'not sure'
                    job['is_new_grad'] = remaining[2].strip().lower() in ['yes', 'y', 'true', '1'] if len(remaining) > 2 else False
                else:
                    job['h1b_sponsored'] = 'not sure'
                    job['is_new_grad'] = False
                
                job['qualifications'] = quals_text
                job['_end_line'] = i + 1
                return job
            else:
                quals_lines.append(line)
            i += 1
        
        # Never found closing quote - use what we have
        job['qualifications'] = '\n'.join(quals_lines)
        job['h1b_sponsored'] = 'not sure'
        job['is_new_grad'] = False
        job['_end_line'] = i
        return job
    else:
        # Single line qualifications
        # Split by tab to get quals, h1b, new_grad
        remaining_parts = quals_and_rest.split('\t')
        job['qualifications'] = remaining_parts[0].strip() if remaining_parts else ''
        job['h1b_sponsored'] = remaining_parts[1].strip().lower() if len(remaining_parts) > 1 else 'not sure'
        job['is_new_grad'] = remaining_parts[2].strip().lower() in ['yes', 'y', 'true', '1'] if len(remaining_parts) > 2 else False
        job['_end_line'] = start_idx + 1
        return job

def main():
    tracker = JobTracker()
    file_path = "02/03/2026.txt"
    
    print(f"📥 Parsing jobs from {file_path}...")
    jobs_data = parse_jobs_from_file(file_path)
    print(f"✅ Found {len(jobs_data)} jobs")
    
    if not jobs_data:
        print("No jobs found. Checking file format...")
        with open(file_path, 'r') as f:
            first_lines = [f.readline() for _ in range(10)]
            for i, line in enumerate(first_lines):
                print(f"Line {i}: {repr(line[:100])}")
        return
    
    print(f"\n📋 Importing {len(jobs_data)} jobs...")
    imported = 0
    
    for i, job_data in enumerate(jobs_data, 1):
        try:
            # Parse industries
            industries = [ind.strip() for ind in job_data.get('company_industry', '').split(',') if ind.strip()]
            
            # Clean location
            location = job_data.get('location', '')
            if '\n' in location:
                loc_lines = [l.strip() for l in location.split('\n') if l.strip()]
                if loc_lines and 'Multi Location' in loc_lines[0]:
                    location = '; '.join(loc_lines[1:]) if len(loc_lines) > 1 else loc_lines[0]
                else:
                    location = loc_lines[0] if loc_lines else location
            
            job = JobListing(
                position_title=job_data['position_title'],
                date=job_data['date'],
                work_model=job_data['work_model'],
                location=location,
                company=job_data['company'],
                salary=job_data['salary'],
                company_size=job_data['company_size'],
                company_industry=industries if industries else ['Unknown'],
                qualifications=job_data.get('qualifications', ''),
                h1b_sponsored=job_data.get('h1b_sponsored', 'not sure'),
                is_new_grad=job_data.get('is_new_grad', False),
                apply_url=job_data.get('apply_url') if job_data.get('apply_url') else None,
                notes=None
            )
            
            if tracker.add_job(job):
                imported += 1
                if imported % 100 == 0:
                    print(f"  Imported {imported} jobs...")
        except Exception as e:
            print(f"  Error on job {i}: {e}")
    
    print(f"\n✅ Imported {imported} jobs successfully!")
    print(f"📊 Total jobs in tracker: {len(tracker.get_all_jobs())}")

if __name__ == "__main__":
    main()
