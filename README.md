This project listens for GitHub issue webhook events. When an issue is opened or labelled with devin, it creates a Devin session to remediate the issue, tracks the Devin session locally, and exposes status, PR links, and session messages through a FastAPI API.

GitHub Issue labelled "devin"
        ↓
GitHub Webhook
        ↓
FastAPI /webhook/github
        ↓
Build Devin prompt from issue context
        ↓
Create Devin session via Devin API
        ↓
Store task record locally
        ↓
GET /tasks shows status, metrics, PRs

How to run:

cp .env.example .env
# Fill in DEVIN_API_KEY and DEVIN_ORG_ID

docker compose up --build

Then:

ngrok http 8000

Webhook URL:

https://YOUR-NGROK-URL/webhook/github

GitHub webhook settings:

Content type: application/json
Events: Issues
Trigger label: devin

Observability endpoints

Document these:

GET  /                  health check
POST /webhook/github    GitHub issue webhook receiver
GET  /tasks             task dashboard and metrics
POST /tasks/{id}/refresh refresh latest Devin session status
GET  /tasks/{id}/messages inspect Devin session messages


Metrics:

total_tasks: number of GitHub issues routed to Devin
tasks_with_prs: number of tasks where Devin opened a PR
active_tasks: sessions still running/new/claimed/resuming
failed_or_needs_attention: sessions that errored or need intervention
pr_percentage: percentage of routed tasks that produced a PR


## Production considerations

For this take-home, task state is stored in a local JSON file. In a production deployment I would use a durable database such as Postgres and key tasks by GitHub issue URL or issue ID to guarantee idempotency across webhook retries.

The GitHub label acts as a human approval gate: only issues explicitly labelled `devin` are routed to Devin. In a customer deployment, I would likely use more specific labels such as `devin-remediate`, `devin-review`, and `devin-investigate`.

The current system requires manual refresh of Devin session status. In production, I would add a background polling worker or scheduled job to refresh active sessions automatically.

The workflow intentionally creates PRs rather than merging changes. Human review remains the control point.