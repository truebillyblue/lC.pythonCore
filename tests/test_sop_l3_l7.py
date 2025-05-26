import unittest
from datetime import datetime as dt, timezone

from mada_schema import (
    MadaSeed,
    L1EpistemicStateOfStartleEnum, L2EpistemicStateOfFramingEnum, L4EpistemicStateOfAnchoringEnum,
    L5EpistemicStateOfFieldProcessingEnum, L6EpistemicStateEnum, L7EpistemicStateEnum,
    SeedIntegrityStatusEnum, L3Trace, L4Trace, L5Trace, L6Trace, L7Trace,
    L3SurfaceKeymapObj, L4AnchorStateObj, L5FieldStateObj, L6ReflectionPayloadObj, L7EncodedApplication, SeedQAQC,
    SignalComponentMetadataL1, EncodingStatusL1Enum # Added for L3 test setup
)
# Import mock services and store for test setup
from ..services.mock_lc_core_services import mock_mada_store, mock_lc_mem_core_create_object # Corrected path

from ..sops.sop_l1_startle import startle_process # Corrected path
from ..sops.sop_l2_frame_click import frame_click_process # Corrected path
from ..sops.sop_l3_keymap_click import keymap_click_process # Corrected path
from ..sops.sop_l4_anchor_click import anchor_click_process # Corrected path
from ..sops.sop_l5_field_click import field_click_process # Corrected path
from ..sops.sop_l6_reflect_boom import reflect_boom_process # Corrected path
from ..sops.sop_l7_apply_done import apply_done_process # Corrected path

# Sample input event for pipeline tests
SAMPLE_INPUT_EVENT = {
    "reception_timestamp_utc_iso": "2023-11-01T12:00:00Z",
    "origin_hint": "Test_Pipeline_Input",
    "data_components": [
        {
            "role_hint": "primary_query",
            "content_handle_placeholder": "This is a test query for the full pipeline.",
            "size_hint": 50,
            "type_hint": "text/plain"
        }
    ]
}

def get_l2_processed_seed(input_event: dict = SAMPLE_INPUT_EVENT) -> MadaSeed:
    """Helper to get an L2 processed MadaSeed."""
    l1_seed = startle_process(input_event)
    return frame_click_process(l1_seed)

def get_l3_processed_seed(input_event: dict = SAMPLE_INPUT_EVENT) -> MadaSeed:
    l2_seed = get_l2_processed_seed(input_event)
    
    # Setup for L3: Ensure the primary content is in mock_mada_store
    # Find the primary_signal_ref_uid that _keymap_get_primary_content_from_madaSeed will look for.
    primary_signal_ref_uid_for_l3: Optional[str] = None
    l1_context_for_l3 = l2_seed.seed_content.L1_startle_reflex.L1_startle_context_obj
    for comp_meta in l1_context_for_l3.signal_components_metadata_L1:
        if comp_meta.component_role_L1 and 'primary' in comp_meta.component_role_L1.lower():
            primary_signal_ref_uid_for_l3 = comp_meta.raw_signal_ref_uid_L1
            break
    if not primary_signal_ref_uid_for_l3 and l1_context_for_l3.signal_components_metadata_L1:
        primary_signal_ref_uid_for_l3 = l1_context_for_l3.signal_components_metadata_L1[0].raw_signal_ref_uid_L1

    if primary_signal_ref_uid_for_l3:
        # Find the corresponding raw_input_signal from the L1 seed content to put into the mock store
        content_to_store = "Default content if not found in raw_signals for L3 test"
        for rs in l2_seed.seed_content.raw_signals:
            if rs.raw_input_id == primary_signal_ref_uid_for_l3:
                content_to_store = str(rs.raw_input_signal) # Ensure it's a string
                break
        mock_lc_mem_core_create_object(primary_signal_ref_uid_for_l3, content_to_store)
        print(f"[L3_TEST_SETUP] Populated mock_mada_store for UID {primary_signal_ref_uid_for_l3} with content: '{content_to_store}'")
    else:
        print("[L3_TEST_SETUP_WARNING] Could not determine primary_signal_ref_uid_for_l3 to populate mock_mada_store.")

    return keymap_click_process(l2_seed)

