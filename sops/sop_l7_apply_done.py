import json # Added for ADK query serialization
from datetime import datetime as dt, timezone
from typing import List, Dict, Tuple, Any, Optional

from ..schemas.mada_schema import (
    MadaSeed, L6ReflectionPayloadObj, L6Trace,
    L7EncodedApplication, L7Trace, SeedQAQC, IntegrityFinding, SeedOutputItem, L7Backlog, PBIEntry, AlignmentVector,
    L7EpistemicStateEnum, SeedIntegrityStatusEnum, QAQCCheckCategoryCodeEnum, QAQCSeverityLevelEnum,
    L7OutputConsumerTypeEnum, L7OutputModalityEnum, L7PbiTypeEnum, L7TemporalPlaneEnum, L7DimensionalPlaneEnum,
    PayloadMetadataTarget, ConsumerTypeEnum
)
# The next line was duplicated and corrected, ensure only one import for mada_schema components
# from ..schemas.mada_schema import MadaSeed, L6ReflectionPayloadObj, L6Trace, L7EncodedApplication, L7Trace as L7TraceModel, SeedQAQC, IntegrityFinding, SeedOutputItem, L7Backlog, PBIEntry, AlignmentVector, L7EpistemicStateEnum, SeedIntegrityStatusEnum, QAQCCheckCategoryCodeEnum, QAQCSeverityLevelEnum, L7OutputConsumerTypeEnum, L7OutputModalityEnum, L7PbiTypeEnum, L7TemporalPlaneEnum, L7DimensionalPlaneEnum, PayloadMetadataTarget # Ensure all models are imported via relative path
from ..services.mock_lc_core_services import mock_lc_gov_core_get_policy
from ....lc_adk_agent.main import process_with_lc_core_tool # Added for ADK agent

# Basic logging function placeholder
def log_internal_error(helper_name: str, error_info: Dict):
    print(f"ERROR in {helper_name}: {error_info}")

def log_internal_warning(helper_name: str, warning_info: Dict):
    print(f"WARNING in {helper_name}: {warning_info}")

def log_internal_info(helper_name: str, info: Dict):
    print(f"INFO in {helper_name}: {info}")

def log_critical_error(process_name: str, error_info: Dict):
    print(f"CRITICAL ERROR in {process_name}: {error_info}")

# --- Internal Helper Function Definitions ---

def _apply_validate_l6_input(mada_seed_input: MadaSeed) -> bool:
    """Validates L6 data within the MadaSeed."""
    try:
        if not mada_seed_input:
            log_internal_warning("Helper:_apply_validate_l6_input", {"error": "Input madaSeed is None"})
            return False
        
        # Access L6 reflection payload object
        l6_payload_obj = mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L6_reflection_payload.L6_reflection_payload_obj
        l6_trace = mada_seed_input.trace_metadata.L6_trace

        if not l6_payload_obj or not l6_payload_obj.version: # Check if it exists and has a version
            log_internal_warning("Helper:_apply_validate_l6_input", {"error": "Missing or invalid L6_reflection_payload_obj in madaSeed for L7"})
            return False
        if not l6_trace or not l6_trace.epistemic_state_L6: # Check if L6 trace exists and has a state
            log_internal_warning("Helper:_apply_validate_l6_input", {"error": "Missing or invalid L6_trace in madaSeed for L7"})
            return False
        # Check if L6 state is suitable for L7 processing
        if l6_trace.epistemic_state_L6.name.startswith("LCL_"):
            log_internal_info("Helper:_apply_validate_l6_input", {"reason": f"L6 state '{l6_trace.epistemic_state_L6.name}' indicates LCL, may not be suitable for standard L7 processing."})
            # Depending on policy, this might still be true if L7 handles certain LCLs
    except AttributeError as e:
        log_internal_warning("Helper:_apply_validate_l6_input", {"error": f"AttributeError validating L6 data: {str(e)}"})
        return False
    except Exception as e:
        log_internal_warning("Helper:_apply_validate_l6_input", {"error": f"Exception validating L6 data: {str(e)}"})
        return False
    return True

def _apply_get_current_timestamp_utc() -> str:
    """Returns a fixed, unique timestamp string."""
    return "2023-10-28T03:00:00Z"

def _apply_resolve_l7_policies(l6_reflection_payload: L6ReflectionPayloadObj) -> Dict[str, str]:
    """Baseline: Returns default policy references, now fetched via mock_lc_gov_core_get_policy."""
    # Define default policy structures to pass to the mock if not found in mock_policy_store
    default_action_selection_policy = {"name": "L7_ActionSelection_Default_v1.0", "default_action": "LogAuditRecord_L7_From_Default_In_Helper"}
    default_capability_check_policy = {"name": "L7_CapabilityCheck_Default_v1.0", "capabilities_required": ["baseline_logging", "baseline_mada_access"]}
    default_lcl_handling_policy = {"name": "L7_LCLHandling_Default_v1.0", "default_lcl_action": "Escalate_To_Admin_Default"}
    default_seed_qa_qc_policy = {"name": "L7_SeedQAQC_Default_v1.0", "min_required_layers_complete": 6, "max_warnings_allowed": 5}
    default_final_state_policy = {"name": "L7_FinalStatePrecedence_Default_v1.0", "precedence": ["L7ActionLCL", "SeedIntegrityLCL", "L7ActionSuccess"]}

    resolved_policies = {
        "action_selection_policy_ref": mock_lc_gov_core_get_policy("L7_ActionSelection_Default_v1.0", default_policy=default_action_selection_policy),
        "capability_check_policy_ref": mock_lc_gov_core_get_policy("L7_CapabilityCheck_Default_v1.0", default_policy=default_capability_check_policy),
        "lcl_handling_policy_ref": mock_lc_gov_core_get_policy("L7_LCLHandling_Default_v1.0", default_policy=default_lcl_handling_policy),
        "seed_qa_qc_policy_ref": mock_lc_gov_core_get_policy("L7_SeedQAQC_Default_v1.0", default_policy=default_seed_qa_qc_policy),
        "final_state_precedence_policy_ref": mock_lc_gov_core_get_policy("L7_FinalStatePrecedence_Default_v1.0", default_policy=default_final_state_policy)
    }
    return resolved_policies

