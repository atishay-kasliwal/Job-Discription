#!/usr/bin/env python3
"""
Import jobs by reading the file content that's visible in the editor
"""

from job_tracker import JobTracker, JobListing
import re

# Read the file using the same method that works
def read_file_content(file_path):
    """Read file content"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except:
        # Try reading line by line
        lines = []
        with open(file_path, 'rb') as f:
            for line in f:
                try:
                    lines.append(line.decode('utf-8', errors='ignore'))
                except:
                    pass
        return '\n'.join(lines)

def parse_jobs(content):
    """Parse jobs from content string"""
    jobs = []
    lines = content.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip empty lines
        if not line.strip():
            i += 1
            continue
        
        # Check if this line starts a new job
        # Pattern: position title, tab, date (YYYY-MM-DD)
        if '\t' in line:
            parts = line.split('\t')
            if len(parts) >= 2 and re.match(r'^\d{4}-\d{2}-\d{2}', parts[1]):
                # This is a job start
                job_data, end_idx = extract_job_from_lines(lines, i)
                if job_data:
                    jobs.append(job_data)
                    i = end_idx
                else:
                    i += 1
            else:
                i += 1
        else:
            i += 1
    
    return jobs

def extract_job_from_lines(lines, start_idx):
    """Extract a job starting at start_idx"""
    first_line = lines[start_idx]
    parts = first_line.split('\t')
    
    if len(parts) < 9:
        return None, start_idx + 1
    
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
    
    # Handle qualifications (may span multiple lines)
    # Check if 9th field starts with quote
    if len(parts) > 9:
        quals_start = parts[9]
    else:
        # Qualifications might be on next line
        quals_start = ''
    
    if quals_start.startswith('"'):
        # Multi-line qualifications
        quals_lines = [quals_start[1:]]  # Remove opening quote
        i = start_idx + 1
        
        while i < len(lines):
            line = lines[i]
            if '"' in line:
                # Found closing quote
                quote_pos = line.find('"')
                if quote_pos >= 0:
                    quals_lines.append(line[:quote_pos])
                    quals_text = '\n'.join(quals_lines)
                    job['qualifications'] = quals_text
                    
                    # After quote: tab, h1b, tab, new_grad
                    after_quote = line[quote_pos+1:].strip()
                    if after_quote.startswith('\t'):
                        remaining = after_quote.split('\t')
                        job['h1b_sponsored'] = remaining[1].strip().lower() if len(remaining) > 1 else 'not sure'
                        job['is_new_grad'] = remaining[2].strip().lower() in ['yes', 'y', 'true', '1'] if len(remaining) > 2 else False
                    else:
                        # Check if h1b is in the remaining text
                        remaining = after_quote.split('\t')
                        job['h1b_sponsored'] = remaining[0].strip().lower() if remaining else 'not sure'
                        job['is_new_grad'] = remaining[1].strip().lower() in ['yes', 'y', 'true', '1'] if len(remaining) > 1 else False
                    
                    return job, i + 1
                else:
                    quals_lines.append(line)
            else:
                quals_lines.append(line)
            i += 1
        
        # Never found closing quote
        job['qualifications'] = '\n'.join(quals_lines)
        job['h1b_sponsored'] = 'not sure'
        job['is_new_grad'] = False
        return job, i
    else:
        # Single line - get quals, h1b, new_grad from remaining parts
        if len(parts) >= 12:
            job['qualifications'] = parts[9].strip()
            job['h1b_sponsored'] = parts[10].strip().lower() if len(parts) > 10 else 'not sure'
            job['is_new_grad'] = parts[11].strip().lower() in ['yes', 'y', 'true', '1'] if len(parts) > 11 else False
        elif len(parts) >= 11:
            job['qualifications'] = parts[9].strip()
            job['h1b_sponsored'] = parts[10].strip().lower()
            job['is_new_grad'] = False
        else:
            job['qualifications'] = parts[9].strip() if len(parts) > 9 else ''
            job['h1b_sponsored'] = 'not sure'
            job['is_new_grad'] = False
        
        return job, start_idx + 1

def main():
    file_path = "02/03/2026.txt"
    
    print(f"📥 Reading file: {file_path}")
    content = read_file_content(file_path)
    
    if not content or len(content.strip()) == 0:
        print("❌ File appears to be empty or cannot be read")
        print("Trying alternative method...")
        # Try reading via read_file tool simulation
        try:
            with open(file_path, 'rb') as f:
                content = f.read().decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"Error: {e}")
            return
    
    print(f"✅ Read {len(content)} characters, {len(content.split(chr(10)))} lines")
    
    print("📋 Parsing jobs...")
    jobs_data = parse_jobs(content)
    print(f"✅ Found {len(jobs_data)} jobs")
    
    if not jobs_data:
        print("\nDebug: First 500 chars of content:")
        print(repr(content[:500]))
        return
    
    # Import to tracker
    tracker = JobTracker()
    print(f"\n📥 Importing {len(jobs_data)} jobs to tracker...")
    
    imported = 0
    for i, job_data in enumerate(jobs_data, 1):
        try:
            industries = [ind.strip() for ind in job_data.get('company_industry', '').split(',') if ind.strip()]
            location = job_data.get('location', '')
            
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
            if i <= 5:  # Show first few errors
                print(f"  Error on job {i}: {e}")
    
    print(f"\n✅ Successfully imported {imported} jobs!")
    print(f"📊 Total jobs in tracker: {len(tracker.get_all_jobs())}")
    
    # Show sample
    if imported > 0:
        print("\n📋 Sample of imported jobs:")
        tracker.display_jobs_table()

if __name__ == "__main__":
    main()
