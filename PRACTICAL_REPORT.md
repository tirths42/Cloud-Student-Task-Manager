# GMIU Cloud Computing Practical Report

> Replace bracketed fields and test results after deployment. Do not claim a URL, live cloud database, screenshot or test that you have not verified.

## Cover details
- Experiment: Deployment of a Cloud-Based Student Task Manager
- Student name: [Your name]
- Enrollment number: [Enrollment number]
- Semester / branch: [Semester / Branch]
- Institution: Gyanmanjari Innovative University (GMIU), Bhavnagar
- Date: [Submission date]
- GitHub repository: [Repository URL]
- Deployed application: [Render URL after deployment]

## 1. Aim
To build and deploy a basic web application using cloud compute and storage services, demonstrate public internet accessibility and observe basic resource management using Render and Supabase PostgreSQL.

## 2. Objectives
1. Develop a browser-based application.
2. Host the Flask application on Render.
3. Store records persistently in Supabase PostgreSQL.
4. Verify the public HTTPS URL.
5. Inspect health, logs and resource limits.

## 3. Technology
HTML5, CSS3, JavaScript, Python, Flask, Gunicorn, Docker, Render, Supabase PostgreSQL and GitHub.

## 4. Architecture
Browser → HTTPS → Render (Flask/Gunicorn) → Supabase PostgreSQL. Render executes application logic and handles HTTP requests. Supabase PostgreSQL stores task records independently of the application container. Render deployment logs help with troubleshooting.

## 5. Features
Create, edit, complete and delete tasks; filter by status and priority; search tasks; dashboard counts; and a service-status endpoint.

## 6. Implementation
The Flask backend exposes REST endpoints under `/api/tasks`. It validates task fields and uses Supabase PostgreSQL when the Render environment variables are configured. Local development uses SQLite and the status endpoint identifies it as a local fallback rather than cloud storage.

## 7. Deployment record
- Supabase Project: [Project name / reference ID]
- Supabase PostgreSQL region: [Region]
- Render service: [Service name]
- Database access: server-side Supabase service-role key stored in Render environment variables
- Render service name: [Your actual service name]
- Public URL: [Actual URL]

## 8. Test results — complete after testing
| Test | Expected result | Actual result |
|---|---|---|
| Public URL | Dashboard loads over HTTPS | [Pass/Fail + notes] |
| Create task | New task appears | [Pass/Fail + notes] |
| Refresh | Task persists | [Pass/Fail + notes] |
| Toggle status | Status changes and persists | [Pass/Fail + notes] |
| Edit task | Updated details appear | [Pass/Fail + notes] |
| Delete task | Task is removed | [Pass/Fail + notes] |
| `/api/status` | Render active and Supabase PostgreSQL connected | [Observed JSON] |
| Supabase Table Editor | Task row exists in `tasks` table | [Pass/Fail + notes] |

## 9. Resource management
Render Free web services sleep after 15 minutes of inactivity and use ephemeral filesystems. Supabase Free includes 500 MB database storage and may pause after a week of low activity. Monitor both dashboards and remain within free-tier limits.

## 10. Screenshots to insert
1. Live application with public Render URL visible.
2. Tasks created in the application.
3. `/api/status` showing Render active and Supabase PostgreSQL connected.
4. Supabase Table Editor showing a row in the `tasks` table.
5. Optional Render metrics/logs.

Use screenshots captured from your own deployment, not mock evidence.

## 11. Conclusion
[Summarise what you actually deployed, tested and observed.]

## 12. Viva questions
**What is cloud computing?** On-demand access to computing, storage and other IT resources over a network.

**What is Render?** A cloud platform for deploying and hosting web applications.

**What is Supabase?** A managed backend platform that includes a PostgreSQL relational database.

**Why use Supabase PostgreSQL rather than a local file?** Supabase PostgreSQL provides managed persistent storage independent of an application container.

**Why keep the service-role key secret?** It has elevated database privileges and must remain on the server, never in frontend code or a public repository.

**What is scale-to-zero?** The service can reduce active compute instances to zero when there is no traffic; it does not mean all associated resources are free.