def _apply_resolve_l7_intent_and_capabilities(l6_reflection_payload: L6ReflectionPayloadObj, l7_policies: Dict[str, Any]) -> Tuple[str, PayloadMetadataTarget, str, bool]: # Changed l7_target type hint
    """Extracts intent from L6, assumes L7 capabilities are met."""
    payload_meta = l6_reflection_payload.payload_metadata
    l7_intent = payload_meta.presentation_intent if payload_meta else "Default_L7_Action_Intent"
    
    # Use Pydantic model for l7_target
    # Assuming L7OutputConsumerTypeEnum.SYSTEM_LOG_L7 is compatible with PayloadMetadataTarget.consumer_type which is ConsumerTypeEnum
    # This might require ensuring ConsumerTypeEnum includes all values from L7OutputConsumerTypeEnum or a mapping.
    # For now, we'll cast assuming SYSTEM_LOG_L7 is a valid ConsumerTypeEnum string value.
    default_consumer_type_str = L7OutputConsumerTypeEnum.SYSTEM_LOG_L7.value 
    l7_target_model = payload_meta.presentation_target if payload_meta and payload_meta.presentation_target else PayloadMetadataTarget(consumer_type=default_consumer_type_str)
    
    action_category_hint = "Generic_Processing_L7"
    if "Summarize" in l7_intent or "Display" in l7_intent : action_category_hint = "Generate_Output_L7"
    elif "Update" in l7_intent: action_category_hint = "Update_MADA_L7"
    elif "Log" in l7_intent: action_category_hint = "Log_Event_L7"
    elif "ProcessWithADKAgent" in l7_intent: action_category_hint = "Invoke_ADK_Agent_L7" # Added for ADK intent
    
    capabilities_ok = True # Baseline: Assume capabilities are met
    return l7_intent, l7_target_model, action_category_hint, capabilities_ok # Return model

def _apply_select_action_path_and_params(l7_intent: str, l7_target: PayloadMetadataTarget, action_category_hint: str, l6_reflection_payload: L6ReflectionPayloadObj, l7_policies: Dict[str, Any], l7_action_intent_override: Optional[str] = None) -> Dict[str, Any]: # Added l7_action_intent_override
    """Selects an action. If target is Google Assistant or ADK Agent, prioritizes specific plans."""
    selected_plan: Dict[str, Any] = {"forked_execution_flag": False}
    l5_cynefin_domain_name = "Unknown"
    if l6_reflection_payload.reflection_surface and l6_reflection_payload.reflection_surface.assessed_cynefin_state:
        l5_cynefin_domain_name = l6_reflection_payload.reflection_surface.assessed_cynefin_state.domain.name

    # Priority for explicit override
    if l7_action_intent_override == "ProcessWithADKAgent":
        selected_plan['primary_action_type'] = "InvokeADKAgent_L7"
        selected_plan['application_function_to_call'] = "lC.SOP.apply_done.InvokeADKAgent"
        selected_plan['target_or_parameters_summary'] = {"input_source_hint": "L6_Reflection_Payload_Content"}
    # Then check the resolved l7_intent or action_category_hint
    elif l7_intent == "ProcessWithADKAgent" or action_category_hint == "Invoke_ADK_Agent_L7":
        selected_plan['primary_action_type'] = "InvokeADKAgent_L7"
        selected_plan['application_function_to_call'] = "lC.SOP.apply_done.InvokeADKAgent"
        selected_plan['target_or_parameters_summary'] = {"input_source_hint": "L6_Reflection_Payload_Content"}
    elif l7_target and l7_target.consumer_type == ConsumerTypeEnum.GOOGLE_ASSISTANT_USER:
        selected_plan['primary_action_type'] = "GenerateAssistantResponse_L7"
        selected_plan['application_function_to_call'] = "lC.SOP.apply_done.GenerateAssistantResponse" # Conceptual
        selected_plan['target_or_parameters_summary'] = {
            "content_source_hint": "L6_Payload_Reflection_Summary", 
            "output_modality_target": "SPEECH_TEXT" 
        }
    elif action_category_hint == "Generate_Output_L7":
        selected_plan['primary_action_type'] = "PresentOutput_L7_Action"
        selected_plan['application_function_to_call'] = "lC.SOP.apply_done.PresentOutput" # Conceptual path
        selected_plan['target_or_parameters_summary'] = {"content_source": "L6_Payload_Content", "target_consumer_hint": l7_target.model_dump()} # Use model_dump for Pydantic
    else: # Default to logging
        selected_plan['primary_action_type'] = "LogAuditRecord_L7_Action"
        selected_plan['application_function_to_call'] = "lC.SOP.apply_done.LogAuditRecord"
        selected_plan['target_or_parameters_summary'] = {"event_details": f"L7 processed trace with intent '{l7_intent}' for target '{l7_target.consumer_type.value if l7_target.consumer_type else 'Unknown'}'. L5 Cynefin: {l5_cynefin_domain_name}", "severity": "Info"}
    return selected_plan

