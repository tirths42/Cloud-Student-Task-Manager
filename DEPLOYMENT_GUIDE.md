# Deployment guide — Google Cloud Run + Firestore

**This ZIP contains source code, not a deployed service.** Google Cloud generates the public URL only after you deploy it in your own project.

## 1. Create a Google Cloud project
1. Open https://console.cloud.google.com/ and create/select a project.
2. Link billing if required. Review pricing and configure a budget alert.
3. In Cloud Shell run:

```bash
gcloud config set project YOUR_PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com firestore.googleapis.com
```

## 2. Create Firestore
1. Open Firestore in the Cloud Console.
2. Create a Native mode database named `(default)`.
3. Choose an appropriate location, for example `asia-south1` (Mumbai) where available. Location cannot be changed later.
4. Use production mode rules. Do not make the database publicly readable.

## 3. Configure IAM
Use a dedicated Cloud Run runtime service account and grant it `roles/datastore.user` on the project. Do not download or commit service-account JSON keys. Cloud Run uses Application Default Credentials.

## 4. Deploy
Upload/extract this project folder in Cloud Shell and change into it. Run:

```bash
gcloud run deploy student-task-manager \
  --source . \
  --region asia-south1 \
  --allow-unauthenticated \
  --service-account YOUR_RUNTIME_SERVICE_ACCOUNT \
  --memory 512Mi --cpu 1 --min 0 --max 2 \
  --set-env-vars GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID,FIRESTORE_DATABASE=\(default\),FIRESTORE_COLLECTION=tasks,CLOUD_RUN_REGION=asia-south1
```

Replace both placeholders. Copy the Service URL printed by the deployment.

## 5. Verify
- Open the Cloud Run URL and add a task.
- Refresh; confirm the task persists.
- Open `SERVICE_URL/api/status`; verify `compute.is_cloud_run=true` and `storage.connected=true`.
- Open `SERVICE_URL/health`; expect `status: ok`.
- Confirm the task exists in Firestore collection `tasks`.
- Capture your own screenshots of the live service and Firestore console.

## 6. Resource management
The deployment limits compute to 1 vCPU, 512 MiB, minimum 0 and maximum 2 instances. Scale-to-zero reduces idle compute but does not guarantee zero charges; builds, image storage, logs, networking and database operations may still incur costs. Monitor Billing, Cloud Run metrics and logs. Remove the service when finished if no longer needed:

```bash
gcloud run services delete student-task-manager --region asia-south1
```

## Local development

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:8080. Without GCP configuration, SQLite is used for local testing and the status indicator reports local mode.
