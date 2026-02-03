#!/usr/bin/env python3
"""
Example: Add a job listing matching the format from the image
"""

from job_tracker import JobTracker, JobListing

def main():
    tracker = JobTracker()
    
    # Example job matching the image format
    example_job = JobListing(
        position_title="Quantitative Software Engineer",
        date="2026-02-03",
        work_model="Hybrid",
        location="New York, United States",
        company="Two Sigma",
        salary="$165000-$250000 /yr",
        company_size="1001-5000",
        company_industry=["Big Data", "Machine Learning"],
        qualifications="1. BS in Computer Science, Engineering, or related field\n2. Strong programming skills in Python, C++, Java, and SQL\n3. Experience with machine learning frameworks: TensorFlow, PyTorch, scikit-learn\n4. Knowledge of cloud platforms: AWS, Azure, Docker, Kubernetes\n5. Experience with databases: PostgreSQL, MongoDB, Redis\n6. Familiarity with big data tools: Spark, Hadoop, Kafka\n7. Understanding of NLP, computer vision, and LLMs\n8. Experience with REST APIs, GraphQL, and microservices architecture\n9. Knowledge of CI/CD pipelines, Git, and agile methodologies",
        h1b_sponsored="not sure",
        is_new_grad=False,
        apply_url="https://example.com/apply",
        notes="Great company, competitive salary"
    )
    
    # Add the job
    if tracker.add_job(example_job):
        print("✅ Example job added successfully!")
    else:
        print("❌ Error adding job")
    
    # Display all jobs
    tracker.display_jobs_table()
    
    # Show detailed view
    print("\n" + "=" * 80)
    print("📋 DETAILED JOB VIEW")
    print("=" * 80)
    
    jobs = tracker.get_all_jobs()
    if jobs:
        job = jobs[0]
        print(f"\nPosition Title: {job.position_title}")
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

if __name__ == "__main__":
    main()