def _apply_execute_l7_action(action_plan: Dict[str, Any], trace_id: str, l6_reflection_payload: L6ReflectionPayloadObj) -> Dict[str, Any]:
    """Simulates action execution, returns mock outcome with "Success" status."""
    action_id = action_plan.get('primary_action_type', 'UnknownAction_L7') + "_" + trace_id[-6:] # Ensure trace_id is string
    current_time_str = _apply_get_current_timestamp_utc()
    outcome: Dict[str, Any] = {
        "action_id": action_id,
        "action_description": action_plan.get('primary_action_type'),
        "status": "Failure", # Default to failure, specific actions set to Success
        "result_payload_summary": {"message": f"Action {action_id} did not execute as expected."},
        "error_code": "L7_EXEC_UNKNOWN_ACTION",
        "error_message": "The planned action type was not recognized for execution.",
        "completion_timestamp": current_time_str
    }

    if action_plan.get('primary_action_type') == "LogAuditRecord_L7_Action":
        outcome['status'] = "Success"
        outcome['result_payload_summary'] = {"message": f"Audit log for {action_id} recorded successfully."}
        outcome['error_code'] = None
        outcome['error_message'] = None
    elif action_plan.get('primary_action_type') == "PresentOutput_L7_Action":
        outcome['status'] = "Success"
        outcome['result_payload_summary'] = {"message": f"Output for {action_id} presented."}
        outcome['error_code'] = None
        outcome['error_message'] = None
    elif action_plan.get('primary_action_type') == "GenerateAssistantResponse_L7":
        l6_content_summary = "Default summary from L6 for Assistant."
        if l6_reflection_payload.payload_content and l6_reflection_payload.payload_content.formatted_text:
             l6_content_summary = l6_reflection_payload.payload_content.formatted_text
        elif l6_reflection_payload.payload_content and l6_reflection_payload.payload_content.structured_data:
             l6_content_summary = str(l6_reflection_payload.payload_content.structured_data) # Fallback to stringified dict

        outcome['status'] = "Success"
        outcome['result_payload_summary'] = {
            "generated_response_text": f"Assistant Response: {l6_content_summary}",
            "modality_used": "SPEECH_TEXT" # Matches what _apply_select_action_path_and_params set
        }
        outcome['error_code'] = None
        outcome['error_message'] = None
    elif action_plan.get('primary_action_type') == "InvokeADKAgent_L7":
        query_string_for_adk = "No specific text content from L6." # Default
        if l6_reflection_payload.payload_content:
            if l6_reflection_payload.payload_content.formatted_text:
                query_string_for_adk = l6_reflection_payload.payload_content.formatted_text
            elif l6_reflection_payload.payload_content.structured_data:
                try:
                    query_string_for_adk = json.dumps(l6_reflection_payload.payload_content.structured_data)
                except (TypeError, OverflowError) as json_err:
                    log_internal_warning("_apply_execute_l7_action (ADK Query Prep)", {"error": f"Failed to serialize L6 structured_data for ADK query: {json_err}. Using default query."})
        
        log_internal_info("_apply_execute_l7_action (ADK Query Prep)", {"adk_query": query_string_for_adk[:200] + "..." if query_string_for_adk else "None"})

        try:
            adk_result_str = process_with_lc_core_tool(user_query=query_string_for_adk)
            outcome['status'] = "Success"
            outcome['result_payload_summary'] = {"adk_agent_response": adk_result_str}
            outcome['error_code'] = None
            outcome['error_message'] = None
            log_internal_info("_apply_execute_l7_action (ADK Call)", {"action_id": action_id, "status": "Success", "response_summary": adk_result_str[:100] + "..." if adk_result_str else "None"})
        except Exception as adk_err:
            error_msg = f"ADK Agent call failed: {str(adk_err)}"
            log_internal_error("_apply_execute_l7_action (ADK Call)", {"action_id": action_id, "error": error_msg})
            outcome['status'] = "Failure"
            outcome['result_payload_summary'] = {"message": f"Action {action_id} failed during ADK agent execution."}
            outcome['error_code'] = "L7_ADK_AGENT_EXECUTION_FAILURE"
            outcome['error_message'] = error_msg
        
    return outcome

def _apply_capture_and_record_outcome(executed_action_outcome: Dict[str, Any], l7_policies: Dict[str, Any]) -> Tuple[str, Optional[str], Dict[str, Any]]: # Changed l7_policies type
    """Determines L7 action LCL state (baseline: "Success", no LCL)."""
    action_status = executed_action_outcome.get('status', 'Failure')
    final_action_status_str = "Success"
    lcl_trigger_str: Optional[str] = None

    if action_status != "Success":
        final_action_status_str = "LCL-Apply-ExecutionFailure" # Example LCL state
        lcl_trigger_str = "LCL-Apply-ExecutionFailure"
        
    action_outcome_record_for_receipt = { # This is for the array item in L7EncodedApplication.action_outcomes
        "action_id": executed_action_outcome.get('action_id'),
        "action_description": executed_action_outcome.get('action_description'),
        "status": executed_action_outcome.get('status'), # Direct status from execution
        "result_payload_summary": executed_action_outcome.get('result_payload_summary'),
        "error_code": executed_action_outcome.get('error_code'),
        "error_message": executed_action_outcome.get('error_message'),
        "completion_timestamp": executed_action_outcome.get('completion_timestamp')
    }
    return final_action_status_str, lcl_trigger_str, action_outcome_record_for_receipt

