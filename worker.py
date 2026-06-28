import os
import time
import tempfile

from db import SessionLocal
from models import Job
from storage import download_file, upload_file
from processing import run_tone_match

def claim_next_job(session):
    job = (
        session.query(Job)
        .filter(Job.status == "queued")
        .order_by(Job.created_at)
        .with_for_update(skip_locked=True)
        .first()
    )
    if job is None:
        return None
    job.status = "processing"
    session.commit()
    return job

def process_job(job):
    with tempfile.TemporaryDirectory() as tmpdir:
        di_local_path = os.path.join(tmpdir, "di.wav")
        reference_local_path = os.path.join(tmpdir, "reference.wav")
        output_local_path = os.path.join(tmpdir, "result.wav")

        download_file(job.di_s3_key, di_local_path)
        download_file(job.reference_s3_key, reference_local_path)

        run_tone_match(di_local_path, reference_local_path, output_local_path)

        output_key = f"jobs/{job.id}/output/result"
        upload_file(output_local_path, output_key)
        job.output_s3_key = output_key

def main():
    print("Worker started. Polling for jobs...")
    while True:
        session = SessionLocal()
        try:
            job = claim_next_job(session)
            if job is None:
                time.sleep(2)  # No jobs available, wait before polling again
                continue

            print(f"Claimed job {job.id}...")
            try:
                process_job(job)
                job.status = "completed"
                session.commit()
                print(f"Job {job.id} completed.")
            except Exception as e:
                session.rollback()
                job.status = "failed"
                session.commit()
                print(f"Job {job.id} failed: {e}")
        finally:
            session.close()

if __name__ == "__main__":
    main()