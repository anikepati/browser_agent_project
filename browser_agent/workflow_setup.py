from google.adk.agents.workflow import Sequential
from config import AppConfig

def setup_workflow(agents, toolset):
    planner, executor, validator = agents
    executor.tools = [toolset]  # MCP tools with docstrings (assumed in MCPToolset)
    workflow = Sequential(
        agents=[planner, executor, validator],
        max_retries=AppConfig.MAX_RETRIES,
        backoff_factor=AppConfig.BACKOFF_FACTOR
    )
    return workflow
