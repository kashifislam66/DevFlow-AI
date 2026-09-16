import os
from jira import JIRA
from dotenv import load_dotenv

load_dotenv()

class JiraAdapter:
    def __init__(self):
        base_url = os.getenv("JIRA_BASE_URL")
        email = os.getenv("JIRA_EMAIL")
        token = os.getenv("JIRA_API_TOKEN")

        if not all([base_url, email, token]):
            raise ValueError("Jira credentials missing in .env")

        self.client = JIRA(
            server=base_url,
            basic_auth=(email, token)
        )

    def get_ticket(self, ticket_id: str) -> str:
        """
        Fetch a Jira ticket and return key details as string.
        """
        try:
            fetch_ticket = self.client.issue(ticket_id)
            fetch_data = fetch_ticket.fields

            info = [
                f"Ticket Key: {ticket_id}",
                f"Summary / Title: {fetch_data.summary}",
                f"Description: {fetch_data.description}",
                f"Status: {fetch_data.status}",
                f"Assignee: {fetch_data.assignee}",
                f"Priority: {fetch_data.priority}",
            ]

            return "\n".join(info)

        except Exception as e:
            return f"Error fetching for ticket: '{ticket_id}': {str(e)}"
