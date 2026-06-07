from fastapi import FastAPI, HTTPException, Request

from app.devin_call_client import DevinCallClient
from app.prompts import build_prompt
from app.observability import (
    create_task_record,
    list_tasks,
    get_task,
    update_task_from_session,
    metrics_summary,
)

# Instance of FastAPI so app can receive messages form Github
app = FastAPI(title="Devin Agent for Apache Superset")

DEVIN = DevinCallClient()


# Validation: Check the incoming JSON has all required fields.
def validate_issue(issue):
    required_fields = [
        "repo_url",
        "issue_number",
        "issue_url",
        "title",
        "body",
    ]
    missing_fields = []

    for field in required_fields:
        if field not in issue:
            missing_fields.append(field)

    if missing_fields:
        raise HTTPException(
            status_code = 400,
            detail = f"Missing required fields: {missing_fields}",
        )
    if not isinstance(issue["issue_number"], int):
        raise HTTPException(
            status_code = 400,
            detail = "issue_number must be an integer",
        )
    return issue


#Takes issue (dict), builds Devin prompt, creates session, stores local task, returns it
def route_issue_to_devin(issue):
    prompt = build_prompt(issue)
    session = DEVIN.create_session(
        prompt=prompt,
        title=f"Remediate issue #{issue['issue_number']}: {issue['title']}",
        tags=[
            "devin",
            "github-issue",
            f"issue-{issue['issue_number']}",
        ],
        max_acu_limit = 5,
    )
    task = create_task_record(issue, session)
    return task


#ENDPOINT FUNCTIONS

@app.get("/")
def root():
    return {"name": "Devin Agent for Apache Superset", "status": "running", "description": "Automation for routing GitHub issues to Devin and tracking session progress."}


# For extracting issue and repo fields from JSON payload from Github
@app.post("/webhook/github")
async def github_webhook(request: Request):

    # #### Ignore GitHub events that are not issue and only route issues explicitly labelled 'devin'
    event_type = request.headers.get("X-GitHub-Event")
    payload = await request.json()

    if event_type != "issues":
        return {"ignored": True, "reason": f"Unsupported GitHub event type: {event_type}"}
    
    action = payload.get("action")

    if action not in ["opened", "labeled"]:
        return {"ignored": True, "reason": f"Unsupported issue action: {action}"}

    #Extracts github_issue 
    github_issue = payload.get("issue", {})
    repository = payload.get("repository", {})
    
    #Extract GitHub label names from the label objects.
    labels = []
    for label in github_issue.get("labels", []):
        labels.append(label.get("name"))

    if "devin" not in labels:
        return {"ignored": True, "reason": "Issue does not have devin label"}


    issue = {
        "repo_url": repository.get("html_url"),
        "issue_number": github_issue.get("number"),
        "issue_url": github_issue.get("html_url"),
        "title": github_issue.get("title"),
        "body": github_issue.get("body") or "",
    }

    issue = {
        "repo_url": repository.get("html_url"),
        "issue_number": github_issue.get("number"),
        "issue_url": github_issue.get("html_url"),
        "title": github_issue.get("title"),
        "body": github_issue.get("body") or "",
    }

    issue = validate_issue(issue)

    # if GitHub sends the same issue event more than once, we must avoid creating duplicated Devin sessions
    for existing_task in list_tasks():
        if existing_task["issue_url"] == issue["issue_url"]:
            return {
                "ignored": True,
                "reason": "Issue already routed to Devin",
                "task": existing_task,
            }

    task = route_issue_to_devin(issue)

    return {"ignored": False, "message": "GitHub issue routed to Devin","task": task }

#ENDPOINT FUNCTIONS ctnd.

@app.get("/tasks")
def tasks():
    return {"metrics": metrics_summary(), "tasks": list_tasks()}



@app.post("/tasks/{task_id}/refresh")
def refresh_task(task_id: int):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code = 404, detail = "Task not found")
    session = DEVIN.get_session(task["devin_session_id"])
    updated = update_task_from_session(task_id, session)
    return {"message": "Task refreshed from Devin session","task": updated}



@app.get("/tasks/{task_id}/messages")
def task_messages(task_id: int):
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code = 404, detail="Task not found")
    try:
        messages = DEVIN.list_messages(task["devin_session_id"])
        return messages
    except Exception as e:
        raise HTTPException(status_code = 500, detail=f"Failed to fetch Devin messages: {str(e)}")