def _apply_assemble_initial_l7_encoded_application(trace_id: str, l6_reflection_payload: L6ReflectionPayloadObj, l7_intent: str, action_plan_summary: Dict[str, Any], action_outcome_records: List[Dict[str, Any]]) -> L7EncodedApplication:
    """Assembles the L7EncodedApplication object (v"0.1.1") with empty L7_backlog and one SeedOutput item."""
    
    # Baseline L7Backlog (empty)
    l7_backlog_obj = L7Backlog(
        version="0.1.0", 
        single_loop=[], double_loop=[], triple_loop=[]
    )

    # Determine content and modality based on action outcome
    content_for_output: Any
    output_modality_enum_val: L7OutputModalityEnum
    target_consumer_hint_dict: Dict[str, Any]

    action_desc = action_outcome_records[0].get("action_description", "") if action_outcome_records else ""
    action_result_summary = action_outcome_records[0].get("result_payload_summary", {}) if action_outcome_records else {}

    # Determine content and modality based on action outcome
    if action_desc == "InvokeADKAgent_L7":
        adk_response = action_result_summary.get("adk_agent_response", "No response from ADK Agent.")
        content_for_output = f"ADK Agent Invoked. Response: {adk_response}" # Updated content for clarity
        output_modality_enum_val = L7OutputModalityEnum.FORMATTED_TEXT_MARKDOWN
        target_consumer_hint_dict = {"consumer_type": "System_Log_L7", "invoked_agent": "lc_adk_agent"}
    elif action_desc == "GenerateAssistantResponse_L7": 
        content_for_output = action_result_summary.get("generated_response_text", "Default Assistant response content.")
        output_modality_enum_val = L7OutputModalityEnum.SPEECH_TEXT 
        target_consumer_hint_dict = {"consumer_type": ConsumerTypeEnum.GOOGLE_ASSISTANT_USER.value}
    else:
        # Fallback to L6 content or generic message for other actions
        if l6_reflection_payload.payload_content and l6_reflection_payload.payload_content.formatted_text:
            content_for_output = l6_reflection_payload.payload_content.formatted_text
            output_modality_enum_val = L7OutputModalityEnum.FORMATTED_TEXT_MARKDOWN
        elif l6_reflection_payload.payload_content and l6_reflection_payload.payload_content.structured_data:
            content_for_output = l6_reflection_payload.payload_content.structured_data
            output_modality_enum_val = L7OutputModalityEnum.STRUCTURED_DATA_JSON
        else:
            content_for_output = action_result_summary if action_result_summary else {"message": "L7 action executed, no specific L6 content."}
            output_modality_enum_val = L7OutputModalityEnum.STRUCTURED_DATA_JSON
        
        # Default target consumer if not Google Assistant specific
        target_consumer_hint_dict = l6_reflection_payload.payload_metadata.presentation_target.model_dump() \
            if l6_reflection_payload.payload_metadata and l6_reflection_payload.payload_metadata.presentation_target \
            else {"consumer_type": L7OutputConsumerTypeEnum.SYSTEM_LOG_L7.value}


    seed_output_item = SeedOutputItem(
        output_UID=_apply_get_current_timestamp_utc().replace(":","").replace("-","").replace("T","").replace("Z","") + "_L7Output",
        target_consumer_hint=target_consumer_hint_dict,
        output_modality=output_modality_enum_val,
        content=content_for_output
    )

    return L7EncodedApplication(
        version_L7_payload="0.1.1",
        L7_backlog=l7_backlog_obj,
        seed_outputs=[seed_output_item]
    )

def _apply_perform_seed_integrity_qa_qc(assembled_mada_seed_obj_concept: MadaSeed, qa_qc_policy_ref: Dict[str, Any]) -> Tuple[str, List[IntegrityFinding]]: # Changed policy_ref type
    """Baseline: Returns "Valid_Complete" and a single informational IntegrityFinding."""
    report_details: List[IntegrityFinding] = []
    overall_status_str = SeedIntegrityStatusEnum.VALID_COMPLETE.value # String value for enum
    
    report_details.append(IntegrityFinding(
        finding_id="QAQC-L7-Baseline-001",
        check_category_code=QAQCCheckCategoryCodeEnum.OTHER_INTEGRITY_CHECK,
        target_layer_or_component="MadaSeed_Global",
        description_of_finding="Baseline L7 QA/QC: All conceptual checks passed.",
        severity_level=QAQCSeverityLevelEnum.INFO,
        applied_policy_ref_for_check=qa_qc_policy_ref
    ))
    return overall_status_str, report_details

