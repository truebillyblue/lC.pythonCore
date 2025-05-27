import json
import time # For explicit wait_for_timeout
from typing import Optional, Dict, Any, List
from playwright.sync_api import Playwright, sync_playwright, TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError

__all__ = ["execute_web_interaction"]

DEFAULT_PAGE_LOAD_TIMEOUT_MS = 30000
DEFAULT_ACTION_TIMEOUT_MS = 10000 # Increased from 5000 for more reliability
DEFAULT_RETRY_DELAY_MS = 500 # For custom retry logic if needed, not used in current script

def execute_web_interaction(
    target_url: str, # Default URL if not specified in a 'goto' action
    interaction_script_json: str,
    browser_control_params_json: Optional[str] = None,
    requesting_persona_context: Optional[Dict[str, Any]] = None # For future use
) -> Dict[str, Any]:
    """
    Executes a series of web interactions defined in interaction_script_json
    using Playwright.
    """
    log: List[str] = []
    extracted_data: Dict[str, Any] = {}

    try:
        interaction_script = json.loads(interaction_script_json)
        if not isinstance(interaction_script, list):
            log.append("Error: interaction_script_json must be a list of actions.")
            return {"status": "Error: interaction_script_json must be a list of actions.", "extracted_data": None, "log": log}
    except json.JSONDecodeError as e:
        log.append(f"Error: Invalid JSON in interaction_script_json: {e}")
        return {"status": f"Error: Invalid JSON in interaction_script_json: {e}", "extracted_data": None, "log": log}

    browser_params: Dict[str, Any] = {}
    if browser_control_params_json:
        try:
            browser_params = json.loads(browser_control_params_json)
        except json.JSONDecodeError as e:
            log.append(f"Error: Invalid JSON in browser_control_params_json: {e}")
            return {"status": f"Error: Invalid JSON in browser_control_params_json: {e}", "extracted_data": None, "log": log}

    browser_type = browser_params.get("browser_type", "chromium")
    headless = browser_params.get("headless", True)
    page_load_timeout = browser_params.get("timeout_ms_page_load", DEFAULT_PAGE_LOAD_TIMEOUT_MS) # Used for launch
    default_action_timeout = browser_params.get("timeout_ms_action", DEFAULT_ACTION_TIMEOUT_MS) # Default for actions

    if browser_type not in ["chromium", "firefox", "webkit"]:
        log.append(f"Error: Invalid browser_type '{browser_type}'. Must be 'chromium', 'firefox', or 'webkit'.")
        return {"status": f"Error: Invalid browser_type '{browser_type}'", "extracted_data": None, "log": log}

    try:
        with sync_playwright() as p:
            log.append(f"Launching browser: {browser_type}, headless: {headless}, page_load_timeout: {page_load_timeout}ms")
            browser_launcher = getattr(p, browser_type)
            # Note: Playwright launch `timeout` is for the entire launch process, not page loads.
            # Page load timeouts are typically set on page.goto() or page.set_default_timeout().
            browser = browser_launcher.launch(headless=headless) # timeout on launch is for launch itself
            page = browser.new_page()
            page.set_default_timeout(default_action_timeout) # Default timeout for actions on the page
            log.append(f"Browser launched and new page created. Default action timeout: {default_action_timeout}ms.")

            current_url_for_script = target_url # Initialize with the overall target_url

            for i, step in enumerate(interaction_script):
                action = step.get("action")
                selector = step.get("selector")
                action_timeout = step.get("timeout_ms", default_action_timeout) # Step-specific timeout

                log_entry_prefix = f"Step {i+1}/{len(interaction_script)}: action='{action}'"
                if selector: log_entry_prefix += f", selector='{selector}'"
                
                try:
                    if action == "goto":
                        url_to_go = step.get("url", current_url_for_script) # Use step URL, fallback to current/target
                        log.append(f"{log_entry_prefix}, url='{url_to_go}', timeout={action_timeout}ms")
                        page.goto(url_to_go, timeout=action_timeout) # Use action_timeout for goto
                        current_url_for_script = page.url # Update current URL
                        log.append(f"  Success: Navigated to {current_url_for_script}")
                    
                    elif action == "wait_for_selector":
                        log.append(f"{log_entry_prefix}, timeout={action_timeout}ms")
                        page.wait_for_selector(selector, timeout=action_timeout)
                        log.append(f"  Success: Selector '{selector}' found.")
                    
                    elif action == "type_text":
                        text_to_type = step.get("text", "")
                        log.append(f"{log_entry_prefix}, text='{text_to_type[:30]}...'")
                        element = page.query_selector(selector)
                        if not element:
                            log.append(f"  Error: Element not found for selector '{selector}'")
                            raise PlaywrightError(f"Element not found for selector '{selector}' during type_text")
                        element.fill(text_to_type, timeout=action_timeout)
                        log.append(f"  Success: Typed text into '{selector}'.")
                    
                    elif action == "click":
                        log.append(f"{log_entry_prefix}, timeout={action_timeout}ms")
                        element = page.query_selector(selector)
                        if not element:
                            log.append(f"  Error: Element not found for selector '{selector}'")
                            raise PlaywrightError(f"Element not found for selector '{selector}' during click")
                        element.click(timeout=action_timeout)
                        log.append(f"  Success: Clicked element '{selector}'.")
                    
                    elif action == "read_text":
                        variable_name = step.get("variable_name")
                        if not variable_name:
                            log.append(f"  Error: 'variable_name' missing for 'read_text' action.")
                            continue # Or raise error
                        log.append(f"{log_entry_prefix}, var_name='{variable_name}'")
                        element = page.query_selector(selector)
                        if not element:
                            log.append(f"  Error: Element not found for selector '{selector}'")
                            extracted_data[variable_name] = None # Explicitly set to None
                            # Consider if this should be a hard error
                            continue
                        content = element.text_content()
                        extracted_data[variable_name] = content.strip() if content else ""
                        log.append(f"  Success: Read text from '{selector}', stored in '{variable_name}'. Value: '{str(extracted_data[variable_name])[:50]}...'")
                    
                    elif action == "read_attribute":
                        variable_name = step.get("variable_name")
                        attribute_name = step.get("attribute_name")
                        if not variable_name or not attribute_name:
                            log.append(f"  Error: 'variable_name' or 'attribute_name' missing for 'read_attribute'.")
                            continue
                        log.append(f"{log_entry_prefix}, attr='{attribute_name}', var_name='{variable_name}'")
                        element = page.query_selector(selector)
                        if not element:
                            log.append(f"  Error: Element not found for selector '{selector}'")
                            extracted_data[variable_name] = None
                            continue
                        attr_value = element.get_attribute(attribute_name)
                        extracted_data[variable_name] = attr_value if attr_value is not None else ""
                        log.append(f"  Success: Read attribute '{attribute_name}' from '{selector}', stored in '{variable_name}'. Value: '{str(extracted_data[variable_name])[:50]}...'")

                    elif action == "wait_for_timeout":
                        timeout_to_wait = step.get("timeout_ms", 1000) # Default to 1s if not specified
                        log.append(f"{log_entry_prefix}, duration={timeout_to_wait}ms")
                        time.sleep(timeout_to_wait / 1000.0) # time.sleep takes seconds
                        log.append(f"  Success: Waited for {timeout_to_wait}ms.")
                        
                    else:
                        log.append(f"  Warning: Unknown action type '{action}' at step {i+1}.")
                
                except PlaywrightTimeoutError as pte:
                    log.append(f"  Error: Timeout during action '{action}' on selector '{selector}': {str(pte)}")
                    browser.close()
                    return {"status": f"Error: Timeout on step {i+1} ({action}) - {str(pte)}", "extracted_data": extracted_data, "log": log}
                except PlaywrightError as pe: # Catch other Playwright-specific errors
                    log.append(f"  Error: Playwright error during action '{action}': {str(pe)}")
                    browser.close()
                    return {"status": f"Error: Playwright error on step {i+1} ({action}) - {str(pe)}", "extracted_data": extracted_data, "log": log}
                except Exception as e: # Catch any other unexpected errors during a step
                    log.append(f"  Error: Unexpected error during action '{action}': {str(e)}")
                    browser.close()
                    return {"status": f"Error: Unexpected error on step {i+1} ({action}) - {str(e)}", "extracted_data": extracted_data, "log": log}

            log.append("Interaction script completed successfully.")
            browser.close()
            return {"status": "Success", "extracted_data": extracted_data, "log": log}

    except PlaywrightError as pe: # Errors during Playwright setup/launch
        log.append(f"Error: Playwright setup failed: {str(pe)}")
        return {"status": f"Error: Playwright setup failed - {str(pe)}", "extracted_data": None, "log": log}
    except Exception as e: # Catch-all for other unexpected errors
        log.append(f"Error: An unexpected error occurred: {str(e)}")
        return {"status": f"Error: An unexpected error occurred - {str(e)}", "extracted_data": None, "log": log}


