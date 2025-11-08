# Central agent definitions as per ADK best practices
from google.adk.agents import SequentialAgent  # Correct import
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
        root_agent = setup_workflow(agents, toolset)  # This returns the SequentialAgent workflow
        logger.info("Root agent (SequentialAgent workflow) initialized and ready for use.")
        return root_agent, mcp
    except Exception as e:
        logger.error(f"Root agent init error: {str(e)}")
        raise
