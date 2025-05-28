from datetime import datetime as dt, timezone
from typing import List, Dict, Tuple, Any, Optional

from ..schemas.mada_schema import ( # Corrected path
    MadaSeed, L4AnchorStateObj, L5FieldStateObj, L5Trace,
    FieldParticipant, ParticipantEngagementReadinessEnum, ParticipantInteractionStats,
    FieldTemporalContext,
    ActiveGovernance, DialogueContext, DialogueModeEnum, DissentStrengthEnum,
    AACFieldReadiness, AACSupportLevelEnum, DialogueStructureSupportEnum,
    MomentumProfile, AxisMomentum,
    WorkManagement,
    FieldRiskAssessment, RiskIndicator, LCLForecastForField,
    BraveSpaceDynamics, BraveSpaceActivationStatusEnum,
    FieldObjectives, SharedTarget,
    CurrentTraceSOPProvenance,
    FieldMaturity, IGDStageAssessmentEnum, # Renamed from SessionMaturity in schema
    DownstreamDirectives,
    L5EpistemicStateOfFieldProcessingEnum, FieldStatusEnum,
    # Enums for L4 validation
    L4EpistemicStateOfAnchoringEnum
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

# --- Internal Helper Function Definitions ---

def _field_validate_l4_data_in_madaSeed(mada_seed_input: MadaSeed) -> bool:
    """Validates essential L4 data presence within the input MadaSeed for L5 processing."""
    try:
        if not mada_seed_input:
            log_internal_warning("Helper:_field_validate_l4_data", {"error": "Input madaSeed is None"})
            return False

        l4_anchor_state_obj = mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L4_anchor_state_obj
        l4_trace = mada_seed_input.trace_metadata.L4_trace

        if not l4_anchor_state_obj or not l4_anchor_state_obj.version:
            log_internal_warning("Helper:_field_validate_l4_data", {"error": "Missing or invalid L4_anchor_state_obj in madaSeed for L5"})
            return False
        if not l4_trace or not l4_trace.epistemic_state_L4:
            log_internal_warning("Helper:_field_validate_l4_data", {"error": "Missing or invalid L4_trace in madaSeed for L5"})
            return False
        if not l4_trace.epistemic_state_L4.name.startswith("ANCHORED"): # ANCHORED, ANCHORED_WITH_GAPS, ANCHORED_LOW_ASSESSABILITY
            log_internal_info("Helper:_field_validate_l4_data", {"reason": f"L4 state '{l4_trace.epistemic_state_L4.name}' not suitable for L5 field processing."})
            return False
    except AttributeError as e:
        log_internal_warning("Helper:_field_validate_l4_data", {"error": f"AttributeError validating L4 data: {str(e)}"})
        return False
    except Exception as e:
        log_internal_warning("Helper:_field_validate_l4_data", {"error": f"Exception validating L4 data: {str(e)}"})
        return False
    return True

def _field_get_current_timestamp_utc() -> str:
    """Returns a fixed, unique timestamp string."""
    return "2023-10-28T10:45:00Z"

def _field_get_chain_id_from_madaSeed(mada_seed_input: MadaSeed) -> Optional[str]:
    """Extracts chain_id from L4 trace threading context, falling back to trace_id."""
    try:
        l4_anchor_state_obj = mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L4_anchor_state_obj
        if l4_anchor_state_obj.trace_threading_context and l4_anchor_state_obj.trace_threading_context.chain_id:
            return l4_anchor_state_obj.trace_threading_context.chain_id
        return mada_seed_input.seed_id # Fallback to trace_id (which is seed_id)
    except AttributeError:
        log_internal_warning("_field_get_chain_id_from_madaSeed", {"warning": "Could not access trace_threading_context or seed_id."})
        return mada_seed_input.seed_id # Fallback if attribute error deeper

def _field_load_or_init_field_state_obj(field_uid: str, mada_seed_input: MadaSeed) -> L5FieldStateObj:
    """
    Baseline: Always initializes a new L5FieldStateObj (version "0.2.0").
    Populates basic fields and initializes complex sub-fields with defaults.
    """
    current_time_dt = dt.fromisoformat(_field_get_current_timestamp_utc().replace('Z', '+00:00'))
    
    # Initialize complex sub-objects with their defaults if they are Pydantic models
    # Many of these have default_factory=list or dict in the schema, or are optional
    new_field_state_obj = L5FieldStateObj(
        version="0.2.0",
        l5_epistemic_state_of_field_processing=None, # Will be set later
        l5_field_processing_completion_time=None, # Will be set later
        overall_field_stability_score_hint=0.5, # Baseline
        field_instance_uid=field_uid,
        field_type="Default_Trace_Interaction_Field_L5",
        field_tags=["trace_driven", f"trace_{mada_seed_input.seed_id}"],
        field_topic_summary=f"Field context for trace {mada_seed_input.seed_id}",
        field_status=FieldStatusEnum.ACTIVE, # Baseline
        related_field_uids=[],
        field_temporal_context=FieldTemporalContext(field_creation_time=current_time_dt, field_last_activity_time=current_time_dt),
        field_participants=[], # Populated by _field_bind_participants
        interaction_pattern_summary=None, # Stubbed helper will init
        active_governance=None, # Stubbed helper will init
        dialogue_context=None, # Stubbed helper will init
        aac_field_readiness=None, # Stubbed helper will init
        momentum_profile=None, # Stubbed helper will init
        linked_backlog_items=[],
        new_backlog_items_generated_by_trace=[],
        work_management=None, # Stubbed helper will init
        field_risk_assessment=None, # Stubbed helper will init
        brave_space_dynamics=None, # Stubbed helper will init
        field_objectives=FieldObjectives(), # Default init
        current_trace_sop_provenance=None, # Stubbed helper will init
        session_maturity=FieldMaturity(igd_stage_assessment=IGDStageAssessmentEnum.S0_UNINITIALIZED, readiness_for_L6_reflection_flag=False), # Default
        downstream_directives=DownstreamDirectives() # Default init
    )
    return new_field_state_obj

def _field_bind_participants_to_field_state(working_field_state_obj: L5FieldStateObj, l4_anchor_state_obj: L4AnchorStateObj, mada_seed_input: MadaSeed) -> L5FieldStateObj:
    """
    Extracts source/destination agent UIDs from L2 communication context
    and adds/updates them in working_field_state_obj.field_participants.
    """
    current_participants = list(working_field_state_obj.field_participants) # Make a mutable copy
    participant_uids = {p.persona_uid for p in current_participants}
    timestamp = dt.fromisoformat(_field_get_current_timestamp_utc().replace('Z', '+00:00'))
    default_stats = ParticipantInteractionStats(contribution_count=0, query_count=0, dissent_signals_observed=0)

    source_id: Optional[str] = None
    dest_id: Optional[str] = None
    try:
        l2_comm_context = mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L2_frame_type_obj.communication_context_L2
        if l2_comm_context:
            source_id = l2_comm_context.source_agent_uid_L2
            dest_id = l2_comm_context.destination_agent_uid_L2
    except AttributeError:
        log_internal_warning("_field_bind_participants", {"warning": "Could not access L2 communication context."})

    if source_id and source_id not in participant_uids:
        current_participants.append(FieldParticipant(
            persona_uid=source_id, 
            role_in_field="Initiator_Of_Trace_L5", 
            engagement_readiness=ParticipantEngagementReadinessEnum.UNKNOWN, # Default
            last_interaction_in_field_time=timestamp, # This trace is an interaction
            interaction_stats_in_field=ParticipantInteractionStats(contribution_count=1)
        ))
        participant_uids.add(source_id)
    elif source_id: # Update existing
        for p in current_participants:
            if p.persona_uid == source_id:
                p.last_interaction_in_field_time = timestamp
                if p.interaction_stats_in_field:
                    p.interaction_stats_in_field.contribution_count = (p.interaction_stats_in_field.contribution_count or 0) + 1
                else:
                    p.interaction_stats_in_field = ParticipantInteractionStats(contribution_count=1)
                break
    
    if dest_id and dest_id not in participant_uids:
        current_participants.append(FieldParticipant(
            persona_uid=dest_id, 
            role_in_field="Primary_Processor_Of_Trace_L5", 
            engagement_readiness=ParticipantEngagementReadinessEnum.READY, # Default
            last_interaction_in_field_time=None, # Not interacted yet in this role for this trace
            interaction_stats_in_field=default_stats
        ))
        participant_uids.add(dest_id)
    
    working_field_state_obj.field_participants = current_participants
    return working_field_state_obj

# --- Stub Helper Functions ---
def _field_map_interactions_in_field_state(working_field_state_obj: L5FieldStateObj, l4_anchor_state_obj: L4AnchorStateObj) -> L5FieldStateObj:
    if working_field_state_obj.interaction_pattern_summary is None:
        from mada_schema import InteractionPatternSummary # Local import if not top-level
        working_field_state_obj.interaction_pattern_summary = InteractionPatternSummary()
    log_internal_info("_field_map_interactions", {"status": "Stub executed, ensured interaction_pattern_summary exists."})
    return working_field_state_obj

def _field_load_governance_for_field_state(working_field_state_obj: L5FieldStateObj, l4_anchor_state_obj: L4AnchorStateObj) -> L5FieldStateObj:
    if working_field_state_obj.active_governance is None:
        working_field_state_obj.active_governance = ActiveGovernance()
    log_internal_info("_field_load_governance", {"status": "Stub executed, ensured active_governance exists."})
    return working_field_state_obj

def _field_assess_dialogue_in_field_state(working_field_state_obj: L5FieldStateObj, l4_anchor_state_obj: L4AnchorStateObj) -> L5FieldStateObj:
    if working_field_state_obj.dialogue_context is None:
        working_field_state_obj.dialogue_context = DialogueContext(
            current_dialogue_mode=DialogueModeEnum.DISCUSSION, # Default
            dissent_strength=DissentStrengthEnum.NONE_OBSERVED # Default
        )
    log_internal_info("_field_assess_dialogue", {"status": "Stub executed, ensured dialogue_context exists."})
    return working_field_state_obj

def _field_assess_aac_readiness_of_field(working_field_state_obj: L5FieldStateObj, l4_anchor_state_obj: L4AnchorStateObj) -> L5FieldStateObj:
    if working_field_state_obj.aac_field_readiness is None:
        working_field_state_obj.aac_field_readiness = AACFieldReadiness(
            die_support_level=AACSupportLevelEnum.NONE, # Default
            consequence_tracking_enabled=False, # Default
            dialogue_structure_support=DialogueStructureSupportEnum.CLOSED # Default
        )
    log_internal_info("_field_assess_aac_readiness", {"status": "Stub executed, ensured aac_field_readiness exists."})
    return working_field_state_obj

def _field_integrate_context_into_field_state(working_field_state_obj: L5FieldStateObj, l4_anchor_state_obj: L4AnchorStateObj, trace_id: str) -> L5FieldStateObj:
    # This is more for merging L4 into an existing field state, covered by _field_log_provenance
    log_internal_info("_field_integrate_context", {"status": "Stub executed (conceptual merge with L4 state for existing field)."})
    return working_field_state_obj

def _field_log_provenance_in_field_state(working_field_state_obj: L5FieldStateObj, trace_id: str) -> L5FieldStateObj:
    if working_field_state_obj.current_trace_sop_provenance is None:
        working_field_state_obj.current_trace_sop_provenance = CurrentTraceSOPProvenance(
            processed_trace_id=trace_id,
            sop_executed_at_L5="lC.SOP.field_click" # Const value from schema
        )
    log_internal_info("_field_log_provenance", {"status": "Stub executed, ensured current_trace_sop_provenance exists."})
    return working_field_state_obj
    
def _field_engage_backlog_for_field(working_field_state_obj: L5FieldStateObj, l4_anchor_state_obj: L4AnchorStateObj, trace_id: str) -> L5FieldStateObj:
    # linked_backlog_items and new_backlog_items_generated_by_trace are already default_factory=list
    log_internal_info("_field_engage_backlog", {"status": "Stub executed, backlog item lists exist."})
    return working_field_state_obj

def _field_map_momentum_in_field_state(working_field_state_obj: L5FieldStateObj, l4_anchor_state_obj: L4AnchorStateObj) -> L5FieldStateObj:
    if working_field_state_obj.momentum_profile is None:
        working_field_state_obj.momentum_profile = MomentumProfile( # Default empty AxisMomentum
            axis1_power_participation=AxisMomentum(),
            axis2_competition_community=AxisMomentum(),
            axis3_hoarding_sustainability=AxisMomentum()
        )
    log_internal_info("_field_map_momentum", {"status": "Stub executed, ensured momentum_profile exists."})
    return working_field_state_obj

def _field_manage_work_in_field_state(working_field_state_obj: L5FieldStateObj) -> L5FieldStateObj:
    if working_field_state_obj.work_management is None:
        working_field_state_obj.work_management = WorkManagement(current_wip_count=0) # Default
    log_internal_info("_field_manage_work", {"status": "Stub executed, ensured work_management exists."})
    return working_field_state_obj

def _field_assess_risk_for_field_state(working_field_state_obj: L5FieldStateObj) -> L5FieldStateObj:
    if working_field_state_obj.field_risk_assessment is None:
        working_field_state_obj.field_risk_assessment = FieldRiskAssessment(risk_indicators=[], lcl_forecast_for_field=[]) # Default
    log_internal_info("_field_assess_risk", {"status": "Stub executed, ensured field_risk_assessment exists."})
    return working_field_state_obj

def _field_track_temporal_in_field_state(working_field_state_obj: L5FieldStateObj) -> L5FieldStateObj:
    # field_temporal_context is set in _field_load_or_init_field_state_obj
    # This stub might update last_activity_time if it were a real update
    if working_field_state_obj.field_temporal_context:
        working_field_state_obj.field_temporal_context.field_last_activity_time = dt.fromisoformat(_field_get_current_timestamp_utc().replace('Z', '+00:00'))
    log_internal_info("_field_track_temporal", {"status": "Stub executed, updated field_last_activity_time."})
    return working_field_state_obj

def _field_manage_brave_space_in_field_state(working_field_state_obj: L5FieldStateObj) -> L5FieldStateObj:
    if working_field_state_obj.brave_space_dynamics is None:
        working_field_state_obj.brave_space_dynamics = BraveSpaceDynamics(activation_status=BraveSpaceActivationStatusEnum.INACTIVE) # Default
    log_internal_info("_field_manage_brave_space", {"status": "Stub executed, ensured brave_space_dynamics exists."})
    return working_field_state_obj

def _field_update_objectives_in_field_state(working_field_state_obj: L5FieldStateObj, l4_anchor_state_obj: L4AnchorStateObj) -> L5FieldStateObj:
    # field_objectives is default_factory=dict in schema, so it's FieldObjectives() by default
    log_internal_info("_field_update_objectives", {"status": "Stub executed, field_objectives exists."})
    return working_field_state_obj

def _field_assess_maturity_of_field(working_field_state_obj: L5FieldStateObj) -> L5FieldStateObj:
    # session_maturity (FieldMaturity) is set in _field_load_or_init_field_state_obj
    log_internal_info("_field_assess_maturity", {"status": "Stub executed, session_maturity exists."})
    return working_field_state_obj

def _field_prep_directives_for_field_state(working_field_state_obj: L5FieldStateObj) -> L5FieldStateObj:
    # downstream_directives is default_factory=dict in schema, so it's DownstreamDirectives() by default
    log_internal_info("_field_prep_directives", {"status": "Stub executed, downstream_directives exists."})
    return working_field_state_obj
# --- End Stub Helper Functions ---


def _field_determine_final_l5_outcome(working_field_state_obj: L5FieldStateObj) -> str: # Returns L5EpistemicStateOfFieldProcessingEnum string value
    """
    Baseline: Returns state based on field_status and session_maturity.
    """
    if working_field_state_obj.session_maturity and \
       working_field_state_obj.session_maturity.igd_stage_assessment == IGDStageAssessmentEnum.SX_FRACTURED_REGRESSED:
        return L5EpistemicStateOfFieldProcessingEnum.LCL_FRAGMENT_FIELD.value
    
    if working_field_state_obj.field_status == FieldStatusEnum.ACTIVE: # Set in init
        # If it was truly an update of an *existing* field, this would be chosen.
        # For baseline, since we always init, this might not be hit unless field_status is changed by a (future) helper.
        # To match MR logic for now, if it's Active, it's considered Updated.
        return L5EpistemicStateOfFieldProcessingEnum.FIELD_UPDATED_EXISTING.value
        
    # Default for a newly initialized field if not fractured and not explicitly "Active" from a loaded state
    return L5EpistemicStateOfFieldProcessingEnum.FIELD_INSTANTIATED_NEW.value


# --- Main field_click Process Function ---

def field_click_process(mada_seed_input: MadaSeed) -> MadaSeed:
    """
    Processes the madaSeed object from L4 (anchor_click) to populate L5 field state information.
    """
    current_time_fail_dt = dt.fromisoformat(_field_get_current_timestamp_utc().replace('Z', '+00:00'))

    if not _field_validate_l4_data_in_madaSeed(mada_seed_input):
        error_detail_msg = "Invalid or incomplete L4 data in input madaSeed for L5 processing."
        log_critical_error("field_click_process L4 Data Error", {"trace_id": mada_seed_input.seed_id if mada_seed_input else "Unknown", "error": error_detail_msg})
        
        if mada_seed_input:
            mada_seed_input.trace_metadata.L5_trace = L5Trace(
                version_L5_trace_schema="0.1.0", sop_name="lC.SOP.field_click",
                completion_timestamp_L5=current_time_fail_dt,
                epistemic_state_L5=L5EpistemicStateOfFieldProcessingEnum.LCL_FAILURE_INTERNAL_L5,
                error_details=error_detail_msg
            )
            mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L5_field_state_obj = L5FieldStateObj(
                version="0.2.0", 
                l5_epistemic_state_of_field_processing=L5EpistemicStateOfFieldProcessingEnum.LCL_FAILURE_INTERNAL_L5, 
                error_details=f"L5 aborted: {error_detail_msg}"
            )
        return mada_seed_input

    trace_id = mada_seed_input.seed_id
    l4_anchor_state_obj = mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L4_anchor_state_obj
    
    try:
        # --- CE Step 1 (A): Field Binding & Initialization ---
        chain_id = _field_get_chain_id_from_madaSeed(mada_seed_input) or trace_id # Ensure chain_id is not None
        working_field_state_obj = _field_load_or_init_field_state_obj(chain_id, mada_seed_input)
        
        # --- CE Step 2 (B): Participant Binding & State Check ---
        working_field_state_obj = _field_bind_participants_to_field_state(working_field_state_obj, l4_anchor_state_obj, mada_seed_input)
        
        # --- Call Stub Helper Functions (CE Steps C through Q conceptually) ---
        working_field_state_obj = _field_load_governance_for_field_state(working_field_state_obj, l4_anchor_state_obj)
        working_field_state_obj = _field_assess_dialogue_in_field_state(working_field_state_obj, l4_anchor_state_obj)
        working_field_state_obj = _field_assess_aac_readiness_of_field(working_field_state_obj, l4_anchor_state_obj)
        working_field_state_obj = _field_integrate_context_into_field_state(working_field_state_obj, l4_anchor_state_obj, trace_id) # Conceptual merge
        working_field_state_obj = _field_log_provenance_in_field_state(working_field_state_obj, trace_id)
        working_field_state_obj = _field_map_interactions_in_field_state(working_field_state_obj, l4_anchor_state_obj)
        working_field_state_obj = _field_engage_backlog_for_field(working_field_state_obj, l4_anchor_state_obj, trace_id)
        working_field_state_obj = _field_map_momentum_in_field_state(working_field_state_obj, l4_anchor_state_obj)
        working_field_state_obj = _field_manage_work_in_field_state(working_field_state_obj)
        working_field_state_obj = _field_assess_risk_for_field_state(working_field_state_obj)
        working_field_state_obj = _field_track_temporal_in_field_state(working_field_state_obj) # Updates last_activity_time
        working_field_state_obj = _field_manage_brave_space_in_field_state(working_field_state_obj)
        working_field_state_obj = _field_update_objectives_in_field_state(working_field_state_obj, l4_anchor_state_obj)
        working_field_state_obj = _field_assess_maturity_of_field(working_field_state_obj)
        working_field_state_obj = _field_prep_directives_for_field_state(working_field_state_obj)

        # --- CE Step 18 (Q): Determine Final L5 Outcome ---
        final_l5_epistemic_state_str = _field_determine_final_l5_outcome(working_field_state_obj)
        final_l5_epistemic_state = L5EpistemicStateOfFieldProcessingEnum(final_l5_epistemic_state_str)
        working_field_state_obj.l5_epistemic_state_of_field_processing = final_l5_epistemic_state
        
        # Set completion time
        current_time_l5_final_dt = dt.fromisoformat(_field_get_current_timestamp_utc().replace('Z', '+00:00'))
        working_field_state_obj.l5_field_processing_completion_time = current_time_l5_final_dt
        
        # --- CE Step 19 (R): Update madaSeed object with L5 contributions ---
        mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L5_field_state_obj = working_field_state_obj

        # --- Populate L5_trace ---
        l5_trace_obj = L5Trace(
            version_L5_trace_schema="0.1.0", 
            sop_name="lC.SOP.field_click", 
            completion_timestamp_L5=current_time_l5_final_dt,
            epistemic_state_L5=final_l5_epistemic_state,
            L5_field_instance_uid_processed=working_field_state_obj.field_instance_uid,
            L5_field_status_after_update=working_field_state_obj.field_status,
            L5_dialogue_mode_assessed_in_trace=working_field_state_obj.dialogue_context.current_dialogue_mode if working_field_state_obj.dialogue_context else None,
            L5_igd_stage_assessed_in_trace=working_field_state_obj.session_maturity.igd_stage_assessment if working_field_state_obj.session_maturity else None
        )
        mada_seed_input.trace_metadata.L5_trace = l5_trace_obj
        
        return mada_seed_input

    except Exception as critical_process_error:
        error_msg = f"Critical L5 Failure: {str(critical_process_error)}"
        log_critical_error("Field Click Process Failed Critically", {"trace_id": trace_id, "error": error_msg})
        
        current_time_crit_fail_dt = dt.fromisoformat(_field_get_current_timestamp_utc().replace('Z', '+00:00'))
        
        mada_seed_input.trace_metadata.L5_trace = L5Trace(
             version_L5_trace_schema="0.1.0", sop_name="lC.SOP.field_click",
             completion_timestamp_L5=current_time_crit_fail_dt, 
             epistemic_state_L5=L5EpistemicStateOfFieldProcessingEnum.LCL_FAILURE_INTERNAL_L5,
             error_details=error_msg
        )
        # Ensure L5_field_state_obj is set with error details
        error_l5_field_state = L5FieldStateObj(
            version="0.2.0", 
            l5_epistemic_state_of_field_processing=L5EpistemicStateOfFieldProcessingEnum.LCL_FAILURE_INTERNAL_L5, 
            field_instance_uid=chain_id if 'chain_id' in locals() and chain_id else trace_id, # Use chain_id if available
            error_details=error_msg,
            # Fill other required fields with defaults
            field_temporal_context=FieldTemporalContext(field_creation_time=current_time_crit_fail_dt, field_last_activity_time=current_time_crit_fail_dt),
            session_maturity=FieldMaturity(igd_stage_assessment=IGDStageAssessmentEnum.S0_UNINITIALIZED, readiness_for_L6_reflection_flag=False)
        )
        mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L5_field_state_obj = error_l5_field_state
        
        return mada_seed_input


if __name__ == '__main__':
    from sop_l1_startle import startle_process
    from sop_l2_frame_click import frame_click_process
    from sop_l3_keymap_click import keymap_click_process
    from sop_l4_anchor_click import anchor_click_process

    print("--- Running sop_l5_field_click.py example ---")

    # 1. Create L1 MadaSeed
    example_input_event = {
        "reception_timestamp_utc_iso": "2023-10-31T06:00:00Z",
        "origin_hint": "Test_Field_Input",
        "data_components": [
            {"role_hint": "primary_text", "content_handle_placeholder": "Field click test content.", "size_hint": 25, "type_hint": "text/plain"}
        ]
    }
    l1_seed = startle_process(example_input_event)

    # 2. Create L2 MadaSeed
    l2_seed = frame_click_process(l1_seed)
    
    # 3. Create L3 MadaSeed
    l3_seed = keymap_click_process(l2_seed)

    # 4. Create L4 MadaSeed
    l4_seed = anchor_click_process(l3_seed)
    print(f"\nL4 Epistemic State: {l4_seed.trace_metadata.L4_trace.epistemic_state_L4.name if l4_seed.trace_metadata.L4_trace.epistemic_state_L4 else 'N/A'}")
    if not l4_seed.trace_metadata.L4_trace.epistemic_state_L4.name.startswith("ANCHORED"):
         print("L4 processing did not result in ANCHORED state, L5 test might not be fully meaningful.")

    # 5. Pass L4 MadaSeed to field_click_process
    print("\nCalling field_click_process with L4 MadaSeed...")
    l5_seed = field_click_process(l4_seed)

    # print("\nL5 MadaSeed (field_click_process output):")
    # print(l5_seed.json(indent=2, exclude_none=True)) # Pydantic v2: by_alias=True, exclude_none=True

    if l5_seed:
        l5_field_obj = l5_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L5_field_state_obj
        print(f"\nL5 Field State Object Version: {l5_field_obj.version}")
        print(f"L5 Epistemic State of Field Processing: {l5_field_obj.l5_epistemic_state_of_field_processing.name if l5_field_obj.l5_epistemic_state_of_field_processing else 'N/A'}")
        print(f"L5 Field Instance UID: {l5_field_obj.field_instance_uid}")
        print(f"L5 Field Status: {l5_field_obj.field_status.name if l5_field_obj.field_status else 'N/A'}")
        if l5_field_obj.field_participants:
            print(f"L5 Field Participants Count: {len(l5_field_obj.field_participants)}")
            for participant in l5_field_obj.field_participants:
                print(f"  - Participant UID: {participant.persona_uid}, Role: {participant.role_in_field}")
        if l5_field_obj.session_maturity:
             print(f"L5 IGD Stage Assessment: {l5_field_obj.session_maturity.igd_stage_assessment.name if l5_field_obj.session_maturity.igd_stage_assessment else 'N/A'}")

        l5_trace_meta = l5_seed.trace_metadata.L5_trace
        print(f"\nL5 Trace Version: {l5_trace_meta.version_L5_trace_schema}")
        print(f"L5 Trace SOP Name: {l5_trace_meta.sop_name}")
        print(f"L5 Trace Epistemic State: {l5_trace_meta.epistemic_state_L5.name if l5_trace_meta.epistemic_state_L5 else 'N/A'}")
        print(f"L5 Trace Field Status After Update: {l5_trace_meta.L5_field_status_after_update.name if l5_trace_meta.L5_field_status_after_update else 'N/A'}")

    print("\n--- sop_l5_field_click.py example run complete ---")
