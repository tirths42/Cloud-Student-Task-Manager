# Cloud-Based Student Task Manager — GMIU Practical

A task-manager web application for demonstrating cloud compute, database storage, public hosting and resource management.

## Architecture
```text
Browser --HTTPS--> Google Cloud Run (Flask + Gunicorn)
                           |
                           +----> Google Cloud Firestore (tasks collection)
```

## Features
- Create, edit, complete and delete tasks
- Search and filter by status and priority
- Dashboard statistics and health endpoints
- Responsive interface
- Firestore persistence on Cloud Run
- SQLite fallback for local testing only; status reports it honestly

## Main files
`app.py` backend/API · `templates/index.html` dashboard · `static/` CSS/JS · `Dockerfile` container · `cloudbuild.yaml` build pipeline template · `DEPLOYMENT_GUIDE.md` deployment steps · `PRACTICAL_REPORT.md` report template · `test_app.py` tests.

## Run locally
Python 3.10+:
```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:8080. Without GCP credentials, data is stored in local `tasks.db`; this is not cloud storage.

Run tests:
```bash
python -m unittest -v test_app.py
```

## Deploy
Follow `DEPLOYMENT_GUIDE.md`. Create your own GCP project and Firestore database, grant the Cloud Run runtime identity `roles/datastore.user`, and deploy. The real service URL is generated during deployment and is not pre-filled here.

## GitHub
Create your own repository and upload the extracted contents of this ZIP. Do not upload `.env`, database files or service-account credentials.

## Reference
Prepared independently with a similar task-manager concept to the public reference repository https://github.com/shreyash2256/Cloud-Student-Task-Manager. This package is not affiliated with or a modification of that repository.
