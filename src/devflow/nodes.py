from .state import DevFlowState
import json, re 
from .logging_utils import node_timer, log_event
from .integrations.github_adapter import GitHubAdapter
from .token_utils import clip
from .memory import store_memory
from .tools import list_files, read_file, extract_pdf_text, analyze_python_file
from langchain_core.messages import HumanMessage, SystemMessage
from config import llm_with_tools, implementation_llm, testing_llm, structured_security_llm, structured_code_review_llm, llm_with_code_generation
from .prompt import IMPLEMENTATION_PROMPT_TEMPLATE, TESTING_PROMPT_TEMPLATE, SECURITY_PROMPT_TEMPLATE, CODE_REVIEW_PROMPT_TEMPLATE, CODE_GENERATION_PROMPT_TEMPLATE

MAX_REVISION_ATTEMPTS = 3


def format_review_feedback(review: dict, attempt: int) -> str:
    """Create the canonical, actionable feedback payload for a revision."""
    items = review.get("items", [])
    changes = []
    for item in items:
        if not isinstance(item, dict):
            continue
        action = (item.get("suggestion") or item.get("comment") or "").strip()
        if not action:
            continue
        category = item.get("category", "quality")
        severity = item.get("severity", "medium")
        changes.append(f"- [{category}/{severity}] {action}")

    if not changes:
        return ""
    return f"REQUIRED CHANGES FROM REVIEW ATTEMPT {attempt}:\n" + "\n".join(changes)


def requirement_node(state: DevFlowState) -> dict:
    """
    Extract requirements and source tracking from the request and PDF content.
    """
    # Extract inputs.
    user_request_raw = state.get("user_request", "")
    pdf_content_raw = state.get("pdf_content", "")
    completed = state.get("completed_agents", [])
    requested_agents = state.get("requested_agents", [])

    # Text normalization for analysis
    user_req_lower = user_request_raw.lower()
    pdf_lower = pdf_content_raw.lower()
    combined_text = f"{user_req_lower} {pdf_lower}"

    # Track keywords and sources.
    keywords = ["pdf", "download", "invoice", "vendor", "auth", "payment"]
    found_in_user = [kw for kw in keywords if kw in user_req_lower]
    found_in_pdf = [kw for kw in keywords if kw in pdf_lower]
    found_keywords = list(set(found_in_user + found_in_pdf))

    # Determine source based on where keywords/content were found
    if found_in_user and found_in_pdf:
        source_str = "User Request + PDF"
    elif found_in_pdf:
        source_str = "PDF Content"
    elif found_in_user:
        source_str = "User Request"
    else:
        source_str = "User Request" if user_request_raw else "Unknown"

    # Build the requirement record.
    if found_keywords:
        feature_parts = []
        actors_parts = []
        action_parts = []

        if "invoice" in found_keywords or "pdf" in found_keywords or "download" in found_keywords:
            feature_parts.append("Invoice PDF Download")
            action_parts.append("Download approved invoices as PDF")
        
        if "vendor" in found_keywords:
            actors_parts.append("Approved Vendors")
            
        if "auth" in found_keywords:
            feature_parts.append("Authentication & Authorization")
            action_parts.append("Verify user access permissions")

        if "payment" in found_keywords:
            feature_parts.append("Payment Processing")

        feature_str = " / ".join(feature_parts) if feature_parts else "General Feature"
        actors_str = ", ".join(actors_parts) if actors_parts else "System Users"
        action_str = " & ".join(action_parts) if action_parts else "Process requested operations"

        requirement = (
            f"Feature: {feature_str}\n"
            f"Actors: {actors_str}\n"
            f"Action: {action_str}\n"
            f"Sources: {source_str}"
        )
    else:
        # Fallback handling
        requirement = (
            "Feature: General Request\n"
            "Actors: System Users\n"
            f"Action: Process request - '{user_request_raw}' (No domain keywords detected)\n"
            f"Sources: {source_str}"
        )

    final_response = (
        "=== Requirement Record ===\n"
        f"[Requirement Summary]\n{requirement}\n\n"
    )

    # Return the state update.
    if "architecture_node" in requested_agents:
        return {
            "requirement": requirement,
            "completed_agents": completed + ["requirement_node"]    
        }
    else:
        return {
            "requirement": requirement,
            "completed_agents": completed + ["requirement_node"],
            "final_response": final_response
        } 
    


