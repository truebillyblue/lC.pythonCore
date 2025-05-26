import unittest
from datetime import datetime as dt, timezone

from ..schemas.mada_schema import ( # Corrected path
    MadaSeed, RawSignal, SignalComponentMetadataL1,
    L1StartleContextObj, L1Trace, L1EpistemicStateOfStartleEnum, EncodingStatusL1Enum,
    L2FrameTypeObj, L2Trace, L2EpistemicStateOfFramingEnum, InputClassL2Enum,
    TemporalHintProvenanceL2Enum, L2ValidationStatusOfFrameEnum, CommunicationContextL2, TemporalHintL2
)
from ..sops.sop_l1_startle import startle_process, _startle_create_initial_madaSeed_shell # Corrected path
from ..sops.sop_l2_frame_click import frame_click_process # Corrected path


class TestMadaSchema(unittest.TestCase):
    def test_mada_seed_shell_instantiation(self):
        """Test basic instantiation of MadaSeed shell."""
        # Use the helper from startle to create a shell, as it's complex
        # This indirectly tests if the basic model can be created
        shell = _startle_create_initial_madaSeed_shell(
            seed_uid="urn:crux:uid::testshell",
            trace_id_val="urn:crux:uid::testshell",
            raw_signals_list=[]
        )
        self.assertIsInstance(shell, MadaSeed)
        self.assertEqual(shell.seed_id, "urn:crux:uid::testshell")
        self.assertEqual(shell.version, "0.3.0") # As defined in _startle_create_initial_madaSeed_shell
        self.assertIsNotNone(shell.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L6_reflection_payload.L7_encoded_application)


