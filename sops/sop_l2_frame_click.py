from datetime import datetime as dt, timezone
from typing import List, Dict, Tuple, Any, Optional

from ..schemas.mada_schema import (
    MadaSeed, L1StartleContextObj, L2FrameTypeObj, L2Trace, TemporalHintL2,
    CommunicationContextL2,
    L2EpistemicStateOfFramingEnum, InputClassL2Enum,
    TemporalHintProvenanceL2Enum, L2ValidationStatusOfFrameEnum
)

# Basic logging function placeholder (reuse from L1 or define if separate)
def log_internal_error(helper_name: str, error_info: Dict):
    print(f"ERROR in {helper_name}: {error_info}")

def log_internal_warning(helper_name: str, warning_info: Dict):
    print(f"WARNING in {helper_name}: {warning_info}")

def log_internal_info(helper_name: str, info: Dict):
    print(f"INFO in {helper_name}: {info}")

def log_critical_error(process_name: str, error_info: Dict):
    print(f"CRITICAL ERROR in {process_name}: {error_info}")

# --- Internal Helper Function Definitions ---

def _frame_validate_l1_data_in_madaSeed(mada_seed_input: MadaSeed) -> bool:
    """Validates essential L1 data presence within the input MadaSeed for L2 processing."""
    try:
        if not mada_seed_input:
            log_internal_warning("Helper:_frame_validate_l1_data", {"error": "Input madaSeed is None"})
            return False

        l1_startle_context_obj = mada_seed_input.seed_content.L1_startle_reflex.L1_startle_context_obj
        l1_trace = mada_seed_input.trace_metadata.L1_trace

        if not l1_startle_context_obj or not l1_startle_context_obj.version:
            log_internal_warning("Helper:_frame_validate_l1_data", {"error": "Missing or invalid L1_startle_context_obj in madaSeed for L2"})
            return False
        if not l1_trace or not l1_trace.epistemic_state_L1:
            log_internal_warning("Helper:_frame_validate_l1_data", {"error": "Missing or invalid L1_trace in madaSeed for L2"})
            return False
        if not l1_trace.epistemic_state_L1.startswith("Startle_Complete"):
            log_internal_info("Helper:_frame_validate_l1_data", {"reason": f"L1 state '{l1_trace.epistemic_state_L1}' not suitable for L2 framing."})
            return False
        # In madaSeed v0.3, raw_signals is at seed_content.raw_signals
        if not mada_seed_input.seed_content.raw_signals: # Check for None or empty list
            log_internal_warning("Helper:_frame_validate_l1_data", {"error": "Missing raw_signals in madaSeed.seed_content for L2"})
            return False
    except AttributeError as e: # Handles cases where nested attributes might be missing
        log_internal_warning("Helper:_frame_validate_l1_data", {"error": f"AttributeError validating L1 data: {str(e)}"})
        return False
    except Exception as e:
        log_internal_warning("Helper:_frame_validate_l1_data", {"error": f"Exception validating L1 data: {str(e)}"})
        return False
    return True

def _frame_get_current_timestamp_utc() -> str:
    """Returns a fixed, unique timestamp string."""
    return "2023-10-28T11:30:00Z"

def _frame_extract_communication_context_from_input(input_event_comm_context_conceptual: Optional[Dict[str, Any]]) -> CommunicationContextL2:
    """
    Extracts communication context. For baseline, uses hints or defaults.
    input_event_comm_context_conceptual is a conceptual dict passed from L1 or system.
    """
    if input_event_comm_context_conceptual is None:
        input_event_comm_context_conceptual = {}
        
    return CommunicationContextL2(
        source_agent_uid_L2=input_event_comm_context_conceptual.get('source_agent_id_hint'),
        destination_agent_uid_L2=input_event_comm_context_conceptual.get('destination_agent_id_hint'),
        origin_environment_L2=input_event_comm_context_conceptual.get('origin_env_hint'),
        interaction_channel_L2=input_event_comm_context_conceptual.get('channel_hint')
    )

