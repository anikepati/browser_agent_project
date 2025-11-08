import subprocess
from tenacity import retry, stop_after_attempt, wait_exponential
from config import AppConfig
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from logging_setup import setup_logging

class MCPManager:
    def __init__(self):
        self.toolset = None
        self.logger = setup_logging()

    @retry(stop=stop_after_attempt(AppConfig.MAX_RETRIES), wait=wait_exponential(multiplier=AppConfig.BACKOFF_FACTOR, min=1, max=10))
    async def start(self):
        try:
            # Check if MCP is installed
            subprocess.run(["npx", "@playwright/mcp@latest", "--version"], check=True, capture_output=True, timeout=AppConfig.TIMEOUT_MS / 1000)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            self.logger.info("Installing @playwright/mcp@latest...")
            subprocess.run(["npm", "install", "-g", "@playwright/mcp@latest"], check=True, capture_output=True, timeout=AppConfig.TIMEOUT_MS / 1000)
        
        try:
            self.toolset = MCPToolset(connection_params=AppConfig.MCP_PARAMS)
            self.logger.json_log("MCP started with vision capabilities.", extra={"status": "success"})
            return self.toolset
        except Exception as e:
            self.logger.error(f"MCP start failed: {str(e)}")
            raise

    async def stop(self):
        if self.toolset:
            await self.toolset.close()
        self.logger.info("MCP stopped.")
