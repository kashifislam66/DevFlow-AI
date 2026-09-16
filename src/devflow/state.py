from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

class DevFlowState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    user_request: str
    requirement: str
    architecture: str
    requested_agents: list[str]
    current_agent: str
    completed_agents: list[str]
    file_list: str
    readme_content: str
    pdf_content: str
    ast_analysis:str
    implementation_plan: str
    security_review: str
    testing_plan: str
    code_review: str
    review_feedback: str
    applied_review_feedback: str
    approval_status: str
    approval_feedback: str
    force_approve: bool
    revision_count: int
    git_result: str
    pr_result: str
    commit_result: list[str]
    final_response: str        # Final output
    generated_code: str
