import os
import json
import requests
from typing import Optional, Dict, Any, List

__all__ = ["execute_api_call"]

REQUEST_TIMEOUT_SECONDS = 60

def _get_value_from_path(data: Dict[str, Any], path: str) -> Optional[Any]:
    """
    Navigates a dictionary using a dot-separated path.
    Supports simple dictionary key access and list indexing.
    Example: "choices[0].message.content"
    """
    keys = path.replace("[", ".").replace("]", "").split('.')
    current = data
    for key_part in keys:
        if not key_part: # Handles cases like "choices..content" after replace
            continue
        if isinstance(current, dict):
            if key_part in current:
                current = current[key_part]
            else:
                # print(f"Key '{key_part}' not found in dict: {current.keys()}")
                return None
        elif isinstance(current, list):
            try:
                idx = int(key_part)
                if 0 <= idx < len(current):
                    current = current[idx]
                else:
                    # print(f"Index {idx} out of bounds for list of length {len(current)}")
                    return None  # Index out of bounds
            except ValueError:
                # print(f"Cannot use '{key_part}' as list index.")
                return None  # Not an int index
        else:
            # print(f"Path broken at '{key_part}', current is not dict or list: {type(current)}")
            return None  # Path broken, current is not a traversable type
    return current

def execute_api_call(
    api_endpoint_url: str,
    prompt_text: str,
    api_key_env_var: Optional[str] = None,
    request_payload_template_json: Optional[str] = None,
    conversation_history_json: Optional[str] = None,
    response_extraction_path: Optional[str] = None,
    request_parameters_json: Optional[str] = None,
    requesting_persona_context: Optional[Dict[str, Any]] = None # For future use (logging, context passing)
) -> Dict[str, Any]:
    """
    Executes an API call to a specified endpoint, typically an LLM.
    """
    api_key: Optional[str] = None
    headers = {"Content-Type": "application/json"}

    if api_key_env_var:
        api_key = os.getenv(api_key_env_var)
        if not api_key:
            return {"status": f"Error: API key not found in environment variable '{api_key_env_var}'", 
                    "agent_response_text": None, "full_response_json": None, "http_status_code": None}
        headers["Authorization"] = f"Bearer {api_key}"

    # 1. Initialize payload
    payload: Dict[str, Any] = {}
    if request_payload_template_json:
        try:
            payload = json.loads(request_payload_template_json)
        except json.JSONDecodeError as e:
            return {"status": f"Error: Invalid JSON in request_payload_template_json: {e}", 
                    "agent_response_text": None, "full_response_json": None, "http_status_code": None}

    # 2. Integrate conversation history
    conversation_messages: List[Dict[str, str]] = []
    if conversation_history_json:
        try:
            history = json.loads(conversation_history_json)
            if isinstance(history, list): # Assuming history is a list of message dicts
                conversation_messages.extend(history)
            else: # Or perhaps it's a dict with a 'messages' key
                if isinstance(history, dict) and "messages" in history and isinstance(history["messages"], list):
                     conversation_messages.extend(history["messages"])
                else:
                    return {"status": "Error: conversation_history_json is not a list of messages or a dict containing a 'messages' list.",
                            "agent_response_text": None, "full_response_json": None, "http_status_code": None}
        except json.JSONDecodeError as e:
            return {"status": f"Error: Invalid JSON in conversation_history_json: {e}", 
                    "agent_response_text": None, "full_response_json": None, "http_status_code": None}

    # 3. Add current prompt text
    # This assumes a common pattern like OpenAI's API.
    # If the template defines 'messages', append. Otherwise, set a default field or rely on template.
    if "messages" in payload and isinstance(payload["messages"], list):
        # Prepend history, then add current prompt
        payload["messages"] = conversation_messages + payload["messages"] 
        # Check if the last message in the template is meant to be the prompt (e.g. if it's a user role)
        # Or, more simply, append the new user message.
        # For this implementation, let's assume the template might be empty or have a system message,
        # and we always add the history then the current user prompt.
        
        # If payload["messages"] was from template, it might contain system prompt.
        # We want history first, then current prompt.
        # If template had messages, they should be system messages or prefix to history.
        # Let's refine: If template has messages, assume it's a base. Add history, then prompt.
        # If template has messages: payload_messages = template_messages + history_messages + current_prompt_message
        # If template has no messages: payload_messages = history_messages + current_prompt_message
        
        current_prompt_message = {"role": "user", "content": prompt_text}
        if not payload["messages"]: # If template's messages list was empty
            payload["messages"] = conversation_messages + [current_prompt_message]
        else: # Template had messages, prepend history and append current prompt
            payload["messages"] = payload["messages"] + conversation_messages + [current_prompt_message]

    elif "prompt" in payload and isinstance(payload["prompt"], str): # Simpler "prompt" field
        # If history exists, concatenate. This is a basic approach.
        history_text = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in conversation_messages])
        payload["prompt"] = f"{history_text}\n{payload['prompt']}{prompt_text}".strip() # Template prompt + current prompt
    else: # Default to adding a messages list if not in template
        payload.setdefault("messages", conversation_messages + [{"role": "user", "content": prompt_text}])
        # If neither 'messages' nor 'prompt' was in template, this creates 'messages'.

    # 4. Merge request parameters
    if request_parameters_json:
        try:
            params = json.loads(request_parameters_json)
            if isinstance(params, dict):
                payload.update(params) # Overwrites template values if keys conflict
            else:
                return {"status": "Error: request_parameters_json is not a valid JSON object.", 
                        "agent_response_text": None, "full_response_json": None, "http_status_code": None}
        except json.JSONDecodeError as e:
            return {"status": f"Error: Invalid JSON in request_parameters_json: {e}", 
                    "agent_response_text": None, "full_response_json": None, "http_status_code": None}
    
    # Make the API call
    try:
        response = requests.post(
            api_endpoint_url, 
            headers=headers, 
            json=payload, 
            timeout=REQUEST_TIMEOUT_SECONDS
        )
        
        http_status_code = response.status_code
        full_response_content = response.text # Use .text for cases where .json() might fail

        if response.ok: # Typically 200-299
            try:
                full_response_dict = response.json()
            except json.JSONDecodeError as e:
                 return {"status": f"Error: Failed to parse successful JSON response: {e}", 
                        "agent_response_text": None, "full_response_json": full_response_content, 
                        "http_status_code": http_status_code}

            extracted_text: Optional[str] = None
            if response_extraction_path:
                extracted_value = _get_value_from_path(full_response_dict, response_extraction_path)
                if isinstance(extracted_value, str):
                    extracted_text = extracted_value
                elif extracted_value is not None: # Path led somewhere, but not a string
                    extracted_text = json.dumps(extracted_value) # Return it as JSON string
                else: # Path was invalid or led to None
                    # Try some defaults if path fails
                    extracted_text = _get_value_from_path(full_response_dict, "choices[0].message.content") \
                                  or _get_value_from_path(full_response_dict, "candidates[0].content.parts[0].text") \
                                  or _get_value_from_path(full_response_dict, "text")
                    if not isinstance(extracted_text, str) and extracted_text is not None:
                        extracted_text = json.dumps(extracted_text) # convert if found but not string
                    elif extracted_text is None:
                         extracted_text = f"Could not extract text using path '{response_extraction_path}' or defaults. Full response available."

            else: # No extraction path, try common defaults
                extracted_text = _get_value_from_path(full_response_dict, "choices[0].message.content") \
                              or _get_value_from_path(full_response_dict, "candidates[0].content.parts[0].text") \
                              or _get_value_from_path(full_response_dict, "text")
                if not isinstance(extracted_text, str) and extracted_text is not None:
                    extracted_text = json.dumps(extracted_text)
                elif extracted_text is None:
                    # If no common path worked, return a snippet of the JSON as string
                    extracted_text = json.dumps(full_response_dict, indent=2)[:1000] # First 1000 chars

            return {"status": "Success", "agent_response_text": extracted_text, 
                    "full_response_json": full_response_dict, "http_status_code": http_status_code}
        else:
            return {"status": f"Error: HTTP {http_status_code}", "agent_response_text": None, 
                    "full_response_json": full_response_content, "http_status_code": http_status_code}

    except requests.exceptions.Timeout:
        return {"status": "Error: Request timed out", "agent_response_text": None, 
                "full_response_json": None, "http_status_code": None}
    except requests.exceptions.RequestException as e:
        return {"status": f"Error: Request failed: {e}", "agent_response_text": None, 
                "full_response_json": None, "http_status_code": None}
    except Exception as e: # Catch any other unexpected errors
        return {"status": f"Error: An unexpected error occurred: {e}", "agent_response_text": None, 
                "full_response_json": None, "http_status_code": None}

