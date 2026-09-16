# DevFlow AI

Multi-agent **LangGraph** workflow that turns a **user request** and/or a **Jira ticket** into:

- structured requirements & architecture
- implementation / testing / security / code-review plans
- human approval gate with a **bounded revision loop**
- suggested code under `generated/`
- GitHub branch + commits + **pull request** (no auto-merge)
- project memory (ChromaDB)
- structured logging + LangSmith tracing (latency, LLM calls, run timeline)

> AI assists the engineering process. **Humans still approve and merge.**

---

## Architecture

```text
Input (user_request and/or jira_ticket_id)
  → requirement → architecture
  → implementation plan → testing plan → security review → code review
  → human approval
       ├─ rejected → revise implementation (max 3 attempts)
       └─ approved → code generation → git (branch/commit/PR) → memory store
```

### Nodes

| Node | Responsibility |
|---|---|
| `supervisor_node` | Decides which agents the request needs |
| `requirement_node` | Extracts feature, actors, action, and source tracking |
| `architecture_node` | Suggests backend / frontend / DB / auth stack |
| `pdf_extractor_node` | Pulls text from an input PDF |
| `codebase_inspector_node` | Lists files, reads README, runs AST analysis |
| `implementation_node` | Produces the structured implementation plan |
| `testing_node` | Derives test cases from the plan |
| `security_node` | Reports material security findings |
| `code_review_node` | Plan-level review → approve / request_changes / needs_discussion |
| `human_approval_node` | Maps the review recommendation to workflow status |
| `code_generation_node` | Generates code files from the approved plan |
| `git_automation_node` | Branch + commits + PR via `GitHubAdapter` |
| `memory_store_node` | Persists a compact run summary to ChromaDB |

---

## Revision loop behavior

This is the part worth understanding, because it controls whether a run converges.

**First review (attempt 1)** runs a full plan-level review. It can raise implementation, testing, security, quality, or completeness gaps. If any exist, it returns `request_changes` and the feedback is stored in `applied_review_feedback`.

**Re-review (attempt 2+)** switches to a **revision-mode prompt**. The reviewer's only job is to verify whether each item from the previous feedback was addressed. It is explicitly told not to re-scan the plan for fresh issues.

**Deterministic guard.** LLMs drift, so the prompt alone is not enough. After the call, `code_review_node` filters the returned items:

- items whose wording overlaps the previous feedback (≥ 0.35 token overlap) are **kept** — they represent genuinely unresolved work
- items with `severity: critical` are **always kept** — a real authorization, injection, or data-exposure flaw still blocks
- everything else is **dropped** as reviewer drift

If nothing survives the filter, the recommendation is rewritten to `approve` and a `code_review_auto_resolved` event is logged.

Net effect: requested changes are made once, then approved. The workflow no longer cycles through three attempts collecting a new set of complaints each round.

### Tuning

| Knob | Location | Notes |
|---|---|---|
| `MAX_REVISION_ATTEMPTS` | `nodes.py` | Currently `3`. Acts as a safety net; in practice runs approve on attempt 2. |
| Overlap threshold | `_is_previously_raised()` | `0.35`. Lower to `0.25` if genuine unresolved items get dropped; raise to `0.45` if new items still slip through. |
| Plan clip size | `clip(..., 4000)` | Raised from `1500`. Below ~4000 the plan JSON gets cut mid-structure after a revision, and reviewers invent "incomplete plan" findings that are really truncation artifacts. |

---

## Observability

### Structured logging

Each important node emits JSON logs:

- `node_started` / `node_completed` / `node_failed`
- `duration_ms` (per-node latency)
- `thread_id`, `status`, and error message when failed
- domain events: `implementation_summary`, `code_review_summary`, `code_review_auto_resolved`, `human_approval_summary`, `git_automation_summary`

This makes it easy to see which agent was slow or failed in the server console.

### LangSmith

With LangSmith enabled, each workflow run is traced in the LangSmith UI:

- full graph / LLM call timeline
- per-call latency
- prompts, responses, and token usage (where available)

Optional env:

```env
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_key
LANGSMITH_PROJECT=DevFlow-AI
```

Local logs = ops view · LangSmith = deep LLM/debug view.

---

## Safety

- No automatic merge to `main`
- Suggested code lands under `generated/` (not live app paths by default)
- Git automation runs only after approval status is `approved`
- Critical-severity review items are never auto-dismissed by the revision guard
- Secrets via `.env` only

---

## Quick start

```bash
pip install -r requirements.txt
uvicorn src.api.main:app --reload --port 8000
```

Run from a user request:

```bash
curl -X POST http://127.0.0.1:8000/workflow/run ^
  -H "Content-Type: application/json" ^
  -d "{\"user_request\": \"Add invoice PDF download for approved vendors\"}"
```

Run from a Jira ticket:

```bash
curl -X POST http://127.0.0.1:8000/workflow/run ^
  -H "Content-Type: application/json" ^
  -d "{\"jira_ticket_id\": \"KAN-1\", \"user_request\": \"\"}"
```

Provide at least one of `user_request` or `jira_ticket_id`.

---
