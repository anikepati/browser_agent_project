import subprocess
from config import AppConfig
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from logging_setup import setup_logging

class MCPManager:
    def __init__(self):
        self.toolset = None
        self.logger = setup_logging()  # Initialize logger here if needed, but prefer global init

    async def start(self):
        try:
            # Check if MCP is installed to avoid redundant global installs
            subprocess.run(["npx", "@playwright/mcp@latest", "--version"], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            self.logger.info("Installing @playwright/mcp@latest...")
            subprocess.run(["npm", "install", "-g", "@playwright/mcp@latest"], check=True, capture_output=True)
        
        self.toolset = MCPToolset(connection_params=AppConfig.MCP_PARAMS)
        self.logger.info("MCP started with vision capabilities for handling form variations.")
        return self.toolset

    async def stop(self):
        if self.toolset:
            await self.toolset.close()
        self.logger.info("MCP stopped.")