def architecture_node(state: DevFlowState) -> dict:
    """
    Generate architecture suggestions from the requirement.
    """
    requirement = state.get("requirement", "")
    completed = state["completed_agents"]
    req_lower = requirement.lower()

    # Collect dynamic suggestions.
    backend_tech = []
    frontend_tech = ["React (Tailwind CSS)"]
    database_tech = ["PostgreSQL"]
    security_auth = []
    extra_features = []

    # Detect authentication and vendor requirements.
    if any(kw in req_lower for kw in ["auth", "login", "vendor", "user"]):
        security_auth.append("JWT Bearer Authentication")
        security_auth.append("Role-Based Access Control (RBAC)")

    # Detect PDF, download, invoice, and file requirements.
    if any(kw in req_lower for kw in ["pdf", "download", "invoice", "file"]):
        backend_tech.append("FastAPI / Laravel (StreamingResponse / File Stream)")
        extra_features.append("S3 / Local Storage Bucket for Generated Files")
        extra_features.append("PDF Generator Library (e.g., ReportLab / Dompdf)")
    else:
        backend_tech.append("FastAPI / Laravel")

    # Detect payment requirements.
    if "payment" in req_lower:
        security_auth.append("Stripe / Payment Gateway SDK Integration")
        extra_features.append("Webhook listener for payment status updates")

    # Fallback default values
    if not security_auth:
        security_auth.append("Standard Session / API Key Auth")

    # Architectural output string formatting
    arch_components = [
        f"- Backend: {', '.join(backend_tech)}",
        f"- Frontend: {', '.join(frontend_tech)}",
        f"- Database: {', '.join(database_tech)}",
        f"- Auth & Security: {', '.join(security_auth)}"
    ]

    if extra_features:
        arch_components.append(f"- Services & Modules: {', '.join(extra_features)}")

    architecture_str = "\n".join(arch_components)

    # Clean multi-line final response structure
    final_response = (
        "=== Architecture Decision Record ===\n"
        f"[Requirement Summary]\n{requirement}\n\n"
        f"[Suggested Architecture]\n{architecture_str}"
    )

    return {
        "architecture": architecture_str,
        "completed_agents": completed + ["architecture_node"],
        "final_response": final_response
    }

def supervisor_node(state: DevFlowState) -> dict:

    user_request_raw = state["user_request"]
    user_request = user_request_raw.lower()

    if "architecture" in user_request and "requirement" in user_request:
        return {
                    "requested_agents": ["requirement_node", "architecture_node"],
                    "current_agent": "requirement_node",   # pehla agent
                }
    elif "architecture" in user_request:
        return {
                    "requested_agents": [ "architecture_node"],
                    "current_agent": "architecture_node",   # pehla agent
                }
    elif "requirement" in user_request:
        return {
                    "requested_agents": ["requirement_node"],
                    "current_agent": "requirement_node",   # pehla agent
                }
    else:

        return {
                    "requested_agents": ["requirement_node", "architecture_node"],
                    "current_agent": "requirement_node",   # pehla agent
                }

def decide_next_agent(state: DevFlowState) -> str:
    # Return the selected node name.
    return state["current_agent"]

def after_requirement_router(state: DevFlowState) -> str:
    requested_agents = state["requested_agents"]

    if "architecture_node" in requested_agents:
        return "architecture_node"
    else:
        return END

def codebase_inspector_node(state: DevFlowState) -> dict:
    completed = state.get("completed_agents", [])
    file_list = list_files.invoke({"directory": "."})

    file_read = read_file.invoke({"file_path": "README.md"})

    ast_analysis = analyze_python_file.invoke({
        "file_path": "src/devflow/nodes.py"
    })

    return {
            "file_list": file_list,
            "readme_content": file_read,
            "completed_agents": completed + ["codebase_inspector_node"],
            "ast_analysis": ast_analysis
        } 

def pdf_extractor_node(state: DevFlowState) -> dict:
    completed = state.get("completed_agents", [])
    pdf_data = extract_pdf_text.invoke({"pdf_path": "data/Kashif_Islam_Resume_GCC.pdf"})


    return {
            "pdf_content": pdf_data,
            "completed_agents": completed + ["pdf_extractor_node"]
        }


