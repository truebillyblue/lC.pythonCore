import uuid
from datetime import datetime as dt, timezone
from typing import List, Dict, Any, AsyncGenerator, Optional, Tuple

from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

# Assuming mada_schema and original sop_l1_startle helpers will be accessible
# Option 1: If lc_python_core is structured as a proper package, use relative imports
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
    L2EpistemicStateOfFramingEnum,
    L4EpistemicStateOfAnchoringEnum,
    L5EpistemicStateOfFieldProcessingEnum,
    L6EpistemicStateEnum,
    L7EpistemicStateEnum,
    SeedIntegrityStatusEnum,
)
# Option 2: If you need to copy helper functions directly or adjust paths
# For now, let's assume they can be imported or will be moved/refactored.
# We might need to copy/adapt _startle_get_current_timestamp_utc, _startle_generate_crux_uid,
# _startle_process_input_components, _startle_create_initial_madaSeed_shell,
# and logging functions from the original sop_l1_startle.py.

# Placeholder for logging functions (can be adapted from sop_l1_startle.py)
def log_internal_error(helper_name: str, error_info: Dict):
    print(f"ADK_AGENT_ERROR in {helper_name}: {error_info}")

def log_internal_warning(helper_name: str, warning_info: Dict):
    print(f"ADK_AGENT_WARNING in {helper_name}: {warning_info}")

def log_critical_error(process_name: str, error_info: Dict):
    print(f"ADK_AGENT_CRITICAL_ERROR in {process_name}: {error_info}")

# Helper functions from sop_l1_startle.py (to be copied or imported)
# For this subtask, we will copy them directly into this file for simplicity.
# In a larger refactor, these might live in a shared 'utils' module.

