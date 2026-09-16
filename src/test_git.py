import json
from devflow.nodes import git_automation_node  # Import path set kar lein


def test_git_node_only():
  # Mock state structure for the standalone test.
  mock_state = {
      "user_request": "generate invoice PDF download feature",
      "implementation_plan": (
          "### Plan\nAdd PDF download endpoint with vendor authorization."
      ),
      "approval_status": "approved",
      "approval_feedback": "Approved via manual review",
      "completed_agents": [
          "implementation_node",
          "security_node",
          "code_generation_node",
      ],
      # Code-generation output format.
      "generated_code": {
          "summary": "PDF invoice generation feature",
          "files": [
              {
                  "path": "backend/app/services/InvoiceService.py",
                  "content": (
                      "from fastapi import HTTPException\n\ndef"
                      " download_invoice():\n    pass"
                  ),
              },
              {
                  "path": (
                      "frontend/src/components/InvoiceDownloadButton.js"
                  ),
                  "content": "import React from 'react';",
              },
          ],
      },
  }

  print("🚀 Testing git_automation_node in isolation...\n")

  # Direct node call
  result = git_automation_node(mock_state)

  print("--- Test Results ---")
  print(f"Git Branch Result  : {result.get('git_result')}")
  print(f"Commit Results     : {result.get('commit_result')}")
  print(f"PR Creation Result : {result.get('pr_result')}\n")
  print("--- Final Response ---")
  print(result.get("final_response"))


if __name__ == "__main__":
  test_git_node_only()