def _frame_build_signal_components_summary_from_l1(l1_startle_context_obj: L1StartleContextObj) -> Dict[str, Any]:
    """Extracts summary from L1's signal components metadata."""
    summary: Dict[str, Any] = {"component_count": 0, "primary_component_role": None, "primary_component_media_type_hint": None, "total_byte_size_hint": 0}
    components_l1 = l1_startle_context_obj.signal_components_metadata_L1
    
    if components_l1: # Ensure components_l1 is not None and not empty
        summary['component_count'] = len(components_l1)
        total_size = 0
        for comp in components_l1:
            if comp.component_role_L1 and 'primary' in comp.component_role_L1.lower():
                summary['primary_component_role'] = comp.component_role_L1
                summary['primary_component_media_type_hint'] = comp.media_type_hint_L1
            
            size_hint = comp.byte_size_hint_L1
            if isinstance(size_hint, int): # Check if size_hint is a number
                total_size += size_hint
        summary['total_byte_size_hint'] = total_size
    return summary

def _frame_classify_input(components_summary_l2: Dict[str, Any], input_origin_l1: Optional[str], interaction_channel_l2: Optional[str]) -> InputClassL2Enum:
    """Classifies input based on component summary and context."""
    primary_type = components_summary_l2.get('primary_component_media_type_hint', '').lower() if components_summary_l2.get('primary_component_media_type_hint') else ""
    component_count = components_summary_l2.get('component_count', 1)
    
    is_prompt_like = False
    is_comms_like = False

    if primary_type.startswith("text/") or primary_type == '':
        is_prompt_like = True
    if primary_type.startswith("application/json") or primary_type.startswith("application/xml"):
        is_comms_like = True
    
    if input_origin_l1:
        input_origin_l1_lower = input_origin_l1.lower()
        if 'api' in input_origin_l1_lower or 'system_event' in input_origin_l1_lower:
            is_comms_like = True
    
    if interaction_channel_l2:
        interaction_channel_l2_lower = interaction_channel_l2.lower()
        if 'log' in interaction_channel_l2_lower: # Example, might need more sophisticated logic
            is_comms_like = True
            
    if is_prompt_like and is_comms_like:
        return InputClassL2Enum.MIXED
    if is_comms_like:
        return InputClassL2Enum.COMMS
    if is_prompt_like:
        return InputClassL2Enum.PROMPT
    if component_count > 1: # If multiple components, often more like "comms"
        return InputClassL2Enum.COMMS
        
    return InputClassL2Enum.UNKNOWN_L2_CLASSIFIED

def _frame_initial_checks(components_summary_l2: Dict[str, Any]) -> Tuple[L2ValidationStatusOfFrameEnum, List[str]]:
    """
    Performs initial checks like size/noise, returning status and anomaly flags.
    Baseline: Returns ("OK", []) if component count is reasonable.
    The "OK" status is not an enum, so we use Success_Framed for the positive case if no other error.
    """
    anomaly_flags: List[str] = []
    # Mock policy: Max 5 components, max total size 1MB
    MAX_COMPONENTS = 5
    MAX_SIZE_BYTES = 1 * 1024 * 1024 

    if components_summary_l2.get('component_count', 0) > MAX_COMPONENTS:
        anomaly_flags.append("Excessive_Component_Count")
        return L2ValidationStatusOfFrameEnum.FAILURE_SIZEORNOISE, anomaly_flags
    if components_summary_l2.get('total_byte_size_hint', 0) > MAX_SIZE_BYTES:
        anomaly_flags.append("Excessive_Total_Size")
        return L2ValidationStatusOfFrameEnum.FAILURE_SIZEORNOISE, anomaly_flags
        
    # If no specific check fails, it implies it's okay for structure validation to proceed.
    # The actual "Success_Framed" or other status will be determined by _frame_validate_structure.
    # This function primarily flags size/noise issues. If none, it doesn't mean success yet.
    # The pseudo-code implies check_status != "OK" leads to LCL. Here, if no specific failure,
    # we return a neutral state allowing structure validation to proceed.
    # Let's return a generic success that means "initial checks passed".
    # The actual framing success is determined later.
    # For now, let's return Success_Framed as a placeholder for "checks_ok"
    # and let _frame_validate_structure determine the final framing status.
    # This is a bit tricky as the pseudo-code's "OK" isn't a direct enum.
    # We'll use Success_Framed if no direct failure here, but it will be overwritten.
    return L2ValidationStatusOfFrameEnum.SUCCESS_FRAMED, anomaly_flags


