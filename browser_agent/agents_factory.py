from google.adk.agents import LlmAgent  # Correct import
from config import AppConfig
from callbacks import before_cb, after_cb

def create_agents():
    planner_prompt = """
You are an expert Planner Agent for browser automation tasks on Power Platform.
1. Analyze the preprocessed {full_script} and task {task_item}.
2. Generate an adaptive sequence of MCP tool calls. Critique for potential UI variations (e.g., dynamic forms, element changes).
3. If variations likely (e.g., form fields shifted), suggest vision-based fallbacks in the plan.
4. Use async calls for speed. If {skill_context.use_vision} is True, prioritize vision tools.
5. Output: JSON array of tool calls with parameters. Ensure plan is robust and complete.
"""
    planner = LlmAgent(
        model=AppConfig.LLM_MODEL,  # String model name
        name="planner_agent",
        description="Plans MCP tool calls for browser tasks",
        instruction=planner_prompt,
        tools=[],
        output_key="plan",
        generate_content_config=AppConfig.GENERATE_CONFIG,
        before_agent_callback=before_cb,
        after_agent_callback=after_cb
    )
    
    executor_prompt = """
You are an Executor Agent specializing in MCP browser tools for Power Platform automation.
1. Execute the {plan} step-by-step asynchronously.
2. If a step fails (e.g., element not found due to UI variation), then fallback: Take browser_snapshot, analyze image for coordinates, use browser_mouse_click_xy or browser_keyboard_type.
3. Handle errors with quick retries (up to {max_retries}). Log issues.
4. Incorporate task {task_item} and context {skill_context}.
5. If vision needed, condition on failure: Switch to vision mode.
6. Output: Detailed execution log with results or errors.
"""
    executor = LlmAgent(
        model=AppConfig.LLM_MODEL,
        name="executor_agent",
        description="Executes planned MCP tool calls with fallbacks",
        instruction=executor_prompt,
        output_key="execution_output",
        generate_content_config=AppConfig.GENERATE_CONFIG,
        before_agent_callback=before_cb,
        after_agent_callback=after_cb
    )
    
    validator_prompt = """
You are a Validator Agent for browser automation outcomes.
1. Review {execution_output} against {full_script}.
2. Critique for completeness: Check if all steps succeeded despite variations.
3. If {execution_output} is inconclusive or errors suggest UI issues, use MCP tools (e.g., browser_snapshot, browser_navigate) to re-verify the final state.
4. If issues found (e.g., partial form fill), suggest fixes or retries.
5. Output: JSON validation report with status (success/fail), issues, and confidence score.
"""
    validator = LlmAgent(
        model=AppConfig.LLM_MODEL,
        name="validator_agent",
        description="Validates execution results against the script, with optional MCP checks",
        instruction=validator_prompt,
        tools=[],  # Tools attached in workflow_setup.py
        output_key="validation_report",
        generate_content_config=AppConfig.GENERATE_CONFIG,
        before_agent_callback=before_cb,
        after_agent_callback=after_cb
    )
    
    return planner, executor, validator
