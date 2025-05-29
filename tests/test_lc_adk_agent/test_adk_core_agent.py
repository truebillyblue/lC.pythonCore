import sys
import os
import asyncio # Required for async test cases

# Add the 'lab/modules' directory to sys.path to help resolve 'lC.pythonCore'
# This is crucial for the 'from lC.pythonCore...' import below to work,
# assuming the test runner itself doesn't correctly add /app/lab/modules to sys.path.
modules_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if modules_path not in sys.path:
    sys.path.insert(0, modules_path)
    # print(f"DEBUG: Added to sys.path in test_adk_core_agent.py: {modules_path}")
    # print(f"DEBUG: Current sys.path: {sys.path}")


import unittest
from unittest.mock import patch, MagicMock, AsyncMock # Added AsyncMock

# Attempt to import CoreADKAgent.
# This import is known to be problematic due to 'lC.pythonCore' directory naming.
# If this fails, the tests in this file won't run.
try:
    from lC.pythonCore.lc_adk_agent.adk_core_agent import CoreADKAgent
except ModuleNotFoundError as e:
    print(f"CRITICAL_ERROR_TEST_SETUP: Failed to import CoreADKAgent: {e}. Tests in this file will likely fail to load or run.")
    CoreADKAgent = None # Define as None to allow file to parse if import fails.
except Exception as e:
    print(f"CRITICAL_ERROR_TEST_SETUP: An unexpected error occurred during CoreADKAgent import: {e}")
    CoreADKAgent = None


