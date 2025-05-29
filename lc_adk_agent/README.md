# lC.pythonCore ADK Agent (`lc_adk_agent`)

This module contains the core components for integrating Google's Agent Development Kit (ADK) to provide Large Language Model (LLM) capabilities within the learnt.cloud ecosystem.

## CoreADKAgent

The primary class is `CoreADKAgent`, located in `adk_core_agent.py`.

### Purpose
`CoreADKAgent` is responsible for direct interactions with an LLM using the Google ADK. It handles the initialization of the ADK's LLM client and executes prompts.

### Configuration
The `CoreADKAgent` is typically instantiated with:
- `llm_model_name`: The identifier for the desired LLM (e.g., "gemini-pro").
- `api_key`: The API key for accessing the LLM.

It is expected that this agent is used via the `AdkLlmService` (located in `lab/modules/lC.pythonCore/services/adk_llm_service.py`), which manages the instantiation and configuration of `CoreADKAgent`. The `AdkLlmService` likely sources its configuration (LLM model, API key) from environment variables or a central project configuration.

### Usage
```python
# Conceptual usage, likely within AdkLlmService
# from lC.pythonCore.lc_adk_agent.adk_core_agent import CoreADKAgent
#
# # Configuration would be sourced by AdkLlmService
# API_KEY = "your_api_key" 
# MODEL_NAME = "gemini-pro"
#
# agent = CoreADKAgent(llm_model_name=MODEL_NAME, api_key=API_KEY)
# response = agent.execute_prompt("Translate 'hello' to French.")
# print(response)
```

### Unit Testing Note
There is a known issue with running standalone unit tests for modules within `lC.pythonCore` (including this one) due to the dot (`.`) in the `lC.pythonCore` directory name. This can cause `ModuleNotFoundError` during test discovery and execution. Workarounds involving `sys.path` manipulation have been attempted but were not fully successful in the automated testing environment for this specific case. The code for `CoreADKAgent` itself has been implemented as per requirements.
