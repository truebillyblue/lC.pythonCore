from google.adk.agents import Agent
from google.adk.tools import FunctionTool

# Attempt to import from lc_python_core
# These imports are based on the subtask description.
# If lc_python_core is not in the PYTHONPATH, these will fail at runtime.
try:
    from lc_python_core.schemas.mada_schema import (
        MadaSeed, InputEvent, L1Context, L2Frame, L3Keymap,
        L4Anchor, L5Field, L6Reflection, L7Application, SeedOutputs
    )
    from lc_python_core.sops import (
        sop_l1_startle, sop_l2_frame_click, sop_l3_keymap_select,
        sop_l4_anchor_find, sop_l5_field_fill, sop_l6_reflect_infer,
        sop_l7_apply_done
    )
    from lc_python_core.services.mock_lc_core_services import MockLcCoreServices
    LC_CORE_AVAILABLE = True
except ImportError as e:
    LC_CORE_AVAILABLE = False
    # Store the exception to provide more context if the tool is called
    LC_CORE_IMPORT_ERROR = e 
    # Define dummy classes if lc_python_core is not available to allow for agent definition
    # This is primarily for the ADK to be able to inspect the agent structure.
    # Actual execution of the tool will fail informatively.
    class MadaSeed: pass
    class InputEvent: pass
    class L1Context: pass
    class L2Frame: pass
    class L3Keymap: pass
    class L4Anchor: pass
    class L5Field: pass
    class L6Reflection: pass
    class L7Application: pass
    class SeedOutputs: pass # Added this as it's used in the tool
    class MockLcCoreServices: pass
    def sop_l1_startle(seed, services): return seed
    def sop_l2_frame_click(seed, services): return seed
    def sop_l3_keymap_select(seed, services): return seed
    def sop_l4_anchor_find(seed, services): return seed
    def sop_l5_field_fill(seed, services): return seed
    def sop_l6_reflect_infer(seed, services): return seed
    def sop_l7_apply_done(seed, services): return seed


# Define the original echo_tool for basic testing/reference
def echo_tool(message: str) -> str:
  """Echoes the input message."""
  return f"Agent received: {message}"

# Define the new tool function for lc_python_core integration
def process_with_lc_core_tool(user_query: str) -> str:
    """
    Processes the user query using lc_python_core SOPs and returns a result.
    """
    if not LC_CORE_AVAILABLE:
        return (
            "Error: lc_python_core modules are not available. "
            f"ImportError: {LC_CORE_IMPORT_ERROR}"
        )

    try:
        # 1. Initialize MockLcCoreServices
        mock_services = MockLcCoreServices()

        # 2. Create an InputEvent
        input_event = InputEvent(
            event_data={"user_query": user_query},
            event_source_id="adk_agent"
            # Add other necessary fields for InputEvent if any, using defaults or placeholders
        )

        # 3. Create an initial MadaSeed object
        # For many fields, we'll rely on default_factory or provide basic initial values.
        # This might need adjustment based on lc_python_core's exact expectations.
        mada_seed = MadaSeed(
            l1_context=L1Context(
                input_event=input_event,
                # Initialize other L1Context fields as necessary
            ),
            l2_frame=L2Frame(), # Initialize with defaults
            l3_keymap=L3Keymap(), # Initialize with defaults
            l4_anchor=L4Anchor(), # Initialize with defaults
            l5_field=L5Field(), # Initialize with defaults
            l6_reflection=L6Reflection(summary_of_reasoning="Initial state"), # Initialize with defaults
            l7_application=L7Application(seed_outputs=SeedOutputs()) # Initialize with defaults
            # Populate other top-level MadaSeed fields if necessary
        )

        # 4. Invoke the L1-L7 SOPs sequentially
        mada_seed = sop_l1_startle(mada_seed, mock_services)
        mada_seed = sop_l2_frame_click(mada_seed, mock_services)
        mada_seed = sop_l3_keymap_select(mada_seed, mock_services)
        mada_seed = sop_l4_anchor_find(mada_seed, mock_services)
        mada_seed = sop_l5_field_fill(mada_seed, mock_services)
        mada_seed = sop_l6_reflect_infer(mada_seed, mock_services)
        mada_seed = sop_l7_apply_done(mada_seed, mock_services)

        # 5. Extract a meaningful part of the mada_seed to return
        # speech_output = mada_seed.l7_application.seed_outputs.SPEECH_TEXT.GOOGLE_ASSISTANT_USER.text
        # For now, returning a summary from l6_reflection or l7_application outputs
        if mada_seed.l7_application and mada_seed.l7_application.seed_outputs:
             # Check if SPEECH_TEXT and GOOGLE_ASSISTANT_USER are available and have text
            speech_text_map = mada_seed.l7_application.seed_outputs.get("SPEECH_TEXT", {})
            google_assistant_output = speech_text_map.get("GOOGLE_ASSISTANT_USER", {})
            speech_text = google_assistant_output.get("text", "")
            if speech_text:
                return f"LC Core processed: {speech_text}"
            
            # Fallback if specific speech text is not found
            return f"LC Core processed. L7 Outputs: {str(mada_seed.l7_application.seed_outputs)}"
        elif mada_seed.l6_reflection and mada_seed.l6_reflection.summary_of_reasoning:
            return f"LC Core processed. L6 Reflection: {mada_seed.l6_reflection.summary_of_reasoning}"
        else:
            return "LC Core processed, but no specific output found in L7 or L6."

    except Exception as e:
        # import traceback
        # tb_str = traceback.format_exc()
        return f"Error during lc_python_core processing: {str(e)}"


# Original root_agent using echo_tool (can be kept for reference)
echo_agent = Agent(
    name="echo_agent",
    description="A simple agent that echoes the input.",
    model="gemini-1.5-flash", 
    tools=[
        FunctionTool(
            func=process_with_lc_core_tool,
            description="Echoes the input message."
        )
    ]
)

# New agent using the lc_python_core tool
lc_core_agent = Agent(
    name="lc_core_agent",
    description="Agent that processes input using lc_python_core.",
    model="gemini-1.5-flash", # Or any other valid model
    tools=[
        FunctionTool(
            fn=process_with_lc_core_tool,
            description="Processes the user query via lc_python_core SOPs."
        )
    ]
)


if __name__ == "__main__":
  print("Agents defined. To run an agent, use the ADK CLI. Examples:")
  print("  adk run lab.frontends.lc_adk_agent.main:echo_agent")
  print("  adk run lab.frontends.lc_adk_agent.main:lc_core_agent")
  
  print("\nSimulating direct calls to tools for basic testing:")
  
  # Test echo_tool
  test_echo_message = "hello from echo_tool direct call"
  echo_response = echo_tool(test_echo_message)
  print(f"Direct call to echo_tool with '{test_echo_message}': {echo_response}")

  # Test process_with_lc_core_tool
  # This will provide an error message if lc_python_core is not found.
  test_lc_core_query = "hello from lc_core_tool direct call"
  # print(f"\nAttempting direct call to process_with_lc_core_tool with query: '{test_lc_core_query}'")
  # print("Note: This will fail if lc_python_core is not correctly installed or not in PYTHONPATH.")
  
  lc_core_response = process_with_lc_core_tool(test_lc_core_query)
  print(f"Direct call to process_with_lc_core_tool with '{test_lc_core_query}': {lc_core_response}")

  # The following is for more advanced ADK runner programmatic invocation,
  # typically not needed for simple CLI-based execution.
  # from google.adk.runner import run
  # run(lc_core_agent) # Example: This would usually start a server or interactive session.
  pass
