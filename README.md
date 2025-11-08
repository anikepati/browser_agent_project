# Enterprise-Grade Browser Agent Project

Automates Power Platform tasks using Google ADK, MCP (Playwright with vision), and LLMs for resilient browser interactions.

## Setup
- Install deps: `pip install -r requirements.txt`
- Env vars: Edit `.env` (e.g., LLM_MODEL=gemini-1.5-flash)
- Run tests: `pytest browser_agent/tests.py`
- Interactive test: `adk web` from project root
- Programmatic: `python browser_agent/main.py`
- Docker: `docker build -t browser-agent . && docker run browser-agent`

## Deployment to Vertex AI
- `adk deploy agent_engine --agent-dir browser_agent/ --project YOUR_PROJECT --region us-central1`

## Features
- Modular agents: Planner, Executor, Validator with MCP tools.
- Persistent artifacts via SQLite.
- Vision fallbacks for UI variations.
- Enterprise: Retries, logging, security, tests.