class TestStartleProcess(unittest.TestCase):
    sample_input_event_multi = {
        "reception_timestamp_utc_iso": "2023-10-27T10:00:00Z",
        "origin_hint": "Test_UI_Input_Multi",
        "data_components": [
            {
                "role_hint": "primary_text_content",
                "content_handle_placeholder": "This is a test prompt.",
                "size_hint": 23,
                "type_hint": "text/plain"
            },
            {
                "role_hint": "attachment_file",
                "content_handle_placeholder": "some_binary_data_placeholder_for_attachment.pdf",
                "size_hint": 1024,
                "type_hint": "application/pdf"
            }
        ]
    }

    sample_input_event_empty_components = {
        "reception_timestamp_utc_iso": "2023-10-27T10:10:00Z",
        "origin_hint": "System_Internal_Trigger_NoData",
        "data_components": [] 
    }

    def _assert_crux_uid(self, uid_string, uid_name):
        self.assertIsInstance(uid_string, str, f"{uid_name} should be a string")
        self.assertTrue(uid_string.startswith("urn:crux:uid::"), f"{uid_name} should start with 'urn:crux:uid::'")
        uuid_part = uid_string.split("::")[-1]
        self.assertTrue(len(uuid_part) == 32, f"{uid_name} UUID part should be 32 chars, got {len(uuid_part)}")
        try:
            int(uuid_part, 16) # Check if it's a valid hex string
        except ValueError:
            self.fail(f"{uid_name} UUID part is not a valid hex string: {uuid_part}")


    def test_startle_process_valid_input_multi_components(self):
        mada_seed = startle_process(self.sample_input_event_multi)
        self.assertIsInstance(mada_seed, MadaSeed)

        # Assert seed_id and trace_id
        self._assert_crux_uid(mada_seed.seed_id, "mada_seed.seed_id")
        self._assert_crux_uid(mada_seed.trace_metadata.trace_id, "mada_seed.trace_metadata.trace_id")
        self.assertEqual(mada_seed.seed_id, mada_seed.trace_metadata.trace_id)

        # Assert raw_signals
        self.assertEqual(len(mada_seed.seed_content.raw_signals), 2)
        self._assert_crux_uid(mada_seed.seed_content.raw_signals[0].raw_input_id, "raw_signals[0].raw_input_id")
        self.assertEqual(mada_seed.seed_content.raw_signals[0].raw_input_signal, "This is a test prompt.")
        self._assert_crux_uid(mada_seed.seed_content.raw_signals[1].raw_input_id, "raw_signals[1].raw_input_id")
        self.assertEqual(mada_seed.seed_content.raw_signals[1].raw_input_signal, "some_binary_data_placeholder_for_attachment.pdf")

        # Assert L1_startle_context_obj
        l1_context = mada_seed.seed_content.L1_startle_reflex.L1_startle_context_obj
        self.assertEqual(l1_context.version, "0.1.1")
        self.assertEqual(l1_context.trace_creation_time_L1, dt.fromisoformat("2023-10-27T10:00:00+00:00"))
        self.assertEqual(l1_context.input_origin_L1, "Test_UI_Input_Multi")
        self.assertEqual(l1_context.L1_epistemic_state_of_startle, L1EpistemicStateOfStartleEnum.STARTLE_COMPLETE_SIGNALREFS_GENERATED)
        
        self.assertEqual(len(l1_context.signal_components_metadata_L1), 2)
        component1_meta = l1_context.signal_components_metadata_L1[0]
        self.assertEqual(component1_meta.component_role_L1, "primary_text_content")
        self._assert_crux_uid(component1_meta.raw_signal_ref_uid_L1, "component1_meta.raw_signal_ref_uid_L1")
        self.assertEqual(component1_meta.encoding_status_L1, EncodingStatusL1Enum.ASSUMEDUTF8_TEXTHINT)
        
        component2_meta = l1_context.signal_components_metadata_L1[1]
        self.assertEqual(component2_meta.component_role_L1, "attachment_file")
        self._assert_crux_uid(component2_meta.raw_signal_ref_uid_L1, "component2_meta.raw_signal_ref_uid_L1")
        self.assertEqual(component2_meta.encoding_status_L1, EncodingStatusL1Enum.DETECTEDBINARY)


        # Assert L1_trace
        l1_trace = mada_seed.trace_metadata.L1_trace
        self.assertEqual(l1_trace.version_L1_trace_schema, "0.1.0")
        self.assertEqual(l1_trace.sop_name, "lC.SOP.startle")
        self.assertEqual(l1_trace.epistemic_state_L1, L1EpistemicStateOfStartleEnum.STARTLE_COMPLETE_SIGNALREFS_GENERATED)
        # Fixed timestamp from helper for completion
        self.assertEqual(l1_trace.completion_timestamp_L1, dt.fromisoformat("2023-10-28T11:45:00+00:00"))
        self.assertEqual(l1_trace.L1_trace_creation_time_from_context, dt.fromisoformat("2023-10-27T10:00:00+00:00"))
        self.assertEqual(l1_trace.L1_input_origin_from_context, "Test_UI_Input_Multi")
        self.assertEqual(l1_trace.L1_signal_component_count, 2)
        self.assertEqual(l1_trace.L1_generated_trace_id, mada_seed.seed_id)


    def test_startle_process_empty_components(self):
        mada_seed = startle_process(self.sample_input_event_empty_components)
        self.assertIsInstance(mada_seed, MadaSeed)
        self._assert_crux_uid(mada_seed.seed_id, "mada_seed.seed_id")

        # Assert raw_signals for placeholder
        self.assertEqual(len(mada_seed.seed_content.raw_signals), 1)
        self.assertEqual(mada_seed.seed_content.raw_signals[0].raw_input_signal, "[[EMPTY_INPUT_EVENT]]")
        self._assert_crux_uid(mada_seed.seed_content.raw_signals[0].raw_input_id, "raw_signals[0].raw_input_id_placeholder")

        # Assert L1_startle_context_obj for placeholder
        l1_context = mada_seed.seed_content.L1_startle_reflex.L1_startle_context_obj
        self.assertEqual(l1_context.version, "0.1.1")
        self.assertEqual(l1_context.input_origin_L1, "System_Internal_Trigger_NoData")
        self.assertEqual(len(l1_context.signal_components_metadata_L1), 1)
        placeholder_meta = l1_context.signal_components_metadata_L1[0]
        self.assertEqual(placeholder_meta.component_role_L1, "placeholder_empty_input")
        self.assertEqual(placeholder_meta.raw_signal_ref_uid_L1, mada_seed.seed_content.raw_signals[0].raw_input_id) # Should match
        self.assertEqual(placeholder_meta.encoding_status_L1, EncodingStatusL1Enum.UNKNOWN_L1)

        # Assert L1_trace
        l1_trace = mada_seed.trace_metadata.L1_trace
        self.assertEqual(l1_trace.epistemic_state_L1, L1EpistemicStateOfStartleEnum.STARTLE_COMPLETE_SIGNALREFS_GENERATED)
        self.assertEqual(l1_trace.L1_signal_component_count, 1)