def get_l4_processed_seed(input_event: dict = SAMPLE_INPUT_EVENT) -> MadaSeed:
    l3_seed = get_l3_processed_seed(input_event)
    # Manually add an entity mention to L3 output for L4 to process, as per L4 test needs
    if l3_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj.lexical_affordances:
        from ..schemas.mada_schema import EntityMentionRaw # Corrected path
        l3_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj.lexical_affordances.entity_mentions_raw.append(
            EntityMentionRaw(mention="Test Entity L3", confidence=0.9, possible_types=["THING"])
        )
    return anchor_click_process(l3_seed)

def get_l5_processed_seed(input_event: dict = SAMPLE_INPUT_EVENT) -> MadaSeed:
    l4_seed = get_l4_processed_seed(input_event)
    return field_click_process(l4_seed)

def get_l6_processed_seed(input_event: dict = SAMPLE_INPUT_EVENT) -> MadaSeed:
    l5_seed = get_l5_processed_seed(input_event)
    return reflect_boom_process(l5_seed)


class TestKeymapClickProcess(unittest.TestCase):
    def test_keymap_click_valid_l2_output(self):
        l2_seed = get_l2_processed_seed()
        # Ensure L2 processing was successful enough for L3
        self.assertEqual(l2_seed.trace_metadata.L2_trace.epistemic_state_L2, L2EpistemicStateOfFramingEnum.FRAMED, "L2 processing did not result in FRAMED state")

        l3_seed = keymap_click_process(l2_seed)
        self.assertIsInstance(l3_seed, MadaSeed)

        l3_content = l3_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj
        self.assertIsInstance(l3_content, L3SurfaceKeymapObj)
        self.assertEqual(l3_content.version, "0.1.1")
        self.assertIsNotNone(l3_content.lexical_affordances)
        self.assertIsNotNone(l3_content.syntactic_hints)

        l3_trace = l3_seed.trace_metadata.L3_trace
        self.assertIsInstance(l3_trace, L3Trace)
        self.assertEqual(l3_trace.version_L3_trace_schema, "0.1.0")
        self.assertEqual(l3_trace.sop_name, "lC.SOP.keymap_click")
        self.assertEqual(l3_trace.epistemic_state_L3, "Keymapped_Successfully") # String as per L3 MR logic
        self.assertEqual(l3_trace.completion_timestamp_L3, dt.fromisoformat("2023-10-28T11:15:00+00:00"))


class TestAnchorClickProcess(unittest.TestCase):
    def test_anchor_click_valid_l3_output(self):
        l3_seed = get_l3_processed_seed()
        self.assertEqual(l3_seed.trace_metadata.L3_trace.epistemic_state_L3, "Keymapped_Successfully", "L3 processing did not result in Keymapped_Successfully state")

        l4_seed = anchor_click_process(l3_seed)
        self.assertIsInstance(l4_seed, MadaSeed)

        l4_content = l4_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L4_anchor_state_obj
        self.assertIsInstance(l4_content, L4AnchorStateObj)
        self.assertEqual(l4_content.version, "0.2.17")
        self.assertIsNotNone(l4_content.aac_assessability_map)
        self.assertEqual(l4_content.aac_assessability_map.version, "0.1.1")
        self.assertIsNotNone(l4_content.persona_alignment_context_engaged)
        self.assertEqual(l4_content.persona_alignment_context_engaged.version, "0.1.1")

        l4_trace = l4_seed.trace_metadata.L4_trace
        self.assertIsInstance(l4_trace, L4Trace)
        self.assertEqual(l4_trace.version_L4_trace_schema, "0.1.0")
        self.assertEqual(l4_trace.sop_name, "lC.SOP.anchor_click")
        self.assertIn(l4_trace.epistemic_state_L4, [L4EpistemicStateOfAnchoringEnum.ANCHORED, L4EpistemicStateOfAnchoringEnum.ANCHORED_WITH_GAPS]) # Baseline logic might result in this
        self.assertEqual(l4_trace.completion_timestamp_L4, dt.fromisoformat("2023-10-28T11:00:00+00:00"))


