# Learnt.Cloud ADK Agent

## Overview

This package provides an Agent Development Kit (ADK) interface to the `lc_python_core` engine. Its primary purpose is to allow interaction with the L1-L7 Standard Operating Procedures (SOPs) of `lc_python_core` using the Google ADK framework. This enables structured, tool-based interactions with the core functionalities of Learnt.Cloud.

The agent defines tools that wrap the `lc_python_core` processing pipeline, making it accessible to ADK-compatible clients and orchestrators.

## Setup and Installation

### Dependencies:

1.  **`google-adk`**: This is the core framework for running the agent.
2.  **`lc_python_core`**: This is the Learnt.Cloud core engine that the agent interfaces with.

### Installation Steps:

1.  **Ensure `lc_python_core` is Accessible:**
    The `lc_python_core` package must be available in your Python environment. It is typically located as a sibling directory to `lc_adk_agent` within the `lab/frontends/` directory. To ensure it can be imported, you need to add the `lab/frontends` directory to your `PYTHONPATH`.

    From the repository root, you can set `PYTHONPATH` for your current session:

    *   **Linux/macOS:**
        ```bash
        export PYTHONPATH=${PYTHONPATH}:$(pwd)/lab/frontends
        # Or, if PYTHONPATH is not yet set or you want to prioritize this path:
        # export PYTHONPATH=$(pwd)/lab/frontends
        ```

    *   **Windows (Command Prompt):**
        ```cmd
        set PYTHONPATH=%PYTHONPATH%;%cd%\lab\frontends
        ```

    *   **Windows (PowerShell):**
        ```powershell
        $env:PYTHONPATH += ";${pwd}\lab\frontends"
        ```
    Alternatively, configure this path in your IDE.

2.  **Install Requirements:**
    Navigate to this `lc_adk_agent` directory (`./lab/frontends/lc_adk_agent/`) and install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
    This will install `google-adk` and set up an editable install for `lc_python_core` (referencing the local path).

## Running the Agent

The agent is run using the `adk` command-line interface (CLI).

1.  **Navigate to the repository root directory.** This is important because the agent path used in the `adk run` command is relative to the current working directory from which ADK discovers modules. (Alternatively, ensure your PYTHONPATH is set up so ADK can find `lab.frontends...` from anywhere).

2.  **Use the `adk run` command followed by the path to the agent definition:**

    *   To run the agent that interacts with `lc_python_core`:
        ```bash
        adk run lab.frontends.lc_adk_agent.main:lc_core_agent
        ```

    *   To run a simple echo agent (for basic ADK testing):
        ```bash
        adk run lab.frontends.lc_adk_agent.main:echo_agent
        ```

3.  **Interact with the Agent:**
    Once started, the ADK typically launches a local development server (e.g., at `http://localhost:8000` or `http://127.0.0.1:8000`). You can interact with the agent by making HTTP requests (e.g., using `curl` or tools like Postman) to the appropriate endpoints, as detailed in the Google ADK documentation. The ADK web UI also provides an interface for interaction.

## Running Tests

Unit tests are provided to verify the agent's functionality.

1.  **Ensure `PYTHONPATH` is set up correctly** as described in the "Setup and Installation" section, so that the tests can import both the agent code and `lc_python_core`.

2.  **Run tests using one of the following commands:**

    *   **From the repository root:**
        ```bash
        python -m unittest discover ./lab/frontends/lc_adk_agent/tests
        ```

    *   **From within the `lc_adk_agent` directory (`./lab/frontends/lc_adk_agent/`):**
        ```bash
        python -m unittest discover ./tests
        ```

    **Note:** Tests that specifically require `lc_python_core` (like `test_process_with_lc_core_tool_basic_flow`) will be automatically skipped if `lc_python_core` or its dependencies are not correctly set up and importable. The test output will indicate if these tests were skipped.
```
