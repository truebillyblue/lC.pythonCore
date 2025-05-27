import unittest
import json
import shutil
from pathlib import Path
import os

# Adjust import path to access lc_mem_service from the tests directory
# This assumes 'lc_python_core' is structured such that 'services' is a sibling to 'tests'
# or that PYTHONPATH is set up correctly for testing.
# For testing, it's common to adjust sys.path or use relative imports carefully.
# Given the structure, if tests/ is run as a module, services might be found via ..services
try:
    from ..services.lc_mem_service import (
        mock_lc_mem_core_ensure_uid,
        mock_lc_mem_core_create_object,
        mock_lc_mem_core_get_object,
        mock_lc_mem_core_update_object,
        mock_lc_mem_core_delete_object,
        mock_lc_mem_core_query_objects,
        MADA_VAULT_DIR # Import to use and clean up
    )
except ImportError: # Fallback for direct script execution or different test runner setup
    import sys
    # Assuming the script is run from within lc_python_core/tests or similar context
    # Go up two levels from tests/test_lc_mem_service.py to frontends/ then into lc_python_core/
    # This path needs to be robust depending on how tests are discovered and run.
    # A safer way is to ensure lc_python_core is in PYTHONPATH when running tests.
    # For this subtask, we'll assume a common structure or that PYTHONPATH handles it.
    # If this file is lab/frontends/lc_python_core/tests/test_lc_mem_service.py
    # then Path(__file__).resolve().parents[1] is .../tests/
    # Path(__file__).resolve().parents[2] is .../lc_python_core/
    # Path(__file__).resolve().parents[3] is .../frontends/
    # Path(__file__).resolve().parents[4] is .../lab/
    
    # This relative path adjustment is fragile. A better solution for a real project
    # would be to use a proper package installation or PYTHONPATH setup.
    # For now, let's try a common relative path approach if the direct one fails.
    package_path = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(package_path.parent)) # Add 'frontends' to path
    
    from lc_python_core.services.lc_mem_service import (
        mock_lc_mem_core_ensure_uid,
        mock_lc_mem_core_create_object,
        mock_lc_mem_core_get_object,
        mock_lc_mem_core_update_object,
        mock_lc_mem_core_delete_object,
        mock_lc_mem_core_query_objects,
        MADA_VAULT_DIR
    )


