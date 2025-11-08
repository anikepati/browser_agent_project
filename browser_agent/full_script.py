# Expanded to ~24 steps for Power Platform automation (e.g., create business unit, team, mailbox, group).
# Uses placeholders like {{parent_business_unit.name}} for preprocessing.
# Steps handle navigation, clicks, form-filling with vision fallbacks in executor.
FULL_SCRIPT = {
    "actions": [
        {"tool": "browser_navigate", "parameters": {"url": "https://admin.powerplatform.microsoft.com/home"}},
        {"tool": "browser_click", "parameters": {"element": "Environments"}},  # Navigate to environments
        {"tool": "browser_wait", "parameters": {"timeout": 5000}},  # Wait for load
        {"tool": "browser_click", "parameters": {"element": "Settings > Business units"}},  # Go to business units
        {"tool": "browser_click", "parameters": {"element": "New business unit"}},  # Create new BU
        {"tool": "browser_fill_form", "parameters": {"element": "#name_field", "value": "{{parent_business_unit.name}}"}},
        {"tool": "browser_fill_form", "parameters": {"element": "#parent_field", "value": "{{parent_business_unit.parent}}"}},
        {"tool": "browser_fill_form", "parameters": {"element": "#date_field", "value": "{{current_date}}"}},
        {"tool": "browser_click", "parameters": {"element": "Save"}},  # Save BU
        {"tool": "browser_wait", "parameters": {"timeout": 10000}},  # Wait for confirmation
        {"tool": "browser_click", "parameters": {"element": "Settings > Teams"}},  # Go to teams
        {"tool": "browser_click", "parameters": {"element": "New team"}},  # Create new team
        {"tool": "browser_fill_form", "parameters": {"element": "#team_name", "value": "{{team.name}}"}},
        {"tool": "browser_fill_form", "parameters": {"element": "#business_unit", "value": "{{parent_business_unit.name}}"}},
        {"tool": "browser_click", "parameters": {"element": "Save"}},  # Save team
        {"tool": "browser_click", "parameters": {"element": "Settings > Mailboxes"}},  # Go to mailboxes
        {"tool": "browser_click", "parameters": {"element": "New mailbox"}},  # Create new mailbox
        {"tool": "browser_fill_form", "parameters": {"element": "#email_field", "value": "{{mailbox.email}}"}},
        {"tool": "browser_fill_form", "parameters": {"element": "#owner_field", "value": "{{mailbox.owner}}"}},
        {"tool": "browser_click", "parameters": {"element": "Approve"}},  # Approve mailbox
        {"tool": "browser_click", "parameters": {"element": "Settings > Groups"}},  # Go to groups
        {"tool": "browser_click", "parameters": {"element": "New group"}},  # Create new group
        {"tool": "browser_fill_form", "parameters": {"element": "#group_name", "value": "{{group.name}}"}},
        {"tool": "browser_fill_form", "parameters": {"element": "#date_field", "value": "{{current_date}}"}},
        {"tool": "browser_click", "parameters": {"element": "Save"}}  # Save group
        # Add more steps as needed; for variations, executor uses vision (e.g., snapshot + click_xy)
    ]
}
