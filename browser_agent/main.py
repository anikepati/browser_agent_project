import asyncio
import json
from logging_setup import setup_logging
from script_preprocessor import ScriptPreprocessor
from full_script import FULL_SCRIPT
from services_setup import setup_services
from google.adk.runners import Runner
from vertexai.agent_engines import AdkApp
from agent import initialize_root_agent  # Imports root setup

async def main(inputs):
    logger = setup_logging()
    try:
        root_agent, mcp = await initialize_root_agent()  # Initializes the Sequential workflow as root_agent
        session_service, artifact_service = setup_services()
        
        # Use Runner for batch execution (ADK compatible), passing the root_agent (workflow)
        runner = Runner(workflow=root_agent, session_service=session_service, artifact_service=artifact_service)
        
        preprocessed_script = ScriptPreprocessor.preprocess(FULL_SCRIPT, inputs.get('task_item', {}))
        inputs['full_script'] = preprocessed_script
        
        # Programmatic run with Runner
        result = await runner.run_async(inputs)
        
        # Alternative: Use AdkApp for interactive/streaming queries
        app = AdkApp(agent=root_agent, session_service_builder=lambda: session_service)
        session = await app.async_create_session(user_id="default_user")
        async for event in app.async_stream_query(user_id="default_user", session_id=session.id, message=json.dumps(inputs)):
            logger.json_log(f"Stream event: {event}", extra={"event_type": type(event).__name__})
        
        return result
    except Exception as e:
        logger.error(f"Execution error: {str(e)}")
        raise
    finally:
        await mcp.stop()

if __name__ == "__main__":
    # Example task_item for testing
    task_item = {
        "parent_business_unit": {"name": "CustomBU", "parent": "RootBU"},
        "team": {"name": "DevTeam"},
        "mailbox": {"email": "test@example.com", "owner": "admin"},
        "group": {"name": "AdminGroup"}
    }
    inputs = {"task_item": task_item}
    result = asyncio.run(main(inputs))
    print(json.dumps(result, indent=2))
