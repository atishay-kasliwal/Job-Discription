#!/usr/bin/env python3
"""
Import jobs from text file into job tracker
Parses tab-separated job listings and converts them to JobListing format
"""

import re
from pathlib import Path
from job_tracker import JobTracker, JobListing
from typing import List


def parse_job_file(file_path: str) -> List[dict]:
    """Parse tab-separated job listings from text file"""
    jobs = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n\r')
        
        # Skip empty lines
        if not line.strip():
            i += 1
            continue
        
        # Check if this line starts a new job (doesn't start with tab and has content)
        # A new job starts when we see a position title (not starting with tab, not a number, not quoted continuation)
        if not line.startswith('\t') and line.strip():
            # Try to parse this job
            job_data = parse_single_job(lines, i)
            if job_data:
                jobs.append(job_data)
                # Move to next job (skip lines we've processed)
                i = job_data.get('_next_index', i + 1)
            else:
                i += 1
        else:
            i += 1
    
    return jobs


def parse_single_job(lines: List[str], start_idx: int) -> dict:
    """Parse a single job starting at start_idx"""
    # Collect all lines for this job
    job_lines = []
    i = start_idx
    in_quotes = False
    quote_started = False
    
    while i < len(lines):
        line = lines[i].rstrip('\n\r')
        
        # Check for quote start/end
        quote_count = line.count('"')
        if quote_count > 0:
            # Check if we're entering or exiting quotes
            if '"' in line and not in_quotes:
                in_quotes = True
                quote_started = True
            elif '"' in line and in_quotes and quote_count % 2 == 1:
                # Odd number means we're closing quotes
                in_quotes = False
                quote_started = False
        
        job_lines.append(line)
        
        # If we're not in quotes and this line doesn't start with tab, might be next job
        # But wait - we need to check if next line starts a new job
        if not in_quotes and i + 1 < len(lines):
            next_line = lines[i + 1].rstrip('\n\r')
            # Next job starts if: not empty, doesn't start with tab, and is not a continuation
            if next_line and not next_line.startswith('\t') and not next_line[0].isdigit():
                # Check if it looks like a position title (has a date pattern nearby)
                # Actually, simpler: if we have enough fields and next line starts new job, we're done
                break
        
        i += 1
    
    # Now parse the collected lines
    full_text = '\n'.join(job_lines)
    
    # Split by tabs, but be careful with quoted multi-line fields
    fields = []
    current_field = ""
    in_field_quotes = False
    
    for char in full_text:
        if char == '"':
            in_field_quotes = not in_field_quotes
            current_field += char
        elif char == '\t' and not in_field_quotes:
            # End of field
            fields.append(current_field.strip())
            current_field = ""
        else:
            current_field += char
    
    # Don't forget last field
    if current_field:
        fields.append(current_field.strip())
    
    # Clean up fields - remove quotes from quoted fields
    cleaned_fields = []
    for field in fields:
        if field.startswith('"') and field.endswith('"'):
            field = field[1:-1]
        cleaned_fields.append(field)
    
    if len(cleaned_fields) < 10:
        return None
    
    # Parse into job data structure
    job_data = {
        'position_title': cleaned_fields[0] if len(cleaned_fields) > 0 else '',
        'date': cleaned_fields[1] if len(cleaned_fields) > 1 else '',
        'apply_url': cleaned_fields[2] if len(cleaned_fields) > 2 else None,
        'work_model': cleaned_fields[3] if len(cleaned_fields) > 3 else '',
        'location': cleaned_fields[4] if len(cleaned_fields) > 4 else '',
        'company': cleaned_fields[5] if len(cleaned_fields) > 5 else '',
        'salary': cleaned_fields[6] if len(cleaned_fields) > 6 else '',
        'company_size': cleaned_fields[7] if len(cleaned_fields) > 7 else '',
        'company_industry': cleaned_fields[8] if len(cleaned_fields) > 8 else '',
        'qualifications': cleaned_fields[9] if len(cleaned_fields) > 9 else '',
        'h1b_sponsored': cleaned_fields[10].lower() if len(cleaned_fields) > 10 else 'not sure',
        'is_new_grad': cleaned_fields[11].lower() in ['yes', 'y', 'true', '1'] if len(cleaned_fields) > 11 else False,
        '_next_index': i
    }
    
    return job_data


def parse_job_fields(fields: List[str]) -> dict:
    """Parse individual job fields from tab-separated list"""
    # This function is kept for compatibility but parse_single_job does the work
    pass


def import_jobs_to_tracker(file_path: str, tracker: JobTracker = None) -> int:
    """Import jobs from file into job tracker"""
    if tracker is None:
        tracker = JobTracker()
    
    print(f"📥 Reading jobs from {file_path}...")
    jobs_data = parse_job_file(file_path)
    
    print(f"✅ Parsed {len(jobs_data)} jobs")
    print("\n📋 Importing jobs...")
    
    imported = 0
    skipped = 0
    
    for i, job_data in enumerate(jobs_data, 1):
        try:
            # Parse company industry
            industries = []
            if job_data.get('company_industry'):
                industries = [ind.strip() for ind in str(job_data['company_industry']).split(',') if ind.strip()]
            
            # Clean up location (handle multi-line)
            location = str(job_data.get('location', ''))
            if '\n' in location:
                location_lines = [l.strip() for l in location.split('\n') if l.strip()]
                if location_lines and 'Multi Location' in location_lines[0]:
                    location = '; '.join(location_lines[1:]) if len(location_lines) > 1 else location_lines[0]
                else:
                    location = location_lines[0] if location_lines else location
            
            # Create JobListing object
            job = JobListing(
                position_title=str(job_data.get('position_title', '')),
                date=str(job_data.get('date', '')),
                work_model=str(job_data.get('work_model', '')),
                location=location,
                company=str(job_data.get('company', '')),
                salary=str(job_data.get('salary', '')),
                company_size=str(job_data.get('company_size', '')),
                company_industry=industries if industries else ['Unknown'],
                qualifications=str(job_data.get('qualifications', '')),
                h1b_sponsored=str(job_data.get('h1b_sponsored', 'not sure')),
                is_new_grad=bool(job_data.get('is_new_grad', False)),
                apply_url=str(job_data.get('apply_url', '')) if job_data.get('apply_url') else None,
                notes=None
            )
            
            if tracker.add_job(job):
                imported += 1
                if imported % 50 == 0:
                    print(f"  Imported {imported} jobs...")
            else:
                skipped += 1
        except Exception as e:
            print(f"  ⚠️  Error importing job {i}: {e}")
            skipped += 1
    
    print(f"\n✅ Successfully imported {imported} jobs")
    if skipped > 0:
        print(f"⚠️  Skipped {skipped} jobs due to errors")
    
    return imported


def main():
    """Main function"""
    import sys
    
    # Default file path
    file_path = "02/03/2026.txt"
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return
    
    tracker = JobTracker()
    
    # Show current job count
    current_count = len(tracker.get_all_jobs())
    print(f"Current jobs in tracker: {current_count}")
    
    # Import jobs
    imported = import_jobs_to_tracker(file_path, tracker)
    
    # Show new total
    new_count = len(tracker.get_all_jobs())
    print(f"\n📊 Total jobs in tracker: {new_count} (added {imported} new jobs)")
    
    # Display summary
    print("\n" + "=" * 80)
    print("📋 JOB SUMMARY")
    print("=" * 80)
    tracker.display_jobs_table()


if __name__ == "__main__":
    main()
