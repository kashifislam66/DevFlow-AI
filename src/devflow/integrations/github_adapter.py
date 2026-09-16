import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

class GitHubAdapter:
    def __init__(self):
        token = os.getenv("GITHUB_TOKEN")
        repo_name = os.getenv("GITHUB_REPO")
        
        if not token or not repo_name:
            raise ValueError("GITHUB_TOKEN or GITHUB_REPO missing in .env")
        
        self.client = Github(token)
        self.repo = self.client.get_repo(repo_name)

    def get_repo_info(self) -> str:
        """Basic repository information in string format."""
        
        repo_name = self.repo.full_name
        default_branch = self.repo.default_branch
        description = self.repo.description or "No description provided."
        open_issues = self.repo.open_issues_count
        visibility = "Private" if self.repo.private else "Public"

        info = [
            f"Repo Full Name: {repo_name}",
            f"Default Branch: {default_branch}",
            f"Description: {description}",
            f"Open Issues Count: {open_issues}",
            f"Visibility: {visibility}",
        ]

        return "\n".join(info)

    def get_current_branch(self) -> str:
        """Returns default branch as current active branch."""
        
        return self.repo.default_branch

    def list_branches(self) -> str:
        """List all branches in the repository."""
        try:

            branches = self.repo.get_branches()
            branch_names = [b.name for b in branches]
            
            if not branch_names:
                return f"No branches found in repository '{self.repo}'."
                
            return branch_names
        except Exception as e:
            return f"Error fetching branches for '{self.repo}': {str(e)}"

    def create_branch(self, new_branch_name: str, source_branch: str = None) -> str:
        """Create a new branch from the source branch, or reuse it if it already exists."""

        if source_branch is None:
            source_branch = self.repo.default_branch

        # Check if branch already exists
        try:
            self.repo.get_git_ref(f"heads/{new_branch_name}")
            return f"Branch '{new_branch_name}' already exists — reusing it."
        except Exception as e:
            if e.status != 404:
                raise  # some other real error, don't swallow it

        # Branch doesn't exist yet — create it
        source_ref = self.repo.get_git_ref(f"heads/{source_branch}")
        self.repo.create_git_ref(
            f"refs/heads/{new_branch_name}",
            source_ref.object.sha
        )

        return f"Branch '{new_branch_name}' created successfully from '{source_branch}'."

    def commit_file(self, file_path: str, commit_message: str, branch_name: str, content: str = None) -> str:
        """Commit a file to the specified branch."""
        print(f"Committing file '{file_path}' to branch '{branch_name}' with message '{commit_message}'")
        try:
            if content is None:
                with open(file_path, "r") as f:
                    content = f.read()

            # Check if the file already exists in the branch
            try:
                existing_file = self.repo.get_contents(file_path, ref=branch_name)
                self.repo.update_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    sha=existing_file.sha,
                    branch=branch_name
                )
                return f"File '{file_path}' updated successfully in branch '{branch_name}'."
            except Exception:
                # If the file does not exist, create it
                self.repo.create_file(
                    path=file_path,
                    message=commit_message,
                    content=content,
                    branch=branch_name
                )
                return f"File '{file_path}' created successfully in branch '{branch_name}'."
        except Exception as e:
            return f"Error committing file '{file_path}' to branch '{branch_name}': {str(e)}"

    def create_pull_request(self, title: str, body: str, head: str, base: str) -> str:
        """Create a pull request, or return the existing open one if it already exists."""

        existing = self.repo.get_pulls(
            state="open",
            head=f"{self.repo.owner.login}:{head}",
            base=base
        )
        for pr in existing:
            return pr.html_url  # already exists — reuse it

        pr = self.repo.create_pull(title=title, body=body, head=head, base=base)
        return pr.html_url