def _frame_validate_structure(input_class: InputClassL2Enum, primary_media_hint: Optional[str]) -> Tuple[Optional[str], L2ValidationStatusOfFrameEnum]:
    """
    Determines frame type and validation status.
    Baseline: if input_class is "prompt" and primary_media_hint is "text/plain" or empty,
    return ("plaintext_prompt", "Success_Framed"). Otherwise, ("unknown_frame_L2", "Failure_NoStructureDetected").
    """
    if input_class == InputClassL2Enum.PROMPT and \
       (primary_media_hint is None or primary_media_hint.lower() == "text/plain" or primary_media_hint == ""):
        return "plaintext_prompt", L2ValidationStatusOfFrameEnum.SUCCESS_FRAMED
    
    # Add more sophisticated frame detection here based on input_class and hints
    # e.g., if input_class is "comms" and primary_media_hint is "application/json"
    if input_class == InputClassL2Enum.COMMS and primary_media_hint and primary_media_hint.lower() == "application/json":
        # Conceptual: try to parse, if fails -> Failure_AmbiguousStructure or Failure_NoStructureDetected
        return "json_comms_L2", L2ValidationStatusOfFrameEnum.SUCCESS_FRAMED # Assuming valid JSON for baseline

    return "unknown_frame_L2", L2ValidationStatusOfFrameEnum.FAILURE_NOSTRUCTUREDETECTED


def _frame_extract_temporal_hint_l2(
    l2_determined_frame_type: Optional[str], 
    l1_trace_creation_time: dt, # Changed to datetime for direct use
    primary_raw_signal_ref_uid: Optional[str]
) -> Optional[TemporalHintL2]:
    """
    Extracts temporal hint. Baseline returns L1 creation time with "fallback_L1_creation_time" provenance.
    """
    # Future HR: Implement parsing based on l2_determined_frame_type.
    # For baseline, directly use l1_trace_creation_time.
    return TemporalHintL2(
        value=l1_trace_creation_time, 
        provenance=TemporalHintProvenanceL2Enum.FALLBACK_L1_CREATION_TIME
    )

# --- Main frame_click Process Function ---

