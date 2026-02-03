#!/usr/bin/env python3
"""
Complete Pipeline Runner
Processes a new job listings file and runs the full analysis pipeline:
1. Copies/processes the input file to documents/sheets/
2. Imports jobs to tracker
3. Generates resume skills tables
4. Generates date-wise skill count CSVs
5. Generates master skill counts CSV
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime
from convert_to_table import parse_tsv_with_quotes, import_jobs_to_tracker
from job_tracker import JobTracker
from resume_builder import ResumeBuilder


def process_new_job_file(input_file: str, target_date: str = None):
    """
    Process a new job listings file through the complete pipeline
    
    Args:
        input_file: Path to the input file (txt or tsv)
        target_date: Optional date in YYYY-MM-DD format. If None, uses today's date
    """
    print("=" * 80)
    print("🚀 JOB LISTINGS PIPELINE")
    print("=" * 80)
    
    # Determine target date
    if target_date is None:
        target_date = datetime.now().strftime("%Y-%m-%d")
    
    # Create target path
    sheets_dir = Path("documents/sheets")
    sheets_dir.mkdir(parents=True, exist_ok=True)
    target_file = sheets_dir / f"{target_date}.tsv"
    
    print(f"\n📥 Step 1: Processing input file")
    print(f"   Input: {input_file}")
    print(f"   Target: {target_file}")
    
    # Copy file to target location
    try:
        shutil.copy2(input_file, target_file)
        print(f"   ✅ File copied to {target_file}")
    except Exception as e:
        print(f"   ❌ Error copying file: {e}")
        return False
    
    # Verify file has content
    if not target_file.exists() or target_file.stat().st_size == 0:
        print(f"   ⚠️  Warning: Target file appears empty")
        print(f"   Please ensure the source file is saved and has content")
        return False
    
    # Step 2: Import jobs
    print(f"\n📋 Step 2: Importing jobs to tracker")
    tracker = JobTracker()
    current_count = len(tracker.get_all_jobs())
    
    imported = import_jobs_to_tracker(str(target_file), tracker)
    
    if imported == 0:
        print(f"   ⚠️  No jobs imported. Check file format.")
        return False
    
    new_count = len(tracker.get_all_jobs())
    print(f"   ✅ Imported {imported} jobs")
    print(f"   📊 Total jobs in tracker: {new_count} (added {imported} new)")
    
    # Step 3: Generate resume skills tables
    print(f"\n📝 Step 3: Generating resume skills tables")
    builder = ResumeBuilder()
    
    try:
        builder.save_resume_table()  # Saves to outcome/resume_skills.json
        builder.export_resume_csv(date_wise=True)  # Creates date-wise CSVs
        print(f"   ✅ Resume skills tables generated")
    except Exception as e:
        print(f"   ⚠️  Error generating resume tables: {e}")
    
    # Step 4: Generate skill counts
    print(f"\n🔢 Step 4: Generating skill count CSVs")
    try:
        builder.export_skill_counts_csv(date_wise=True)  # Creates date-wise + master
        print(f"   ✅ Skill count CSVs generated")
    except Exception as e:
        print(f"   ⚠️  Error generating skill counts: {e}")
    
    # Summary
    print("\n" + "=" * 80)
    print("✅ PIPELINE COMPLETE")
    print("=" * 80)
    print(f"\n📁 Output files:")
    print(f"   - Job tracker: job_listings.json ({new_count} jobs)")
    print(f"   - Resume skills: outcome/resume_skills.json")
    print(f"   - Date-wise skills: outcome/resume_skills_{target_date}.csv")
    print(f"   - Date-wise counts: outcome/count/skill_counts_{target_date}.csv")
    print(f"   - Master counts: outcome/count/skill_counts_master.csv")
    
    return True


def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python3 run_pipeline.py <input_file> [date]")
        print("\nExample:")
        print("  python3 run_pipeline.py new_jobs.txt")
        print("  python3 run_pipeline.py new_jobs.txt 2026-02-04")
        print("\nThe script will:")
        print("  1. Copy file to documents/sheets/YYYY-MM-DD.tsv")
        print("  2. Import jobs to tracker")
        print("  3. Generate resume skills tables")
        print("  4. Generate skill count CSVs (date-wise + master)")
        return
    
    input_file = sys.argv[1]
    target_date = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(input_file).exists():
        print(f"❌ Error: File not found: {input_file}")
        return
    
    success = process_new_job_file(input_file, target_date)
    
    if not success:
        print("\n⚠️  Pipeline completed with warnings. Please check the output above.")


if __name__ == "__main__":
    main()
