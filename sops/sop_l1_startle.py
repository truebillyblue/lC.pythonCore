import uuid
from datetime import datetime as dt, timezone
from typing import List, Dict, Tuple, Any, Optional

from ..schemas.mada_schema import (
    MadaSeed, SeedContent, TraceMetadata, RawSignal,
    L1StartleReflex, L1StartleContextObj, L1Trace,
    L2FrameType, L2FrameTypeObj, L2Trace,
    L3SurfaceKeymap, L3SurfaceKeymapObj, L3Trace,
    L4AnchorState, L4AnchorStateObj, L4Trace,
    L5FieldState, L5FieldStateObj, L5Trace,
    L6ReflectionPayload, L6ReflectionPayloadObj, L6Trace,
    L7EncodedApplication, L7Trace, SeedQAQC,
    SignalComponentMetadataL1,
    L1EpistemicStateOfStartleEnum, EncodingStatusL1Enum,
    # Enums for pending states in other layers
    L2EpistemicStateOfFramingEnum,
    # L3EpistemicStateEnum, # Actual enum for L3 success is Keymapped_Successfully
    L4EpistemicStateOfAnchoringEnum,
    L5EpistemicStateOfFieldProcessingEnum,
    L6EpistemicStateEnum,
    L7EpistemicStateEnum,
    SeedIntegrityStatusEnum,
)

# Basic logging function placeholder
def log_internal_error(helper_name: str, error_info: Dict):
    print(f"ERROR in {helper_name}: {error_info}")

def log_internal_warning(helper_name: str, warning_info: Dict):
    print(f"WARNING in {helper_name}: {warning_info}")

def log_internal_info(helper_name: str, info: Dict):
    print(f"INFO in {helper_name}: {info}")

def log_critical_error(process_name: str, error_info: Dict):
    print(f"CRITICAL ERROR in {process_name}: {error_info}")

# Helper function to generate UUIDs (as per pseudo-code's generate_system_uuidv4_primitive)
def generate_system_uuidv4_primitive() -> uuid.UUID:
    return uuid.uuid4()

def format_uuid_as_hex(system_uuid: uuid.UUID) -> str:
    return system_uuid.hex

# --- Internal Helper Function Definitions ---

def _startle_get_current_timestamp_utc() -> str:
    # Per instruction, return a fixed, unique timestamp string for consistent testing.
    # Real implementation would use: return dt.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')
    return "2023-10-28T11:45:00Z"

def _startle_generate_crux_uid(type_hint: str, context_hint: Dict) -> str:
    """
    Generates a UUID, formats it as hex, and prepends "urn:crux:uid::".
    """
    try:
        system_uuid = generate_system_uuidv4_primitive()
        crux_uid_string = "urn:crux:uid::" + format_uuid_as_hex(system_uuid)
        return crux_uid_string
    except Exception as e:
        log_internal_error("_startle_generate_crux_uid", {"type": type_hint, "context": context_hint, "error": str(e)})
        raise Exception(f"CRUX UID Generation Failed for {type_hint}")