def frame_click_process(mada_seed_input: MadaSeed) -> MadaSeed:
    """
    Processes the madaSeed object from L1 (startle) to populate L2 framing information.
    """
    current_time_fail_dt = dt.fromisoformat(_frame_get_current_timestamp_utc().replace('Z', '+00:00'))

    if not _frame_validate_l1_data_in_madaSeed(mada_seed_input):
        error_detail_msg = "Invalid or incomplete L1 data in input madaSeed for L2 processing."
        log_critical_error("frame_click_process L1 Data Error", {"trace_id": mada_seed_input.seed_id if mada_seed_input else "Unknown", "error": error_detail_msg})
        
        # Update L2 trace and content with error state
        if mada_seed_input: # Ensure mada_seed_input is not None before trying to update
            mada_seed_input.trace_metadata.L2_trace = L2Trace(
                version_L2_trace_schema="0.1.0", sop_name="lC.SOP.frame_click",
                completion_timestamp_L2=current_time_fail_dt,
                epistemic_state_L2=L2EpistemicStateOfFramingEnum.LCL_FAILURE_INTERNAL_L2,
                error_detail=error_detail_msg
            )
            # Update L2 content part
            mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L2_frame_type_obj = L2FrameTypeObj(
                version="0.1.2", 
                L2_epistemic_state_of_framing=L2EpistemicStateOfFramingEnum.LCL_FAILURE_INTERNAL_L2, 
                error_details=f"L2 aborted: {error_detail_msg}"
            )
        return mada_seed_input # Return modified madaSeed or original if None

    trace_id = mada_seed_input.seed_id
    l1_startle_context_obj = mada_seed_input.seed_content.L1_startle_reflex.L1_startle_context_obj
    # raw_signals = mada_seed_input.seed_content.raw_signals # Not directly used in MR logic for L2 helpers

    # Initialize L2_frame_type_obj with version, to be populated
    working_l2_frame_type_obj = L2FrameTypeObj(
        version="0.1.2",
        L2_epistemic_state_of_framing=L2EpistemicStateOfFramingEnum.LCL_FAILURE_INTERNAL_L2, # Default to error
        # Initialize other required fields to default/None if not immediately available
        input_class_L2=None,
        frame_type_L2=None,
        temporal_hint_L2=None,
        communication_context_L2=None,
        L2_validation_status_of_frame=None,
        L2_anomaly_flags_from_framing=[],
        L2_framing_confidence_score=None
    )
    
    try:
        # --- Step 2: Determine Communication Context ---
        # Conceptual: L1 might pass comms hints. For baseline, use L1 origin.
        conceptual_input_comm_context = {
            "source_agent_id_hint": None, # Could be derived from a session ID in L1 origin_hint
            "destination_agent_id_hint": trace_id, # Or a system agent UID
            "origin_env_hint": l1_startle_context_obj.input_origin_L1,
            "channel_hint": None # Could be part of origin_hint
        }
        comms_context_l2 = _frame_extract_communication_context_from_input(conceptual_input_comm_context)
        working_l2_frame_type_obj.communication_context_L2 = comms_context_l2
        
        # --- Prepare summary of L1 signal components ---
        components_summary_for_l2 = _frame_build_signal_components_summary_from_l1(l1_startle_context_obj)

        # --- Step 3: Classify Input ---
        input_class = _frame_classify_input(
            components_summary_for_l2, 
            l1_startle_context_obj.input_origin_L1, 
            comms_context_l2.interaction_channel_L2
        )
        working_l2_frame_type_obj.input_class_L2 = input_class
        
        # --- Step 4: Initial Checks (Size/Noise) ---
        initial_check_status, anomaly_flags = _frame_initial_checks(components_summary_for_l2)
        working_l2_frame_type_obj.L2_anomaly_flags_from_framing = anomaly_flags
        # This status is more of an intermediate one for the MR logic.
        # The final validation status is set by _frame_validate_structure.
        
        final_l2_epistemic_state = L2EpistemicStateOfFramingEnum.FRAMED # Assume success if all goes well
        determined_frame_type_l2: Optional[str] = None
        determined_temporal_hint_l2: Optional[TemporalHintL2] = None
        final_validation_status_of_frame = L2ValidationStatusOfFrameEnum.FAILURE_NOSTRUCTUREDETECTED # Default

        if initial_check_status == L2ValidationStatusOfFrameEnum.FAILURE_SIZEORNOISE:
            final_l2_epistemic_state = L2EpistemicStateOfFramingEnum.LCL_FAILURE_SIZENOISE
            final_validation_status_of_frame = L2ValidationStatusOfFrameEnum.FAILURE_SIZEORNOISE
        else:
            # --- Step 5-7: Structure Validation/Pattern/Ambiguity -> Determine frame_type_L2 ---
            primary_media_hint = components_summary_for_l2.get('primary_component_media_type_hint')
            determined_frame_type_l2_candidate, validation_status_from_struct = _frame_validate_structure(input_class, primary_media_hint)
            final_validation_status_of_frame = validation_status_from_struct

            if validation_status_from_struct != L2ValidationStatusOfFrameEnum.SUCCESS_FRAMED:
                final_l2_epistemic_state = L2EpistemicStateOfFramingEnum.LCL_CLARIFY_STRUCTURE # Default LCL
                if validation_status_from_struct == L2ValidationStatusOfFrameEnum.FAILURE_AMBIGUOUSSTRUCTURE: # Conceptual, not baseline
                    final_l2_epistemic_state = L2EpistemicStateOfFramingEnum.LCL_FAILURE_AMBIGUOUSFRAME
            else:
                determined_frame_type_l2 = determined_frame_type_l2_candidate
                # --- Step 8: Temporal Hint Extraction ---
                # primary_raw_signal_ref = mada_seed_input.seed_content.raw_signals[0].raw_input_id if mada_seed_input.seed_content.raw_signals else None
                # L1 trace_creation_time_L1 is already a datetime object
                determined_temporal_hint_l2 = _frame_extract_temporal_hint_l2(
                    determined_frame_type_l2, 
                    l1_startle_context_obj.trace_creation_time_L1, 
                    None # primary_raw_signal_ref - Not needed for baseline
                )
                # --- Step 9: Determine Final Outcome (Success Case) ---
                final_l2_epistemic_state = L2EpistemicStateOfFramingEnum.FRAMED
        
        working_l2_frame_type_obj.frame_type_L2 = determined_frame_type_l2
        working_l2_frame_type_obj.temporal_hint_L2 = determined_temporal_hint_l2
        working_l2_frame_type_obj.L2_epistemic_state_of_framing = final_l2_epistemic_state
        working_l2_frame_type_obj.L2_validation_status_of_frame = final_validation_status_of_frame
        
        # Baseline confidence for successful framing
        if final_l2_epistemic_state == L2EpistemicStateOfFramingEnum.FRAMED:
            working_l2_frame_type_obj.L2_framing_confidence_score = 0.7 
        else:
            working_l2_frame_type_obj.L2_framing_confidence_score = 0.3


        # --- Update madaSeed object with L2 contributions ---
        mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L2_frame_type_obj = working_l2_frame_type_obj

        # --- Populate L2_trace ---
        current_time_l2_final_dt = dt.fromisoformat(_frame_get_current_timestamp_utc().replace('Z', '+00:00'))
        l2_trace_obj = L2Trace(
            version_L2_trace_schema="0.1.0", 
            sop_name="lC.SOP.frame_click", 
            completion_timestamp_L2=current_time_l2_final_dt,
            epistemic_state_L2=final_l2_epistemic_state,
            L2_input_class_determined_in_trace=working_l2_frame_type_obj.input_class_L2,
            L2_frame_type_determined_in_trace=working_l2_frame_type_obj.frame_type_L2,
            L2_validation_status_in_trace=working_l2_frame_type_obj.L2_validation_status_of_frame,
            L2_temporal_hint_provenance_in_trace=working_l2_frame_type_obj.temporal_hint_L2.provenance if working_l2_frame_type_obj.temporal_hint_L2 else None,
            L2_communication_context_summary={ # Example summary
                "source_agent_uid_hint": comms_context_l2.source_agent_uid_L2,
                "destination_agent_uid_hint": comms_context_l2.destination_agent_uid_L2
            } if comms_context_l2 else None,
            L2_anomaly_flags_count=len(working_l2_frame_type_obj.L2_anomaly_flags_from_framing or [])
        )
        mada_seed_input.trace_metadata.L2_trace = l2_trace_obj
        
        return mada_seed_input

    except Exception as critical_process_error:
        error_msg = f"Critical L2 Failure: {str(critical_process_error)}"
        log_critical_error("Frame Click Process Failed Critically", {"trace_id": trace_id, "error": error_msg})
        
        current_time_crit_fail_dt = dt.fromisoformat(_frame_get_current_timestamp_utc().replace('Z', '+00:00'))
        
        mada_seed_input.trace_metadata.L2_trace = L2Trace(
             version_L2_trace_schema="0.1.0", sop_name="lC.SOP.frame_click",
             completion_timestamp_L2=current_time_crit_fail_dt, 
             epistemic_state_L2=L2EpistemicStateOfFramingEnum.LCL_FAILURE_INTERNAL_L2,
             error_detail=error_msg
        )
        mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L2_frame_type_obj = L2FrameTypeObj(
            version="0.1.2", 
            L2_epistemic_state_of_framing=L2EpistemicStateOfFramingEnum.LCL_FAILURE_INTERNAL_L2, 
            error_details=error_msg
        )
        return mada_seed_input


