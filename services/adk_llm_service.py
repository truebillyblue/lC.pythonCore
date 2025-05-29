"""Provides a service for interacting with LLMs using the Google ADK."""

import os # Retained for os.getenv for fallback check, though primary config is via genai.configure
import asyncio

# Corrected ADK imports
from google.adk.agents import LlmAgent
from google.adk.sessions import InMemorySessionService, Session # Session might be needed for get/create
from google.adk.runners import Runner
from google.genai import types as genai_types # For creating content messages
# Attempt to import google.generativeai for programmatic API key configuration
try:
    import google.generativeai as genai
except ImportError:
    genai = None # Define genai as None if import fails, to be checked later

class AdkLlmService:
    """A service to interact with LLMs via the Google ADK, using LlmAgent and Runner."""

    def __init__(self, model_name: str = "gemini-1.5-flash-001", api_key: str = None): # Modified signature
        """
        Initializes the ADK LLM service.

        Args:
            model_name: The name of the LLM model to use (e.g., "gemini-1.5-flash-001").
            api_key: Optional. The Google API Key. If provided, it will be used to configure
                     the google-generativeai library. Otherwise, relies on environment configuration.
        """
        self.model_name = model_name
        
        if api_key:
            if genai:
                try:
                    genai.configure(api_key=api_key)
                    print(f"AdkLlmService: Programmatically configured google-generativeai with provided API key.")
                except Exception as e:
                    print(f"ERROR (AdkLlmService): Failed to configure google-generativeai with API key: {e}")
            else:
                print("ERROR (AdkLlmService): Failed to import google.generativeai. API key not configured programmatically.")
        else:
            print("INFO (AdkLlmService): No direct API key provided, relying on environment configuration (e.g., GOOGLE_API_KEY).")
            # Optional: Check if GOOGLE_API_KEY is set if no direct key provided, for more robust warning
            if not os.getenv("GOOGLE_API_KEY"):
                print("WARNING (AdkLlmService): No direct API key provided AND GOOGLE_API_KEY environment variable is not set. ADK operations will likely fail.")


        try:
            self.llm_agent = LlmAgent(
                name="adk_llm_service_agent", 
                model=self.model_name, 
                instruction="You are a helpful AI assistant performing specific text analysis tasks."
            )
            self.session_service = InMemorySessionService()
            self.runner = Runner(
                agent=self.llm_agent, 
                app_name="lc_adk_llm_service_app", 
                session_service=self.session_service
            )
            print(f"AdkLlmService initialized successfully with model: {self.model_name}")
        except Exception as e:
            print(f"Error initializing AdkLlmService components: {e}")
            self.llm_agent = None
            self.session_service = None
            self.runner = None
            raise ConnectionError(f"Failed to initialize AdkLlmService: {e}") from e


    async def prompt_llm(self, prompt_text: str, user_id: str = "adk_service_user", session_id: str = "adk_service_session") -> str:
        """
        Sends a prompt to the configured LLM using the ADK Runner and returns the response.
        (Method body remains unchanged from previous correct version)
        """
        if not self.runner or not self.llm_agent or not self.session_service:
            raise RuntimeError("AdkLlmService is not properly initialized. Runner, LlmAgent, or SessionService is missing.")

        content = genai_types.Content(role="user", parts=[genai_types.Part(text=prompt_text)])
        final_response_text = "Error: No final response from ADK LLM service." 

        try:
            try:
                session = self.session_service.get_session(app_name=self.runner.app_name, user_id=user_id, session_id=session_id)
            except KeyError: 
                session = self.session_service.create_session(app_name=self.runner.app_name, user_id=user_id, session_id=session_id)

            async for event in self.runner.run_async(
                user_id=session.user_id, session_id=session.id, new_message=content
            ):
                if event.is_final_response():
                    if event.content and event.content.parts and event.content.parts[0].text:
                        final_response_text = event.content.parts[0].text.strip()
                        break 
            return final_response_text
        except Exception as e:
            print(f"Error during AdkLlmService prompt execution: {e}")
            raise RuntimeError(f"AdkLlmService call failed: {e}") from e

# Example usage
async def main_example():
    """Example of how to use the AdkLlmService."""
    print("Starting ADK LLM Service example...")
    
    # Scenario 1: Relying on environment variable
    print("\n--- Scenario 1: Relying on GOOGLE_API_KEY environment variable ---")
    if not os.getenv("GOOGLE_API_KEY"):
        print("INFO_EXAMPLE: GOOGLE_API_KEY not set for Scenario 1. Service will show warning.")
    try:
        service_env = AdkLlmService(model_name="gemini-1.0-pro")
        if service_env.llm_agent: # Check if initialization succeeded
            response_env = await service_env.prompt_llm("What is the capital of Germany?")
            print(f"LLM Response (env key): {response_env}")
        else:
            print("Service (env key) did not initialize llm_agent correctly.")
    except Exception as e:
        print(f"Error in Scenario 1: {e}")

    # Scenario 2: Providing API key programmatically
    print("\n--- Scenario 2: Providing API key programmatically ---")
    # Replace "YOUR_ACTUAL_API_KEY_HERE" with a real key for this to work.
    # IMPORTANT: Do not commit real API keys to version control.
    programmatic_api_key = os.getenv("TEST_GOOGLE_API_KEY_PROGRAMMATIC", "YOUR_ACTUAL_API_KEY_HERE") 
    if programmatic_api_key == "YOUR_ACTUAL_API_KEY_HERE" and not os.getenv("GOOGLE_API_KEY"):
        print("INFO_EXAMPLE: No actual programmatic API key provided for Scenario 2 and GOOGLE_API_KEY not set. This will likely fail if the key is invalid or ADK requires it.")
    
    try:
        service_prog = AdkLlmService(model_name="gemini-1.0-pro", api_key=programmatic_api_key)
        if service_prog.llm_agent: # Check if initialization succeeded
            response_prog = await service_prog.prompt_llm("What is the currency of Japan?")
            print(f"LLM Response (programmatic key): {response_prog}")
        else:
            print("Service (programmatic key) did not initialize llm_agent correctly.")
    except Exception as e:
        print(f"Error in Scenario 2: {e}")


if __name__ == '__main__':
    print("AdkLlmService defined. To run the main_example, ensure GOOGLE_API_KEY (for scenario 1) or a valid key for scenario 2 is available, then execute:")
    print("import asyncio; asyncio.run(main_example())")
    # Example of direct execution (ensure any required API keys are set as environment variables or in the code for testing)
    # try:
    #     asyncio.run(main_example())
    # except Exception as e:
    #     print(f"Error running main_example directly: {e}")
    pass
