# DevFlow-AI

DevFlow-AI is a LangGraph workflow that turns a feature request into a reviewed implementation plan, optional generated code, and GitHub automation.

## Workflow

`PDF extraction → supervisor → requirements → architecture → implementation plan → testing → security → code review → approval → code generation → GitHub → memory`

The PDF extraction step reads the configured local PDF when present. Requirements and architecture are deterministic nodes; planning, testing, security review, code review, and code generation use structured LLM outputs.

## Revision flow

The review loop is bounded to three implementation attempts:

1. `code_review_node` produces structured review items and converts requested changes into canonical `review_feedback`.
2. `human_approval_node` uses the review recommendation. A rejected review routes back to `implementation_node` only while fewer than three attempts have run.
3. `implementation_node` receives the latest canonical feedback and the previous plan. It preserves valid prior work, maps every requested change in `addressed_review_items`, then clears old testing, security, approval, and review artifacts.
4. Testing, security, and code review run against that new plan. The reviewer receives the feedback applied to the revision so it can verify closure rather than repeat stale findings.
5. An approval proceeds to code generation even on attempt three. A third rejected attempt exits as `max_revisions_reached`; it never starts a fourth LLM revision.

`force_approve` is an explicit API option for controlled automation/testing. It defaults to `false`.

## API

Start the FastAPI app with your preferred ASGI server, then call:

```http
POST /workflow/run
Content-Type: application/json

{
  "user_request": "Add invoice PDF download for approved vendors",
  "thread_id": "feature-123",
  "force_approve": false
}
```

Use a distinct `thread_id` per independently resumable workflow. Configure Ollama and any GitHub/Jira credentials through environment variables before enabling those integrations.