def _startle_process_input_components(input_data_components: List[Dict], trace_id_for_context: str) -> Tuple[List[RawSignal], List[SignalComponentMetadataL1]]:
    """
    Processes input_event.data_components to create raw_signals for madaSeed
    and signal_components_metadata_L1 for L1_startle_context_obj.
    Returns: raw_signals_array, signal_components_metadata_array
    """
    raw_signals_for_madaSeed: List[RawSignal] = []
    signal_meta_for_L1_context: List[SignalComponentMetadataL1] = []

    if not input_data_components: # Handles None or empty list
        log_internal_warning("_startle_process_input_components", {"warning": "No data_components found in input_event."})
        # Add a placeholder component as per pseudo-code for minItems: 1 constraint
        placeholder_comp_uid = _startle_generate_crux_uid("raw_signal_placeholder", {"trace_id": trace_id_for_context})
        
        signal_meta_for_L1_context.append(SignalComponentMetadataL1(
            component_role_L1="placeholder_empty_input",
            raw_signal_ref_uid_L1=placeholder_comp_uid,
            byte_size_hint_L1=0,
            encoding_status_L1=EncodingStatusL1Enum.UNKNOWN_L1,
            media_type_hint_L1=None
        ))
        raw_signals_for_madaSeed.append(RawSignal(
            raw_input_id=placeholder_comp_uid,
            raw_input_signal="[[EMPTY_INPUT_EVENT]]"
        ))
        return raw_signals_for_madaSeed, signal_meta_for_L1_context

    for component_event_data in input_data_components:
        role_hint = component_event_data.get('role_hint', 'primary_content') # Default role
        raw_signal_ref_uid = _startle_generate_crux_uid("raw_signal_content", {"trace_id": trace_id_for_context, "role": role_hint})

        content_handle = component_event_data.get('content_handle_placeholder', '[[CONTENT_REF_OMITTED]]')
        
        raw_signals_for_madaSeed.append(RawSignal(
            raw_input_id=raw_signal_ref_uid,
            raw_input_signal=str(content_handle) 
        ))

        encoding_status = EncodingStatusL1Enum.UNKNOWN_L1
        type_hint = component_event_data.get('type_hint')
        if type_hint:
            type_hint_lower = type_hint.lower()
            if type_hint_lower.startswith("text/"):
                encoding_status = EncodingStatusL1Enum.ASSUMEDUTF8_TEXTHINT
            elif type_hint_lower in ["application/octet-stream", "image/jpeg", "application/pdf"]: # Example binary types
                encoding_status = EncodingStatusL1Enum.DETECTEDBINARY
            else:
                encoding_status = EncodingStatusL1Enum.POSSIBLEENCODINGISSUE_L1
        
        signal_meta_for_L1_context.append(SignalComponentMetadataL1(
            component_role_L1=role_hint,
            raw_signal_ref_uid_L1=raw_signal_ref_uid,
            byte_size_hint_L1=component_event_data.get('size_hint'),
            encoding_status_L1=encoding_status,
            media_type_hint_L1=type_hint
        ))
    return raw_signals_for_madaSeed, signal_meta_for_L1_context


