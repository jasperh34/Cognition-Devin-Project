import json
import time
from pathlib import Path

#Path where we will store all session information
p = Path("tasks.json")

#Reading the JSON file
def load_tasks():
    if not p.exists():
        return []
    with open(p, "r") as f:
        return json.load(f)

#Writing to the JSON file
def save_tasks(tasks):
    with open(p, "w") as f:
        json.dump(tasks, f, indent=2)

#Calls save_tasks() and specifies what to write based on issue and session
def create_task_record(issue, devin_session):
    tasks = load_tasks()
    task = {
        "task_id": len(tasks) + 1,
        "created_at": int(time.time()),
        "issue_number": issue["issue_number"],
        "issue_title": issue["title"],
        "issue_url": issue["issue_url"],
        "repo_url": issue["repo_url"],
        "devin_session_id": devin_session["session_id"],
        "devin_session_url": devin_session["url"],
        "status": devin_session.get("status"),
        "status_detail": devin_session.get("status_detail"),
        "acus_consumed": devin_session.get("acus_consumed", 0.0),
        "pull_requests": devin_session.get("pull_requests", []),
        "last_updated_at": int(time.time()),
    }
    tasks.append(task)
    save_tasks(tasks)
    return task

#Updates record of a task using session information
def update_task_from_session(task_id, session):
    tasks = load_tasks()
    for task in tasks:
        if task["task_id"] == task_id:
            task["status"] = session.get("status")
            task["status_detail"] = session.get("status_detail")
            task["acus_consumed"] = session.get("acus_consumed", 0.0)
            task["pull_requests"] = session.get("pull_requests", [])
            task["last_updated_at"] = int(time.time())
            save_tasks(tasks)
            return task
    return None


#Gets a specific task based on id
def get_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task["task_id"] == task_id:
            return task
    return None


#Returns a metric summary
def metrics_summary():
    tasks = load_tasks()
    total = len(tasks)
    those_with_pr = sum(1 for t in tasks if len(t["pull_requests"]) > 0)
    active = sum(1 for t in tasks if t.get("status") in ["new", "claimed", "running", "resuming"])
    failed_or_attention = sum(1 for t in tasks if t.get("status") in ["error", "suspended"] and t.get("status_detail") not in ["finished", "inactivity"])
    return {"total_tasks": total, "tasks_with_prs": those_with_pr, "active_tasks": active, "failed_or_needs_attention": failed_or_attention, "pr_percentage": those_with_pr / total * 100 if total else 0}


#For flexibility, if later we store in SQLite or elsewhere
def list_tasks():
    return load_tasks()
