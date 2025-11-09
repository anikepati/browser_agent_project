import json
from google.adk.agents import CallbackContext
from logging_setup import setup_logging

logger = setup_logging()  # Global logger init (called in main)
# --- File: adk_callbacks.py ---

import hashlib
from google.adk.callbacks import after_tool_callback
from google.adk.callbacks.context import ToolContext

# Key to store the last hash of the snapshot in the ADK session state
LAST_SNAPSHOT_HASH_KEY = "last_browser_snapshot_hash"

@after_tool_callback
async def conditional_snapshot_reducer(tool_context: ToolContext, tool_result: dict) -> dict:
    """
    Checks if the new snapshot is identical to the last one. 
    If they are the same, it deletes the new snapshot content from the result.
    """
    # 1. Check if the tool result contains a 'snapshot' (the large token data)
    new_snapshot = tool_result.get("snapshot")
    if not new_snapshot:
        return tool_result  # No snapshot to check

    # 2. Hash the new snapshot content
    # We use SHA256 to create a compact, consistent ID for the large string
    new_hash = hashlib.sha256(new_snapshot.encode('utf-8')).hexdigest()
    
    # 3. Retrieve the previous hash from the session state
    last_hash = tool_context.state.get(LAST_SNAPSHOT_HASH_KEY)
    
    # 4. Compare the hashes
    if new_hash == last_hash:
        # **REDUCE THE TOKEN LOAD**
        # If the snapshot hasn't changed, replace the large snapshot content 
        # with a small confirmation message.
        del tool_result["snapshot"]
        tool_result["note"] = f"Snapshot content is identical to the previous step (Hash: {new_hash[:8]}). Snapshot data was removed from LLM context."
        
    # 5. Update the session state with the new hash for the next iteration
    tool_context.state[LAST_SNAPSHOT_HASH_KEY] = new_hash
    
    return tool_result # Return the modified (or original) result
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