def _startle_create_initial_madaSeed_shell(seed_uid: str, trace_id_val: str, raw_signals_list: List[RawSignal]) -> MadaSeed:
    """
    Creates the top-level madaSeed structure with L1 trace_id and raw_signals.
    L2-L7 content and trace objects are initialized with minimal placeholders.
    """
    # Placeholder objects for layers L2-L7, ensuring all required fields are set
    # Note: For enums, using the first valid enum value or a specific "Pending" if defined.
    # Many ".version" fields have pattern constraints; ensure they are met.
    
    pending_l2_frame_obj = L2FrameTypeObj(version="0.1.2", L2_epistemic_state_of_framing=L2EpistemicStateOfFramingEnum.LCL_FAILURE_INTERNAL_L2, error_details="Pending_L2")
    pending_l3_keymap_obj = L3SurfaceKeymapObj(version="0.1.1", lexical_affordances={}, syntactic_hints={}, pragmatic_affective_affordances={}, relational_linking_markers={}, L3_flags={}, error_details="Pending_L3") # Fill required sub-models
    pending_l4_anchor_obj = L4AnchorStateObj(version="0.2.17", l4_epistemic_state_of_anchoring=L4EpistemicStateOfAnchoringEnum.LCL_FAILURE_INTERNAL_L4, error_details="Pending_L4")
    pending_l5_field_obj = L5FieldStateObj(version="0.2.0", l5_epistemic_state_of_field_processing=L5EpistemicStateOfFieldProcessingEnum.LCL_FAILURE_INTERNAL_L5, error_details="Pending_L5")
    pending_l6_reflection_payload_obj = L6ReflectionPayloadObj(
        version="0.1.6", l6_epistemic_state=L6EpistemicStateEnum.LCL_FAILURE_INTERNAL_L6, redaction_applied_summary=False,
        payload_metadata={"generation_sop":"lC.SOP.reflect_boom", "generation_timestamp":_startle_get_current_timestamp_utc(), "source_trace_id":trace_id_val, "presentation_target":{"consumer_type":"System_Module"}, "presentation_intent":"Pending_L6", "output_modality":"Structured_Data"},
        transformation_metadata={"redaction_status":{"redaction_applied":False}, "omitted_content_summary":{"omission_applied":False}},
        reflection_surface={"assessed_cynefin_state":{"domain":"Unknown"}, "brave_space_reflection":{"l6_transformation_dissent_risk_hint":"Minimal", "l6_representation_discomfort_risk_hint":"Minimal"}},
        payload_content={"structured_data": {"status": "Pending_L6"}}
    )
    pending_l7_encoded_app = L7EncodedApplication(version_L7_payload="0.1.1", L7_backlog={"version":"0.1.0"}, seed_outputs=[])


    shell = MadaSeed(
        version="0.3.0",
        seed_id=seed_uid,
        seed_content=SeedContent(
            raw_signals=raw_signals_list,
            L1_startle_reflex=L1StartleReflex(
                L1_startle_context_obj=L1StartleContextObj( # Placeholder, will be filled by L1 logic
                    version="0.0.0", # Temp version
                    L1_epistemic_state_of_startle=L1EpistemicStateOfStartleEnum.LCL_FAILURE_INTERNAL_L1,
                    trace_creation_time_L1=_startle_get_current_timestamp_utc(), # Temp time
                    signal_components_metadata_L1=[] # Temp list
                ), 
                L2_frame_type=L2FrameType( # Nesting L2 placeholder
                    L2_frame_type_obj=pending_l2_frame_obj,
                    L3_surface_keymap=L3SurfaceKeymap( # Nesting L3 placeholder
                        L3_surface_keymap_obj=pending_l3_keymap_obj,
                        L4_anchor_state=L4AnchorState( # Nesting L4 placeholder
                            L4_anchor_state_obj=pending_l4_anchor_obj,
                            L5_field_state=L5FieldState( # Nesting L5 placeholder
                                L5_field_state_obj=pending_l5_field_obj,
                                L6_reflection_payload=L6ReflectionPayload( # Nesting L6 placeholder
                                    L6_reflection_payload_obj=pending_l6_reflection_payload_obj,
                                    L7_encoded_application=pending_l7_encoded_app # Nesting L7 placeholder
                                )
                            )
                        )
                    )
                )
            )
        ),
        trace_metadata=TraceMetadata(
            trace_id=trace_id_val,
            L1_trace=L1Trace( # Placeholder, will be filled by L1 logic
                version_L1_trace_schema="0.0.0", sop_name="lC.SOP.startle", 
                completion_timestamp_L1=_startle_get_current_timestamp_utc(), 
                epistemic_state_L1=L1EpistemicStateOfStartleEnum.LCL_FAILURE_INTERNAL_L1,
                L1_trace_creation_time_from_context=_startle_get_current_timestamp_utc(),
                L1_signal_component_count=0
            ), 
            L2_trace=L2Trace(version_L2_trace_schema="0.1.0", sop_name="lC.SOP.frame_click", completion_timestamp_L2=_startle_get_current_timestamp_utc(), epistemic_state_L2=L2EpistemicStateOfFramingEnum.LCL_FAILURE_INTERNAL_L2, error_detail="Pending_L2"),
            L3_trace=L3Trace(version_L3_trace_schema="0.1.0", sop_name="lC.SOP.keymap_click", completion_timestamp_L3=_startle_get_current_timestamp_utc(), epistemic_state_L3="Pending_L3"),
            L4_trace=L4Trace(version_L4_trace_schema="0.1.0", sop_name="lC.SOP.anchor_click", completion_timestamp_L4=_startle_get_current_timestamp_utc(), epistemic_state_L4=L4EpistemicStateOfAnchoringEnum.LCL_FAILURE_INTERNAL_L4, error_details="Pending_L4"),
            L5_trace=L5Trace(version_L5_trace_schema="0.1.0", sop_name="lC.SOP.field_click", completion_timestamp_L5=_startle_get_current_timestamp_utc(), epistemic_state_L5=L5EpistemicStateOfFieldProcessingEnum.LCL_FAILURE_INTERNAL_L5, error_details="Pending_L5"),
            L6_trace=L6Trace(version_L6_trace_schema="0.1.0", sop_name="lC.SOP.reflect_boom", completion_timestamp_L6=_startle_get_current_timestamp_utc(), epistemic_state_L6=L6EpistemicStateEnum.LCL_FAILURE_INTERNAL_L6, error_details="Pending_L6"),
            L7_trace=L7Trace(version_L7_trace_schema="0.1.1", sop_name="lC.SOP.apply_done", completion_timestamp_L7=_startle_get_current_timestamp_utc(), epistemic_state_L7=L7EpistemicStateEnum.LCL_FAILURE_INTERNAL_L7, error_details="Pending_L7")
        ),
        seed_QA_QC=SeedQAQC(version_seed_qa_qc_schema="0.1.0", overall_seed_integrity_status=SeedIntegrityStatusEnum.QA_QC_PROCESS_ERROR, qa_qc_assessment_timestamp=_startle_get_current_timestamp_utc(), error_details="Pending_L7_QA"),
        seed_completion_timestamp=None 
    )
    return shell

