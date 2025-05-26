import unittest
import os
import sys

# Add Python path modifications
# Assuming the script is in lab/frontends/lc_adk_agent/tests/
# Repo root is ../../../../
# lc_python_core is in ../../../lc_python_core (relative to this file)
# lc_adk_agent is in ../ (relative to this file)

# Path to the repository root
# Corrected path: three levels up from 'tests' directory to reach 'lab/frontends/lc_adk_agent', 
# then two more levels to reach the assumed repository root.
# So, from lab/frontends/lc_adk_agent/tests/ to lab/ is three levels up
# And lab/ is not the repo root. The repo root is one level above 'lab'.
# Let's assume the repo root is the parent of 'lab'.
# So, from lab/frontends/lc_adk_agent/tests to repo root:
# tests -> lc_adk_agent -> frontends -> lab -> <repo_root> (4 levels)
repo_root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
sys.path.insert(0, repo_root_path)

# Path to the 'lab' directory which contains 'frontends' (and thus lc_python_core, lc_adk_agent)
# This is needed because lc_python_core is likely imported as `lc_python_core...`
# and lc_adk_agent as `lab.frontends.lc_adk_agent...`
# The structure is assumed to be:
# <repo_root>/
#   lab/
#     frontends/
#       lc_adk_agent/
#         main.py
#         tests/
#           test_agent.py
#       lc_python_core/
#         ...
# So, we need to add <repo_root> to sys.path for `lab.frontends...` imports
# And we need to add <repo_root>/lab/frontends for `lc_python_core...` if it's directly imported like that.
# However, requirements.txt for lc_adk_agent has "-e ../lc_python_core",
# which implies that when lc_adk_agent is installed (even editable),
# lc_python_core should be discoverable if it's a sibling directory within frontends.
# Let's adjust to ensure `lab.frontends.lc_adk_agent.main` and `lc_python_core` can be imported.
# Adding repo_root should allow `from lab.frontends.lc_adk_agent import main`
# Adding repo_root should also allow `from lc_python_core...` if lc_python_core is in the repo root.
# Given "-e ../lc_python_core" in requirements.txt (relative to lc_adk_agent),
# lc_python_core is at <repo_root>/lab/frontends/lc_python_core.
# So, adding <repo_root> to path should be sufficient if all imports are absolute from repo_root.
# For `from lc_python_core...` to work, `<repo_root>/lab/frontends` needs to be in path.
lab_frontends_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, lab_frontends_path) # for `from lc_python_core...`

LC_CORE_AVAILABLE = False
process_with_lc_core_tool_real = None

try:
    from lab.frontends.lc_adk_agent.main import process_with_lc_core_tool
    process_with_lc_core_tool_real = process_with_lc_core_tool
    # Try importing a known class from lc_python_core to check availability
    from lc_python_core.schemas.mada_schema import MadaSeed
    LC_CORE_AVAILABLE = True
except ImportError:
    LC_CORE_AVAILABLE = False

# Placeholder if lc_python_core or the main tool is not available
def mock_process_with_lc_core_tool(user_query: str) -> str:
    return f"Mock response: lc_python_core not found. Query was: {user_query}"

if not LC_CORE_AVAILABLE:
    process_with_lc_core_tool = mock_process_with_lc_core_tool
elif process_with_lc_core_tool_real is not None: # Should always be true if LC_CORE_AVAILABLE is true
     process_with_lc_core_tool = process_with_lc_core_tool_real


class TestLcAdkAgent(unittest.TestCase):

    def test_runner_works(self):
        """Confirms the test runner itself is functioning."""
        self.assertEqual(1, 1)

    @unittest.skipUnless(LC_CORE_AVAILABLE, "lc_python_core and/or main agent tool not available. Skipping integration test.")
    def test_process_with_lc_core_tool_basic_flow(self):
        """Tests the basic flow of process_with_lc_core_tool when lc_python_core is available."""
        test_query = "test query for lc_core"
        # Ensure we are calling the real function
        self.assertTrue(process_with_lc_core_tool.__name__ != "mock_process_with_lc_core_tool", "Should be testing real function")
        
        result = process_with_lc_core_tool(test_query)
        
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)
        self.assertNotIn("Mock response", result, "Result should not be from the mock function.")
        self.assertNotIn("lc_python_core not found", result, "Result should not indicate lc_python_core is missing.")
        # A more specific check depends on the actual output of the real tool
        # For now, we check that it doesn't return the specific error message from main.py's import fallback
        self.assertNotIn("Error: lc_python_core modules are not available.", result)


    @unittest.skipIf(LC_CORE_AVAILABLE, "lc_python_core is available. Skipping unavailable test.")
    def test_process_with_lc_core_tool_unavailable(self):
        """Tests the behavior when lc_python_core is not available (uses mock)."""
        test_query = "test query when lc_core is unavailable"
        # Ensure we are calling the mock function
        self.assertTrue(process_with_lc_core_tool.__name__ == "mock_process_with_lc_core_tool", "Should be testing mock function")
        
        result = process_with_lc_core_tool(test_query)
        
        self.assertIsInstance(result, str)
        self.assertIn("Mock response", result)
        self.assertIn("lc_python_core not found", result)
        self.assertIn(test_query, result)

if __name__ == '__main__':
    unittest.main()