class TestFrameClickProcess(unittest.TestCase):
    # Use the same valid input event from TestStartleProcess for generating L1 output
    sample_input_event_for_l1 = TestStartleProcess.sample_input_event_multi

    def test_frame_click_process_valid_startle_output(self):
        output_from_l1 = startle_process(self.sample_input_event_for_l1)
        self.assertEqual(output_from_l1.trace_metadata.L1_trace.epistemic_state_L1, L1EpistemicStateOfStartleEnum.STARTLE_COMPLETE_SIGNALREFS_GENERATED)

        mada_seed_l2 = frame_click_process(output_from_l1)
        self.assertIsInstance(mada_seed_l2, MadaSeed)

        # Assert L1 parts remain unchanged
        self.assertEqual(mada_seed_l2.seed_id, output_from_l1.seed_id)
        self.assertEqual(mada_seed_l2.trace_metadata.L1_trace, output_from_l1.trace_metadata.L1_trace)
        self.assertEqual(mada_seed_l2.seed_content.L1_startle_reflex.L1_startle_context_obj, output_from_l1.seed_content.L1_startle_reflex.L1_startle_context_obj)

        # Assert L2_frame_type_obj
        l2_frame_obj = mada_seed_l2.seed_content.L1_startle_reflex.L2_frame_type.L2_frame_type_obj
        self.assertEqual(l2_frame_obj.version, "0.1.2")
        self.assertEqual(l2_frame_obj.L2_epistemic_state_of_framing, L2EpistemicStateOfFramingEnum.FRAMED)
        # Based on sample_input_event_multi (text + pdf) and baseline _frame_classify_input logic
        self.assertEqual(l2_frame_obj.input_class_L2, InputClassL2Enum.COMMS) 
        # Based on baseline _frame_validate_structure for "comms"
        self.assertEqual(l2_frame_obj.frame_type_L2, "unknown_frame_L2") # Or specific if logic was more complex
        self.assertEqual(l2_frame_obj.L2_validation_status_of_frame, L2ValidationStatusOfFrameEnum.FAILURE_NOSTRUCTUREDETECTED) # if frame_type_L2 is unknown

        # If the logic was to make it "mixed" and "plaintext_prompt" based on primary component
        # For "primary_text_content" type_hint "text/plain"
        # self.assertEqual(l2_frame_obj.input_class_L2, InputClassL2Enum.MIXED) # Or PROMPT depending on exact classify logic for multi-component
        # self.assertEqual(l2_frame_obj.frame_type_L2, "plaintext_prompt") # if primary component dictates
        # self.assertEqual(l2_frame_obj.L2_validation_status_of_frame, L2ValidationStatusOfFrameEnum.SUCCESS_FRAMED)


        self.assertIsNotNone(l2_frame_obj.communication_context_L2)
        self.assertEqual(l2_frame_obj.communication_context_L2.origin_environment_L2, self.sample_input_event_for_l1["origin_hint"])
        
        self.assertIsNotNone(l2_frame_obj.temporal_hint_L2)
        # L1 trace_creation_time_L1 comes from input_event's reception_timestamp_utc_iso
        expected_l1_creation_dt = dt.fromisoformat(self.sample_input_event_for_l1["reception_timestamp_utc_iso"].replace('Z', '+00:00'))
        self.assertEqual(l2_frame_obj.temporal_hint_L2.value, expected_l1_creation_dt)
        self.assertEqual(l2_frame_obj.temporal_hint_L2.provenance, TemporalHintProvenanceL2Enum.FALLBACK_L1_CREATION_TIME)

        # Assert L2_trace
        l2_trace = mada_seed_l2.trace_metadata.L2_trace
        self.assertEqual(l2_trace.version_L2_trace_schema, "0.1.0")
        self.assertEqual(l2_trace.sop_name, "lC.SOP.frame_click")
        self.assertEqual(l2_trace.epistemic_state_L2, L2EpistemicStateOfFramingEnum.FRAMED) # This should match L2_frame_type_obj's state
        # Fixed timestamp from helper for completion
        self.assertEqual(l2_trace.completion_timestamp_L2, dt.fromisoformat("2023-10-28T11:30:00+00:00"))
        self.assertEqual(l2_trace.L2_input_class_determined_in_trace, l2_frame_obj.input_class_L2)
        self.assertEqual(l2_trace.L2_frame_type_determined_in_trace, l2_frame_obj.frame_type_L2)
        self.assertEqual(l2_trace.L2_validation_status_in_trace, l2_frame_obj.L2_validation_status_of_frame)


    def test_frame_click_process_l1_failure_state(self):
        # Create an L1 MadaSeed that indicates an L1 processing failure
        input_event_for_l1_fail = {
            "reception_timestamp_utc_iso": "2023-10-27T11:00:00Z", # Valid timestamp
            "origin_hint": "Test_L1_Simulated_Fail",
            "data_components": [{"role_hint":"test", "content_handle_placeholder":"data", "size_hint":10, "type_hint":"text/plain"}]
        }
        output_from_l1_failed_state = startle_process(input_event_for_l1_fail)
        # Manually set L1 epistemic state to a failure/non-complete state
        output_from_l1_failed_state.trace_metadata.L1_trace.epistemic_state_L1 = L1EpistemicStateOfStartleEnum.LCL_FAILURE_INTERNAL_L1
        output_from_l1_failed_state.seed_content.L1_startle_reflex.L1_startle_context_obj.L1_epistemic_state_of_startle = L1EpistemicStateOfStartleEnum.LCL_FAILURE_INTERNAL_L1


        mada_seed_l2_after_l1_fail = frame_click_process(output_from_l1_failed_state)
        self.assertIsInstance(mada_seed_l2_after_l1_fail, MadaSeed)

        # Assert L2 trace indicates an internal failure or specific LCL due to L1 state
        l2_trace = mada_seed_l2_after_l1_fail.trace_metadata.L2_trace
        self.assertEqual(l2_trace.sop_name, "lC.SOP.frame_click")
        self.assertEqual(l2_trace.epistemic_state_L2, L2EpistemicStateOfFramingEnum.LCL_FAILURE_INTERNAL_L2) # As per _frame_validate_l1_data_in_madaSeed path
        self.assertIsNotNone(l2_trace.error_detail)
        self.assertTrue("Invalid or incomplete L1 data" in l2_trace.error_detail)

        # Assert L2_frame_type_obj also reflects this failure
        l2_frame_obj = mada_seed_l2_after_l1_fail.seed_content.L1_startle_reflex.L2_frame_type.L2_frame_type_obj
        self.assertEqual(l2_frame_obj.L2_epistemic_state_of_framing, L2EpistemicStateOfFramingEnum.LCL_FAILURE_INTERNAL_L2)
        self.assertIsNotNone(l2_frame_obj.error_details)
        self.assertTrue("L2 aborted: Invalid L1 data" in l2_frame_obj.error_details)


if __name__ == '__main__':
    unittest.main()
