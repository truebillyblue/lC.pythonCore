import unittest
import shutil
from pathlib import Path
import os
import json

# Adjust import paths for testing
try:
    from ..sops.meta_sops.sop_rdsotm_management import (
        initiate_rdsotm_cycle,
        create_rdsotm_component,
        get_rdsotm_component,
        update_rdsotm_component,
        get_rdsotm_cycle_details,
        # link_components_in_cycle, # Not testing placeholder thoroughly
        RDSOTM_CYCLE_LINKAGE_TYPE,
        TEXT_DOCUMENT_TYPE
    )
    from ..services.lc_mem_service import MADA_VAULT_DIR, mock_lc_mem_core_get_object # For direct verification
except ImportError:
    import sys
    package_path = Path(__file__).resolve().parents[2] # up to lc_python_core
    sys.path.insert(0, str(package_path.parent)) # up to frontends
    from lc_python_core.sops.meta_sops.sop_rdsotm_management import (
        initiate_rdsotm_cycle,
        create_rdsotm_component,
        get_rdsotm_component,
        update_rdsotm_component,
        get_rdsotm_cycle_details,
        RDSOTM_CYCLE_LINKAGE_TYPE,
        TEXT_DOCUMENT_TYPE
    )
    from lc_python_core.services.lc_mem_service import MADA_VAULT_DIR, mock_lc_mem_core_get_object


