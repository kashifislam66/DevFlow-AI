from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from .state import DevFlowState
from .nodes import (requirement_node,
architecture_node,
decide_next_agent, 
supervisor_node, 
after_requirement_router,
codebase_inspector_node,
pdf_extractor_node,
implementation_node,
testing_node,
security_node,
code_review_node,
human_approval_node,
after_approval_router,
git_automation_node,
memory_store_node,
code_generation_node
)

memory = MemorySaver()
builder = StateGraph(DevFlowState)

builder.add_node("pdf_extractor_node", pdf_extractor_node)

builder.add_node(
    "supervisor_node",
    supervisor_node
    )

builder.add_node(
    "codebase_inspector_node",
    codebase_inspector_node
    )

builder.add_node(
    "after_requirement_router",
    after_requirement_router
)

builder.add_node(
    "human_approval_node",
    human_approval_node
)

builder.add_node(
    "requirement_node",
    requirement_node
    )
builder.add_node(
    "architecture_node",
     architecture_node
    )

builder.add_node(
    "implementation_node",
     implementation_node
    )

builder.add_node(
    "testing_node",
     testing_node
    )

builder.add_node(
    "security_node",
     security_node
    )

builder.add_node(
    "code_review_node",
    code_review_node
    )

builder.add_node(
    "git_automation_node",
    git_automation_node
    )

builder.add_node(
    "memory_store_node",
    memory_store_node
    )

builder.add_node(
    "code_generation_node",
    code_generation_node
    )


builder.add_edge(
    START, 
    "supervisor_node"
    )

# builder.add_edge(
#     "pdf_extractor_node",
#     "supervisor_node"
#     )

builder.add_conditional_edges(
    "supervisor_node",
    decide_next_agent,
    {
        "requirement_node": "requirement_node",
        "architecture_node": "architecture_node",
    }
)
builder.add_conditional_edges(
    "requirement_node",
    after_requirement_router,
    {
        "architecture_node": "architecture_node",
        END:END,
    }
)

builder.add_edge(
    "architecture_node", 
    "implementation_node"
    )

builder.add_edge(
    "implementation_node", 
    "testing_node"
    )

builder.add_edge(
    "testing_node", 
    "security_node"
    )

builder.add_edge(
    "security_node", 
    "code_review_node"
    )

builder.add_edge(
    "code_review_node", 
    "human_approval_node"
    )

builder.add_conditional_edges(
    "human_approval_node",
    after_approval_router,
    {
        "approved_path": "code_generation_node",
        "implementation_node": "implementation_node",
        "pending_path": END,
        "max_revisions_reached": END,
    }
)

builder.add_edge(
    "code_generation_node",
    "git_automation_node"
)
builder.add_edge(
    "git_automation_node",
    "memory_store_node"
    )
builder.add_edge(
    "memory_store_node",
    END
    )


builder.add_edge(
    "codebase_inspector_node",
    END
    )


graph = builder.compile(checkpointer=memory)

def run_devflow(user_request: str, thread_id: str = "devflow-1", force_approve: bool = False) -> dict:
    """Run the DevFlow workflow for one request."""
    initial_state = {
        "user_request": user_request,
        "thread_id": thread_id,
        "messages": [],
        "ast_analysis": "",
        "requirement": "",
        "architecture": "",
        "final_response": "",
        "requested_agents": [],
        "current_agent": "",
        "implementation_plan": "",
        "testing_plan":"",
        "security_review":"",
        "code_review":"",
        "review_feedback": "",
        "applied_review_feedback": "",
        "completed_agents": [],
        "approval_status": "",
        "approval_feedback": "",
        "force_approve": force_approve,
        "revision_count": 0,
        "git_result": "",
        "pr_result": "",
    }

    config = {
        "configurable": {"thread_id": thread_id},
        "tags": ["devflow", "workflow"],
        "metadata": {
            "app": "DevFlow-AI",
            "source": "api",  # "cli"
        },
    }
    
    config = {"configurable": {"thread_id": thread_id}}
    return graph.invoke(initial_state, config=config)