def implementation_node(state: DevFlowState) -> dict:

    user_request_raw = state.get("user_request", "")
    requirement_raw = state.get("requirement", "")
    architecture_raw = state.get("architecture", "")

    previous_plan = clip(state.get("implementation_plan", ""), 4000)
    revision_feedback = clip(state.get("review_feedback", ""), 4000)

    completed = state.get("completed_agents", [])
    revision_count = state.get("revision_count", 0)
    thread_id = state.get("thread_id")
    with node_timer("implementation_node", thread_id=thread_id):

        full_context = (
            f"REQUEST:\n{user_request_raw}\n\nREQUIREMENTS:\n{requirement_raw}\n"
            f"\nARCHITECTURE:\n{architecture_raw}\n\nATTEMPT: {revision_count + 1}"
        )
        if revision_count and previous_plan:
            full_context += f"\n\nPREVIOUS PLAN (preserve valid work):\n{previous_plan}"
        if revision_feedback:
            full_context += f"\n\n{revision_feedback}"

        formatted_prompt = IMPLEMENTATION_PROMPT_TEMPLATE.format(
            user_message=full_context
        )

        result = implementation_llm.invoke(formatted_prompt)

        plan_json = result.model_dump_json(indent=2)

        log_event(
            "implementation_summary",
            thread_id=thread_id,
            overall_risk=getattr(result, "overall_risk", None),
        )

        return {
            "implementation_plan": plan_json,
            "approval_status": "",
            "approval_feedback": "",
            "applied_review_feedback": revision_feedback,
            "review_feedback": "",
            "completed_agents": completed + ["implementation_node"],
            "revision_count": revision_count + 1
        }

def testing_node(state: DevFlowState) -> dict:

    implementation_plan_raw = clip(state.get("implementation_plan", ""), 4000)
    completed = state["completed_agents"]
    thread_id = state.get("thread_id")
    with node_timer("testing_node", thread_id=thread_id):
        formatted_prompt = TESTING_PROMPT_TEMPLATE.format(
            implementation_plan=implementation_plan_raw
        )

        result = testing_llm.invoke(formatted_prompt)

        plan_json = result.model_dump_json(indent=2)

        log_event(
            "testing_summary",
            thread_id=thread_id,
            overall_risk=getattr(result, "overall_risk", None),
        )

        return {
            "testing_plan": plan_json,
            "completed_agents": completed + ["testing_node"]
        }

def security_node(state: DevFlowState) -> dict:

    implementation_plan_raw = clip(state.get("implementation_plan", ""), 4000)
    completed = state["completed_agents"]
    thread_id = state.get("thread_id")
    with node_timer("security_node", thread_id=thread_id):
        formatted_prompt = SECURITY_PROMPT_TEMPLATE.format(
            implementation_plan=implementation_plan_raw
        )

        result = structured_security_llm.invoke(formatted_prompt)

        plan_json = result.model_dump_json(indent=2)

        log_event(
            "security_summary",
            thread_id=thread_id,
            overall_risk=getattr(result, "overall_risk", None),
        )

        return {
            "security_review": plan_json,
            "completed_agents": completed + ["security_node"]
        }

def code_review_node(state: DevFlowState) -> dict:
    implementation_plan_raw = clip(state.get("implementation_plan", ""), 4000)
    testing_plan_raw = clip(state.get("testing_plan", ""), 4000)
    security_review_raw = clip(state.get("security_review", ""), 4000)
    previous_feedback = state.get("applied_review_feedback", "") or "None"
    revision_count = state.get("revision_count", 0)
    completed = state.get("completed_agents", [])
    thread_id = state.get("thread_id")
    with node_timer("code_review_node", thread_id=thread_id):

        formatted_prompt = CODE_REVIEW_PROMPT_TEMPLATE.format(
            implementation_plan=implementation_plan_raw,
            testing_plan=testing_plan_raw,
            security_review=security_review_raw,
            previous_feedback=previous_feedback,
            revision_count=revision_count,
        )

        result = structured_code_review_llm.invoke(formatted_prompt)

        plan_json = result.model_dump_json(indent=2)
        review_data = result.model_dump()
        review_feedback = ""
        if review_data.get("recommendation", "").strip().lower() == "request_changes":
            review_feedback = format_review_feedback(review_data, revision_count)
        
        log_event(
            "code_review_summary",
            thread_id=thread_id,
            overall_risk=getattr(result, "overall_risk", None),
        )

        return {
            "code_review": plan_json,
            "review_feedback": review_feedback,
            "completed_agents": completed + ["code_review_node"],
        }

