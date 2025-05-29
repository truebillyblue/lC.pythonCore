import os # Retained for os.getenv for fallback check
import asyncio # Required for async operations

# Corrected ADK imports
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService, Session
from google.adk.runners import Runner
from google.genai import types as genai_types # For creating content messages
# Attempt to import google.generativeai for programmatic API key configuration
try:
    import google.generativeai as genai
except ImportError:
    genai = None # Define genai as None if import fails, to be checked later

class CoreADKAgent:
    def __init__(self, llm_model_name: str, api_key: str = None, agent_name: str = "CoreADKAgentV1"): # Modified signature
        """
        Initializes the CoreADKAgent.

        Args:
            llm_model_name (str): The name of the LLM model to use (e.g., "gemini-pro").
            api_key (str, optional): The API key for the LLM service. If provided, it will be used
                                     to configure the google-generativeai library. Otherwise,
                                     relies on environment configuration.
            agent_name (str, optional): A name for this agent instance.
        """
        self.model_name = llm_model_name
        self.agent_name = agent_name
        # self.provided_api_key = api_key # No longer needed to store separately like before

        if api_key:
            if genai:
                try:
                    genai.configure(api_key=api_key)
                    print(f"CoreADKAgent: Programmatically configured google-generativeai with provided API key for agent '{agent_name}'.")
                except ImportError: # This specific except block might be redundant if genai is None
                    print(f"ERROR (CoreADKAgent - {agent_name}): Failed to import google.generativeai (should have been caught earlier). API key not configured programmatically.")
                except Exception as e:
                    print(f"ERROR (CoreADKAgent - {agent_name}): Failed to configure google-generativeai with API key: {e}")
            else: # genai import failed
                print(f"ERROR (CoreADKAgent - {agent_name}): Failed to import google.generativeai. API key not configured programmatically.")
        else:
            print(f"INFO (CoreADKAgent - {agent_name}): No direct API key provided, relying on environment configuration (e.g., GOOGLE_API_KEY).")
            # Optional: Check if GOOGLE_API_KEY is set if no direct key provided, for more robust warning
            if not os.getenv("GOOGLE_API_KEY"):
                print(f"WARNING (CoreADKAgent - {agent_name}): No direct API key provided AND GOOGLE_API_KEY environment variable is not set. ADK operations will likely fail.")

        
        # Instantiate the ADK LlmAgent
        try:
            self.llm_agent = LlmAgent(
                name=self.agent_name,
                model=self.model_name,
                instruction="You are a helpful AI assistant." 
            )
        except Exception as e:
            print(f"Error initializing ADK LlmAgent for agent '{agent_name}': {e}")
            self.llm_agent = None
            self.session_service = None
            self.runner = None
            return

        # Instantiate a session service (InMemorySessionService for simplicity)
        self.session_service = InMemorySessionService()

        # Instantiate a runner
        self.runner = Runner(
            agent=self.llm_agent,
            app_name=f"lc_core_adk_app_{agent_name}", # Make app_name unique per agent instance
            session_service=self.session_service
        )

    async def execute_prompt(self, prompt: str, user_id: str = "user_default", session_id: str = "session_default") -> str:
        """
        Sends a prompt to the LLM via the ADK Runner and returns the response.
        (Method body remains unchanged from previous correct version)
        """
        if not self.runner or not self.llm_agent:
            return "Error: ADK Runner or LlmAgent not initialized."

        try:
            session = self.session_service.get_session(user_id=user_id, session_id=session_id)
            if not session:
                session = self.session_service.create_session(user_id=user_id, session_id=session_id)
            
            user_message = genai_types.Content(role="user", parts=[genai_types.Part(text=prompt)])

            final_response_text = "Error: No final response from agent."
            
            async for event in self.runner.run_async(
                user_id=session.user_id, 
                session_id=session.id, 
                new_message=user_message
            ):
                if event.is_final_response():
                    if event.content and event.content.parts and event.content.parts[0].text:
                        final_response_text = event.content.parts[0].text.strip()
                        break 
            
            return final_response_text

        except Exception as e:
            return f"Error during ADK prompt execution: {e}"

# Example Usage (for testing purposes, requires an async context to run execute_prompt)
async def main_test():
    print("Starting CoreADKAgent main_test...")
    
    # Scenario 1: Using API key from environment variable
    print("\n--- CoreADKAgent: Scenario 1: Relying on GOOGLE_API_KEY environment variable ---")
    if not os.getenv("GOOGLE_API_KEY"):
        print("INFO_EXAMPLE (CoreADKAgent): GOOGLE_API_KEY not set for Scenario 1. Service will show warning and likely fail if key is required.")
    try:
        agent_env = CoreADKAgent(llm_model_name="gemini-1.0-pro", agent_name="EnvAgent")
        if agent_env.llm_agent:
            response_env = await agent_env.execute_prompt("What is the capital of Spain?")
            print(f"LLM Response (EnvAgent): {response_env}")
        else:
            print("CoreADKAgent (EnvAgent) did not initialize llm_agent correctly.")
    except Exception as e:
        print(f"Error in CoreADKAgent Scenario 1: {e}")

    # Scenario 2: Providing API key programmatically
    print("\n--- CoreADKAgent: Scenario 2: Providing API key programmatically ---")
    programmatic_api_key = os.getenv("TEST_GOOGLE_API_KEY_PROGRAMMATIC", "YOUR_ACTUAL_API_KEY_HERE_CORE_AGENT")
    if programmatic_api_key == "YOUR_ACTUAL_API_KEY_HERE_CORE_AGENT" and not os.getenv("GOOGLE_API_KEY"):
         print("INFO_EXAMPLE (CoreADKAgent): No actual programmatic API key provided for Scenario 2 and GOOGLE_API_KEY not set. This will likely fail.")

    try:
        agent_prog = CoreADKAgent(llm_model_name="gemini-1.0-pro", api_key=programmatic_api_key, agent_name="ProgAgent")
        if agent_prog.llm_agent:
            response_prog = await agent_prog.execute_prompt("What is the largest ocean on Earth?")
            print(f"LLM Response (ProgAgent): {response_prog}")
        else:
            print("CoreADKAgent (ProgAgent) did not initialize llm_agent correctly.")
    except Exception as e:
        print(f"Error in CoreADKAgent Scenario 2: {e}")
    
    print("CoreADKAgent main_test finished.")

if __name__ == "__main__":
    print("CoreADKAgent class defined. To run the main_test, ensure GOOGLE_API_KEY (for scenario 1) or a valid key for scenario 2 is available, then execute:")
    print("import asyncio; asyncio.run(main_test())")
    # Example of direct execution:
    # try:
    #     asyncio.run(main_test())
    # except Exception as e:
    #     print(f"Error running main_test directly: {e}")
    pass
