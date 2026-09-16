from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

from src.devflow.graph import run_devflow
from src.devflow.integrations.jira_adapter import JiraAdapter

app = FastAPI(title="DevFlow AI", version="0.1.0")

class RunRequest(BaseModel):
    user_request: str
    thread_id: Optional[str] = "devflow-1"
    jira_ticket_id: Optional[str] = None
    force_approve: Optional[bool] = False

class RunResponse(BaseModel):
    thread_id: str
    approval_status: str = ""
    pr_result: str = ""
    final_response: str = ""
    completed_agents: list = []

def build_user_request(user_request: str, jira_ticket_id: str | None) -> str:
    parts = []
    if jira_ticket_id:
        try:
            ticket_text = JiraAdapter().get_ticket(jira_ticket_id)
            parts.append(f"Jira Ticket {jira_ticket_id}:\n{ticket_text}")
        except Exception as e:
            parts.append(f"Jira Ticket {jira_ticket_id}: (fetch failed: {e})")
    if user_request.strip():
        parts.append(f"User Request:\n{user_request.strip()}")
    return "\n\n".join(parts)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/workflow/run", response_model=RunResponse)
def run_workflow(body: RunRequest):
    combined = build_user_request(body.user_request, body.jira_ticket_id)
    result = run_devflow(
        user_request=combined,
        thread_id=body.thread_id,
        force_approve=body.force_approve,
    )
    return RunResponse(
        thread_id=body.thread_id,
        approval_status=result.get("approval_status", ""),
        pr_result=result.get("pr_result", ""),
        final_response=result.get("final_response", ""),
        completed_agents=result.get("completed_agents", []),
    )
