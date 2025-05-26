from datetime import datetime as dt, timezone
from typing import List, Dict, Tuple, Any, Optional

from ..schemas.mada_schema import ( # Corrected path
    MadaSeed, L3SurfaceKeymapObj, L4AnchorStateObj, L4Trace,
    PersonaAlignmentContextEngaged, PAEngagementStatusEnum, EngagedLevelFindings, LevelFindingItem, FindingTypeEnum,
    ResolvedEntity, ResolutionSummary, # Assuming ResolvedEntity is the correct model for L4 from schema
    AacAssessabilityMap, ConsequenceVector,
    IdentifiedKnowledgeGapL4, KnowledgeGapTypeEnum, KnowledgeGapPriorityEnum, # IdentifiedKnowledgeGapL4 is used for KnowledgeGapL4
    L4EpistemicStateOfAnchoringEnum, L4ValidationStatusEnum,
    TemporalSummaryL4, RelationshipSummaryL4, InterpretationSummaryL4, ValidationSummaryL4, TraceThreadingContext
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

def _anchor_validate_l3_data_in_madaSeed(mada_seed_input: MadaSeed) -> bool:
    """Validates essential L3 data presence within the input MadaSeed for L4 processing."""
    try:
        if not mada_seed_input:
            log_internal_warning("Helper:_anchor_validate_l3_data", {"error": "Input madaSeed is None"})
            return False

        l3_surface_keymap_obj = mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj
        l3_trace = mada_seed_input.trace_metadata.L3_trace
        l2_trace = mada_seed_input.trace_metadata.L2_trace # For comms context check

        if not l3_surface_keymap_obj or not l3_surface_keymap_obj.version:
            log_internal_warning("Helper:_anchor_validate_l3_data", {"error": "Missing or invalid L3_surface_keymap_obj in madaSeed for L4"})
            return False
        if not l3_trace or not l3_trace.epistemic_state_L3:
            log_internal_warning("Helper:_anchor_validate_l3_data", {"error": "Missing or invalid L3_trace in madaSeed for L4"})
            return False
        # Assuming epistemic_state_L3 is a string, not an enum object, based on L3 MR logic's output
        if not isinstance(l3_trace.epistemic_state_L3, str) or not l3_trace.epistemic_state_L3.startswith("Keymapped"):
            log_internal_info("Helper:_anchor_validate_l3_data", {"reason": f"L3 state '{l3_trace.epistemic_state_L3}' not suitable for L4 anchoring."})
            return False
        if not l2_trace or not l2_trace.epistemic_state_L2: # Ensure L2 trace exists for comms context
            log_internal_warning("Helper:_anchor_validate_l3_data", {"error": "Missing or invalid L2_trace for L4 comms context"})
            return False
    except AttributeError as e:
        log_internal_warning("Helper:_anchor_validate_l3_data", {"error": f"AttributeError validating L3 data: {str(e)}"})
        return False
    except Exception as e:
        log_internal_warning("Helper:_anchor_validate_l3_data", {"error": f"Exception validating L3 data: {str(e)}"})
        return False
    return True

def _anchor_get_current_timestamp_utc() -> str:
    """Returns a fixed, unique timestamp string."""
    return "2023-10-28T11:00:00Z"

def _anchor_engage_pa_context_from_madaSeed(trace_id: str, mada_seed_input: MadaSeed, prior_pa_context_from_seed_anchor: Optional[Dict[str, Any]]) -> PersonaAlignmentContextEngaged:
    """
    Extracts anchoring_persona_uid and returns a baseline PersonaAlignmentContextEngaged object.
    """
    anchoring_persona_uid = "Unknown_L4_Anchor_Persona" # Default
    try:
        l2_comm_context = mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L2_frame_type_obj.communication_context_L2
        if l2_comm_context and l2_comm_context.destination_agent_uid_L2:
            anchoring_persona_uid = l2_comm_context.destination_agent_uid_L2
    except AttributeError:
        log_internal_warning("_anchor_engage_pa_context", {"warning": "Could not retrieve destination_agent_uid_L2 for anchoring_persona_uid."})

    # Baseline: returns a default engaged state.
    engaged_pa = PersonaAlignmentContextEngaged(
        version="0.1.1",
        persona_uid=anchoring_persona_uid,
        alignment_profile_ref="urn:crux:uid::Default_PA_Profile_Ref_L4", # Default URN
        profile_version_ref="1.0", # Example version
        engagement_status=PAEngagementStatusEnum.INFERRED_STATE_USED,
        B0_P3_boundary_findings=[], # Empty list for baseline
        B11_boundary_findings=[], # Empty list for baseline
        engaged_level_findings=EngagedLevelFindings( # Populate L1_Environment with a default finding
            L1_Environment=[LevelFindingItem(finding_type=FindingTypeEnum.STATE_OBSERVATION_L1, description="L4 anchoring initiated for trace: " + trace_id)]
        )
    )
    return engaged_pa

def _anchor_resolve_entities_from_surface_map(l3_surface_keymap_obj: L3SurfaceKeymapObj, pa_context_engaged: PersonaAlignmentContextEngaged, prior_resolutions_from_seed_anchor: Optional[List[Any]]) -> List[ResolvedEntity]:
    """
    Baseline: Mock resolution. Iterates L3 entity mentions and returns ResolvedEntity list.
    """
    resolved_entities_list: List[ResolvedEntity] = []
    raw_mentions = l3_surface_keymap_obj.lexical_affordances.entity_mentions_raw
    
    for mention_obj in raw_mentions:
        resolved_entities_list.append(ResolvedEntity(
            mention=mention_obj.mention,
            resolved_uid="urn:crux:uid::Resolved_" + mention_obj.mention.replace(" ", "_") + "_L4",
            candidates=[], # Empty list for baseline
            confidence=0.6, # Baseline confidence
            resolution_status="MockResolved_L4",
            source_component_ref=mention_obj.source_component_ref,
            status_flag="new" # As per pseudo-code example
        ))
    return resolved_entities_list

def _anchor_assess_aac_map(working_anchor_state_obj: L4AnchorStateObj, l3_surface_keymap_obj: L3SurfaceKeymapObj, pa_context_engaged: PersonaAlignmentContextEngaged, prior_aac_map_from_seed_anchor: Optional[Dict[str, Any]]) -> AacAssessabilityMap:
    """
    Baseline: Returns a default AacAssessabilityMap object.
    """
    return AacAssessabilityMap(
        version="0.1.1",
        die_score=0.5,
        consequence_vector=ConsequenceVector(immediacy=0.3, visibility=0.6, delay_ms=None),
        dialogue_intensity=0.4,
        aac_visibility_score=0.45 # Example score
    )

def _anchor_synthesize_knowledge_gaps(working_anchor_state_obj: L4AnchorStateObj, pa_context_engaged: PersonaAlignmentContextEngaged, prior_gaps_from_seed_anchor: Optional[List[Any]]) -> List[IdentifiedKnowledgeGapL4]:
    """
    Baseline: If overall_anchor_confidence < 0.5, add a generic KnowledgeGapL4.
    """
    gaps: List[IdentifiedKnowledgeGapL4] = []
    if working_anchor_state_obj.overall_anchor_confidence is not None and \
       working_anchor_state_obj.overall_anchor_confidence < 0.5:
        gaps.append(IdentifiedKnowledgeGapL4(
            gap_id="L4_LowAnchorConfidence_001", 
            gap_type=KnowledgeGapTypeEnum.CONTEXT_MISSING,
            required_info_description="Overall anchoring confidence is low, further context may be needed for L3 surface map.",
            priority_hint=KnowledgeGapPriorityEnum.MEDIUM
        ))
    return gaps

def _anchor_determine_final_l4_outcome(working_anchor_state_obj: L4AnchorStateObj, l4_policies: Dict[str, Any]) -> str: # Returns L4EpistemicStateOfAnchoringEnum string value
    """
    Baseline: Determines L4 epistemic state based on validation and AAC score.
    """
    validation_summary = working_anchor_state_obj.validation_summary_L4
    aac_map = working_anchor_state_obj.aac_assessability_map
    gaps_count = len(working_anchor_state_obj.identified_knowledge_gaps_L4)

    if validation_summary and validation_summary.overall_status_L4 == L4ValidationStatusEnum.FAILURE:
        return L4EpistemicStateOfAnchoringEnum.LCL_FAILURE_INTERNAL_L4.value
    
    # Using the policy value passed, e.g. l4_policies.get("LCL_on_low_AAC_threshold", 0.3)
    low_aac_threshold = l4_policies.get("LCL_on_low_AAC_threshold", 0.3)
    
    if aac_map and aac_map.aac_visibility_score < low_aac_threshold:
        return L4EpistemicStateOfAnchoringEnum.ANCHORED_LOW_ASSESSABILITY.value
    
    # Example policy for gaps
    max_allowed_gaps = l4_policies.get("max_gaps_before_AnchoredWithGaps", 2)
    if gaps_count > max_allowed_gaps:
        return L4EpistemicStateOfAnchoringEnum.ANCHORED_WITH_GAPS.value
        
    if validation_summary and validation_summary.overall_status_L4 == L4ValidationStatusEnum.SUCCESS:
         return L4EpistemicStateOfAnchoringEnum.ANCHORED.value
    
    # Default fallback if other conditions not met, could be more specific
    return L4EpistemicStateOfAnchoringEnum.ANCHORED_WITH_GAPS.value


# --- Main anchor_click Process Function ---

def anchor_click_process(mada_seed_input: MadaSeed) -> MadaSeed:
    """
    Processes the madaSeed object from L3 (keymap_click) to populate L4 anchoring information.
    """
    current_time_fail_dt = dt.fromisoformat(_anchor_get_current_timestamp_utc().replace('Z', '+00:00'))

    if not _anchor_validate_l3_data_in_madaSeed(mada_seed_input):
        error_detail_msg = "Invalid or incomplete L3 data in input madaSeed for L4 processing."
        log_critical_error("anchor_click_process L3 Data Error", {"trace_id": mada_seed_input.seed_id if mada_seed_input else "Unknown", "error": error_detail_msg})
        
        if mada_seed_input:
            mada_seed_input.trace_metadata.L4_trace = L4Trace(
                version_L4_trace_schema="0.1.0", sop_name="lC.SOP.anchor_click",
                completion_timestamp_L4=current_time_fail_dt,
                epistemic_state_L4=L4EpistemicStateOfAnchoringEnum.LCL_FAILURE_INTERNAL_L4,
                error_details=error_detail_msg
            )
            mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L4_anchor_state_obj = L4AnchorStateObj(
                version="0.2.17", 
                l4_epistemic_state_of_anchoring=L4EpistemicStateOfAnchoringEnum.LCL_FAILURE_INTERNAL_L4, 
                error_details=f"L4 aborted: {error_detail_msg}"
            )
        return mada_seed_input

    trace_id = mada_seed_input.seed_id
    l3_surface_keymap_obj = mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj
    
    # Initialize L4_anchor_state_obj with version and default empty/None for sub-objects
    working_l4_anchor_state_obj = L4AnchorStateObj(
        version="0.2.17",
        l4_epistemic_state_of_anchoring=None, # Will be set by _anchor_determine_final_l4_outcome
        overall_anchor_confidence=None, # Will be set (e.g., baseline 0.7)
        aac_assessability_map=None, # Will be set by _anchor_assess_aac_map
        persona_alignment_context_engaged=None, # Will be set by _anchor_engage_pa_context_from_madaSeed
        trace_threading_context=TraceThreadingContext(version="0.1.1"), # Default empty
        resolution_summary=ResolutionSummary(resolved_entities=[], resolved_concepts=[], coreference_links=[]), # Default empty
        temporal_summary_L4=[], # Default empty list
        relationship_summary_L4=[], # Default empty list
        interpretation_summary_L4=InterpretationSummaryL4(), # Default empty
        validation_summary_L4=ValidationSummaryL4(overall_status_L4=L4ValidationStatusEnum.FAILURE), # Default to failure
        identified_knowledge_gaps_L4=[] # Default empty list
    )
    
    try:
        # --- Conceptual CE Steps from L4 anchor_click table ---
        # Prior anchor state (seed_anchor_state) is Null for this baseline.

        # Step 2 (Engage PA Context)
        working_l4_anchor_state_obj.persona_alignment_context_engaged = _anchor_engage_pa_context_from_madaSeed(trace_id, mada_seed_input, None)
        if working_l4_anchor_state_obj.persona_alignment_context_engaged.engagement_status == PAEngagementStatusEnum.ENGAGEMENT_FAILED: # Enum comparison
            raise ValueError("L4 PA Context Engagement Failed")

        # Step 3-7 (Resolve Entities, Concepts, Temporals, Corefs, Bind Relations)
        # For baseline, only entities are resolved from L3. Others remain empty.
        working_l4_anchor_state_obj.resolution_summary.resolved_entities = _anchor_resolve_entities_from_surface_map(l3_surface_keymap_obj, working_l4_anchor_state_obj.persona_alignment_context_engaged, None)
        # temporal_summary_L4, relationship_summary_L4 remain empty for baseline.
        
        # Step 8-9 (Structure Interpretation, Match Schemas)
        working_l4_anchor_state_obj.interpretation_summary_L4 = InterpretationSummaryL4(
            primary_interaction_pattern_L4="Unknown_L4_Interpreted_Baseline", # Baseline value
            overall_relevance_score_L4=0.5 # Baseline value
        )

        # Step 10 (Perform Anchored Validation)
        # Baseline: Assume success if we reached this point without prior critical errors.
        working_l4_anchor_state_obj.validation_summary_L4 = ValidationSummaryL4(
            overall_status_L4=L4ValidationStatusEnum.SUCCESS, 
            key_anomaly_flags_L4=[]
        )

        # Step 11 (Assess AAC Visibility)
        working_l4_anchor_state_obj.aac_assessability_map = _anchor_assess_aac_map(working_l4_anchor_state_obj, l3_surface_keymap_obj, working_l4_anchor_state_obj.persona_alignment_context_engaged, None)
        
        # Set overall_anchor_confidence before synthesizing gaps
        working_l4_anchor_state_obj.overall_anchor_confidence = 0.7 # Baseline confidence

        # Step 12 (Synthesize Knowledge Gaps)
        working_l4_anchor_state_obj.identified_knowledge_gaps_L4 = _anchor_synthesize_knowledge_gaps(working_l4_anchor_state_obj, working_l4_anchor_state_obj.persona_alignment_context_engaged, None)

        # Step 13 (Determine Final L4 Outcome)
        # Mock L4 policies for the helper
        mock_l4_policies = {"LCL_on_low_AAC_threshold": 0.3, "max_gaps_before_AnchoredWithGaps": 2}
        final_l4_epistemic_state_str = _anchor_determine_final_l4_outcome(working_l4_anchor_state_obj, mock_l4_policies)
        # Convert string back to enum member for Pydantic model
        final_l4_epistemic_state = L4EpistemicStateOfAnchoringEnum(final_l4_epistemic_state_str)
        working_l4_anchor_state_obj.l4_epistemic_state_of_anchoring = final_l4_epistemic_state
        
        # Step 14 (Bind Final State & Finalize L4 - Set completion time)
        current_time_l4_final_dt = dt.fromisoformat(_anchor_get_current_timestamp_utc().replace('Z', '+00:00'))
        working_l4_anchor_state_obj.l4_anchoring_completion_time = current_time_l4_final_dt
        
        # --- Update madaSeed object with L4 contributions ---
        mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L4_anchor_state_obj = working_l4_anchor_state_obj

        # --- Populate L4_trace ---
        l4_trace_obj = L4Trace(
            version_L4_trace_schema="0.1.0", 
            sop_name="lC.SOP.anchor_click", 
            completion_timestamp_L4=current_time_l4_final_dt,
            epistemic_state_L4=final_l4_epistemic_state,
            L4_pa_profile_engaged_ref_in_trace=working_l4_anchor_state_obj.persona_alignment_context_engaged.alignment_profile_ref if working_l4_anchor_state_obj.persona_alignment_context_engaged else None,
            L4_aac_visibility_score_from_anchor_state=working_l4_anchor_state_obj.aac_assessability_map.aac_visibility_score if working_l4_anchor_state_obj.aac_assessability_map else None,
            L4_overall_anchor_confidence_from_anchor_state=working_l4_anchor_state_obj.overall_anchor_confidence,
            L4_knowledge_gaps_identified_count=len(working_l4_anchor_state_obj.identified_knowledge_gaps_L4)
        )
        mada_seed_input.trace_metadata.L4_trace = l4_trace_obj
        
        # Step 15 (Expose L4 Output Package - is the updated madaSeed)
        return mada_seed_input

    except Exception as critical_process_error:
        error_msg = f"Critical L4 Failure: {str(critical_process_error)}"
        log_critical_error("Anchor Click Process Failed Critically", {"trace_id": trace_id, "error": error_msg})
        
        current_time_crit_fail_dt = dt.fromisoformat(_anchor_get_current_timestamp_utc().replace('Z', '+00:00'))
        
        mada_seed_input.trace_metadata.L4_trace = L4Trace(
             version_L4_trace_schema="0.1.0", sop_name="lC.SOP.anchor_click",
             completion_timestamp_L4=current_time_crit_fail_dt, 
             epistemic_state_L4=L4EpistemicStateOfAnchoringEnum.LCL_FAILURE_INTERNAL_L4,
             error_details=error_msg
        )
        # Update L4_anchor_state_obj in madaSeed with error state
        # Ensure all required fields are present even in error state
        error_l4_anchor_state = L4AnchorStateObj(
            version="0.2.17", 
            l4_epistemic_state_of_anchoring=L4EpistemicStateOfAnchoringEnum.LCL_FAILURE_INTERNAL_L4, 
            error_details=error_msg,
            # Fill other required fields with defaults or None if optional
            aac_assessability_map=None, 
            persona_alignment_context_engaged=None,
            resolution_summary=ResolutionSummary(),
            validation_summary_L4=ValidationSummaryL4(overall_status_L4=L4ValidationStatusEnum.FAILURE)
        )
        mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L4_anchor_state_obj = error_l4_anchor_state
        
        return mada_seed_input

if __name__ == '__main__':
    from sop_l1_startle import startle_process
    from sop_l2_frame_click import frame_click_process
    from sop_l3_keymap_click import keymap_click_process

    print("--- Running sop_l4_anchor_click.py example ---")

    # 1. Create L1 MadaSeed
    example_input_event = {
        "reception_timestamp_utc_iso": "2023-10-30T07:00:00Z",
        "origin_hint": "Test_Anchor_Input",
        "data_components": [
            {"role_hint": "primary_text", "content_handle_placeholder": "Anchor this: John Doe mentioned urgency for Project Alpha.", "size_hint": 60, "type_hint": "text/plain"}
        ]
    }
    l1_seed = startle_process(example_input_event)

    # 2. Create L2 MadaSeed
    l2_seed = frame_click_process(l1_seed)
    
    # 3. Create L3 MadaSeed
    l3_seed = keymap_click_process(l2_seed)
    print(f"\nL3 Epistemic State: {l3_seed.trace_metadata.L3_trace.epistemic_state_L3}")
    # Manually add an entity mention to L3 output for L4 to process
    if l3_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj.lexical_affordances:
        from mada_schema import EntityMentionRaw # Ensure this is imported if not already
        l3_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj.lexical_affordances.entity_mentions_raw.append(
            EntityMentionRaw(mention="John Doe", confidence=0.9, possible_types=["PERSON"])
        )
        l3_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj.lexical_affordances.entity_mentions_raw.append(
            EntityMentionRaw(mention="Project Alpha", confidence=0.85, possible_types=["PROJECT"])
        )


    if l3_seed.trace_metadata.L3_trace.epistemic_state_L3 != "Keymapped_Successfully":
         print("L3 processing did not result in Keymapped_Successfully state, L4 test might not be fully meaningful.")

    # 4. Pass L3 MadaSeed to anchor_click_process
    print("\nCalling anchor_click_process with L3 MadaSeed...")
    l4_seed = anchor_click_process(l3_seed)

    # print("\nL4 MadaSeed (anchor_click_process output):")
    # print(l4_seed.json(indent=2, exclude_none=True))

    if l4_seed:
        l4_anchor_obj = l4_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L4_anchor_state_obj
        print(f"\nL4 Anchor State Object Version: {l4_anchor_obj.version}")
        print(f"L4 Epistemic State of Anchoring: {l4_anchor_obj.l4_epistemic_state_of_anchoring.name if l4_anchor_obj.l4_epistemic_state_of_anchoring else 'N/A'}")
        if l4_anchor_obj.persona_alignment_context_engaged:
             print(f"L4 Anchoring Persona UID: {l4_anchor_obj.persona_alignment_context_engaged.persona_uid}")
        if l4_anchor_obj.aac_assessability_map:
            print(f"L4 AAC Visibility Score: {l4_anchor_obj.aac_assessability_map.aac_visibility_score}")
        if l4_anchor_obj.resolution_summary and l4_anchor_obj.resolution_summary.resolved_entities:
            print(f"L4 Resolved Entities Count: {len(l4_anchor_obj.resolution_summary.resolved_entities)}")
            for entity in l4_anchor_obj.resolution_summary.resolved_entities:
                print(f"  - Resolved Entity: {entity.mention} -> {entity.resolved_uid} ({entity.resolution_status})")
        
        l4_trace_meta = l4_seed.trace_metadata.L4_trace
        print(f"\nL4 Trace Version: {l4_trace_meta.version_L4_trace_schema}")
        print(f"L4 Trace SOP Name: {l4_trace_meta.sop_name}")
        print(f"L4 Trace Epistemic State: {l4_trace_meta.epistemic_state_L4.name if l4_trace_meta.epistemic_state_L4 else 'N/A'}")

    print("\n--- sop_l4_anchor_click.py example run complete ---")