# --- Main startle Process Function ---

def startle_process(input_event: Dict[str, Any]) -> MadaSeed:
    """
    Defines the mandatory epistemic reflex initiating a processing loop upon detection of any raw input signal event.
    Accepts an input_event dictionary and returns a populated MadaSeed Pydantic object.
    """
    current_time_init_fail_str = _startle_get_current_timestamp_utc()
    # Attempt to parse the string timestamp to datetime object for Pydantic model
    try:
        current_time_init_fail_dt = dt.fromisoformat(current_time_init_fail_str.replace('Z', '+00:00'))
    except ValueError: # Fallback if parsing fails, though fixed string should be fine
        current_time_init_fail_dt = dt.now(timezone.utc)


    # Initialize madaSeed with error state in case of early failure
    # This shell must be valid according to Pydantic models from the start.
    error_seed_shell = _startle_create_initial_madaSeed_shell("ERROR_SEED_ID", "ERROR_TRACE_ID", [])
    error_seed_shell.trace_metadata.L1_trace = L1Trace(
        version_L1_trace_schema="0.1.0", sop_name="lC.SOP.startle", 
        completion_timestamp_L1=current_time_init_fail_dt,
        epistemic_state_L1=L1EpistemicStateOfStartleEnum.LCL_FAILURE_INTERNAL_L1,
        error_detail="Startle initialization failure.",
        L1_trace_creation_time_from_context=current_time_init_fail_dt,
        L1_signal_component_count=0
    )
    error_seed_shell.seed_content.L1_startle_reflex.L1_startle_context_obj = L1StartleContextObj(
        version="0.1.1", 
        L1_epistemic_state_of_startle=L1EpistemicStateOfStartleEnum.LCL_FAILURE_INTERNAL_L1,
        error_details="Startle initialization failure.",
        trace_creation_time_L1=current_time_init_fail_dt,
        signal_components_metadata_L1=[ # Must satisfy minItems=1
            SignalComponentMetadataL1(component_role_L1="placeholder_error", raw_signal_ref_uid_L1="ERROR_UID", encoding_status_L1=EncodingStatusL1Enum.UNKNOWN_L1)
        ]
    )

    try:
        # --- Step 1: Acknowledge Event Reception & Basic Validation ---
        if not input_event or input_event.get('reception_timestamp_utc_iso') is None: # Changed from Null
            raise ValueError("Invalid Input: Missing reception_timestamp_utc_iso.") # Changed to ValueError
        
        l1_trace_creation_time_str = input_event.get('reception_timestamp_utc_iso')
        l1_trace_creation_time_dt = dt.fromisoformat(l1_trace_creation_time_str.replace('Z', '+00:00'))
        
        l1_input_origin = input_event.get('origin_hint')
        input_components_data = input_event.get('data_components', [])

        # --- Step 2: Instantiate Trace ID ---
        generated_trace_id = _startle_generate_crux_uid("trace_event_L1", {"origin": l1_input_origin, "time": l1_trace_creation_time_str})

        # --- Process input components ---
        raw_signals_for_seed, signal_components_meta_for_l1_payload = _startle_process_input_components(input_components_data, generated_trace_id)
        
        # Initialize madaSeed shell structure
        working_mada_seed = _startle_create_initial_madaSeed_shell(generated_trace_id, generated_trace_id, raw_signals_for_seed)
        
        # --- Step 3 & 4: Assemble L1_startle_context_obj ---
        l1_final_epistemic_state = L1EpistemicStateOfStartleEnum.STARTLE_COMPLETE_SIGNALREFS_GENERATED
        
        l1_startle_context_obj_payload = L1StartleContextObj(
            version="0.1.1",
            L1_epistemic_state_of_startle=l1_final_epistemic_state,
            trace_creation_time_L1=l1_trace_creation_time_dt,
            input_origin_L1=l1_input_origin,
            signal_components_metadata_L1=signal_components_meta_for_l1_payload
        )
        working_mada_seed.seed_content.L1_startle_reflex.L1_startle_context_obj = l1_startle_context_obj_payload
        
        # --- Populate L1_trace metadata ---
        l1_completion_time_str = _startle_get_current_timestamp_utc()
        l1_completion_time_dt = dt.fromisoformat(l1_completion_time_str.replace('Z', '+00:00'))
        
        l1_trace_obj = L1Trace(
            version_L1_trace_schema="0.1.0", 
            sop_name="lC.SOP.startle", 
            completion_timestamp_L1=l1_completion_time_dt,
            epistemic_state_L1=l1_final_epistemic_state,
            L1_trace_creation_time_from_context=l1_trace_creation_time_dt,
            L1_input_origin_from_context=l1_input_origin,
            L1_signal_component_count=len(signal_components_meta_for_l1_payload),
            L1_generated_trace_id=generated_trace_id,
            L1_generated_raw_signal_ref_uids_summary={"count": len(raw_signals_for_seed)}
        )
        working_mada_seed.trace_metadata.L1_trace = l1_trace_obj
        
        # --- Step 5 & 6: Finalize & Expose (Return the madaSeed) ---
        return working_mada_seed

    except Exception as critical_process_error:
        log_critical_error("Startle Process Failed Critically", {"input_origin": input_event.get('origin_hint') if input_event else "N/A", "error": str(critical_process_error)})
        
        # Populate error details in the pre-initialized error_seed_shell
        error_detail_str = str(critical_process_error)
        if hasattr(error_seed_shell.trace_metadata.L1_trace, 'error_detail'): # Check if field exists
             error_seed_shell.trace_metadata.L1_trace.error_detail = error_detail_str
        
        # If trace_id was generated before fail, use it
        generated_trace_id_before_fail = locals().get('generated_trace_id')
        if generated_trace_id_before_fail:
            error_seed_shell.seed_id = generated_trace_id_before_fail
            error_seed_shell.trace_metadata.trace_id = generated_trace_id_before_fail
        
        if hasattr(error_seed_shell.seed_content.L1_startle_reflex.L1_startle_context_obj, 'error_details'):
            error_seed_shell.seed_content.L1_startle_reflex.L1_startle_context_obj.error_details = error_detail_str
        error_seed_shell.seed_content.L1_startle_reflex.L1_startle_context_obj.L1_epistemic_state_of_startle = L1EpistemicStateOfStartleEnum.LCL_FAILURE_INTERNAL_L1
        
        return error_seed_shell