if __name__ == '__main__':
    print("--- Testing execute_web_interaction ---")

    # Test 1: Simple navigation and text reading from example.com
    script1_json = json.dumps([
        {"action": "goto", "url": "https://example.com"},
        {"action": "wait_for_selector", "selector": "h1"},
        {"action": "read_text", "selector": "h1", "variable_name": "page_title"},
        {"action": "read_text", "selector": "p", "variable_name": "first_paragraph"}
    ])
    print("\n--- Test 1: example.com navigation and read ---")
    result1 = execute_web_interaction(
        target_url="https://example.com", # Fallback, but script has goto
        interaction_script_json=script1_json
    )
    print(f"Status: {result1['status']}")
    print(f"Extracted Data: {result1['extracted_data']}")
    # print("Log:")
    # for log_entry in result1['log']: print(f"  {log_entry}")
    assert result1['status'] == "Success"
    assert result1['extracted_data'].get('page_title') == "Example Domain"

    # Test 2: Interaction with a form on toscrape.com (quotes.toscrape.com)
    # This site is designed for scraping.
    script2_json = json.dumps([
        {"action": "goto", "url": "http://quotes.toscrape.com/login"},
        {"action": "wait_for_selector", "selector": "#username"},
        {"action": "type_text", "selector": "#username", "text": "testuser"},
        {"action": "type_text", "selector": "#password", "text": "testpassword"},
        {"action": "click", "selector": "input[type='submit']"},
        # After clicking login, we expect to see a "Logout" link or an error message
        # Let's try to read the error message if login fails (which it will with dummy creds)
        {"action": "wait_for_selector", "selector": ".container"}, # Wait for page content
        {"action": "read_text", "selector": "form .alert", "variable_name": "login_error_message"}, # If error
        {"action": "read_text", "selector": "a[href='/logout']", "variable_name": "logout_link_text"} # If success
    ])
    print("\n--- Test 2: quotes.toscrape.com login attempt and read ---")
    # Note: quotes.toscrape.com might be http, ensure your playwright allows it or it redirects.
    result2 = execute_web_interaction(
        target_url="http://quotes.toscrape.com", 
        interaction_script_json=script2_json,
        browser_control_params_json=json.dumps({"timeout_ms_action": 15000}) # Give more time for actions
    )
    print(f"Status: {result2['status']}")
    print(f"Extracted Data: {result2['extracted_data']}")
    # print("Log:")
    # for log_entry in result2['log']: print(f"  {log_entry}")
    assert result2['status'] == "Success" # Script completes, even if login fails
    # Depending on site behavior, one of these might be populated
    assert result2['extracted_data'].get('login_error_message') or result2['extracted_data'].get('logout_link_text') is not None
    if result2['extracted_data'].get('login_error_message'):
        print(f"  Login error found: {result2['extracted_data']['login_error_message']}")
        assert "Invalid user name or password" in result2['extracted_data']['login_error_message']


    # Test 3: Invalid action
    script3_json = json.dumps([{"action": "non_existent_action"}])
    print("\n--- Test 3: Invalid action ---")
    result3 = execute_web_interaction(target_url="https://example.com", interaction_script_json=script3_json)
    print(f"Status: {result3['status']}")
    # The current implementation logs a warning for unknown actions and continues.
    # If it should be an error, the function logic would need to change.
    # For now, it should be "Success" as it completes the script (of 1 unknown action).
    assert result3['status'] == "Success" 
    assert "Warning: Unknown action type 'non_existent_action'" in result3['log'][-1]


    # Test 4: Timeout on wait_for_selector
    script4_json = json.dumps([
        {"action": "goto", "url": "https://example.com"},
        {"action": "wait_for_selector", "selector": "#nonExistentElement", "timeout_ms": 100} # Very short timeout
    ])
    print("\n--- Test 4: Timeout on wait_for_selector ---")
    result4 = execute_web_interaction(target_url="https://example.com", interaction_script_json=script4_json)
    print(f"Status: {result4['status']}")
    assert "Error: Timeout on step 2 (wait_for_selector)" in result4['status']
    
    # Test 5: Invalid interaction_script_json
    print("\n--- Test 5: Invalid interaction_script_json ---")
    result5 = execute_web_interaction(target_url="https://example.com", interaction_script_json="not valid json")
    print(f"Status: {result5['status']}")
    assert "Error: Invalid JSON in interaction_script_json" in result5['status']

    print("\n--- All local tests for execute_web_interaction finished ---")


# Added stubs
def execute_web_interaction(payload: dict) -> dict:
    print("[Stub] execute_web_interaction called")
    return {"status": "stubbed", "received": payload}