def _startle_get_current_timestamp_utc() -> str:
    return dt.now(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z') # Use real time

def generate_system_uuidv4_primitive() -> uuid.UUID:
    return uuid.uuid4()

def format_uuid_as_hex(system_uuid: uuid.UUID) -> str:
    return system_uuid.hex

def _startle_generate_crux_uid(type_hint: str, context_hint: Dict) -> str:
    try:
        system_uuid = generate_system_uuidv4_primitive()
        crux_uid_string = "urn:crux:uid::" + format_uuid_as_hex(system_uuid)
        return crux_uid_string
    except Exception as e:
        log_internal_error("_startle_generate_crux_uid", {"type": type_hint, "context": context_hint, "error": str(e)})
        # Re-raise as ADK agent might handle it or log it via its own mechanisms
        raise Exception(f"ADK Agent: CRUX UID Generation Failed for {type_hint}")


def _startle_process_input_components(input_data_components: List[Dict], trace_id_for_context: str) -> Tuple[List[RawSignal], List[SignalComponentMetadataL1]]:
    raw_signals_for_madaSeed: List[RawSignal] = []
    signal_meta_for_L1_context: List[SignalComponentMetadataL1] = []

    if not input_data_components:
        log_internal_warning("_startle_process_input_components", {"warning": "No data_components found in input_event."})
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
        role_hint = component_event_data.get('role_hint', 'primary_content')
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
            elif type_hint_lower in ["application/octet-stream", "image/jpeg", "application/pdf"]:
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
    pending_l2_frame_obj = L2FrameTypeObj(version="0.1.2", L2_epistemic_state_of_framing=L2EpistemicStateOfFramingEnum.LCL_FAILURE_INTERNAL_L2, error_details="Pending_L2")
    pending_l3_keymap_obj = L3SurfaceKeymapObj(version="0.1.1", lexical_affordances={}, syntactic_hints={}, pragmatic_affective_affordances={}, relational_linking_markers={}, L3_flags={}, error_details="Pending_L3")
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
                L1_startle_context_obj=L1StartleContextObj(
                    version="0.0.0", 
                    L1_epistemic_state_of_startle=L1EpistemicStateOfStartleEnum.LCL_FAILURE_INTERNAL_L1,
                    trace_creation_time_L1=dt.fromisoformat(_startle_get_current_timestamp_utc().replace('Z', '+00:00')), 
                    signal_components_metadata_L1=[] 
                ), 
                L2_frame_type=L2FrameType( 
                    L2_frame_type_obj=pending_l2_frame_obj,
                    L3_surface_keymap=L3SurfaceKeymap( 
                        L3_surface_keymap_obj=pending_l3_keymap_obj,
                        L4_anchor_state=L4AnchorState( 
                            L4_anchor_state_obj=pending_l4_anchor_obj,
                            L5_field_state=L5FieldState( 
                                L5_field_state_obj=pending_l5_field_obj,
                                L6_reflection_payload=L6ReflectionPayload( 
                                    L6_reflection_payload_obj=pending_l6_reflection_payload_obj,
                                    L7_encoded_application=pending_l7_encoded_app 
                                )
                            )
                        )
                    )
                )
            )
        ),
        trace_metadata=TraceMetadata(
            trace_id=trace_id_val,
            L1_trace=L1Trace(
                version_L1_trace_schema="0.0.0", sop_name="lC.SOP.startle", 
                completion_timestamp_L1=dt.fromisoformat(_startle_get_current_timestamp_utc().replace('Z', '+00:00')), 
                epistemic_state_L1=L1EpistemicStateOfStartleEnum.LCL_FAILURE_INTERNAL_L1,
                L1_trace_creation_time_from_context=dt.fromisoformat(_startle_get_current_timestamp_utc().replace('Z', '+00:00')),
                L1_signal_component_count=0
            ), 
            L2_trace=L2Trace(version_L2_trace_schema="0.1.0", sop_name="lC.SOP.frame_click", completion_timestamp_L2=dt.fromisoformat(_startle_get_current_timestamp_utc().replace('Z', '+00:00')), epistemic_state_L2=L2EpistemicStateOfFramingEnum.LCL_FAILURE_INTERNAL_L2, error_detail="Pending_L2"),
            L3_trace=L3Trace(version_L3_trace_schema="0.1.0", sop_name="lC.SOP.keymap_click", completion_timestamp_L3=dt.fromisoformat(_startle_get_current_timestamp_utc().replace('Z', '+00:00')), epistemic_state_L3="Pending_L3"),
            L4_trace=L4Trace(version_L4_trace_schema="0.1.0", sop_name="lC.SOP.anchor_click", completion_timestamp_L4=dt.fromisoformat(_startle_get_current_timestamp_utc().replace('Z', '+00:00')), epistemic_state_L4=L4EpistemicStateOfAnchoringEnum.LCL_FAILURE_INTERNAL_L4, error_details="Pending_L4"),
            L5_trace=L5Trace(version_L5_trace_schema="0.1.0", sop_name="lC.SOP.field_click", completion_timestamp_L5=dt.fromisoformat(_startle_get_current_timestamp_utc().replace('Z', '+00:00')), epistemic_state_L5=L5EpistemicStateOfFieldProcessingEnum.LCL_FAILURE_INTERNAL_L5, error_details="Pending_L5"),
            L6_trace=L6Trace(version_L6_trace_schema="0.1.0", sop_name="lC.SOP.reflect_boom", completion_timestamp_L6=dt.fromisoformat(_startle_get_current_timestamp_utc().replace('Z', '+00:00')), epistemic_state_L6=L6EpistemicStateEnum.LCL_FAILURE_INTERNAL_L6, error_details="Pending_L6"),
            L7_trace=L7Trace(version_L7_trace_schema="0.1.1", sop_name="lC.SOP.apply_done", completion_timestamp_L7=dt.fromisoformat(_startle_get_current_timestamp_utc().replace('Z', '+00:00')), epistemic_state_L7=L7EpistemicStateEnum.LCL_FAILURE_INTERNAL_L7, error_details="Pending_L7")
        ),
        seed_QA_QC=SeedQAQC(version_seed_qa_qc_schema="0.1.0", overall_seed_integrity_status=SeedIntegrityStatusEnum.QA_QC_PROCESS_ERROR, qa_qc_assessment_timestamp=dt.fromisoformat(_startle_get_current_timestamp_utc().replace('Z', '+00:00')), error_details="Pending_L7_QA"),
        seed_completion_timestamp=None 
    )
    return shell

