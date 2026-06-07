# Devin Agent for Apache Superset
 
This is a FastAPI service that is triggered on GitHub issue webhook events and automatically routes labelled issues to Devin for fixing. Devin creates a branch and makes the fix and opens a pull request. There is also a live task dashboard with observability metrics.
 
## Pipeline
 
```
GitHub Issue is labelled "devin"
        ↓
GitHub Webhook
        ↓
Validate payload + duplicated check
        ↓
Build Devin prompt from issue context
        ↓
Create Devin session (using Devin API)
        ↓
Store task record in tasks.json
        ↓
GET /tasks — status, metrics, PR links
```
 
## Prerequisites
 
- Docker and Docker Compose
- A Devin account: API key and org ID
- A GitHub repository with a configured webhook
- ngrok for exposing the local server
 
## Setup
 
### 1. Fill in credentials in `.env`:
 
```
DEVIN_API_KEY = 
DEVIN_ORG_ID=
```
 
### 2. Create task store
 
This file must exist before starting the container (Docker will treat a missing file as a directory otherwise).
 
### 3. Start server and then expose with ngrok
 
```
docker compose up --build
```
 
```
ngrok http 8000
```
 
Copy the HTTPS forwarding URL as this is the URL needed for setting up the webhook.
 
### 4. GitHub webhook
 
In working repository: Settings → Webhooks → Add webhook using the URL, and setting content type to `application/json`
 
To trigger Devin, add label **`devin`** to any issue.
 
## API Endpoints and observability
 
| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/webhook/github` | GitHub issue webhook receiver |
| `GET` | `/tasks` | Task dashboard with metrics |
| `POST` | `/tasks/{id}/refresh` | Pull latest status from Devin session |
| `GET` | `/tasks/{id}/messages` | Inspect Devin session messages |
 
`GET /tasks` returns a metrics summary alongside all task records:
 
| Metric | Description |
|--------|-------------|
| `total_tasks` | Total GitHub issues routed to Devin |
| `tasks_with_prs` | Issues where Devin opened a pull request |
| `active_tasks` | Sessions currently running |
| `failed_or_needs_attention` | Sessions in error or suspended state |
| `pr_percentage` | Percentage of routed tasks that produced a PR |


## Result
 
The automation creates pull requests rather than merging directly.

 
## Notes for further improvement
 
**Storage:** Task state is stored in a local `tasks.json` file. In production I would use a durable database such as Postgres, keyed by GitHub issue URL to guarantee idempotency across webhook retries.
 
**Status refresh:** The current system requires manual `POST /tasks/{id}/refresh` calls to update session status. In production I would add a background polling worker or scheduled job to refresh active sessions automatically.
 
 
