from flask import Flask, jsonify
from db import SessionLocal
from models import Job

app = Flask(__name__)

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/jobs", methods=["POST"])
def create_job():
    session = SessionLocal()
    try:
        job = Job(user_id="test-user")
        session.add(job)
        session.commit()
        return jsonify({"id": job.id, "status": job.status}), 201
    finally:
        session.close()

@app.route("/jobs/<job_id>")
def get_job(job_id):
    session = SessionLocal()
    try:
        job = session.get(Job, job_id)
        if job is None:
            return {"error": "not found"}, 404
        return jsonify({
            "id": job.id,
            "status": job.status,
            "created_at": job.created_at.isoformat(),
        })
    finally:
        session.close()

if __name__ == "__main__":
    app.run(debug=True)