class TestFieldClickProcess(unittest.TestCase):
    def test_field_click_valid_l4_output(self):
        l4_seed = get_l4_processed_seed()
        self.assertIn(l4_seed.trace_metadata.L4_trace.epistemic_state_L4, [L4EpistemicStateOfAnchoringEnum.ANCHORED, L4EpistemicStateOfAnchoringEnum.ANCHORED_WITH_GAPS], "L4 processing did not result in an ANCHORED state")

        l5_seed = field_click_process(l4_seed)
        self.assertIsInstance(l5_seed, MadaSeed)

        l5_content = l5_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L5_field_state_obj
        self.assertIsInstance(l5_content, L5FieldStateObj)
        self.assertEqual(l5_content.version, "0.2.0")
        self.assertIsNotNone(l5_content.field_instance_uid)
        self.assertTrue(len(l5_content.field_participants) > 0) # Baseline adds participants

        l5_trace = l5_seed.trace_metadata.L5_trace
        self.assertIsInstance(l5_trace, L5Trace)
        self.assertEqual(l5_trace.version_L5_trace_schema, "0.1.0")
        self.assertEqual(l5_trace.sop_name, "lC.SOP.field_click")
        self.assertIn(l5_trace.epistemic_state_L5, [L5EpistemicStateOfFieldProcessingEnum.FIELD_INSTANTIATED_NEW, L5EpistemicStateOfFieldProcessingEnum.FIELD_UPDATED_EXISTING])
        self.assertEqual(l5_trace.completion_timestamp_L5, dt.fromisoformat("2023-10-28T10:45:00+00:00"))


class TestReflectBoomProcess(unittest.TestCase):
    def test_reflect_boom_valid_l5_output(self):
        l5_seed = get_l5_processed_seed()
        self.assertIn(l5_seed.trace_metadata.L5_trace.epistemic_state_L5, [L5EpistemicStateOfFieldProcessingEnum.FIELD_INSTANTIATED_NEW, L5EpistemicStateOfFieldProcessingEnum.FIELD_UPDATED_EXISTING], "L5 processing did not result in a suitable FIELD_ state")
        
        l6_seed = reflect_boom_process(l5_seed)
        self.assertIsInstance(l6_seed, MadaSeed)

        l6_content = l6_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L6_reflection_payload.L6_reflection_payload_obj
        self.assertIsInstance(l6_content, L6ReflectionPayloadObj)
        self.assertEqual(l6_content.version, "0.1.6")
        self.assertIsNotNone(l6_content.payload_metadata)
        self.assertIsNotNone(l6_content.payload_content)
        self.assertIsNotNone(l6_content.transformation_metadata)
        self.assertIsNotNone(l6_content.reflection_surface)

        l6_trace = l6_seed.trace_metadata.L6_trace
        self.assertIsInstance(l6_trace, L6Trace)
        self.assertEqual(l6_trace.version_L6_trace_schema, "0.1.0")
        self.assertEqual(l6_trace.sop_name, "lC.SOP.reflect_boom")
        self.assertIn(l6_trace.epistemic_state_L6, [L6EpistemicStateEnum.REFLECTION_PREPARED, L6EpistemicStateEnum.REFLECTION_PREPARED_WITH_WARNINGS])
        self.assertEqual(l6_trace.completion_timestamp_L6, dt.fromisoformat("2023-10-28T10:30:00+00:00"))


class TestApplyDoneProcess(unittest.TestCase):
    def test_apply_done_valid_l6_output(self):
        l6_seed = get_l6_processed_seed()
        self.assertIn(l6_seed.trace_metadata.L6_trace.epistemic_state_L6, [L6EpistemicStateEnum.REFLECTION_PREPARED, L6EpistemicStateEnum.REFLECTION_PREPARED_WITH_WARNINGS], "L6 processing did not result in a suitable REFLECTION_ state")

        l7_seed = apply_done_process(l6_seed)
        self.assertIsInstance(l7_seed, MadaSeed)

        l7_content = l7_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L6_reflection_payload.L7_encoded_application
        self.assertIsInstance(l7_content, L7EncodedApplication)
        self.assertEqual(l7_content.version_L7_payload, "0.1.1")
        self.assertIsNotNone(l7_content.L7_backlog)
        self.assertTrue(len(l7_content.seed_outputs) > 0) # Baseline adds one output

        l7_trace = l7_seed.trace_metadata.L7_trace
        self.assertIsInstance(l7_trace, L7Trace)
        self.assertEqual(l7_trace.version_L7_trace_schema, "0.1.0")
        self.assertEqual(l7_trace.sop_name, "lC.SOP.apply_done")
        self.assertIn(l7_trace.epistemic_state_L7, [L7EpistemicStateEnum.APPLICATION_SUCCESSFUL_SEED_VALID, L7EpistemicStateEnum.APPLICATION_SUCCESSFUL_SEED_WARNINGS])
        
        seed_qaqc = l7_seed.seed_QA_QC
        self.assertIsInstance(seed_qaqc, SeedQAQC)
        self.assertEqual(seed_qaqc.version_seed_qa_qc_schema, "0.1.0")
        self.assertIn(seed_qaqc.overall_seed_integrity_status, [SeedIntegrityStatusEnum.VALID_COMPLETE, SeedIntegrityStatusEnum.VALID_WITH_WARNINGS])
        
        self.assertIsNotNone(l7_seed.seed_completion_timestamp)
        self.assertEqual(l7_seed.seed_completion_timestamp, dt.fromisoformat("2023-10-28T03:00:00+00:00")) # Fixed timestamp from L7 helper