class StartleAgent(BaseAgent):
    def __init__(self, name: str = "StartleAgent", description: str = "ADK Agent for L1 Startle SOP"):
        super().__init__(name=name, description=description)

    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        print(f"[{self.name}] Starting Startle SOP execution via ADK.")
        
        input_event = ctx.session.state.get("input_event")
        if not input_event:
            log_critical_error(self.name, {"error": "input_event not found in session state."})
            # Potentially yield an error event or raise an exception
            # For now, just setting state and returning
            ctx.session.state["mada_seed_output"] = None
            ctx.session.state["trace_id"] = "ERROR_NO_INPUT_EVENT"
            # Yield a final event indicating failure if ADK expects one
            yield self.create_final_response_event(ctx, content={"error": "input_event not found"})
            return

        # This is the core logic from sop_l1_startle.startle_process
        try:
            current_time_init_fail_str = _startle_get_current_timestamp_utc()
            try:
                current_time_init_fail_dt = dt.fromisoformat(current_time_init_fail_str.replace('Z', '+00:00'))
            except ValueError: 
                current_time_init_fail_dt = dt.now(timezone.utc)

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
                signal_components_metadata_L1=[
                    SignalComponentMetadataL1(component_role_L1="placeholder_error", raw_signal_ref_uid_L1="ERROR_UID", encoding_status_L1=EncodingStatusL1Enum.UNKNOWN_L1)
                ]
            )
            
            # --- Original startle_process logic starts here ---
            if not input_event or input_event.get('reception_timestamp_utc_iso') is None:
                raise ValueError("Invalid Input: Missing reception_timestamp_utc_iso.")
            
            l1_trace_creation_time_str = input_event.get('reception_timestamp_utc_iso')
            l1_trace_creation_time_dt = dt.fromisoformat(l1_trace_creation_time_str.replace('Z', '+00:00'))
            
            l1_input_origin = input_event.get('origin_hint')
            input_components_data = input_event.get('data_components', [])

            generated_trace_id = _startle_generate_crux_uid("trace_event_L1", {"origin": l1_input_origin, "time": l1_trace_creation_time_str})
            raw_signals_for_seed, signal_components_meta_for_l1_payload = _startle_process_input_components(input_components_data, generated_trace_id)
            working_mada_seed = _startle_create_initial_madaSeed_shell(generated_trace_id, generated_trace_id, raw_signals_for_seed)
            
            l1_final_epistemic_state = L1EpistemicStateOfStartleEnum.STARTLE_COMPLETE_SIGNALREFS_GENERATED
            
            l1_startle_context_obj_payload = L1StartleContextObj(
                version="0.1.1",
                L1_epistemic_state_of_startle=l1_final_epistemic_state,
                trace_creation_time_L1=l1_trace_creation_time_dt,
                input_origin_L1=l1_input_origin,
                signal_components_metadata_L1=signal_components_meta_for_l1_payload
            )
            working_mada_seed.seed_content.L1_startle_reflex.L1_startle_context_obj = l1_startle_context_obj_payload
            
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
            
            mada_seed_output = working_mada_seed
            trace_id_output = generated_trace_id
            # --- Original startle_process logic ends here ---

        except Exception as critical_process_error:
            log_critical_error(f"{self.name} Process Failed Critically", {"input_origin": input_event.get('origin_hint') if input_event else "N/A", "error": str(critical_process_error)})
            
            error_detail_str = str(critical_process_error)
            if hasattr(error_seed_shell.trace_metadata.L1_trace, 'error_detail'):
                 error_seed_shell.trace_metadata.L1_trace.error_detail = error_detail_str
            
            generated_trace_id_before_fail = locals().get('generated_trace_id') # Check if trace_id was generated
            final_error_trace_id = generated_trace_id_before_fail if generated_trace_id_before_fail else "ERROR_TRACE_ID_RUNTIME"

            error_seed_shell.seed_id = final_error_trace_id
            error_seed_shell.trace_metadata.trace_id = final_error_trace_id
            
            if hasattr(error_seed_shell.seed_content.L1_startle_reflex.L1_startle_context_obj, 'error_details'):
                error_seed_shell.seed_content.L1_startle_reflex.L1_startle_context_obj.error_details = error_detail_str
            error_seed_shell.seed_content.L1_startle_reflex.L1_startle_context_obj.L1_epistemic_state_of_startle = L1EpistemicStateOfStartleEnum.LCL_FAILURE_INTERNAL_L1
            
            mada_seed_output = error_seed_shell
            trace_id_output = final_error_trace_id

        # Store results in session state
        ctx.session.state["mada_seed_output"] = mada_seed_output
        ctx.session.state["trace_id"] = trace_id_output
        
        print(f"[{self.name}] Startle SOP execution finished. Trace ID: {trace_id_output}")
        
        # Yield a final event. The content of this event can be structured as needed.
        # For now, just indicating completion and the trace_id.
        yield self.create_final_response_event(ctx, content={"status": "completed", "trace_id": trace_id_output})