# Use IsolatedAsyncioTestCase for async test methods
class TestCoreADKAgent(unittest.IsolatedAsyncioTestCase):

    # Path to the module where LlmAgent, InMemorySessionService, Runner, genai_types are imported by adk_core_agent.py
    ADK_CORE_AGENT_MODULE_PATH = 'lC.pythonCore.lc_adk_agent.adk_core_agent'

    def setUp(self):
        # This check ensures tests don't run if CoreADKAgent couldn't be imported.
        if CoreADKAgent is None:
            self.skipTest("CoreADKAgent could not be imported, skipping tests.")

    @patch.dict(os.environ, {"GOOGLE_API_KEY": "test_api_key_env"}, clear=True)
    @patch(f'{ADK_CORE_AGENT_MODULE_PATH}.Runner')
    @patch(f'{ADK_CORE_AGENT_MODULE_PATH}.InMemorySessionService')
    @patch(f'{ADK_CORE_AGENT_MODULE_PATH}.LlmAgent')
    async def test_agent_instantiation_with_env_api_key(self, MockLlmAgent, MockSessionService, MockRunner):
        """Test CoreADKAgent instantiation when API key is from environment."""
        mock_llm_agent_instance = MockLlmAgent.return_value
        MockSessionService.return_value = MagicMock()
        MockRunner.return_value = MagicMock()

        agent = CoreADKAgent(llm_model_name="gemini-pro")
        
        self.assertEqual(agent.model_name, "gemini-pro")
        self.assertEqual(agent.provided_api_key, None) # API key was from env
        MockLlmAgent.assert_called_once_with(
            name="CoreADKAgentV1", 
            model="gemini-pro", 
            instruction="You are a helpful AI assistant."
        )
        self.assertIsNotNone(agent.session_service)
        self.assertIsNotNone(agent.runner)

    @patch.dict(os.environ, {}, clear=True) # No GOOGLE_API_KEY in env
    @patch(f'{ADK_CORE_AGENT_MODULE_PATH}.Runner')
    @patch(f'{ADK_CORE_AGENT_MODULE_PATH}.InMemorySessionService')
    @patch(f'{ADK_CORE_AGENT_MODULE_PATH}.LlmAgent')
    async def test_agent_instantiation_with_direct_api_key_and_no_env_key(self, MockLlmAgent, MockSessionService, MockRunner):
        """Test CoreADKAgent instantiation with a directly provided API key and no env var."""
        mock_llm_agent_instance = MockLlmAgent.return_value
        MockSessionService.return_value = MagicMock()
        MockRunner.return_value = MagicMock()

        # Suppress the print warning for this specific test
        with patch('builtins.print') as mock_print:
            agent = CoreADKAgent(llm_model_name="gemini-pro", api_key="test_api_key_direct")
        
        self.assertEqual(agent.model_name, "gemini-pro")
        self.assertEqual(agent.provided_api_key, "test_api_key_direct")
        MockLlmAgent.assert_called_once_with(
            name="CoreADKAgentV1", 
            model="gemini-pro", 
            instruction="You are a helpful AI assistant."
        )
        # Check if the info print about using provided key occurred (since env var not set)
        mock_print.assert_any_call("Info: api_key provided to CoreADKAgent, but GOOGLE_API_KEY environment variable was not set. ADK will likely fail if it relies solely on the env var.")


    @patch(f'{ADK_CORE_AGENT_MODULE_PATH}.genai_types')
    @patch(f'{ADK_CORE_AGENT_MODULE_PATH}.Runner')
    @patch(f'{ADK_CORE_AGENT_MODULE_PATH}.InMemorySessionService')
    @patch(f'{ADK_CORE_AGENT_MODULE_PATH}.LlmAgent')
    async def test_execute_prompt_success(self, MockLlmAgent, MockSessionService, MockRunner, MockGenaiTypes):
        """Test successful async prompt execution."""
        mock_llm_agent_instance = MockLlmAgent.return_value
        mock_session_service_instance = MockSessionService.return_value
        mock_runner_instance = MockRunner.return_value
        
        # Mock session object
        mock_session = MagicMock(spec=Session) # Use Session spec from google.adk.sessions
        mock_session.user_id = "test_user"
        mock_session.id = "test_session"
        mock_session_service_instance.get_session.return_value = mock_session
        mock_session_service_instance.create_session.return_value = mock_session # If get_session returns None

        # Mock genai_types for message creation
        MockGenaiTypes.Content.return_value = MagicMock(name="UserMessage")
        MockGenaiTypes.Part.return_value = MagicMock(name="UserMessagePart")

        # Mock the async generator for runner.run_async
        async def mock_run_async_generator(*args, **kwargs):
            mock_event = MagicMock()
            mock_event.is_final_response.return_value = True
            mock_event.content = MagicMock()
            mock_event.content.parts = [MagicMock()]
            mock_event.content.parts[0].text = "LLM response text"
            yield mock_event

        mock_runner_instance.run_async = mock_run_async_generator

        with patch.dict(os.environ, {"GOOGLE_API_KEY": "fake_key"}): # Ensure env var is set for LlmAgent init
            agent = CoreADKAgent(llm_model_name="gemini-pro")
        
        prompt = "Explain quantum computing."
        response = await agent.execute_prompt(prompt, user_id="test_user", session_id="test_session")

        self.assertEqual(response, "LLM response text")
        MockGenaiTypes.Content.assert_called_once_with(role="user", parts=[MockGenaiTypes.Part.return_value])
        MockGenaiTypes.Part.assert_called_once_with(text=prompt)
        # Note: Checking call to mock_runner_instance.run_async is tricky with async generators.
        # We are implicitly testing it by checking the response.

    @patch(f'{ADK_CORE_AGENT_MODULE_PATH}.LlmAgent', side_effect=Exception("LlmAgent Init Failed"))
    async def test_agent_initialization_failure(self, MockLlmAgent):
        """Test handling of LlmAgent initialization failure."""
        with patch('builtins.print') as mock_print:
            agent = CoreADKAgent(llm_model_name="gemini-pro")
        
        self.assertIsNone(agent.llm_agent)
        self.assertIsNone(agent.runner)
        self.assertIsNone(agent.session_service)
        mock_print.assert_any_call("Error initializing ADK LlmAgent: LlmAgent Init Failed")
        
        response = await agent.execute_prompt("Any prompt")
        self.assertEqual(response, "Error: ADK Runner or LlmAgent not initialized.")

    @patch.dict(os.environ, {}, clear=True) # No GOOGLE_API_KEY
    @patch(f'{ADK_CORE_AGENT_MODULE_PATH}.LlmAgent') # Mock LlmAgent to avoid init error for this specific test
    async def test_agent_instantiation_no_api_key_warning(self, MockLlmAgent):
        """Test warning if no API key is provided or found in environment."""
        MockLlmAgent.return_value = MagicMock() # Successful LlmAgent mock
        with patch('builtins.print') as mock_print, \
             patch(f'{ADK_CORE_AGENT_MODULE_PATH}.Runner'), \
             patch(f'{ADK_CORE_AGENT_MODULE_PATH}.InMemorySessionService'): # Mock other ADK components
            CoreADKAgent(llm_model_name="gemini-pro") # api_key not provided
            mock_print.assert_any_call("Warning: GOOGLE_API_KEY environment variable is not set, and no api_key was provided to CoreADKAgent.")


if __name__ == "__main__":
    # This allows running the test file directly.
    # The try-except for CoreADKAgent import handles the case where it can't be found.
    if CoreADKAgent is None:
        print("Skipping test execution via __main__ because CoreADKAgent could not be imported.")
    else:
        print(f"Running tests in {__file__} via __main__...")
        unittest.main()
