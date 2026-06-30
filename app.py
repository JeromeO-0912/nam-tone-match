from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename
from db import SessionLocal
from models import Job
from storage import upload_fileobj, get_object_bytes

app = Flask(__name__)

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/jobs", methods=["POST"])
def create_job():
    di = request.files.get("di")
    reference = request.files.get("reference")
    if di is None or reference is None:
        return {"error": "Missing required files, 'di' and 'reference' are required"}, 400
    
    session = SessionLocal()
    try:
        job = Job(user_id="test-user")
        session.add(job)
        session.flush()  # Get job.id before commit

        di_key = f"jobs/{job.id}/di/{secure_filename(di.filename)}"
        reference_key = f"jobs/{job.id}/reference/{secure_filename(reference.filename)}"

        upload_fileobj(di, di_key, content_type=di.content_type)
        upload_fileobj(reference, reference_key, content_type=reference.content_type)

        job.di_s3_key = di_key
        job.reference_s3_key = reference_key
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
            "di_s3_key": job.di_s3_key,
            "reference_s3_key": job.reference_s3_key,
            "created_at": job.created_at.isoformat(),
        })
    finally:
        session.close()

@app.route("/jobs/<job_id>/result")
def get_job_result(job_id):
    session = SessionLocal()
    try:
        job = session.get(Job, job_id)
        if job is None:
            return {"error": "not found"}, 404
        if job.status != "completed" or not job.output_s3_key:
            return {"error": "result not ready", "status": job.status}, 409
        data = get_object_bytes(job.output_s3_key)
        return app.response_class(data, mimetype="application/json")
    finally:
        session.close()

if __name__ == "__main__":
    app.run(debug=True)