def _apply_determine_final_trace_epistemic_state(l7_action_execution_status: str, l7_action_lcl_trigger: Optional[str], seed_integrity_final_status_str: str, precedence_policy_ref: str) -> str: # Returns L7EpistemicStateEnum string value
    """Baseline: Returns "Application_Successful_Seed_Valid" or adapts based on inputs."""
    # Convert string inputs to enums for comparison if they match enum names
    # This is a bit fragile if strings don't exactly match enum member names.
    # For robust solution, pass Enums or use a mapping.
    
    seed_integrity_enum = SeedIntegrityStatusEnum(seed_integrity_final_status_str)

    if seed_integrity_enum == SeedIntegrityStatusEnum.INVALID_LCL_LOOPBACK_TO_L6_REQUIRED:
        return L7EpistemicStateEnum.LCL_LOOPBACK_TO_L6.value
    if seed_integrity_enum == SeedIntegrityStatusEnum.INVALID_LCL_SEED_INCOMPLETE:
        return L7EpistemicStateEnum.LCL_SEED_INCOMPLETE.value
    
    if l7_action_lcl_trigger: # If L7 action itself had an LCL
        try: # Validate if it's a valid L7EpistemicStateEnum member
            return L7EpistemicStateEnum(l7_action_lcl_trigger).value
        except ValueError:
            return L7EpistemicStateEnum.LCL_APPLY_EXECUTIONFAILURE.value # Fallback LCL

    if l7_action_execution_status == "Success": # String from _apply_capture_and_record_outcome
        if seed_integrity_enum == SeedIntegrityStatusEnum.VALID_WITH_WARNINGS or \
           seed_integrity_enum == SeedIntegrityStatusEnum.VALID_WITH_WARNINGS_MINOR or \
           seed_integrity_enum == SeedIntegrityStatusEnum.VALID_WITH_WARNINGS_MODERATE:
            return L7EpistemicStateEnum.APPLICATION_SUCCESSFUL_SEED_WARNINGS.value
        return L7EpistemicStateEnum.APPLICATION_SUCCESSFUL_SEED_VALID.value
    
    elif l7_action_execution_status == "Partial_Success":
        if seed_integrity_enum == SeedIntegrityStatusEnum.VALID_WITH_WARNINGS or \
           seed_integrity_enum == SeedIntegrityStatusEnum.VALID_WITH_WARNINGS_MINOR or \
           seed_integrity_enum == SeedIntegrityStatusEnum.VALID_WITH_WARNINGS_MODERATE:
            return L7EpistemicStateEnum.APPLICATION_PARTIAL_SUCCESS_SEED_WARNINGS.value
        return L7EpistemicStateEnum.APPLICATION_PARTIAL_SUCCESS_SEED_VALID.value
        
    return L7EpistemicStateEnum.LCL_APPLY_EXECUTIONFAILURE.value # Default if action failed

def _apply_finalize_l7_trace_and_qa_qc(
    initial_l7_encoded_app: L7EncodedApplication, 
    seed_integrity_status_str: str, 
    seed_integrity_report_array: List[IntegrityFinding], 
    final_trace_state_str: str, # This is an L7EpistemicStateEnum string value
    l7_policies: Dict[str, Any], # Changed type
    current_time_str: str,
    l7_intent_resolved_str: str 
) -> Tuple[L7Trace, SeedQAQC]:
    """Prepares the L7Trace (v"0.1.0") and SeedQAQC (v"0.1.0") objects."""
    
    completion_timestamp_dt = dt.fromisoformat(current_time_str.replace('Z', '+00:00'))
    final_trace_state_enum = L7EpistemicStateEnum(final_trace_state_str)

    # Extract policy names for L7_applied_policy_refs, as the values are now dicts
    applied_policy_names = [policy.get("name", "UnknownPolicy") for policy_name_key, policy in l7_policies.items()]


    l7_trace_obj = L7Trace(
        version_L7_trace_schema="0.1.0", 
        sop_name="lC.SOP.apply_done",
        completion_timestamp_L7=completion_timestamp_dt,
        epistemic_state_L7=final_trace_state_enum,
        L7_application_intent_resolved=l7_intent_resolved_str, 
        summary_seed_integrity_status_from_receipt=SeedIntegrityStatusEnum(seed_integrity_status_str), 
        summary_outcome_confidence_from_receipt=0.7, 
        L7_summary_flags_for_orchestration={ 
            "action_completed_successfully": not final_trace_state_enum.name.startswith("LCL_APPLY"),
            "seed_integrity_passed_cleanly": seed_integrity_status_str == SeedIntegrityStatusEnum.VALID_COMPLETE.value,
            "critical_lcl_triggered_at_L7": final_trace_state_enum.name.startswith("LCL_")
        },
        L7_applied_policy_refs=applied_policy_names
    )

    seed_qa_qc_obj = SeedQAQC(
        version_seed_qa_qc_schema="0.1.0", 
        overall_seed_integrity_status=SeedIntegrityStatusEnum(seed_integrity_status_str), 
        qa_qc_assessment_timestamp=completion_timestamp_dt,
        integrity_findings=seed_integrity_report_array
    )
    return l7_trace_obj, seed_qa_qc_obj


# --- Main apply_done Process Function ---

