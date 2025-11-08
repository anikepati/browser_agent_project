from vertexai.generative_models import GenerativeModel
from google.adk.agents import LlmAgent
from config import AppConfig
from callbacks import before_cb, after_cb

def create_agents():
    llm = GenerativeModel(AppConfig.LLM_MODEL)
    
    planner_prompt = """
You are an expert Planner Agent for browser automation tasks on Power Platform.
1. Analyze the preprocessed {full_script} and task {task_item}.
2. Generate an adaptive sequence of MCP tool calls. Critique for potential UI variations (e.g., dynamic forms, element changes).
3. If variations likely (e.g., form fields shifted), suggest vision-based fallbacks in the plan.
4. Use async calls for speed. If {skill_context.use_vision} is True, prioritize vision tools.
5. Output: JSON array of tool calls with parameters. Ensure plan is robust and complete.
"""
    planner = LlmAgent(llm=llm, system_prompt=planner_prompt, tools=[], output_key="plan",
                       generate_content_config=AppConfig.GENERATE_CONFIG,
                       before_agent_callback=before_cb, after_agent_callback=after_cb)
    
    executor_prompt = """
You are an Executor Agent specializing in MCP browser tools for Power Platform automation.
1. Execute the {plan} step-by-step asynchronously.
2. If a step fails (e.g., element not found due to UI variation), then fallback: Take browser_snapshot, analyze image for coordinates, use browser_mouse_click_xy or browser_keyboard_type.
3. Handle errors with quick retries (up to {max_retries}). Log issues.
4. Incorporate task {task_item} and context {skill_context}.
5. If vision needed, condition on failure: Switch to vision mode.
6. Output: Detailed execution log with results or errors.
"""
    executor = LlmAgent(llm=llm, system_prompt=executor_prompt, output_key="execution_output",
                        generate_content_config=AppConfig.GENERATE_CONFIG,
                        before_agent_callback=before_cb, after_agent_callback=after_cb)
    
    validator_prompt = """
You are a Validator Agent for browser automation outcomes.
1. Review {execution_output} against {full_script}.
2. Critique for completeness: Check if all steps succeeded despite variations.
3. If issues found (e.g., partial form fill), suggest fixes or retries.
4. Output: JSON validation report with status (success/fail), issues, and confidence score.
"""
    validator = LlmAgent(llm=llm, system_prompt=validator_prompt, tools=[], output_key="validation_report",
                         generate_content_config=AppConfig.GENERATE_CONFIG,
                         before_agent_callback=before_cb, after_agent_callback=after_cb)
    
    return planner, executor, validator
