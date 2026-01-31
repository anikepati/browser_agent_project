"""
PowerApps Business Unit Creator Agent
Uses Google ADK with Playwright MCP for browser automation in Microsoft Power Platform admin center.
Implements creation of a business unit (can be adapted for parent/child by setting parent in dropdown).
Assumes auth storage state in 'state.json' (generate via manual login and playwright codegen).
Runs in headless mode for efficiency.
"""

import asyncio
import os
from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.apps import App
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import McpToolset
from google.adk.tools.mcp_toolset import StdioServerParams
from google.adk.llm import LlmConfig

# Load environment variables (for GEMINI_API_KEY if using Gemini; adjust for your LLM)
load_dotenv()
if not os.getenv("GEMINI_API_KEY"):
    raise ValueError("GEMINI_API_KEY environment variable must be set")

def create_instruction(context) -> str:
    """
    Dynamic instruction for business unit creation.
    """
    current_step = context.session.state.get('current_step', 1)
    business_unit_name = context.session.state.get('business_unit_name', 'Test Business Unit')
    parent_bu_name = context.session.state.get('parent_bu_name', None)  # Optional for child BU
    completed_steps = context.session.state.get('completed_steps', [])
    
    parent_select = f"8. Select parent '{parent_bu_name}' from dropdown if creating child BU.\n" if parent_bu_name else ""
    
    instruction = f"""You are a browser automation agent using Playwright MCP tools to create a business unit in Microsoft Power Platform admin center.
**Current Status:**
- Current Step: {current_step}
- Business Unit Name: {business_unit_name}
- Parent (if child): {parent_bu_name or 'Root (default)'}
- Completed Steps: {', '.join(completed_steps) if completed_steps else 'None'}
**Authentication:**
Browser has auth storage state loaded (state.json) - no login needed.
**Workflow Steps:**
1. Navigate to https://admin.powerplatform.microsoft.com/ if not already there (browser_navigate).
2. Take snapshot to get element references (browser_snapshot).
3. Click to select the target environment.
4. Click on "Settings".
5. Navigate to "Users + permissions" → "Business units".
6. Click "New" to create new business unit.
7. Type business unit name into the name field (browser_type).
{parent_select}8. Click "Save" button.
9. Take final snapshot to confirm creation and output 'BU_CREATED'.
**Instructions:**
- Resume from step {current_step}.
- Execute ONLY the current step, update state, then stop.
- Use tools: browser_navigate, browser_snapshot, browser_click, browser_type, browser_select_option.
- For click/type: Provide 'element' (description) and 'ref' (from snapshot).
- Batch where possible for efficiency.
- Update state after step: current_step (next), completed_steps (add desc), step_details (refs/errors).
- On completion, output 'BU_CREATED'.
Begin from step {current_step}."""
    return instruction

# Define the agent
bu_agent = LlmAgent(
    name="BusinessUnitCreator",
    instruction=create_instruction,
    tools=[
        McpToolset(
            connection_params=StdioServerParams(
                command="npx",
                args=[
                    "-y",
                    "@playwright/mcp@latest",
                    "--isolated",
                    "--headless",
                    "--storage-state=state.json"
                ]
            )
        )
    ],
    llm_config=LlmConfig(model="gemini-1.5-flash-latest", max_tokens=512, temperature=0)
)

# App with session service (add compaction if needed)
app = App(
    root_agent=bu_agent,
    session_service=InMemorySessionService()
)

async def create_business_unit(
    business_unit_name: str = "Test Business Unit",
    parent_bu_name: Optional[str] = None,  # For child BU
    max_steps: int = 15,
    verbose: bool = True
):
    """
    Run the agent step by step to create a business unit.
    
    Args:
        business_unit_name: Name of the BU to create
        parent_bu_name: Name of parent BU (for child creation)
        max_steps: Max iterations (safety)
        verbose: Print progress
    """
    runner = Runner(app=app)
    
    # Create session with initial state
    session = await app.session_service.create_session_async()
    session.state['business_unit_name'] = business_unit_name
    session.state['parent_bu_name'] = parent_bu_name
    session.state['current_step'] = 1
    session.state['completed_steps'] = []
    session.state['step_details'] = {}
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Creating Business Unit: {business_unit_name}")
        if parent_bu_name:
            print(f"Parent: {parent_bu_name}")
        print(f"Session ID: {session.session_id}")
        print(f"{'='*60}\n")
    
    step_count = 0
    task_completed = False
    
    while not task_completed and step_count < max_steps:
        step_count += 1
        current_step = session.state.get('current_step', 1)
        
        if verbose:
            print(f"\n[Step {step_count}] Executing agent step {current_step}...")
            print(f"Completed steps so far: {', '.join(session.state.get('completed_steps', []))}")
        
        try:
            response = await runner.run_async(
                user_content=f"Execute step {current_step} of the business unit creation workflow.",
                session_id=session.session_id
            )
            
            response_text = response.text if hasattr(response, 'text') else str(response)
            
            if verbose:
                print(f"\nAgent Response:")
                print(f"{response_text}")
            
            if "BU_CREATED" in response_text.upper():
                task_completed = True
                if verbose:
                    print(f"\n{'='*60}")
                    print("✅ Business Unit created successfully!")
                    print(f"{'='*60}")
                break
            
            # Reload session to get updated state
            session = await app.session_service.get_session_async(session.session_id)
            
            # Check if stuck
            new_step = session.state.get('current_step', 1)
            if new_step == current_step:
                if verbose:
                    print(f"\n⚠️ Warning: Still on step {current_step}. Agent may need another iteration.")
            
        except Exception as e:
            print(f"\n❌ Error during step {step_count}: {str(e)}")
            if verbose:
                import traceback
                traceback.print_exc()
            break
    
    if not task_completed and step_count >= max_steps:
        print(f"\n⚠️ Maximum steps ({max_steps}) reached without completion.")
    
    # Final state summary
    if verbose:
        print(f"\n{'='*60}")
        print("Final State Summary:")
        print(f"{'='*60}")
        print(f"Total iterations: {step_count}")
        print(f"Final step: {session.state.get('current_step', 'Unknown')}")
        print(f"Completed steps: {session.state.get('completed_steps', [])}")
        print(f"{'='*60}\n")
    
    return session

# Main execution
async def main():
    """Main execution function."""
    print("\nPowerApps Business Unit Creator")
    print("="*60)
    
    bu_name = input("Enter business unit name (or press Enter for 'Test Business Unit'): ").strip() or "Test Business Unit"
    parent_name = input("Enter parent BU name for child (or press Enter for root): ").strip() or None
    
    await create_business_unit(
        business_unit_name=bu_name,
        parent_bu_name=parent_name
    )

if __name__ == "__main__":
    asyncio.run(main())
