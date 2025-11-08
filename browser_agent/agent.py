# Central agent definitions as per ADK best practices
from google.adk.agents.workflow import Sequential
from agents_factory import create_agents
from workflow_setup import setup_workflow
from mcp_manager import MCPManager
from config import AppConfig
from logging_setup import setup_logging

logger = setup_logging()

async def initialize_root_agent():
    mcp = MCPManager()
    toolset = await mcp.start()
    try:
        agents = create_agents()
        workflow = setup_workflow(agents, toolset)
        root_agent = Sequential(
            name="browser_root_agent",
            description="Root agent for browser automation on Power Platform, handling planning, execution, and validation with MCP tools.",
            agents=agents,  # Sub-agents: planner, executor, validator
            max_retries=AppConfig.MAX_RETRIES
        )
        logger.info("Root agent initialized.")
        return root_agent, mcp
    except Exception as e:
        logger.error(f"Root agent init error: {str(e)}")
        raise

# Export for __init__.py
root_agent = None  # Initialized dynamically in main.py
