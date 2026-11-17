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
- Deployed application: [Cloud Run URL after deployment]

## 1. Aim
To build and deploy a basic web application using cloud compute and storage services, demonstrate public internet accessibility and observe basic resource management using Google Cloud Run and Google Cloud Firestore.

## 2. Objectives
1. Develop a browser-based application.
2. Host the Flask application on Cloud Run.
3. Store records persistently in Firestore.
4. Verify the public HTTPS URL.
5. Inspect health, logs and resource limits.

## 3. Technology
HTML5, CSS3, JavaScript, Python, Flask, Gunicorn, Docker, Google Cloud Run, Google Cloud Firestore and GitHub.

## 4. Architecture
Browser → HTTPS → Cloud Run (Flask/Gunicorn container) → Firestore. Cloud Run executes application logic and handles requests. Firestore stores task documents independently of an individual container instance. Cloud Logging and Cloud Monitoring provide operational visibility.

## 5. Features
Create, edit, complete and delete tasks; filter by status and priority; search tasks; dashboard counts; and a service-status endpoint.

## 6. Implementation
The Flask backend exposes REST endpoints under `/api/tasks`. It validates task fields and uses the Firestore Python client when the project configuration and runtime credentials are available. Without GCP access, local development uses SQLite and the status endpoint identifies it as a local fallback rather than cloud storage.

## 7. Deployment record
- GCP Project ID: [Project ID]
- Firestore region: [Region]
- Runtime service account: [Service account]
- IAM role granted: `roles/datastore.user`
- Cloud Run service: `student-task-manager`
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
| `/api/status` | Cloud Run active and Firestore connected | [Observed JSON] |
| Firestore console | Task document exists | [Pass/Fail + notes] |

## 9. Resource management
Deployment parameters: 1 vCPU, 512 MiB memory, minimum instances 0 and maximum instances 2. Scale-to-zero can reduce idle compute usage. It does not remove charges for other resources such as builds, images, logs, network use or database operations. Monitor Cloud Billing and Cloud Monitoring.

## 10. Screenshots to insert
1. Live application with public Cloud Run URL visible.
2. Tasks created in the application.
3. `/api/status` showing Cloud Run active and Firestore connected.
4. Firestore console showing the `tasks` collection.
5. Optional Cloud Run metrics/logs.

Use screenshots captured from your own deployment, not mock evidence.

## 11. Conclusion
[Summarise what you actually deployed, tested and observed.]

## 12. Viva questions
**What is cloud computing?** On-demand access to computing, storage and other IT resources over a network.

**What is Cloud Run?** A managed platform for running containerized applications without managing servers directly.

**What is Firestore?** A managed NoSQL document database organized into collections and documents.

**Why use Firestore rather than a local file?** Firestore provides managed persistent storage independent of an application container.

**What is IAM?** Identity and Access Management controls which identities can access cloud resources and what actions they can perform.

**What is scale-to-zero?** The service can reduce active compute instances to zero when there is no traffic; it does not mean all associated resources are free.
