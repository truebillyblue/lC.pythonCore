import unittest
import json
import shutil
from pathlib import Path
import os

# Adjust import paths for testing
try:
    from ..sops.meta_sops.sop_oia_cycle_management import (
        initiate_oia_cycle,
        add_observation_to_cycle,
        add_interpretation_to_cycle,
        add_application_to_cycle,
        update_oia_cycle_status,
        get_oia_cycle_state,
        OIA_CYCLE_OBJECT_TYPE
    )
    from ..services.lc_mem_service import MADA_VAULT_DIR
except ImportError:
    import sys
    package_path = Path(__file__).resolve().parents[2] # up to lc_python_core
    sys.path.insert(0, str(package_path.parent)) # up to frontends
    from lc_python_core.sops.meta_sops.sop_oia_cycle_management import (
        initiate_oia_cycle,
        add_observation_to_cycle,
        add_interpretation_to_cycle,
        add_application_to_cycle,
        update_oia_cycle_status,
        get_oia_cycle_state,
        OIA_CYCLE_OBJECT_TYPE
    )
    from lc_python_core.services.lc_mem_service import MADA_VAULT_DIR


class TestOiaCycleManagement(unittest.TestCase):

    def setUp(self):
        if MADA_VAULT_DIR.exists():
            shutil.rmtree(MADA_VAULT_DIR)
        MADA_VAULT_DIR.mkdir(parents=True, exist_ok=True)
        self.test_persona_context = {"user_id": "oia_tester"} # Needed for MADA service calls

    def tearDown(self):
        if MADA_VAULT_DIR.exists():
            shutil.rmtree(MADA_VAULT_DIR)

    def test_01_initiate_oia_cycle(self):
        cycle_name = "Test OIA Cycle Initiation"
        prompt = "Initial prompt for testing."
        trace_id = "trace_init_001"
        
        oia_uid = initiate_oia_cycle(name=cycle_name, initial_focus_prompt=prompt, related_trace_id=trace_id)
        self.assertIsNotNone(oia_uid)
        self.assertTrue(oia_uid.startswith("urn:crux:uid::"))

        # Verify MADA object creation
        cycle_state = get_oia_cycle_state(oia_uid)
        self.assertIsNotNone(cycle_state)
        self.assertEqual(cycle_state.get("oia_cycle_uid"), oia_uid)
        self.assertEqual(cycle_state.get("oia_cycle_name"), cycle_name)
        self.assertEqual(cycle_state.get("status"), "Initiated")
        self.assertEqual(cycle_state.get("current_focus_prompt"), prompt)
        self.assertIn(trace_id, cycle_state.get("related_trace_ids", []))
        self.assertEqual(len(cycle_state.get("log", [])), 1)
        self.assertEqual(cycle_state.get("log")[0].get("event_type"), "CycleInitiated")

    def test_02_add_observation(self):
        oia_uid = initiate_oia_cycle("Observation Test Cycle")
        self.assertIsNotNone(oia_uid)

        obs_summary = "First observation made."
        obs_id = add_observation_to_cycle(oia_uid, obs_summary, data_source_mada_uid="urn:crux:uid::data_source_1")
        self.assertIsNotNone(obs_id)
        self.assertTrue(obs_id.startswith("obs_")) # Corrected prefix obs_ as per sop_oia_cycle_management.py

        cycle_state = get_oia_cycle_state(oia_uid)
        self.assertEqual(cycle_state.get("status"), "Observing")
        self.assertEqual(len(cycle_state.get("observations", [])), 1)
        observation = cycle_state["observations"][0]
        self.assertEqual(observation.get("observation_id"), obs_id)
        self.assertEqual(observation.get("summary"), obs_summary)
        self.assertEqual(observation.get("data_source_mada_uid"), "urn:crux:uid::data_source_1")
        self.assertEqual(len(cycle_state.get("log", [])), 2) # Init + AddObs

    def test_03_add_interpretation(self):
        oia_uid = initiate_oia_cycle("Interpretation Test Cycle")
        add_observation_to_cycle(oia_uid, "Some observation") # Need an observation first

        interp_summary = "Interpreting the observation."
        principles = ["Principle A", "Principle B"]
        interp_id = add_interpretation_to_cycle(oia_uid, interp_summary, timeless_principles_extracted=principles)
        self.assertIsNotNone(interp_id)
        self.assertTrue(interp_id.startswith("int_")) # Corrected prefix int_

        cycle_state = get_oia_cycle_state(oia_uid)
        self.assertEqual(cycle_state.get("status"), "Interpreting")
        self.assertEqual(len(cycle_state.get("interpretations", [])), 1)
        interpretation = cycle_state["interpretations"][0]
        self.assertEqual(interpretation.get("interpretation_id"), interp_id)
        self.assertEqual(interpretation.get("summary"), interp_summary)
        self.assertEqual(interpretation.get("timeless_principles_extracted"), principles)
        self.assertEqual(len(cycle_state.get("log", [])), 3) # Init + AddObs + AddInterp

    def test_04_add_application(self):
        oia_uid = initiate_oia_cycle("Application Test Cycle")
        # Need to add observation and interpretation before application for a more complete flow
        obs_id = add_observation_to_cycle(oia_uid, "Observation for application")
        interp_id = add_interpretation_to_cycle(oia_uid, "Interpretation for application", references_observation_ids=[obs_id])


        app_summary = "Applying the interpretation."
        app_id = add_application_to_cycle(oia_uid, app_summary, target_mada_uid="urn:crux:uid::target_doc_1", references_interpretation_ids=[interp_id])
        self.assertIsNotNone(app_id)
        self.assertTrue(app_id.startswith("app_")) # Corrected prefix app_

        cycle_state = get_oia_cycle_state(oia_uid)
        self.assertEqual(cycle_state.get("status"), "Applying") 
        self.assertEqual(len(cycle_state.get("applications", [])), 1)
        application = cycle_state["applications"][0]
        self.assertEqual(application.get("application_id"), app_id)
        self.assertEqual(application.get("summary_of_action_taken_or_planned"), app_summary)
        self.assertEqual(application.get("target_mada_uid"), "urn:crux:uid::target_doc_1")
        self.assertEqual(len(cycle_state.get("log", [])), 4) # Init + AddObs + AddInterp + AddApp

    def test_05_update_status(self):
        oia_uid = initiate_oia_cycle("Status Update Test Cycle")
        self.assertIsNotNone(oia_uid)

        new_status = "Completed_Applied"
        log_msg = "Cycle marked as complete after application."
        success = update_oia_cycle_status(oia_uid, new_status, log_msg)
        self.assertTrue(success)

        cycle_state = get_oia_cycle_state(oia_uid)
        self.assertEqual(cycle_state.get("status"), new_status)
        self.assertEqual(len(cycle_state.get("log", [])), 2) # Init + UpdateStatus
        self.assertEqual(cycle_state.get("log")[-1].get("details"), log_msg)

    def test_06_get_nonexistent_cycle(self):
        state = get_oia_cycle_state("urn:crux:uid::nonexistent_oia_cycle")
        self.assertIsNone(state)

if __name__ == '__main__':
    # Adjust sys.path if running directly for lc_python_core imports
    if "lc_python_core" not in sys.path[0] and "lc_python_core" not in os.getcwd():
        current_dir_parent = Path(__file__).resolve().parent
        if current_dir_parent.name == "tests" and current_dir_parent.parent.name == "lc_python_core":
             sys.path.insert(0, str(current_dir_parent.parent.parent))
    unittest.main()