def human_approval_node(state: DevFlowState) -> dict:
    """Map the structured review recommendation to workflow approval state."""
    code_review = state.get("code_review", "")
    completed = state.get("completed_agents", [])
    thread_id = state.get("thread_id") or state.get("user_request", "")[:40]

    with node_timer("human_approval_node", thread_id=thread_id):  # Fix timer label

        if state.get("force_approve", False):
            approval_status = "approved"
            feedback = "Approval was explicitly forced by the caller."
            
            # Log event for forced approval
            log_event(
                "human_approval_summary",
                thread_id=thread_id,
                approval_status=approval_status,
                recommendation="forced",
                forced=True,
            )

            return {
                "approval_status": approval_status,
                "approval_feedback": feedback,
                "completed_agents": completed + ["human_approval_node"],
            }

        try:
            code_review_data = json.loads(code_review)
            recommendation = code_review_data.get("recommendation", "").strip().lower()
            summary = code_review_data.get("summary", "")
            feedback = state.get("review_feedback", "") or summary
        
            # Status Mapping Logic
            if recommendation == "approve":
                approval_status = "approved"
                feedback = "Plan approved automatically by system review."
            elif recommendation == "request_changes":
                if state.get("revision_count", 0) >= MAX_REVISION_ATTEMPTS:
                    approval_status = "max_revisions_reached"
                    feedback = f"Maximum of {MAX_REVISION_ATTEMPTS} implementation attempts reached. Outstanding feedback:\n{feedback or summary}"
                else:
                    approval_status = "rejected"
                    feedback = f"Changes requested:\n{feedback or summary}"
            else:  # needs_discussion or fallback
                approval_status = "pending"
                feedback = f"Manual discussion required:\n{feedback or 'No review rationale was provided.'}"

            # Log event here before returning
            log_event(
                "human_approval_summary",
                thread_id=thread_id,
                approval_status=approval_status,
                recommendation=recommendation,
                revision_count=state.get("revision_count", 0),
            )

            res_dict = {
                "approval_status": approval_status,
                "approval_feedback": feedback,
                "completed_agents": completed + ["human_approval_node"],
            }
            if approval_status == "max_revisions_reached":
                res_dict["final_response"] = feedback

            return res_dict

        except json.JSONDecodeError:
            log_event(
                "human_approval_summary",
                thread_id=thread_id,
                approval_status="pending",
                error="Invalid JSON in code review",
            )
            return {
                "approval_status": "pending",
                "approval_feedback": "Invalid JSON in code review. Manual review required.",
                "completed_agents": completed + ["human_approval_node"],
            }
def code_generation_node(state: DevFlowState) -> dict:
    """Generate code from the approved implementation plan."""
    requirement_raw = state.get("requirement", "")
    implementation_plan = clip(state.get("implementation_plan", ""), 4000)
    security_review = clip(state.get("security_review", ""), 4000)
    completed = state.get("completed_agents", [])

    formatted_prompt = CODE_GENERATION_PROMPT_TEMPLATE.format(
        implementation_plan=implementation_plan,
        requirement_raw=requirement_raw,
        security_review=security_review,
    )

    generated_code = llm_with_code_generation.invoke(formatted_prompt)
    generated_code_json = generated_code.model_dump_json(indent=2)
    return {
        "generated_code": generated_code_json,
        "completed_agents": completed + ["code_generation_node"]
    }

def slugify(text: str) -> str:
    """Create a clean branch-name slug from a user request."""
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    return re.sub(r'[\s_]+', '-', text).strip('-')[:30]