if __name__ == '__main__':
    # Example Usage:
    print("--- Running sop_l1_startle.py example ---")

    # Example 1: Input event with multiple components
    example_input_event_multi = {
        "reception_timestamp_utc_iso": "2023-10-27T10:00:00Z",
        "origin_hint": "User_Interface_Upload",
        "data_components": [
            {"role_hint": "primary_text_content", "content_handle_placeholder": "This is the main text.", "size_hint": 25, "type_hint": "text/plain"},
            {"role_hint": "attachment_file", "content_handle_placeholder": "file_ref_xyz.pdf", "size_hint": 102400, "type_hint": "application/pdf"}
        ]
    }
    print(f"\nProcessing example_input_event_multi: {example_input_event_multi}")
    mada_seed_output_multi = startle_process(example_input_event_multi)
    print("Output MadaSeed (Multi-component):")
    # print(mada_seed_output_multi.json(indent=2)) # Using .json() for pretty print if needed

    # Example 2: Input event with a single component
    example_input_event_single = {
        "reception_timestamp_utc_iso": "2023-10-27T10:05:00Z",
        "origin_hint": "API_Ingest_Point_A",
        "data_components": [
            {"role_hint": "json_payload", "content_handle_placeholder": {"key": "value", "num": 123}, "size_hint": 50, "type_hint": "application/json"}
        ]
    }
    print(f"\nProcessing example_input_event_single: {example_input_event_single}")
    mada_seed_output_single = startle_process(example_input_event_single)
    # print("Output MadaSeed (Single-component):")
    # print(mada_seed_output_single.json(indent=2))


    # Example 3: Input event with no data components (edge case)
    example_input_event_empty_components = {
        "reception_timestamp_utc_iso": "2023-10-27T10:10:00Z",
        "origin_hint": "System_Internal_Trigger_NoData",
        "data_components": [] # Empty list
    }
    print(f"\nProcessing example_input_event_empty_components: {example_input_event_empty_components}")
    mada_seed_output_empty_components = startle_process(example_input_event_empty_components)
    # print("Output MadaSeed (Empty data_components):")
    # print(mada_seed_output_empty_components.json(indent=2))

    # Example 4: Invalid input event (missing timestamp)
    example_input_event_invalid = {
        "origin_hint": "Test_Invalid_Input",
        "data_components": [{"role_hint": "test", "content_handle_placeholder": "test", "size_hint": 4, "type_hint": "text/plain"}]
    }
    print(f"\nProcessing example_input_event_invalid: {example_input_event_invalid}")
    mada_seed_output_invalid = startle_process(example_input_event_invalid)
    print("Output MadaSeed (Invalid input):")
    # print(mada_seed_output_invalid.json(indent=2))

    # Verify a specific field from one of the outputs
    if mada_seed_output_multi and mada_seed_output_multi.seed_id != "ERROR_SEED_ID":
        print(f"\nTrace ID for multi-component example: {mada_seed_output_multi.trace_metadata.L1_trace.L1_generated_trace_id}")
        print(f"L1 Startle Context version: {mada_seed_output_multi.seed_content.L1_startle_reflex.L1_startle_context_obj.version}")
        print(f"Number of raw signals: {len(mada_seed_output_multi.seed_content.raw_signals)}")
        if len(mada_seed_output_multi.seed_content.raw_signals) > 0:
            print(f"First raw_signal_id: {mada_seed_output_multi.seed_content.raw_signals[0].raw_input_id}")
        print(f"L2 Epistemic State (initial): {mada_seed_output_multi.trace_metadata.L2_trace.epistemic_state_L2}")
    
    if mada_seed_output_empty_components and mada_seed_output_empty_components.seed_id != "ERROR_SEED_ID":
         print(f"\nPlaceholder component role in empty case: {mada_seed_output_empty_components.seed_content.L1_startle_reflex.L1_startle_context_obj.signal_components_metadata_L1[0].component_role_L1}")
         print(f"Placeholder raw_input_signal: {mada_seed_output_empty_components.seed_content.raw_signals[0].raw_input_signal}")

    print("\n--- sop_l1_startle.py example run complete ---")
