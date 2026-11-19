# Free deployment: Render + Supabase

This version is configured for a free-tier demonstration. Render Free web services sleep after 15 minutes of inactivity; the first request after sleep can take around a minute. Supabase Free PostgreSQL includes 500 MB and may pause after a week of low activity. Free tiers can change; check current limits before deployment.

## 1. Create Supabase database
1. Sign up at https://supabase.com/ and create a project on the Free plan.
2. Choose a strong database password and save it privately.
3. Wait until the project is ready.
4. Open SQL Editor > New query. Copy all of `supabase_schema.sql` into the editor and click Run.
5. Open Project Settings > API. Copy the Project URL and the `service_role` secret key. Treat the service-role key as a password. Never commit it to GitHub or put it in frontend code.

## 2. Ensure GitHub repository has every file
The repository must contain `app.py`, `requirements.txt`, `render.yaml`, `supabase_schema.sql`, `templates/index.html`, `static/css/style.css`, and `static/js/app.js`. Upload the full contents of this project folder, including the `templates` and `static` directories. Do not upload `.env`, passwords, or API keys.

## 3. Deploy on Render
1. Sign up at https://render.com/ and connect your GitHub account.
2. Choose New > Web Service. Select `tirths42/Cloud-Student-Task-Manager` (or your updated repository).
3. Select branch `main`. Runtime: Python. Region: choose a nearby available region.
4. Choose the Free instance type.
5. Build command: `pip install -r requirements.txt`
6. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 4`
7. Under Environment Variables add: `SUPABASE_URL` = your Supabase Project URL; `SUPABASE_SERVICE_ROLE_KEY` = your Supabase service_role secret key; `SUPABASE_TABLE` = `tasks`.
8. Click Create Web Service and wait for the deploy to finish. Copy the public `onrender.com` URL.

## 4. Verify cloud database (do not skip)
1. Open `https://YOUR-RENDER-URL/health`; expect `status: ok`.
2. Open `https://YOUR-RENDER-URL/api/status`; verify `compute.is_render` is true, `storage.connected` is true, and `storage.mode` is `supabase_postgres`.
3. In the app, add a task. Refresh the page; it should remain.
4. In Supabase > Table Editor > tasks, verify the task row exists.
5. Test edit, complete, and delete.

If `/api/status` says `local_sqlite`, the app is NOT using the cloud database. Check the two Supabase environment variables and Render logs. If database operations fail, confirm the SQL schema was run and the table is named `tasks`.

## 5. Submission evidence
Capture genuine screenshots of: (a) Render deployment showing Live and service URL, (b) app loaded at the public URL, (c) `/api/status` with Render and Supabase connected, and (d) Supabase Table Editor showing a task row. Fill `PRACTICAL_REPORT.md` with your real project URL and actual test results.

## Cost and security notes
Use only the Free plans and do not select paid instances or upgrades. Free services have limits and can be suspended/paused; this is suitable for a practical demonstration, not guaranteed always-on production hosting. Keep the Supabase service-role key only in Render environment variables. Do not publish it in GitHub, screenshots, or the browser.