def apply_done_process(mada_seed_input: MadaSeed, l7_action_intent_override: Optional[str] = None) -> MadaSeed: # Added l7_action_intent_override
    """
    Processes the madaSeed from L6 (reflect_boom) to perform L7 application and finalize the seed.
    Accepts an optional override for the L7 action intent.
    """
    current_time_str_for_all = _apply_get_current_timestamp_utc()
    current_time_dt_for_all = dt.fromisoformat(current_time_str_for_all.replace('Z', '+00:00'))

    # --- Phase 1: Application Execution (CE Categories 1.1 - 1.6) ---
    if not _apply_validate_l6_input(mada_seed_input):
        error_detail_msg = "Invalid or incomplete L6 data in input madaSeed for L7 processing."
        log_critical_error("apply_done_process L6 Data Error", {"trace_id": mada_seed_input.seed_id if mada_seed_input else "Unknown", "error": error_detail_msg})
        
        if mada_seed_input: # Ensure mada_seed_input is not None
            mada_seed_input.trace_metadata.L7_trace = L7Trace(
                version_L7_trace_schema="0.1.0", sop_name="lC.SOP.apply_done",
                completion_timestamp_L7=current_time_dt_for_all,
                epistemic_state_L7=L7EpistemicStateEnum.LCL_FAILURE_INTERNAL_L7,
                error_details=error_detail_msg
            )
            # Ensure L7_encoded_application exists with error state
            error_l7_app = L7EncodedApplication(version_L7_payload="0.1.1", L7_backlog=L7Backlog(version="0.1.0"), seed_outputs=[SeedOutputItem(output_UID="error", target_consumer_hint={}, output_modality=L7OutputModalityEnum.STRUCTURED_DATA_JSON, content={"error": "L7 Error due to invalid L6 input"})])
            mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L6_reflection_payload.L7_encoded_application = error_l7_app
            mada_seed_input.seed_QA_QC = SeedQAQC(version_seed_qa_qc_schema="0.1.0", overall_seed_integrity_status=SeedIntegrityStatusEnum.QA_QC_PROCESS_ERROR, qa_qc_assessment_timestamp=current_time_dt_for_all, error_details="L7 aborted: Invalid L6 input")
            mada_seed_input.seed_completion_timestamp = current_time_dt_for_all
        return mada_seed_input

    trace_id = mada_seed_input.seed_id
    # Correct path to L6 reflection payload object
    l6_reflection_payload = mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L6_reflection_payload.L6_reflection_payload_obj
    
    final_l7_epistemic_state_enum = L7EpistemicStateEnum.LCL_FAILURE_INTERNAL_L7 # Default
    
    try:
        active_l7_policies = _apply_resolve_l7_policies(l6_reflection_payload)

        resolved_intent, resolved_target, resolved_action_category, capabilities_met = _apply_resolve_l7_intent_and_capabilities(l6_reflection_payload, active_l7_policies)
        if not capabilities_met:
            final_l7_epistemic_state_enum = L7EpistemicStateEnum.LCL_APPLY_CAPABILITYMISMATCH
            raise ValueError(f"L7 Capability Mismatch for intent: {resolved_intent}")

        action_plan_for_l7 = _apply_select_action_path_and_params(resolved_intent, resolved_target, resolved_action_category, l6_reflection_payload, active_l7_policies, l7_action_intent_override) # Pass override
        executed_outcome_from_action = _apply_execute_l7_action(action_plan_for_l7, trace_id, l6_reflection_payload)
        l7_action_status_str, l7_action_lcl_trigger_str, l7_action_outcome_record = _apply_capture_and_record_outcome(executed_outcome_from_action, active_l7_policies)
        
        initial_l7_encoded_app_obj = _apply_assemble_initial_l7_encoded_application(trace_id, l6_reflection_payload, resolved_intent, action_plan_for_l7, [l7_action_outcome_record])
        
        # --- Phase 2: Seed Finalization ---
        # Note: We are modifying mada_seed_input directly, not creating a new conceptual object for QA
        
        seed_integrity_status_result_str, seed_integrity_report_details_result_list = _apply_perform_seed_integrity_qa_qc(mada_seed_input, active_l7_policies.get('seed_qa_qc_policy_ref', ''))
        
        final_l7_epistemic_state_str = _apply_determine_final_trace_epistemic_state(l7_action_status_str, l7_action_lcl_trigger_str, seed_integrity_status_result_str, active_l7_policies.get('final_state_precedence_policy_ref', ''))
        final_l7_epistemic_state_enum = L7EpistemicStateEnum(final_l7_epistemic_state_str)

        final_l7_trace_object, final_seed_qa_qc_object = _apply_finalize_l7_trace_and_qa_qc(
            initial_l7_encoded_app_obj, # Not strictly needed here as per MR, but passed for consistency
            seed_integrity_status_result_str, 
            seed_integrity_report_details_result_list, 
            final_l7_epistemic_state_str, 
            active_l7_policies,
            current_time_str_for_all, # Use consistent timestamp
            resolved_intent # Pass resolved_intent
        )
        
        # --- Update MadaSeed with L7 contributions ---
        mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L6_reflection_payload.L7_encoded_application = initial_l7_encoded_app_obj
        mada_seed_input.trace_metadata.L7_trace = final_l7_trace_object
        mada_seed_input.seed_QA_QC = final_seed_qa_qc_object
        mada_seed_input.seed_completion_timestamp = dt.fromisoformat(current_time_str_for_all.replace('Z', '+00:00'))

        # Conceptual: lC.MEM.CORE.store_final_mada_seed(trace_id, mada_seed_input)
        if final_l7_epistemic_state_enum == L7EpistemicStateEnum.LCL_LOOPBACK_TO_L6:
            log_internal_info("apply_done Loopback", {"trace_id": trace_id, "reason": "Seed Integrity requires L6 reprocessing."})
            # Conceptual: lC.EXE.PROC.requeue_for_layer(trace_id, target_layer="L6", context=mada_seed_input)
        
        return mada_seed_input

    except Exception as critical_process_error:
        error_msg = f"Critical L7 Failure: {str(critical_process_error)}"
        log_critical_error("apply_done Process Failed Critically", {"trace_id": trace_id, "error": error_msg})
        
        mada_seed_input.trace_metadata.L7_trace = L7Trace(
             version_L7_trace_schema="0.1.0", sop_name="lC.SOP.apply_done",
             completion_timestamp_L7=current_time_dt_for_all, 
             epistemic_state_L7=L7EpistemicStateEnum.LCL_FAILURE_INTERNAL_L7, # Use the default from init
             error_details=error_msg
        )
        # Ensure L7_encoded_application is set, even in error
        error_l7_app_critical = L7EncodedApplication(version_L7_payload="0.1.1", L7_backlog=L7Backlog(version="0.1.0"), seed_outputs=[SeedOutputItem(output_UID="critical_error", target_consumer_hint={}, output_modality=L7OutputModalityEnum.STRUCTURED_DATA_JSON, content={"error": error_msg})])
        mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L6_reflection_payload.L7_encoded_application = error_l7_app_critical
        
        # Ensure SeedQAQC is set, even in error
        mada_seed_input.seed_QA_QC = SeedQAQC(
            version_seed_qa_qc_schema="0.1.0",
            overall_seed_integrity_status=SeedIntegrityStatusEnum.QA_QC_PROCESS_ERROR,
            qa_qc_assessment_timestamp=current_time_dt_for_all,
            integrity_findings=[IntegrityFinding(finding_id="L7_CRITICAL_FAILURE", check_category_code=QAQCCheckCategoryCodeEnum.OTHER_INTEGRITY_CHECK, target_layer_or_component="L7_Process", description_of_finding=error_msg, severity_level=QAQCSeverityLevelEnum.ERROR_BLOCKING_INTEGRITY_REQUIRES_LCL)],
            error_details=error_msg
        )
        mada_seed_input.seed_completion_timestamp = current_time_dt_for_all
        return mada_seed_input

