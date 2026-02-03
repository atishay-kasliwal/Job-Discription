#!/usr/bin/env python3
"""
Job Tracker - Store and manage job listings with detailed information
"""

import json
import csv
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class JobListing:
    """Data model for a job listing"""
    position_title: str
    date: str  # Format: YYYY-MM-DD
    work_model: str  # Hybrid, Remote, On-site
    location: str
    company: str
    salary: str  # e.g., "$165000-$250000 /yr"
    company_size: str  # e.g., "1001-5000"
    company_industry: List[str]  # e.g., ["Big Data", "Machine Learning"]
    qualifications: str
    h1b_sponsored: str  # "yes", "no", "not sure"
    is_new_grad: bool
    apply_url: Optional[str] = None
    notes: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'JobListing':
        """Create from dictionary"""
        return cls(**data)


class JobTracker:
    """Manages job listings storage and retrieval"""
    
    def __init__(self, storage_file: str = "job_listings.json"):
        self.storage_file = Path(storage_file)
        self.jobs: List[JobListing] = []
        self.load_jobs()
    
    def load_jobs(self):
        """Load jobs from JSON file"""
        if self.storage_file.exists():
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.jobs = [JobListing.from_dict(job) for job in data]
            except Exception as e:
                print(f"Error loading jobs: {e}")
                self.jobs = []
        else:
            self.jobs = []
    
    def save_jobs(self):
        """Save jobs to JSON file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump([job.to_dict() for job in self.jobs], f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving jobs: {e}")
            return False
    
    def add_job(self, job: JobListing) -> bool:
        """Add a new job listing"""
        self.jobs.append(job)
        return self.save_jobs()
    
    def get_all_jobs(self) -> List[JobListing]:
        """Get all job listings"""
        return self.jobs
    
    def search_jobs(self, **kwargs) -> List[JobListing]:
        """Search jobs by various criteria"""
        results = self.jobs
        
        if 'company' in kwargs:
            results = [j for j in results if kwargs['company'].lower() in j.company.lower()]
        
        if 'location' in kwargs:
            results = [j for j in results if kwargs['location'].lower() in j.location.lower()]
        
        if 'work_model' in kwargs:
            results = [j for j in results if j.work_model.lower() == kwargs['work_model'].lower()]
        
        if 'industry' in kwargs:
            results = [j for j in results 
                      if any(kwargs['industry'].lower() in ind.lower() for ind in j.company_industry)]
        
        if 'h1b_sponsored' in kwargs:
            results = [j for j in results if j.h1b_sponsored.lower() == kwargs['h1b_sponsored'].lower()]
        
        if 'is_new_grad' in kwargs:
            results = [j for j in results if j.is_new_grad == kwargs['is_new_grad']]
        
        return results
    
    def export_to_csv(self, filename: str = "job_listings.csv") -> bool:
        """Export jobs to CSV file"""
        if not self.jobs:
            print("No jobs to export")
            return False
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=[
                    'position_title', 'date', 'work_model', 'location', 'company',
                    'salary', 'company_size', 'company_industry', 'qualifications',
                    'h1b_sponsored', 'is_new_grad', 'apply_url', 'notes'
                ])
                writer.writeheader()
                
                for job in self.jobs:
                    row = job.to_dict()
                    # Convert list to string for CSV
                    row['company_industry'] = ', '.join(row['company_industry'])
                    row['is_new_grad'] = 'Yes' if row['is_new_grad'] else 'No'
                    writer.writerow(row)
            
            print(f"✅ Exported {len(self.jobs)} jobs to {filename}")
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
    
    def display_jobs_table(self, jobs: Optional[List[JobListing]] = None, detailed: bool = False):
        """Display jobs in a formatted table"""
        if jobs is None:
            jobs = self.jobs
        
        if not jobs:
            print("No jobs found")
            return
        
        if detailed:
            # Detailed view with all fields
            for i, job in enumerate(jobs, 1):
                print("\n" + "=" * 100)
                print(f"Job #{i}")
                print("=" * 100)
                print(f"Position Title: {job.position_title}")
                print(f"Date: {job.date}")
                print(f"Company: {job.company}")
                print(f"Location: {job.location}")
                print(f"Work Model: {job.work_model}")
                print(f"Salary: {job.salary}")
                print(f"Company Size: {job.company_size}")
                print(f"Company Industry: {', '.join(job.company_industry)}")
                print(f"H1B Sponsored: {job.h1b_sponsored}")
                print(f"Is New Grad: {'Yes' if job.is_new_grad else 'No'}")
                print(f"\nQualifications:\n{job.qualifications}")
                if job.apply_url:
                    print(f"\nApply URL: {job.apply_url}")
                if job.notes:
                    print(f"\nNotes: {job.notes}")
        else:
            # Compact table view
            print("\n" + "=" * 150)
            print(f"{'#':<4} {'Position Title':<30} {'Date':<12} {'Company':<20} {'Location':<25} {'Work Model':<12} {'Salary':<20}")
            print("=" * 150)
            
            for i, job in enumerate(jobs, 1):
                title = job.position_title[:28] + ".." if len(job.position_title) > 30 else job.position_title
                location = job.location[:23] + ".." if len(job.location) > 25 else job.location
                company = job.company[:18] + ".." if len(job.company) > 20 else job.company
                
                print(f"{i:<4} {title:<30} {job.date:<12} {company:<20} {location:<25} {job.work_model:<12} {job.salary:<20}")
            
            print("=" * 150)
            print(f"\nTotal: {len(jobs)} jobs")


def create_job_interactive():
    """Interactive function to create a new job listing"""
    print("\n📝 Add New Job Listing")
    print("-" * 50)
    
    position_title = input("Position Title: ").strip()
    date = input("Date (YYYY-MM-DD) [default: today]: ").strip() or datetime.now().strftime("%Y-%m-%d")
    work_model = input("Work Model (Hybrid/Remote/On-site): ").strip()
    location = input("Location: ").strip()
    company = input("Company: ").strip()
    salary = input("Salary (e.g., $165000-$250000 /yr): ").strip()
    company_size = input("Company Size (e.g., 1001-5000): ").strip()
    
    print("\nCompany Industry (enter multiple, separated by commas):")
    industries_input = input("  Industries: ").strip()
    company_industry = [ind.strip() for ind in industries_input.split(',') if ind.strip()]
    
    qualifications = input("Qualifications: ").strip()
    h1b_sponsored = input("H1B Sponsored (yes/no/not sure): ").strip().lower()
    is_new_grad_input = input("Is New Grad? (yes/no): ").strip().lower()
    is_new_grad = is_new_grad_input in ['yes', 'y', 'true', '1']
    
    apply_url = input("Apply URL (optional): ").strip() or None
    notes = input("Notes (optional): ").strip() or None
    
    job = JobListing(
        position_title=position_title,
        date=date,
        work_model=work_model,
        location=location,
        company=company,
        salary=salary,
        company_size=company_size,
        company_industry=company_industry,
        qualifications=qualifications,
        h1b_sponsored=h1b_sponsored,
        is_new_grad=is_new_grad,
        apply_url=apply_url,
        notes=notes
    )
    
    return job


def main():
    """Main function"""
    tracker = JobTracker()
    
    while True:
        print("\n" + "=" * 50)
        print("🔍 Job Tracker")
        print("=" * 50)
        print("1. Add new job")
        print("2. View all jobs")
        print("3. Search jobs")
        print("4. Export to CSV")
        print("5. Exit")
        
        choice = input("\nSelect an option (1-5): ").strip()
        
        if choice == '1':
            job = create_job_interactive()
            if tracker.add_job(job):
                print(f"\n✅ Job '{job.position_title}' added successfully!")
            else:
                print("\n❌ Error adding job")
        
        elif choice == '2':
            view_choice = input("View format: (1) Table (2) Detailed: ").strip()
            detailed = view_choice == '2'
            tracker.display_jobs_table(detailed=detailed)
        
        elif choice == '3':
            print("\n🔍 Search Jobs")
            print("Leave blank to skip any filter")
            company = input("Company: ").strip() or None
            location = input("Location: ").strip() or None
            work_model = input("Work Model: ").strip() or None
            industry = input("Industry: ").strip() or None
            h1b = input("H1B Sponsored (yes/no/not sure): ").strip().lower() or None
            new_grad = input("New Grad only? (yes/no): ").strip().lower()
            is_new_grad = new_grad in ['yes', 'y'] if new_grad else None
            
            filters = {}
            if company:
                filters['company'] = company
            if location:
                filters['location'] = location
            if work_model:
                filters['work_model'] = work_model
            if industry:
                filters['industry'] = industry
            if h1b:
                filters['h1b_sponsored'] = h1b
            if is_new_grad is not None:
                filters['is_new_grad'] = is_new_grad
            
            results = tracker.search_jobs(**filters)
            tracker.display_jobs_table(results)
        
        elif choice == '4':
            filename = input("CSV filename [default: job_listings.csv]: ").strip() or "job_listings.csv"
            tracker.export_to_csv(filename)
        
        elif choice == '5':
            print("\n👋 Goodbye!")
            break
        
        else:
            print("\n❌ Invalid option. Please try again.")


if __name__ == "__main__":
    main()