class TestFullPipeline(unittest.TestCase):
    def test_pipeline_valid_input(self):
        l1_seed = startle_process(SAMPLE_INPUT_EVENT)
        self.assertIsInstance(l1_seed, MadaSeed)
        self.assertEqual(l1_seed.trace_metadata.L1_trace.epistemic_state_L1, L1EpistemicStateOfStartleEnum.STARTLE_COMPLETE_SIGNALREFS_GENERATED)
        
        l2_seed = frame_click_process(l1_seed)
        self.assertIsInstance(l2_seed, MadaSeed)
        self.assertEqual(l2_seed.trace_metadata.L2_trace.epistemic_state_L2, L2EpistemicStateOfFramingEnum.FRAMED)
        
        l3_seed = keymap_click_process(l2_seed)
        self.assertIsInstance(l3_seed, MadaSeed)
        self.assertEqual(l3_seed.trace_metadata.L3_trace.epistemic_state_L3, "Keymapped_Successfully")
        
        # Manually add entity for L4 as done in its specific test helper
        if l3_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj.lexical_affordances:
            from ..schemas.mada_schema import EntityMentionRaw # Corrected path
            l3_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj.lexical_affordances.entity_mentions_raw.append(
                EntityMentionRaw(mention="Pipeline Test Entity", confidence=0.9, possible_types=["TEST"])
            )

        l4_seed = anchor_click_process(l3_seed)
        self.assertIsInstance(l4_seed, MadaSeed)
        self.assertIn(l4_seed.trace_metadata.L4_trace.epistemic_state_L4, [L4EpistemicStateOfAnchoringEnum.ANCHORED, L4EpistemicStateOfAnchoringEnum.ANCHORED_WITH_GAPS])
        
        l5_seed = field_click_process(l4_seed)
        self.assertIsInstance(l5_seed, MadaSeed)
        self.assertIn(l5_seed.trace_metadata.L5_trace.epistemic_state_L5, [L5EpistemicStateOfFieldProcessingEnum.FIELD_INSTANTIATED_NEW, L5EpistemicStateOfFieldProcessingEnum.FIELD_UPDATED_EXISTING])
        
        l6_seed = reflect_boom_process(l5_seed)
        self.assertIsInstance(l6_seed, MadaSeed)
        self.assertIn(l6_seed.trace_metadata.L6_trace.epistemic_state_L6, [L6EpistemicStateEnum.REFLECTION_PREPARED, L6EpistemicStateEnum.REFLECTION_PREPARED_WITH_WARNINGS])
        
        final_seed = apply_done_process(l6_seed)
        self.assertIsInstance(final_seed, MadaSeed)

        # High-level checks for the final MadaSeed
        self.assertTrue(final_seed.seed_id.startswith("urn:crux:uid::"))
        self.assertIsNotNone(final_seed.seed_completion_timestamp)
        self.assertEqual(final_seed.seed_QA_QC.overall_seed_integrity_status, SeedIntegrityStatusEnum.VALID_COMPLETE) # Baseline QAQC returns this
        self.assertIn(final_seed.trace_metadata.L7_trace.epistemic_state_L7, [L7EpistemicStateEnum.APPLICATION_SUCCESSFUL_SEED_VALID, L7EpistemicStateEnum.APPLICATION_SUCCESSFUL_SEED_WARNINGS])

        # Check presence of key content objects from each layer
        self.assertIsNotNone(final_seed.seed_content.L1_startle_reflex.L1_startle_context_obj)
        self.assertIsNotNone(final_seed.seed_content.L1_startle_reflex.L2_frame_type.L2_frame_type_obj)
        self.assertIsNotNone(final_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj)
        self.assertIsNotNone(final_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L4_anchor_state_obj)
        self.assertIsNotNone(final_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L5_field_state_obj)
        self.assertIsNotNone(final_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L6_reflection_payload.L6_reflection_payload_obj)
        self.assertIsNotNone(final_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L6_reflection_payload.L7_encoded_application)


if __name__ == '__main__':
    unittest.main()
