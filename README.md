# Cloud-Based Student Task Manager — GMIU Practical

Flask task manager deployed on Render Free with Supabase PostgreSQL Free.

## Features
- Create, edit, complete and delete tasks
- Search and filter by status and priority
- Health and deployment status endpoints
- Supabase PostgreSQL persistence in cloud deployment
- SQLite is used only for local development when Supabase variables are absent

## Local run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:8080. Local SQLite is not cloud storage.

## Free cloud deployment
Follow `DEPLOYMENT_GUIDE.md`. Create a Supabase Free project, run `supabase_schema.sql`, and deploy this repository to Render Free. Set `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and `SUPABASE_TABLE=tasks` as Render environment variables. Never commit secrets.

## Status checks
- `/health` should return `status: ok`.
- `/api/status` should show `compute.is_render=true`, `storage.connected=true`, and `storage.mode=supabase_postgres`.
