from google.adk.agents import SequentialAgent  # Correct import
from config import AppConfig

def setup_workflow(agents, toolset):
    planner, executor, validator = agents
    executor.tools = [toolset]  # MCP tools for execution
    validator.tools = [toolset]  # MCP tools for validation (e.g., snapshots to verify state)
    workflow = SequentialAgent(
        agents=[planner, executor, validator],
        max_retries=AppConfig.MAX_RETRIES,
        backoff_factor=AppConfig.BACKOFF_FACTOR
    )
    return workflow
