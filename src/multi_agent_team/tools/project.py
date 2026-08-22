from langchain_core.tools import tool

@tool
def get_project_status(project_id: str) -> str:
    """Read-only bootstrap project status tool."""
    return f"Project {project_id}: status=PLANNING"
