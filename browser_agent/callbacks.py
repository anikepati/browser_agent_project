import json
from google.adk.agents import CallbackContext
from logging_setup import setup_logging

logger = setup_logging()  # Global logger init (called in main)

def before_cb(context: CallbackContext):
    artifact_service = context.session.artifact_service
    try:
        skill_context_str = artifact_service.load_artifact("skill_context.json") or json.dumps({"use_vision": True, "env": AppConfig.ENV_MODE})
        task_item_str = artifact_service.load_artifact("task_item.json") or json.dumps(context.inputs.get('task_item', {}))
        context.state['skill_context'] = json.loads(skill_context_str)
        context.state['task_item'] = json.loads(task_item_str)
        logger.info("Loaded/attached artifacts for agent execution.")
    except json.JSONDecodeError as e:
        logger.error(f"JSON error in callbacks: {str(e)}")
        raise ValueError("Invalid artifact JSON")

def after_cb(context: CallbackContext):
    artifact_service = context.session.artifact_service
    artifact_service.save_artifact("skill_context.json", json.dumps(context.state['skill_context']))
    artifact_service.save_artifact("task_item.json", json.dumps(context.state['task_item']))
    logger.info("Saved artifacts post-execution.")
