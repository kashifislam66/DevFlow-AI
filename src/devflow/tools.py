import os, ast
from langchain_core.tools import tool
from pypdf import PdfReader
from .integrations.github_adapter import GitHubAdapter
from .integrations.jira_adapter import JiraAdapter

@tool
def list_files(directory: str = ".") -> str:
    """List all files and folders in the given directory."""
    files = os.listdir(directory)
    try:
        if not files:
            return f"Directory '{directory}' is empty."
        return f"Files in '{directory}':\n" + "\n".join(f"- {f}" for f in files)
    except Exception as e:
        return f"Error listing files in '{directory}': {str(e)}"

@tool
def read_file(file_path: str) -> str:
    """
    Read the content of a file with safety checks and limits.
    """
    max_chars = 3000

    # 1. Check if file exists
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' does not exist."
    
    # 2. Check if path is actually a file
    if not os.path.isfile(file_path):
        return f"Error: '{file_path}' is not a file."

    try:
        # 3. Read content safely
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read(max_chars)
            
            # 4. Check if file was truncated due to max_chars limit
            if file.read(1):  # Check whether the content was truncated.
                content += f"\n\n[Note: File is large; only the first {max_chars} characters were read.]"
                
            return content

    except UnicodeDecodeError:
        return "Error: File could not be decoded; it may be binary or non-text."
    except PermissionError:
        return f"Error: Permission denied while reading '{file_path}'."
    except Exception as e:
        return f"Error reading file: {str(e)}"

@tool
def extract_pdf_text(pdf_path: str) -> str:
    """Extract text content from a PDF file."""
    if not os.path.exists(pdf_path):
        return f"Error: File '{pdf_path}' does not exist."
    
    # 2. Check if path is actually a file
    if not os.path.isfile(pdf_path):
        return f"Error: '{pdf_path}' is not a file."
    
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    
    try:
        output_chunks = [
            "=== PDF Content ===",
            f"Total Pages: {total_pages}"
        ]
        for i in range(total_pages):
            page = reader.pages[i]
            output_chunks.append(f"--- Page {i + 1} ---")
            clean_text = page.extract_text().strip()
            output_chunks.append(clean_text)
        final_single_string = "\n\n".join(output_chunks)
        
        return final_single_string
        
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


@tool
def analyze_python_file(file_path: str) -> str:
  """Analyze a Python file and extract functions, classes, and imports."""

  # Check file existence.
  if not os.path.exists(file_path):
    return f"Error: File '{file_path}' does not exist."

  if not os.path.isfile(file_path):
    return f"Error: '{file_path}' is not a file."

  # Read and parse the file.
  try:
    with open(file_path, "r", encoding="utf-8") as file:
      code = file.read()

    tree = ast.parse(code)
  except SyntaxError as e:
    return f"Error: Python syntax error: {str(e)}"
  except Exception as e:
    return f"Error reading or parsing file: {str(e)}"

  # Extract imports, classes, and functions.
  imports = []
  classes = []
  functions = []

  for node in ast.walk(tree):
    # Direct imports (for example, import os).
    if isinstance(node, ast.Import):
      for alias in node.names:
        imports.append(alias.name)

    # From imports (for example, from typing import List).
    elif isinstance(node, ast.ImportFrom):
      module = node.module if node.module else ""
      for alias in node.names:
        imports.append(f"{module}.{alias.name}" if module else alias.name)

    # Classes.
    elif isinstance(node, ast.ClassDef):
      classes.append(node.name)

    # Functions (top-level and methods).
    elif isinstance(node, ast.FunctionDef):
      functions.append(node.name)

  # Format the analysis result.
  output_chunks = [
      f"=== AST Code Analysis: {file_path} ===",
      f"Imports ({len(imports)}): "
      + (", ".join(imports) if imports else "None"),
      f"Classes ({len(classes)}): "
      + (", ".join(classes) if classes else "None"),
      f"Functions ({len(functions)}): "
      + (", ".join(functions) if functions else "None"),
  ]

  return "\n".join(output_chunks)

@tool
def get_github_repo_info() -> str:
    """Get basic information about the configured GitHub repository."""
    try:
        adapter = GitHubAdapter()
        return adapter.get_repo_info()
    except Exception as e:
        return f"Error fetching GitHub repo info: {str(e)}"

@tool
def list_github_branches() -> str:
    """Get branch list of the configured GitHub repository."""
    try:
        adapter = GitHubAdapter()
        return adapter.list_branches()
    except Exception as e:
        return f"Error fetching GitHub repo info: {str(e)}"

@tool
def create_github_branch(branch_name: str, source_branch: str = "main") -> str:
    """Create a new branch in the configured GitHub repository."""
    try:
        adapter = GitHubAdapter()
        return adapter.create_branch(branch_name, source_branch)
    except Exception as e:
        return f"Error creating GitHub branch: {str(e)}"

@tool
def create_github_pr(title: str, body: str, head: str, base: str = "main") -> str:
    """Create a pull request. Returns PR URL on success."""
    try:
        adapter = GitHubAdapter()
        return adapter.create_pull_request(title, body, head, base)
    except Exception as e:
        return f"Error creating GitHub PR: {str(e)}"


@tool
def get_jira_ticket(ticket_id: str) -> str:
    """Fetch details of a Jira ticket by its ID (e.g. PROJ-123)."""
    try:
        adapter = JiraAdapter()
        return adapter.get_ticket(ticket_id)
    except Exception as e:
        return f"Error: {str(e)}"


tools = [
    list_files,
    read_file,
    extract_pdf_text
]