def git_automation_node(state: DevFlowState) -> dict:
    """Create a GitHub branch and pull request for approved output."""

    user_request_raw = state.get("user_request", "")
    implementation_plan = state.get("implementation_plan", "")
    approval_status = state.get("approval_status", "")
    approval_feedback = state.get("approval_feedback", "")
    completed = state.get("completed_agents", [])
    thread_id = state.get("thread_id") or user_request_raw[:40]

    git_result = "Skipped"
    pr_result = "N/A"
    commit_results = []
    branch_name = None

    with node_timer("git_automation_node", thread_id=thread_id):

        if approval_status == "approved":

            try:
                github = GitHubAdapter()

                # 1. Generate branch name
                branch_slug = slugify(user_request_raw) or "feature-update"
                branch_name = f"feature/{branch_slug}"

                # 2. Create branch
                branch_res = github.create_branch(
                    new_branch_name=branch_name
                )
                git_result = branch_res

                # 3. commit plan file
                plan_commit = github.commit_file(
                    file_path=f"docs/devflow-plans/{branch_slug}.md",
                    commit_message="chore: add DevFlow implementation plan",
                    branch_name=branch_name,
                    content=implementation_plan[:8000]
                )

                commit_results.append(f"Plan: {plan_commit}")

                # 4. Commit generated code files
                generated_raw = state.get("generated_code", "")

                if generated_raw:

                    files = []

                    # Safe multi-format extraction
                    if hasattr(generated_raw, "files"):
                        files = generated_raw.files
                    elif hasattr(generated_raw, "model_dump"):
                        files = generated_raw.model_dump().get("files", [])
                    elif isinstance(generated_raw, dict):
                        files = generated_raw.get("files", [])
                    elif isinstance(generated_raw, str) and generated_raw.strip():
                        try:
                            data = json.loads(generated_raw)
                            files = data.get("files", [])
                        except json.JSONDecodeError:
                            commit_results.append("Invalid JSON string in generated_code")

                    # Iterate and commit files
                    for f in files:
                        if isinstance(f, dict):
                            rel_path = str(f.get("path", "")).lstrip("/")
                            code_content = f.get("content", "")
                        else:
                            rel_path = str(getattr(f, "path", "")).lstrip("/")
                            code_content = getattr(f, "content", "")

                        if not rel_path or not code_content:
                            continue

                        repo_path = f"generated/{rel_path}"

                        commit_res = github.commit_file(
                            file_path=repo_path,
                            commit_message=f"feat: add suggested {rel_path}",
                            branch_name=branch_name,
                            content=code_content,
                        )
                        commit_results.append(f"{rel_path}: {commit_res}")

                # 5. Create PR only if commits succeeded
                pr_title = f"feat: {user_request_raw[:50]}"

                pr_body = (
                    f"### User Request\n"
                    f"{user_request_raw}\n\n"
                    f"### Implementation Plan Summary\n"
                    f"```json\n"
                    f"{implementation_plan}\n"
                    f"```\n\n"
                    f"### Security & Testing\n"
                    f"Approved via DevFlow AI Workflow."
                )

                if any(str(c).startswith("Error") for c in commit_results):
                    pr_result = "Skipped: Commit failed"
                    final_response = (
                        "GitHub Automation Failed!\n"
                        f"- Git Result: {git_result}\n"
                        f"- Commit Result: {commit_results}\n"
                        f"- PR Result: {pr_result}"
                    )
                else:
                    pr_result = github.create_pull_request(
                        title=pr_title,
                        body=pr_body,
                        head=branch_name,
                        base="main",
                    )
                    final_response = (
                        "GitHub Automation Completed Successfully!\n"
                        f"- Branch: {branch_name}\n"
                        f"- Commits: {commit_results}\n"
                        f"- PR: {pr_result}"
                    )

            except Exception as e:

                git_result = git_result if git_result != "Skipped" else "Failed"
                commit_results = commit_results if commit_results else ["Failed"]
                pr_result = f"Failed: {str(e)}"

                final_response = (
                    "GitHub Automation Failed!\n"
                    f"- Git Result: {git_result}\n"
                    f"- Commit Result: {commit_results}\n"
                    f"- PR Result: {pr_result}"
                )

        else:

            final_response = (
                f"GitHub automation halted "
                f"(Status: {approval_status}).\n"
                f"Feedback: {approval_feedback}"
            )

        # Log event summary
        log_event(
            "git_automation_summary",
            thread_id=thread_id,
            approval_status=approval_status,
            branch_name=branch_name,
            total_commits=len(commit_results),
            pr_result=pr_result,
            status="success" if "Successfully" in final_response else "halted_or_failed"
        )

    return {
        "git_result": git_result,
        "commit_result": commit_results,
        "pr_result": pr_result,
        "final_response": final_response,
        "completed_agents": completed + ["git_automation_node"],
    }
def after_approval_router(state: DevFlowState) -> str:
    status = state.get("approval_status", "pending")
    revision_count = state.get("revision_count", 0)
    if status == "approved":
        return "approved_path"
    if status == "max_revisions_reached" or revision_count >= MAX_REVISION_ATTEMPTS:
        return "max_revisions_reached"
    elif status == "rejected":
        return "implementation_node"
    else:
        return "pending_path"

def memory_store_node(state: DevFlowState) -> dict:
    completed = state.get("completed_agents", [])

    # Store a compact workflow memory.
    text = f"""
    User Request: {state.get('user_request','')}
    Architecture: {state.get('architecture','')}
    Implementation Summary: {state.get('implementation_plan','')[:1500]}
    Security: {state.get('security_review','')[:1000]}
    Approval: {state.get('approval_status','')} | {state.get('approval_feedback','')}
    """

    metadata = {
        "type": "workflow_run",
        "approval_status": state.get("approval_status", ""),
        "source": "devflow",
    }

    store_memory(text.strip(), metadata)

    return {
        "completed_agents": completed + ["memory_store_node"]
    }

