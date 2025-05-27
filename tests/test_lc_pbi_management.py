import unittest
import shutil
from pathlib import Path
import os
import json
from datetime import datetime, timezone

# Adjust import paths for testing
try:
    from ..services.lc_mem_service import (
        create_pbi,
        get_pbi,
        update_pbi,
        delete_pbi,
        query_pbis,
        PBI_VAULT_DIR, # For direct inspection and cleanup
        MADA_VAULT_DIR # To ensure it's created for PBI_VAULT_DIR parent
    )
except ImportError:
    import sys
    package_path = Path(__file__).resolve().parents[2] # up to lc_python_core
    sys.path.insert(0, str(package_path.parent)) # up to frontends
    from lc_python_core.services.lc_mem_service import (
        create_pbi,
        get_pbi,
        update_pbi,
        delete_pbi,
        query_pbis,
        PBI_VAULT_DIR,
        MADA_VAULT_DIR
    )

class TestLcPbiManagement(unittest.TestCase):

    def setUp(self):
        # Ensure MADA_VAULT_DIR (parent of PBI_VAULT_DIR) exists for PBI_VAULT_DIR creation
        MADA_VAULT_DIR.mkdir(parents=True, exist_ok=True) 
        if PBI_VAULT_DIR.exists():
            shutil.rmtree(PBI_VAULT_DIR)
        PBI_VAULT_DIR.mkdir(parents=True, exist_ok=True)
        self.test_persona_context = {"user_id": "pbi_tester"}

    def tearDown(self):
        if PBI_VAULT_DIR.exists():
            shutil.rmtree(PBI_VAULT_DIR)

    def test_01_create_pbi(self):
        pbi_data = {
            "title": "Test PBI 1",
            "detailed_description": "This is a test PBI.",
            "pbi_type": "UserStory",
            "priority": "High",
            "tags_keywords": ["test", "pbi"]
        }
        pbi_uid = create_pbi(pbi_data, self.test_persona_context)
        self.assertIsNotNone(pbi_uid)
        self.assertTrue(pbi_uid.startswith("urn:crux:uid::"))

        # Verify file creation and basic metadata
        uid_hex = pbi_uid.split('::')[-1]
        pbi_dir = PBI_VAULT_DIR / uid_hex
        self.assertTrue(pbi_dir.exists())
        self.assertTrue((pbi_dir / "object_payload.json").exists())
        self.assertTrue((pbi_dir / "metadata.json").exists())

        with open(pbi_dir / "metadata.json", 'r') as f:
            meta = json.load(f)
        self.assertEqual(meta.get("crux_uid"), pbi_uid)
        self.assertEqual(meta.get("object_type"), "ProductBacklogItem")
        self.assertEqual(meta.get("title"), "Test PBI 1")
        self.assertEqual(meta.get("status"), "New") # Default
        self.assertEqual(meta.get("priority"), "High")


    def test_02_get_pbi(self):
        pbi_data_in = {"title": "PBI to Get", "pbi_type": "Task"}
        pbi_uid = create_pbi(pbi_data_in)
        self.assertIsNotNone(pbi_uid)

        pbi_data_out = get_pbi(pbi_uid)
        self.assertIsNotNone(pbi_data_out)
        self.assertEqual(pbi_data_out.get("pbi_uid"), pbi_uid)
        self.assertEqual(pbi_data_out.get("title"), "PBI to Get")
        self.assertEqual(pbi_data_out.get("pbi_type"), "Task")

    def test_03_get_nonexistent_pbi(self):
        pbi_data_out = get_pbi("urn:crux:uid::nonexistentpbi")
        self.assertIsNone(pbi_data_out)

    def test_04_update_pbi(self):
        pbi_uid = create_pbi({"title": "Initial PBI Title", "status": "New", "priority": "Low"})
        self.assertIsNotNone(pbi_uid)

        updates = {"title": "Updated PBI Title", "status": "InProgress", "priority": "Medium", "new_custom_field": "custom_value"}
        success = update_pbi(pbi_uid, updates)
        self.assertTrue(success)

        updated_pbi = get_pbi(pbi_uid)
        self.assertIsNotNone(updated_pbi)
        self.assertEqual(updated_pbi.get("title"), "Updated PBI Title")
        self.assertEqual(updated_pbi.get("status"), "InProgress")
        self.assertEqual(updated_pbi.get("priority"), "Medium")
        self.assertEqual(updated_pbi.get("new_custom_field"), "custom_value")
        
        # Check metadata file for updated fields reflected there (title, status, priority)
        uid_hex = pbi_uid.split('::')[-1]
        metadata_file = PBI_VAULT_DIR / uid_hex / "metadata.json"
        with open(metadata_file, 'r') as f:
            meta = json.load(f)
        self.assertEqual(meta.get("title"), "Updated PBI Title")
        self.assertEqual(meta.get("status"), "InProgress")
        self.assertEqual(meta.get("priority"), "Medium")
        self.assertTrue("updated_at" in meta)


    def test_05_delete_pbi(self):
        pbi_uid = create_pbi({"title": "PBI to Delete"})
        self.assertIsNotNone(pbi_uid)
        uid_hex = pbi_uid.split('::')[-1]
        self.assertTrue((PBI_VAULT_DIR / uid_hex).exists())

        success = delete_pbi(pbi_uid)
        self.assertTrue(success)
        self.assertFalse((PBI_VAULT_DIR / uid_hex).exists())
        self.assertIsNone(get_pbi(pbi_uid))

    def test_06_query_pbis_by_status_and_priority(self):
        create_pbi({"title": "PBI A", "status": "New", "priority": "High"})
        create_pbi({"title": "PBI B", "status": "InProgress", "priority": "High"})
        create_pbi({"title": "PBI C", "status": "New", "priority": "Medium"})
        create_pbi({"title": "PBI D", "status": "InProgress", "priority": "Medium"})
        create_pbi({"title": "PBI E", "status": "Done", "priority": "High"})

        results1 = query_pbis({"status": "New", "priority": "High"})
        self.assertEqual(len(results1), 1)
        self.assertEqual(results1[0].get("title"), "PBI A")

        results2 = query_pbis({"priority": "High"})
        self.assertEqual(len(results2), 2) # A and E (B is InProgress High) - query logic matches exact for all params
        titles = [r.get("title") for r in results2]
        self.assertIn("PBI A", titles)
        self.assertIn("PBI E", titles) # PBI E is Done/High

        results3 = query_pbis({"status": "InProgress"})
        self.assertEqual(len(results3), 2)
        titles = [r.get("title") for r in results3]
        self.assertIn("PBI B", titles)
        self.assertIn("PBI D", titles)
        
        results_all = query_pbis({}) # Empty query should return all
        self.assertEqual(len(results_all), 5)

    def test_07_query_pbis_by_pbi_type(self):
        create_pbi({"title": "Story A", "pbi_type": "UserStory", "status": "New"})
        create_pbi({"title": "Task B", "pbi_type": "Task", "status": "New"})
        create_pbi({"title": "Story C", "pbi_type": "UserStory", "status": "InProgress"})

        results = query_pbis({"pbi_type": "UserStory"})
        self.assertEqual(len(results), 2)
        titles = [r.get("title") for r in results]
        self.assertIn("Story A", titles)
        self.assertIn("Story C", titles)

        results_tasks = query_pbis({"pbi_type": "Task"})
        self.assertEqual(len(results_tasks), 1)
        self.assertEqual(results_tasks[0].get("title"), "Task B")

    def test_08_query_pbis_by_cynefin_domain(self):
        create_pbi({"title": "PBI Complex", "cynefin_domain_context": "Complex"})
        create_pbi({"title": "PBI Simple", "cynefin_domain_context": "Simple"})
        create_pbi({"title": "PBI Complex Too", "cynefin_domain_context": "Complex"})

        results = query_pbis({"cynefin_domain_context": "Complex"})
        self.assertEqual(len(results), 2)
        titles = [r.get("title") for r in results]
        self.assertIn("PBI Complex", titles)
        self.assertIn("PBI Complex Too", titles)

    def test_09_query_pbis_by_related_oia_cycle_uid(self):
        oia_cycle_1 = "urn:crux:uid::oia_cycle_123"
        oia_cycle_2 = "urn:crux:uid::oia_cycle_456"
        create_pbi({"title": "PBI for OIA 1", "related_oia_cycle_uids": [oia_cycle_1]})
        create_pbi({"title": "PBI for OIA 2", "related_oia_cycle_uids": [oia_cycle_2]})
        create_pbi({"title": "PBI for OIA 1 again", "related_oia_cycle_uids": [oia_cycle_1, "urn:crux:uid::another_oia"]})

        results = query_pbis({"related_oia_cycle_uid": oia_cycle_1})
        self.assertEqual(len(results), 2)
        titles = [r.get("title") for r in results]
        self.assertIn("PBI for OIA 1", titles)
        self.assertIn("PBI for OIA 1 again", titles)

    def test_10_query_pbis_by_related_rdsotm_cycle_linkage_uid(self):
        rdsotm_cycle_1 = "urn:crux:uid::rdsotm_cycle_abc"
        create_pbi({"title": "PBI for RDSOTM Cycle 1", "related_rdsotm_cycle_linkage_uids": [rdsotm_cycle_1]})
        create_pbi({"title": "PBI for another RDSOTM Cycle", "related_rdsotm_cycle_linkage_uids": ["urn:crux:uid::rdsotm_cycle_xyz"]})
        
        results = query_pbis({"related_rdsotm_cycle_linkage_uid": rdsotm_cycle_1})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get("title"), "PBI for RDSOTM Cycle 1")

    def test_11_query_pbis_by_related_rdsotm_component_uid(self):
        rdsotm_comp_1 = "urn:crux:uid::rdsotm_comp_d1"
        create_pbi({"title": "PBI for RDSOTM Comp 1", "related_rdsotm_component_uids": [rdsotm_comp_1]})
        create_pbi({"title": "PBI for another RDSOTM Comp", "related_rdsotm_component_uids": ["urn:crux:uid::rdsotm_comp_s1"]})

        results = query_pbis({"related_rdsotm_component_uid": rdsotm_comp_1})
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get("title"), "PBI for RDSOTM Comp 1")

    def test_12_query_pbis_combined_filters(self):
        oia_cycle_A = "urn:crux:uid::oia_A"
        create_pbi({"title": "PBI 1", "status": "New", "pbi_type": "UserStory", "related_oia_cycle_uids": [oia_cycle_A], "priority": "High", "cynefin_domain_context": "Complex"})
        create_pbi({"title": "PBI 2", "status": "New", "pbi_type": "Task", "related_oia_cycle_uids": [oia_cycle_A], "priority": "High"})
        create_pbi({"title": "PBI 3", "status": "New", "pbi_type": "UserStory", "related_oia_cycle_uids": ["urn:crux:uid::oia_B"], "priority": "High"})
        create_pbi({"title": "PBI 4", "status": "InProgress", "pbi_type": "UserStory", "related_oia_cycle_uids": [oia_cycle_A], "priority": "High"})
        create_pbi({"title": "PBI 5", "status": "New", "pbi_type": "UserStory", "related_oia_cycle_uids": [oia_cycle_A], "priority": "Medium"})
        create_pbi({"title": "PBI 6", "status": "New", "pbi_type": "UserStory", "related_oia_cycle_uids": [oia_cycle_A], "priority": "High", "cynefin_domain_context": "Simple"})


        results = query_pbis({
            "status": "New",
            "pbi_type": "UserStory",
            "related_oia_cycle_uid": oia_cycle_A,
            "priority": "High",
            "cynefin_domain_context": "Complex"
        })
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].get("title"), "PBI 1")

if __name__ == '__main__':
    if "lc_python_core" not in sys.path[0] and "lc_python_core" not in os.getcwd():
        current_dir_parent = Path(__file__).resolve().parent
        if current_dir_parent.name == "tests" and current_dir_parent.parent.name == "lc_python_core":
             sys.path.insert(0, str(current_dir_parent.parent.parent))
    unittest.main()
```
