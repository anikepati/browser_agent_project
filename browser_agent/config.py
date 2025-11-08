import os
from dotenv import load_dotenv  # pip install python-dotenv
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.genai import types  # For safety settings

load_dotenv()  # Load from .env if present

class AppConfig:
    MCP_PARAMS = StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=["@playwright/mcp@latest", "--port", "8931", "--caps=vision", "--headless", "--browser", "chromium"]
        )
    )
    LLM_MODEL = os.getenv('LLM_MODEL', "gemini-1.5-flash")
    MAX_RETRIES = 3
    BACKOFF_FACTOR = 2
    TIMEOUT_MS = 20000
    ARTIFACT_DIR = "./artifacts"
    LOG_FILE = 'adk_browser_agent.log'
    CURRENT_DATE = os.getenv('CURRENT_DATE', "November 07, 2025")
    
    # ADK best practices: Safety and generation config
    SAFETY_SETTINGS = [
        types.SafetySetting(
            category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
            threshold=types.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        ),
    ]
    GENERATE_CONFIG = types.GenerateContentConfig(
        safety_settings=SAFETY_SETTINGS,
        temperature=0.7,
        max_output_tokens=1024,
        top_p=0.95,
    )
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
