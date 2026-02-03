#!/usr/bin/env python3
"""
Convert job listings from text file to table format and import to job tracker
This script handles tab-separated values with multi-line quoted fields
"""

import csv
import re
from job_tracker import JobTracker, JobListing

def parse_tsv_with_quotes(file_path):
    """Parse TSV file handling quoted multi-line fields"""
    jobs = []
    
    # Read entire file
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    if not content.strip():
        print("⚠️  File appears empty. Please save the file first.")
        return []
    
    # Use csv module with tab delimiter - it handles quoted fields automatically
    from io import StringIO
    reader = csv.reader(StringIO(content), delimiter='\t', quotechar='"')
    
    current_row = []
    rows = []
    
    for row in reader:
        if len(row) >= 10:  # Valid job row
            rows.append(row)
    
    # Parse each row into job data
    for row in rows:
        try:
            if len(row) < 10:
                continue
            
            # Extract fields
            job_data = {
                'position_title': row[0].strip(),
                'date': row[1].strip(),
                'apply_url': row[2].strip() if len(row) > 2 else '',
                'work_model': row[3].strip() if len(row) > 3 else '',
                'location': row[4].strip() if len(row) > 4 else '',
                'company': row[5].strip() if len(row) > 5 else '',
                'salary': row[6].strip() if len(row) > 6 else '',
                'company_size': row[7].strip() if len(row) > 7 else '',
                'company_industry': row[8].strip() if len(row) > 8 else '',
                'qualifications': row[9].strip() if len(row) > 9 else '',
                'h1b_sponsored': row[10].strip().lower() if len(row) > 10 else 'not sure',
                'is_new_grad': row[11].strip().lower() in ['yes', 'y', 'true', '1'] if len(row) > 11 else False
            }
            
            jobs.append(job_data)
        except Exception as e:
            print(f"  ⚠️  Error parsing row: {e}")
            continue
    
    return jobs

def main():
    """
    Convert one daily sheet into structured jobs + resume tables.
    By default it reads today's sheet from documents/sheets.
    You can also pass a custom path as the first CLI argument.
    """
    import sys

    # Default location for daily sheets (e.g. 2026-02-03.tsv)
    default_sheet = "documents/sheets/2026-02-03.tsv"

    file_path = sys.argv[1] if len(sys.argv) > 1 else default_sheet
    
    print("=" * 80)
    print("📋 CONVERTING JOB LISTINGS TO TABLE FORMAT")
    print("=" * 80)
    print(f"\n📥 Reading file: {file_path}")
    
    jobs_data = parse_tsv_with_quotes(file_path)
    
    if not jobs_data:
        print("\n❌ No jobs found. Please ensure:")
        print("   1. The file is saved")
        print("   2. The file contains tab-separated job listings")
        return
    
    print(f"✅ Found {len(jobs_data)} jobs")
    
    # Import to tracker
    tracker = JobTracker()
    print(f"\n📥 Importing to job tracker...")
    
    imported = 0
    for i, job_data in enumerate(jobs_data, 1):
        try:
            # Parse industries
            industries = [ind.strip() for ind in job_data.get('company_industry', '').split(',') if ind.strip()]
            
            # Clean location (handle multi-line)
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
                qualifications=job_data['qualifications'],
                h1b_sponsored=job_data['h1b_sponsored'],
                is_new_grad=job_data['is_new_grad'],
                apply_url=job_data.get('apply_url') if job_data.get('apply_url') else None,
                notes=None
            )
            
            if tracker.add_job(job):
                imported += 1
                if imported % 50 == 0:
                    print(f"  ✅ Imported {imported} jobs...")
        except Exception as e:
            if i <= 3:  # Show first few errors for debugging
                print(f"  ⚠️  Error on job {i}: {e}")
            continue
    
    print(f"\n✅ Successfully imported {imported} out of {len(jobs_data)} jobs!")
    print(f"📊 Total jobs in tracker: {len(tracker.get_all_jobs())}")
    
    # Display summary
    if imported > 0:
        print("\n" + "=" * 80)
        print("📋 IMPORTED JOBS SUMMARY")
        print("=" * 80)
        tracker.display_jobs_table()
        
        # Also generate resume table
        print("\n" + "=" * 80)
        print("📝 GENERATING RESUME SKILLS TABLE")
        print("=" * 80)
        from resume_builder import ResumeBuilder
        builder = ResumeBuilder()
        builder.display_resume_table()
        builder.save_resume_table()  # Saves to outcome/resume_skills.json
        builder.export_resume_csv(date_wise=True)  # Creates separate CSV per date in outcome/
        builder.export_skill_counts_csv(date_wise=True)  # Creates skill count CSV per date in outcome/count/

if __name__ == "__main__":
    main()
