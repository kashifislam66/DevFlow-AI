from mcp.server.fastmcp import FastMCP
from devflow.integrations.jira_adapter import JiraAdapter

mcp = FastMCP("Jira Server")

@mcp.tool()
def get_jira_ticket(ticket_id: str) -> str:
        """
        Fetch a Jira ticket detail and return key details as string.
        """
        try:
            jira_client = JiraAdapter()
            ticket_Detail = jira_client.get_ticket(ticket_id)
           
            return ticket_Detail

        except Exception as e:
            return f"Error fetching for ticket: '{ticket_id}': {str(e)}"