class TestRdsotmManagement(unittest.TestCase):

    def setUp(self):
        if MADA_VAULT_DIR.exists():
            shutil.rmtree(MADA_VAULT_DIR)
        MADA_VAULT_DIR.mkdir(parents=True, exist_ok=True)
        self.test_persona_context = {"user_id": "rdsotm_tester"} # For MADA service calls

    def tearDown(self):
        if MADA_VAULT_DIR.exists():
            shutil.rmtree(MADA_VAULT_DIR)

    def test_01_initiate_rdsotm_cycle(self):
        cycle_name = "Test RDSOTM Cycle"
        cycle_uid = initiate_rdsotm_cycle(name=cycle_name)
        self.assertIsNotNone(cycle_uid)
        self.assertTrue(cycle_uid.startswith("urn:crux:uid::"))

        cycle_data = mock_lc_mem_core_get_object(cycle_uid) # Use direct get for verification
        self.assertIsNotNone(cycle_data)
        self.assertEqual(cycle_data.get("cycle_linkage_uid"), cycle_uid)
        self.assertEqual(cycle_data.get("cycle_name"), cycle_name)
        self.assertEqual(cycle_data.get("status"), "Active")

    def test_02_create_rdsotm_component(self):
        cycle_uid = initiate_rdsotm_cycle("Component Test Cycle")
        self.assertIsNotNone(cycle_uid)

        comp_type = "Doctrine"
        comp_name = "Core Principles v1"
        comp_desc = "Foundational guiding principles."
        comp_content = "Principle 1: Do good. Principle 2: Be wise."
        
        comp_uid = create_rdsotm_component(cycle_uid, comp_type, comp_name, comp_desc, comp_content)
        self.assertIsNotNone(comp_uid)

        # Verify component data
        comp_data = get_rdsotm_component(comp_uid, include_content=True)
        self.assertIsNotNone(comp_data)
        self.assertEqual(comp_data.get("name"), comp_name)
        self.assertEqual(comp_data.get("rdsotm_component_type"), comp_type)
        self.assertEqual(comp_data.get("description_summary"), comp_desc)
        self.assertEqual(comp_data.get("embedded_content"), comp_content)
        self.assertIn(cycle_uid, comp_data.get("linked_cycle_linkage_uids", []))

        # Verify cycle linkage update
        cycle_data = get_rdsotm_cycle_details(cycle_uid)
        self.assertIsNotNone(cycle_data)
        if comp_type == "Doctrine": # Special case for doctrine_ref
            self.assertEqual(cycle_data.get("doctrine_ref"), comp_uid)
        else:
            self.assertIn(comp_uid, cycle_data.get(f"{comp_type.lower()}_refs", []))
    
    def test_03_get_component_with_and_without_content(self):
        cycle_uid = initiate_rdsotm_cycle("Get Content Test")
        comp_uid = create_rdsotm_component(cycle_uid, "Strategy", "My Strat", "Desc", "Detailed strategy text.")
        self.assertIsNotNone(comp_uid)

        comp_no_content = get_rdsotm_component(comp_uid, include_content=False)
        self.assertIsNotNone(comp_no_content)
        self.assertNotIn("embedded_content", comp_no_content)

        comp_with_content = get_rdsotm_component(comp_uid, include_content=True)
        self.assertIsNotNone(comp_with_content)
        self.assertIn("embedded_content", comp_with_content)
        self.assertEqual(comp_with_content["embedded_content"], "Detailed strategy text.")

    def test_04_update_rdsotm_component(self):
        cycle_uid = initiate_rdsotm_cycle("Update Test Cycle")
        comp_uid = create_rdsotm_component(cycle_uid, "Tactics", "Initial Tactic", "Desc", "Old tactic details.")
        self.assertIsNotNone(comp_uid)

        updates = {"name": "Revised Tactic", "status": "Active", "description_summary": "Updated description."}
        new_content = "New tactic details after revision."
        
        success = update_rdsotm_component(comp_uid, updates, new_content_text=new_content)
        self.assertTrue(success)

        updated_comp = get_rdsotm_component(comp_uid, include_content=True)
        self.assertIsNotNone(updated_comp)
        self.assertEqual(updated_comp.get("name"), "Revised Tactic")
        self.assertEqual(updated_comp.get("status"), "Active")
        self.assertEqual(updated_comp.get("description_summary"), "Updated description.")
        self.assertEqual(updated_comp.get("embedded_content"), new_content)
        self.assertIn("last_updated_at", updated_comp)

    def test_05_update_component_metadata_only(self):
        cycle_uid = initiate_rdsotm_cycle("Meta Update Cycle")
        original_content = "Content should not change."
        comp_uid = create_rdsotm_component(cycle_uid, "Mission", "My Mission", "Desc", original_content)
        self.assertIsNotNone(comp_uid)

        updates = {"status": "Completed"}
        success = update_rdsotm_component(comp_uid, updates) # No new_content_text
        self.assertTrue(success)
        
        updated_comp = get_rdsotm_component(comp_uid, include_content=True)
        self.assertEqual(updated_comp.get("status"), "Completed")
        self.assertEqual(updated_comp.get("embedded_content"), original_content) # Content unchanged

    def test_06_get_rdsotm_cycle_details(self):
        cycle_uid = initiate_rdsotm_cycle("Cycle Details Test")
        self.assertIsNotNone(cycle_uid)
        
        doc_uid = create_rdsotm_component(cycle_uid, "Doctrine", "D1", "d", "dc")
        strat_uid = create_rdsotm_component(cycle_uid, "Strategy", "S1", "s", "sc")

        details_no_resolve = get_rdsotm_cycle_details(cycle_uid)
        self.assertIsNotNone(details_no_resolve)
        self.assertEqual(details_no_resolve.get("doctrine_ref"), doc_uid)
        self.assertIn(strat_uid, details_no_resolve.get("strategy_refs", []))
        self.assertNotIn("doctrine_ref_summary", details_no_resolve) # Not resolved yet

        details_with_resolve = get_rdsotm_cycle_details(cycle_uid, resolve_component_summaries=True)
        self.assertIsNotNone(details_with_resolve)
        self.assertIn("doctrine_ref_summary", details_with_resolve)
        self.assertEqual(details_with_resolve["doctrine_ref_summary"].get("uid"), doc_uid)
        self.assertEqual(details_with_resolve["doctrine_ref_summary"].get("name"), "D1")
        self.assertTrue(any(s["uid"] == strat_uid and s["name"] == "S1" for s in details_with_resolve.get("strategy_refs_summaries",[])))


if __name__ == '__main__':
    if "lc_python_core" not in sys.path[0] and "lc_python_core" not in os.getcwd():
        current_dir_parent = Path(__file__).resolve().parent
        if current_dir_parent.name == "tests" and current_dir_parent.parent.name == "lc_python_core":
             sys.path.insert(0, str(current_dir_parent.parent.parent))
    unittest.main()
