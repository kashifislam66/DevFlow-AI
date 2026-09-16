from devflow.graph import run_devflow
from devflow.tools import list_files, read_file, extract_pdf_text, get_jira_ticket
from devflow.integrations.github_adapter import GitHubAdapter
from devflow.integrations.jira_adapter import JiraAdapter

if __name__ == "__main__":

    # jira_client = JiraAdapter()
    user_input = "Write a function in [React/Node.js/Python/etc.] that generates a downloadable PDF invoice for a vendor. The download action should only be permitted if the vendor's approval status is set to 'Approved'. Include standard invoice fields like Invoice Number, Date, Line Items, Total Amount, and Vendor details."
    # repo_info = get_jira_ticket.invoke({"ticket_id": "KAN-1"})

    # # 3. Output print karein
    # print("=== GitHub Repo Info ===")
    # print(repo_info)

    # print("\n--- Running DevFlow Day 1 ---\n")
    result = run_devflow(user_input, thread_id="devflow-1")

    # print(result)

    # print("User Request     :", result["user_request"])
    # print("\nRequirement     :", result["requirement"])
    # print("\nArchitecture    :\n", result["architecture"])
    # print("\ncurrent agent     :", result["current_agent"])
    # print("\nrequested agents    :\n", result["requested_agents"])
    # print("\ncompleted agents    :\n", result["completed_agents"])
    # print("\nFile List:\n", result.get("file_list", ""))
    # print("\nFile Read:\n", result.get("readme_content", ""))
    # print("\nPdf content:\n", result.get("pdf_content", ""))
    # print("\nFinal Response  :\n", result["final_response"])
    # print("\nmessages  :\n", result["messages"])
    # print("Ast analysis     :", result["ast_analysis"])
    # print("\nImplementation Plan:\n", result["implementation_plan"]),
    # print("\nTesting Plan:\n", result["testing_plan"]),
    # print("\nSecurity Review:\n", result["security_review"]),
    # print("\nCode Review:\n", result["code_review"]),
    # print("\n Approval Status:\n", result["approval_status"])
    print("\nGenerated Code:\n", result["generated_code"])
    print("\ncommit_result:\n", result["commit_result"])

    

    # from src.devflow.tools import list_files

    # # Test 1: current directory
    # print(extract_pdf_text.invoke({"pdf_path": "data/Kashif_Islam_Resume_GCC.pdf"}))

    # print("\n" + "="*50 + "\n")

    # # Test 2: src directory
    # print(list_files.invoke({"directory": "src"}))