from pydantic import BaseModel
from langchain_core.tools import tool


@tool
def SEND_EMAIL(to: str, subject: str, body: str) -> str:
    """Send an email."""
    # Placeholder response - in real app would send email
    return f"Email sent to {to} with subject '{subject}' and body: {body}"


@tool
class END_WORKFLOW(BaseModel):
    """End the workflow."""
    done: bool


# tools = [SEND_EMAIL, END_WORKFLOW]

# tools_by_name = {tool.name: tool for tool in tools}