if __name__ == '__main__':
    from sop_l1_startle import startle_process
    from sop_l2_frame_click import frame_click_process
    from sop_l3_keymap_click import keymap_click_process
    from sop_l4_anchor_click import anchor_click_process
    from sop_l5_field_click import field_click_process
    from sop_l6_reflect_boom import reflect_boom_process
    import os # For PYTHONPATH manipulation if needed for testing ADK
    import sys # For PYTHONPATH manipulation

    print("--- Running sop_l7_apply_done.py example ---")

    example_input_event = {
        "reception_timestamp_utc_iso": "2023-11-02T04:00:00Z",
        "origin_hint": "Test_ApplyDone_Input",
        "data_components": [
            {"role_hint": "primary_text", "content_handle_placeholder": "Apply done test. Finalize this trace.", "size_hint": 40, "type_hint": "text/plain"}
        ]
    }
    l1_seed = startle_process(example_input_event)
    l2_seed = frame_click_process(l1_seed)
    l3_seed = keymap_click_process(l2_seed)
    l4_seed = anchor_click_process(l3_seed)
    l5_seed = field_click_process(l4_seed)
    l6_seed = reflect_boom_process(l5_seed)

    print(f"\nL6 Epistemic State: {l6_seed.trace_metadata.L6_trace.epistemic_state_L6.name if l6_seed.trace_metadata.L6_trace.epistemic_state_L6 else 'N/A'}")
    if l6_seed.trace_metadata.L6_trace.epistemic_state_L6.name.startswith("LCL_"):
         print("L6 processing resulted in LCL state, L7 test might reflect this.")

    print("\nCalling apply_done_process with L6 MadaSeed...")
    l7_final_seed = apply_done_process(l6_seed) # Standard call
    
    # print("\nL7 Final MadaSeed (apply_done_process output):")
    # print(l7_final_seed.json(indent=2, exclude_none=True))


    if l7_final_seed:
        l7_app_obj = l7_final_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L6_reflection_payload.L7_encoded_application
        print(f"\nL7 Encoded Application Version: {l7_app_obj.version_L7_payload}")
        if l7_app_obj.seed_outputs:
            print(f"L7 Seed Outputs Count: {len(l7_app_obj.seed_outputs)}")
            print(f"L7 First Seed Output Content (summary): {str(l7_app_obj.seed_outputs[0].content)[:100]}...")
        
        l7_trace_meta = l7_final_seed.trace_metadata.L7_trace
        print(f"\nL7 Trace Version: {l7_trace_meta.version_L7_trace_schema}")
        print(f"L7 Trace SOP Name: {l7_trace_meta.sop_name}")
        print(f"L7 Trace Epistemic State: {l7_trace_meta.epistemic_state_L7.name if l7_trace_meta.epistemic_state_L7 else 'N/A'}")
        
        seed_qaqc_obj = l7_final_seed.seed_QA_QC
        print(f"\nSeed QA/QC Version: {seed_qaqc_obj.version_seed_qa_qc_schema}")
        print(f"Seed QA/QC Overall Status: {seed_qaqc_obj.overall_seed_integrity_status.name if seed_qaqc_obj.overall_seed_integrity_status else 'N/A'}")
        if seed_qaqc_obj.integrity_findings:
            print(f"Seed QA/QC First Finding: {seed_qaqc_obj.integrity_findings[0].description_of_finding}")
            
        print(f"\nMadaSeed Completion Timestamp: {l7_final_seed.seed_completion_timestamp}")
        print(f"MadaSeed Final Version (Top Level): {l7_final_seed.version}")


    # Test L6 LCL pass-through effect on L7
    l6_seed_with_lcl = l6_seed.model_copy(deep=True) # Pydantic v2
    l6_seed_with_lcl.trace_metadata.L6_trace.epistemic_state_L6 = L6EpistemicStateEnum.LCL_PRESENTATION_FORMATERROR
    print("\nCalling apply_done_process with L6 MadaSeed (L6 LCL state)...")
    l7_final_seed_with_lcl = apply_done_process(l6_seed_with_lcl) # Standard call with LCL L6 seed
    if l7_final_seed_with_lcl:
        print(f"L7 Trace Epistemic State (after L6 LCL): {l7_final_seed_with_lcl.trace_metadata.L7_trace.epistemic_state_L7.name if l7_final_seed_with_lcl.trace_metadata.L7_trace.epistemic_state_L7 else 'N/A'}")
        # Expected: L7 might still complete, but QA/QC could reflect the upstream LCL.
        # The baseline _apply_perform_seed_integrity_qa_qc returns Valid_Complete but a real one would catch L6 LCL.
        # The _apply_determine_final_trace_epistemic_state might also change based on L6's LCL.
        # Current baseline _apply_validate_l6_input allows LCLs from L6 to pass to L7.
        # The _apply_perform_seed_integrity_qa_qc's baseline doesn't specifically look at L6 LCLs to fail L7.
        # So L7 will likely still show "Application_Successful_Seed_Valid" or "Warnings" due to QAQC.
        print(f"L7 Seed QA/QC Status (after L6 LCL): {l7_final_seed_with_lcl.seed_QA_QC.overall_seed_integrity_status.name if l7_final_seed_with_lcl.seed_QA_QC.overall_seed_integrity_status else 'N/A'}")

    # Test ADK Agent Intent Override
    # For this test to run, lc_adk_agent needs to be in PYTHONPATH.
    # This might require temporarily adding to sys.path if not installed.
    # Example: sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))) # Adjust based on actual structure
    print("\nCalling apply_done_process with L6 MadaSeed and ADK Intent Override...")
    l7_final_seed_with_adk_override = apply_done_process(l6_seed, l7_action_intent_override="ProcessWithADKAgent")
    if l7_final_seed_with_adk_override:
        print(f"L7 Trace Epistemic State (ADK Override): {l7_final_seed_with_adk_override.trace_metadata.L7_trace.epistemic_state_L7.name if l7_final_seed_with_adk_override.trace_metadata.L7_trace.epistemic_state_L7 else 'N/A'}")
        l7_app_obj_adk = l7_final_seed_with_adk_override.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L6_reflection_payload.L7_encoded_application
        if l7_app_obj_adk.seed_outputs:
            print(f"L7 First Seed Output Content (ADK Override): {str(l7_app_obj_adk.seed_outputs[0].content)[:200]}...")

        # --- Testing L7 with ADK Agent Invocation Override ---
        print("\n--- Testing L7 with ADK Agent Invocation Override ---")
        # Reuse l6_seed or create a similar one
        l6_seed_for_adk_test = l6_seed.model_copy(deep=True) # Start with a valid L6 seed

        # Ensure there's content for the ADK agent to process
        # Modify L6 payload content for a specific ADK query
        adk_query_text = "This is a specific query for the ADK agent from L7 SOP test."
        if l6_seed_for_adk_test.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L6_reflection_payload.L6_reflection_payload_obj.payload_content:
            l6_seed_for_adk_test.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L6_reflection_payload.L6_reflection_payload_obj.payload_content.formatted_text = adk_query_text
            l6_seed_for_adk_test.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L6_reflection_payload.L6_reflection_payload_obj.payload_metadata.presentation_intent = "QueryADKAgent"


        l7_final_seed_with_adk = apply_done_process(
            mada_seed_input=l6_seed_for_adk_test, 
            l7_action_intent_override="ProcessWithADKAgent" # Corrected parameter name
        )

        if l7_final_seed_with_adk:
            print(f"L7 Trace Epistemic State (ADK Test): {l7_final_seed_with_adk.trace_metadata.L7_trace.epistemic_state_L7.name if l7_final_seed_with_adk.trace_metadata.L7_trace.epistemic_state_L7 else 'N/A'}")
            l7_app_content = l7_final_seed_with_adk.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L6_reflection_payload.L7_encoded_application
            if l7_app_content and l7_app_content.seed_outputs:
                print("L7 Seed Outputs (ADK Test):")
                for i, output_item in enumerate(l7_app_content.seed_outputs):
                    print(f"  Output {i+1}:")
                    print(f"    UID: {output_item.output_UID}")
                    print(f"    Modality: {output_item.output_modality.name if output_item.output_modality else 'N/A'}")
                    print(f"    Target Consumer Hint: {output_item.target_consumer_hint}")
                    print(f"    Content: {str(output_item.content)[:200]}...") # Print first 200 chars of content
            else:
                print("No seed_outputs found in L7 application content for ADK test.")
        else:
            print("L7 process with ADK override returned None or an error.")
        
        print("\n--- End of L7 ADK Agent Invocation Test ---")


    print("\n--- sop_l7_apply_done.py example run complete ---")