if __name__ == '__main__':
    from sop_l1_startle import startle_process # Assuming sop_l1_startle.py is in the same directory

    print("--- Running sop_l2_frame_click.py example ---")

    # 1. Create a MadaSeed using startle_process (from L1)
    example_input_event_text = {
        "reception_timestamp_utc_iso": "2023-10-28T09:00:00Z",
        "origin_hint": "User_CLI_Input",
        "data_components": [
            {"role_hint": "primary_prompt", "content_handle_placeholder": "This is a simple text prompt.", "size_hint": 30, "type_hint": "text/plain"}
        ]
    }
    l1_mada_seed = startle_process(example_input_event_text)
    print("\nL1 MadaSeed (startle_process output):")
    # print(l1_mada_seed.json(indent=2, exclude_none=True))

    # 2. Pass the L1 MadaSeed to frame_click_process
    print("\nCalling frame_click_process with L1 MadaSeed...")
    l2_mada_seed = frame_click_process(l1_mada_seed)
    
    print("\nL2 MadaSeed (frame_click_process output):")
    # print(l2_mada_seed.json(indent=2, exclude_none=True)) # Pydantic v2: by_alias=True, exclude_none=True
    
    # Verify L2 specific fields
    if l2_mada_seed:
        print(f"\nL2 Frame Type Object Version: {l2_mada_seed.seed_content.L1_startle_reflex.L2_frame_type.L2_frame_type_obj.version}")
        print(f"L2 Epistemic State of Framing: {l2_mada_seed.seed_content.L1_startle_reflex.L2_frame_type.L2_frame_type_obj.L2_epistemic_state_of_framing}")
        print(f"L2 Determined Frame Type: {l2_mada_seed.seed_content.L1_startle_reflex.L2_frame_type.L2_frame_type_obj.frame_type_L2}")
        print(f"L2 Input Class: {l2_mada_seed.seed_content.L1_startle_reflex.L2_frame_type.L2_frame_type_obj.input_class_L2}")
        if l2_mada_seed.seed_content.L1_startle_reflex.L2_frame_type.L2_frame_type_obj.temporal_hint_L2:
            print(f"L2 Temporal Hint Value: {l2_mada_seed.seed_content.L1_startle_reflex.L2_frame_type.L2_frame_type_obj.temporal_hint_L2.value}")
            print(f"L2 Temporal Hint Provenance: {l2_mada_seed.seed_content.L1_startle_reflex.L2_frame_type.L2_frame_type_obj.temporal_hint_L2.provenance}")

        print(f"\nL2 Trace Version: {l2_mada_seed.trace_metadata.L2_trace.version_L2_trace_schema}")
        print(f"L2 Trace SOP Name: {l2_mada_seed.trace_metadata.L2_trace.sop_name}")
        print(f"L2 Trace Epistemic State: {l2_mada_seed.trace_metadata.L2_trace.epistemic_state_L2}")

    # Example with a different input type for frame_click
    example_input_event_json = {
        "reception_timestamp_utc_iso": "2023-10-28T09:05:00Z",
        "origin_hint": "API_System_Event",
        "data_components": [
            {"role_hint": "event_data", "content_handle_placeholder": {"event_id": "evt123", "payload": "data"}, "size_hint": 100, "type_hint": "application/json"}
        ]
    }
    l1_mada_seed_json = startle_process(example_input_event_json)
    print("\nCalling frame_click_process with L1 MadaSeed (JSON input)...")
    l2_mada_seed_json = frame_click_process(l1_mada_seed_json)
    print(f"L2 Determined Frame Type (JSON): {l2_mada_seed_json.seed_content.L1_startle_reflex.L2_frame_type.L2_frame_type_obj.frame_type_L2}")
    print(f"L2 Input Class (JSON): {l2_mada_seed_json.seed_content.L1_startle_reflex.L2_frame_type.L2_frame_type_obj.input_class_L2}")


    # Example of L1 failure leading to L2 not processing deeply
    example_input_event_l1_fail = {
        "reception_timestamp_utc_iso": None, # This will cause L1 to fail
        "origin_hint": "Test_L1_Fail",
         "data_components": []
    }
    l1_mada_seed_failed = startle_process(example_input_event_l1_fail)
    print("\nCalling frame_click_process with FAILED L1 MadaSeed...")
    l2_mada_seed_after_l1_fail = frame_click_process(l1_mada_seed_failed)
    print(f"L2 Trace Epistemic State (after L1 fail): {l2_mada_seed_after_l1_fail.trace_metadata.L2_trace.epistemic_state_L2}")
    print(f"L2 Trace Error Detail: {l2_mada_seed_after_l1_fail.trace_metadata.L2_trace.error_detail}")


    print("\n--- sop_l2_frame_click.py example run complete ---")