class TestLcMemService(unittest.TestCase):

    def setUp(self):
        # Ensure the MADA vault directory is clean before each test
        if MADA_VAULT_DIR.exists():
            shutil.rmtree(MADA_VAULT_DIR)
        MADA_VAULT_DIR.mkdir(parents=True, exist_ok=True)
        self.test_persona_context = {"user_id": "test_user", "roles": ["tester"]}

    def tearDown(self):
        # Clean up the MADA vault directory after each test
        if MADA_VAULT_DIR.exists():
            shutil.rmtree(MADA_VAULT_DIR)

    def test_01_ensure_uid_generation(self):
        uid1 = mock_lc_mem_core_ensure_uid("TestObject")
        self.assertTrue(uid1.startswith("urn:crux:uid::"))
        uid2 = mock_lc_mem_core_ensure_uid("TestObject")
        self.assertTrue(uid2.startswith("urn:crux:uid::"))
        self.assertNotEqual(uid1, uid2)

    def test_02_ensure_uid_validation(self):
        valid_uid = "urn:crux:uid::1234567890abcdef1234567890abcdef" # Example valid format
        validated_uid = mock_lc_mem_core_ensure_uid("TestObject", existing_uid_candidate=valid_uid)
        self.assertEqual(validated_uid, valid_uid)

        invalid_uid_short = "urn:crux:uid::123"
        new_uid_short = mock_lc_mem_core_ensure_uid("TestObject", existing_uid_candidate=invalid_uid_short)
        self.assertNotEqual(new_uid_short, invalid_uid_short) # Should generate new
        self.assertTrue(new_uid_short.startswith("urn:crux:uid::"))

        invalid_uid_prefix = "urn:test:uid::1234567890abcdef"
        new_uid_prefix = mock_lc_mem_core_ensure_uid("TestObject", existing_uid_candidate=invalid_uid_prefix)
        self.assertNotEqual(new_uid_prefix, invalid_uid_prefix)
        self.assertTrue(new_uid_prefix.startswith("urn:crux:uid::"))


    def test_03_create_and_get_object(self):
        object_type = "MyTestObject"
        uid = mock_lc_mem_core_ensure_uid(object_type)
        payload = {"data": "test_data", "value": 123}
        metadata = {"version": "0.1.0", "custom_tag": "test"}

        create_success = mock_lc_mem_core_create_object(uid, payload, initial_metadata=metadata, requesting_persona_context=self.test_persona_context)
        self.assertTrue(create_success)

        retrieved_payload = mock_lc_mem_core_get_object(uid, requesting_persona_context=self.test_persona_context)
        self.assertEqual(retrieved_payload, payload)
        
        # Verify metadata file content (optional, but good for completeness)
        uid_hex = uid.split('::')[-1]
        metadata_file = MADA_VAULT_DIR / uid_hex / "metadata.json"
        self.assertTrue(metadata_file.exists())
        with open(metadata_file, 'r') as f:
            stored_meta = json.load(f)
        self.assertEqual(stored_meta.get("crux_uid"), uid)
        self.assertEqual(stored_meta.get("object_type"), object_type) # Adjusted to use object_type passed to ensure_uid
        self.assertEqual(stored_meta.get("custom_tag"), "test")
        self.assertIn("created_at", stored_meta)


    def test_04_get_nonexistent_object(self):
        uid = "urn:crux:uid::nonexistent123"
        retrieved_payload = mock_lc_mem_core_get_object(uid, requesting_persona_context=self.test_persona_context)
        self.assertIsNone(retrieved_payload)

    def test_05_update_object(self):
        object_type = "UpdatableObject"
        uid = mock_lc_mem_core_ensure_uid(object_type)
        payload1 = {"data": "initial_data"}
        create_success = mock_lc_mem_core_create_object(uid, payload1, {"version":"1.0.0"}, self.test_persona_context)
        self.assertTrue(create_success)

        payload2 = {"data": "updated_data", "new_field": True}
        update_success = mock_lc_mem_core_update_object(uid, payload2, self.test_persona_context, {"version":"1.0.1", "update_note":"test update"})
        self.assertTrue(update_success)

        retrieved_payload = mock_lc_mem_core_get_object(uid, self.test_persona_context)
        self.assertEqual(retrieved_payload, payload2)

        # Verify metadata update
        uid_hex = uid.split('::')[-1]
        metadata_file = MADA_VAULT_DIR / uid_hex / "metadata.json"
        with open(metadata_file, 'r') as f:
            stored_meta = json.load(f)
        self.assertEqual(stored_meta.get("version"), "1.0.1")
        self.assertIn("updated_at", stored_meta)
        self.assertEqual(stored_meta.get("update_note"), "test update")


    def test_06_update_nonexistent_object(self):
        uid = "urn:crux:uid::nonexistentupdate123"
        payload = {"data": "data"}
        update_success = mock_lc_mem_core_update_object(uid, payload, self.test_persona_context)
        self.assertFalse(update_success)

    def test_07_delete_object(self):
        object_type = "DeletableObject"
        uid = mock_lc_mem_core_ensure_uid(object_type)
        payload = {"data": "to_be_deleted"}
        mock_lc_mem_core_create_object(uid, payload, requesting_persona_context=self.test_persona_context)
        
        uid_hex = uid.split('::')[-1]
        self.assertTrue((MADA_VAULT_DIR / uid_hex).exists()) # Check directory exists

        delete_success = mock_lc_mem_core_delete_object(uid, self.test_persona_context, "test deletion")
        self.assertTrue(delete_success)
        self.assertFalse((MADA_VAULT_DIR / uid_hex).exists()) # Check directory removed

        retrieved_payload = mock_lc_mem_core_get_object(uid, self.test_persona_context)
        self.assertIsNone(retrieved_payload)

    def test_08_delete_nonexistent_object(self):
        uid = "urn:crux:uid::nonexistentdelete123"
        delete_success = mock_lc_mem_core_delete_object(uid, self.test_persona_context)
        self.assertTrue(delete_success) # Idempotent delete

    def test_09_query_objects_by_type(self):
        uid1 = mock_lc_mem_core_ensure_uid("TypeA")
        mock_lc_mem_core_create_object(uid1, {"id":1, "type_val":"A"}, {"object_type":"TypeA"}, self.test_persona_context)
        
        uid2 = mock_lc_mem_core_ensure_uid("TypeB")
        mock_lc_mem_core_create_object(uid2, {"id":2, "type_val":"B"}, {"object_type":"TypeB"}, self.test_persona_context)

        uid3 = mock_lc_mem_core_ensure_uid("TypeA") # Another TypeA
        mock_lc_mem_core_create_object(uid3, {"id":3, "type_val":"A2"}, {"object_type":"TypeA"}, self.test_persona_context)

        results_A = mock_lc_mem_core_query_objects({"object_type": "TypeA"}, self.test_persona_context)
        self.assertEqual(len(results_A), 2)
        self.assertTrue(any(uid1 in str(r) for r in results_A)) # Check if UID is in the result (can be full object or UID string)
        self.assertTrue(any(uid3 in str(r) for r in results_A))

        results_B = mock_lc_mem_core_query_objects({"object_type": "TypeB"}, self.test_persona_context)
        self.assertEqual(len(results_B), 1)
        self.assertTrue(any(uid2 in str(r) for r in results_B))

        results_C = mock_lc_mem_core_query_objects({"object_type": "TypeC"}, self.test_persona_context)
        self.assertEqual(len(results_C), 0)

    def test_10_query_objects_all(self):
        uid1 = mock_lc_mem_core_ensure_uid("TypeX")
        mock_lc_mem_core_create_object(uid1, {"id":10}, {"object_type":"TypeX"}, self.test_persona_context)
        uid2 = mock_lc_mem_core_ensure_uid("TypeY")
        mock_lc_mem_core_create_object(uid2, {"id":20}, {"object_type":"TypeY"}, self.test_persona_context)

        results_all_default = mock_lc_mem_core_query_objects({}, self.test_persona_context) # Empty query
        self.assertEqual(len(results_all_default), 2) # Should return all UIDs

        results_all_star = mock_lc_mem_core_query_objects({"object_type": "*"}, self.test_persona_context)
        self.assertEqual(len(results_all_star), 2) # Should return all UIDs
        self.assertIn(f"urn:crux:uid::{uid1.split('::')[-1]}", results_all_star)
        self.assertIn(f"urn:crux:uid::{uid2.split('::')[-1]}", results_all_star)
        
    def test_11_query_objects_by_uid_list(self):
        uid1 = mock_lc_mem_core_ensure_uid("ListQueryObj")
        payload1 = {"data": "object1_for_list_query"}
        mock_lc_mem_core_create_object(uid1, payload1, {"object_type":"ListQueryObj"}, self.test_persona_context)
        
        uid2 = mock_lc_mem_core_ensure_uid("ListQueryObj")
        payload2 = {"data": "object2_for_list_query"}
        mock_lc_mem_core_create_object(uid2, payload2, {"object_type":"ListQueryObj"}, self.test_persona_context)

        uid_nonexistent = mock_lc_mem_core_ensure_uid("NonExistent") # Not created

        results = mock_lc_mem_core_query_objects({"object_uid_list": [uid1, uid_nonexistent, uid2]}, self.test_persona_context)
        self.assertEqual(len(results), 2) # Should find uid1 and uid2
        
        # Assuming query by list returns full payloads
        found_payloads = [r.get("data") for r in results if isinstance(r, dict)]
        self.assertIn(payload1["data"], found_payloads)
        self.assertIn(payload2["data"], found_payloads)


if __name__ == '__main__':
    # This allows running the tests directly from the command line
    # For example: python -m unittest lab.frontends.lc_python_core.tests.test_lc_mem_service
    # Or, if in the 'tests' directory: python test_lc_mem_service.py
    # Ensure MADA_VAULT_DIR path resolution works with your execution context.
    
    # A simple way to try to make imports work if run directly from lc_python_core/tests
    if "lc_python_core" not in sys.path[0] and "lc_python_core" not in os.getcwd():
         # This is a heuristic, might need adjustment based on actual execution path
        current_dir_parent = Path(__file__).resolve().parent 
        # If current_dir_parent is 'tests', then parents[0] is 'tests', parents[1] is 'lc_python_core', parents[2] is 'frontends'
        if current_dir_parent.name == "tests" and current_dir_parent.parent.name == "lc_python_core":
             # Add 'frontends' to sys.path to allow 'from lc_python_core...'
             sys.path.insert(0, str(current_dir_parent.parent.parent))


    unittest.main()