if __name__ == '__main__':
    # This block is for basic local testing of the service function.
    # It requires a mock API endpoint or a real one with a valid key.
    # Example: Using a public test API (Postman Echo)
    print("--- Testing execute_api_call ---")

    # Test 1: Simple POST to Postman Echo (no auth, simple payload)
    print("\n--- Test 1: Postman Echo Simple POST ---")
    test_payload_template1 = json.dumps({"data": {"message": "Hello from test"}})
    test_params1 = json.dumps({"model": "test-model", "temperature": 0.7})
    result1 = execute_api_call(
        api_endpoint_url="https://postman-echo.com/post",
        prompt_text="This is a test prompt for Postman Echo.", # Will be added to 'messages' by default
        request_payload_template_json=test_payload_template1,
        request_parameters_json=test_params1,
        response_extraction_path="json.data.message" # Path within the echoed JSON response
    )
    print(f"Result 1: Status: {result1['status']}, HTTP Code: {result1['http_status_code']}")
    if result1['status'] == 'Success':
        print(f"  Extracted: {result1['agent_response_text']}")
        # print(f"  Full Response: {json.dumps(result1['full_response_json'], indent=2)[:500]}")
        assert result1['agent_response_text'] == "Hello from test"
    else:
        print(f"  Error details: {result1['full_response_json']}")


    # Test 2: Postman Echo with conversation history
    print("\n--- Test 2: Postman Echo with Conversation History ---")
    history2 = json.dumps([
        {"role": "user", "content": "What was my previous question?"},
        {"role": "assistant", "content": "You asked about the weather."}
    ])
    # Template that uses messages
    template_messages = json.dumps({"messages": [{"role":"system", "content":"You are a helpful assistant."}]})
    result2 = execute_api_call(
        api_endpoint_url="https://postman-echo.com/post",
        prompt_text="And what was my first question?",
        conversation_history_json=history2,
        request_payload_template_json=template_messages,
        response_extraction_path="json.messages[-1].content" # Get the last message's content
    )
    print(f"Result 2: Status: {result1['status']}, HTTP Code: {result1['http_status_code']}")
    if result2['status'] == 'Success':
        print(f"  Extracted (last message content): {result2['agent_response_text']}")
        # Verify history and new prompt are in the echoed messages
        if result2['full_response_json'] and 'json' in result2['full_response_json'] and 'messages' in result2['full_response_json']['json']:
            messages_sent = result2['full_response_json']['json']['messages']
            print(f"  Messages sent to echo: {messages_sent}")
            assert len(messages_sent) == 4 # system + 2 history + 1 current
            assert messages_sent[0]['role'] == 'system'
            assert messages_sent[1]['role'] == 'user' and messages_sent[1]['content'] == "What was my previous question?"
            assert messages_sent[3]['role'] == 'user' and messages_sent[3]['content'] == "And what was my first question?"
            assert result2['agent_response_text'] == "And what was my first question?"
    else:
        print(f"  Error details: {result2['full_response_json']}")

    # Test 3: API Key Env Var (will fail if not set, or succeed if set for a real API)
    # This test is illustrative; it would require a real API and key to fully pass.
    # For now, expect it to fail due to missing key or invalid endpoint unless you set one up.
    print("\n--- Test 3: API Key Env Var (Illustrative - Expects failure/error without real setup) ---")
    os.environ["DUMMY_API_KEY_FOR_TEST"] = "test_key_12345" # Set a dummy key for the test
    result3 = execute_api_call(
        api_endpoint_url="https://api.example.com/v1/chat/completions", # Bogus endpoint
        prompt_text="Hello, API!",
        api_key_env_var="DUMMY_API_KEY_FOR_TEST",
        response_extraction_path="choices[0].message.content"
    )
    del os.environ["DUMMY_API_KEY_FOR_TEST"] # Clean up env var
    print(f"Result 3: Status: {result3['status']}, HTTP Code: {result3['http_status_code']}")
    # We expect this to fail because api.example.com is not a real service endpoint
    assert result3['status'] != "Success" 
    assert "Error: Request failed" in result3['status'] or "Error: API key not found" in result3['status'] or "Error: HTTP" in result3['status']


    # Test 4: Invalid JSON in template
    print("\n--- Test 4: Invalid JSON in request_payload_template_json ---")
    result4 = execute_api_call(
        api_endpoint_url="https://postman-echo.com/post",
        prompt_text="Test prompt",
        request_payload_template_json="{'this is not valid json': "
    )
    print(f"Result 4: Status: {result4['status']}")
    assert "Error: Invalid JSON in request_payload_template_json" in result4['status']

    # Test 5: Timeout
    print("\n--- Test 5: Timeout Test ---")
    # postman-echo can delay response: https://postman-echo.com/delay/3 (seconds)
    # Set timeout lower than delay to trigger it.
    # However, this makes test slow. A more reliable way is to point to a non-responsive IP.
    # Using a known non-routable IP address:
    original_timeout = REQUEST_TIMEOUT_SECONDS
    REQUEST_TIMEOUT_SECONDS = 1 # Temporarily shorten for test
    result5 = execute_api_call(
        api_endpoint_url="http://10.255.255.1/timeout", # Non-routable IP
        prompt_text="This should time out."
    )
    REQUEST_TIMEOUT_SECONDS = original_timeout # Restore
    print(f"Result 5: Status: {result5['status']}")
    assert result5['status'] == "Error: Request timed out"
    
    print("\n--- All local tests for execute_api_call finished ---")
