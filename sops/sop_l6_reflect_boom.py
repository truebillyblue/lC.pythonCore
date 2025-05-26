from datetime import datetime as dt, timezone
from typing import List, Dict, Tuple, Any, Optional, Union

from ..schemas.mada_schema import ( # Corrected path
    MadaSeed, L5FieldStateObj, ActiveGovernance, L6ReflectionPayloadObj, L6Trace,
    PayloadMetadata, PayloadMetadataTarget, ConsumerTypeEnum, OutputModalityEnum,
    TransformationMetadata, RedactionStatus, OmittedContentSummary, OmittedContentCategoryEnum, SimplificationLevelHintEnum, OmissionRationaleCodeEnum,
    ReflectionSurface, AssessedCynefinState, CynefinDomainEnum, CynefinZoneTransition, BraveSpaceReflection, TransformationDissentRiskHintEnum, RepresentationDiscomfortRiskHintEnum,
    ReflectedPAContextSummary, KeyLevelFindingSummary,
    FieldDiagnosticsSummaryHints,
    PayloadContent, MultimodalPackageItem,
    NextActionDirective, L7DirectiveTypeEnum, 
    L6EpistemicStateEnum,
    L5EpistemicStateOfFieldProcessingEnum,
    L4AnchorStateObj, IdentifiedKnowledgeGapL4, KnowledgeGapTypeEnum, # For L4 PA context selection
    FieldMaturity, AACFieldReadiness, MomentumProfile, DialogueContext, BraveSpaceDynamics, FieldRiskAssessment, # For L5 diagnostics selection
    IGDStageAssessmentEnum # For L5 session_maturity
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

def _reflect_validate_l5_data_in_madaSeed(mada_seed_input: MadaSeed) -> bool:
    """Validates essential L5 data presence within the input MadaSeed."""
    try:
        if not mada_seed_input:
            log_internal_warning("Helper:_reflect_validate_l5_data", {"error": "Input madaSeed is None"})
            return False

        l5_field_state_obj = mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L5_field_state_obj
        l5_trace = mada_seed_input.trace_metadata.L5_trace

        if not l5_field_state_obj or not l5_field_state_obj.version:
            log_internal_warning("Helper:_reflect_validate_l5_data", {"error": "Missing or invalid L5_field_state_obj in madaSeed"})
            return False
        if not l5_trace or not l5_trace.epistemic_state_L5:
            log_internal_warning("Helper:_reflect_validate_l5_data", {"error": "Missing or invalid L5_trace in madaSeed"})
            return False
        if not l5_trace.epistemic_state_L5.name.startswith("FIELD_"): 
            log_internal_info("Helper:_reflect_validate_l5_data", {"reason": f"L5 state '{l5_trace.epistemic_state_L5.name}' not suitable for L6 processing."})
            return False
    except AttributeError as e:
        log_internal_warning("Helper:_reflect_validate_l5_data", {"error": f"AttributeError validating L5 data: {str(e)}"})
        return False
    except Exception as e:
        log_internal_warning("Helper:_reflect_validate_l5_data", {"error": f"Exception validating L5 data: {str(e)}"})
        return False
    return True

def _reflect_get_current_timestamp_utc() -> str:
    """Returns a fixed, unique timestamp string."""
    return "2023-10-28T10:30:00Z"

def _reflect_resolve_l6_policies_from_madaSeed(mada_seed_input: MadaSeed, target_consumer: Dict, presentation_intent_str: str) -> Dict:
    """Baseline: Returns default policy references."""
    l5_field_state_obj = mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L5_field_state_obj
    field_governance_from_l5 = l5_field_state_obj.active_governance if l5_field_state_obj.active_governance else ActiveGovernance()
    
    default_redaction_policy = "L6_Redaction_Default_v1"
    if field_governance_from_l5.policy_set_refs:
        default_redaction_policy = field_governance_from_l5.policy_set_refs[0]

    return {
        "relevance_policy_ref": "L6_Relevance_Default_v1",
        "transformation_policy_ref": "L6_Transformation_Default_v1",
        "adaptation_policy_ref": "L6_Adaptation_Default_v1",
        "redaction_policy_ref": default_redaction_policy,
        "warning_presentation_policy_ref": "L6_WarningPres_Default_v1",
        "output_validation_policy_ref": "L6_OutputValidation_Default_v1",
        "omission_categories_vocab_ref": "lC.MEM.GLOSS.omission_categories_v0.1"
    }

def _reflect_determine_presentation_details_from_madaSeed(mada_seed_input: MadaSeed, l6_policies: Dict) -> Tuple[PayloadMetadataTarget, str, OutputModalityEnum, Optional[str]]:
    """Determines presentation target, intent, modality. Baseline: uses L5 downstream directives or defaults."""
    l5_field_state_obj = mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L5_field_state_obj
    
    target_consumer = PayloadMetadataTarget(consumer_type=ConsumerTypeEnum.HUMAN_UI, consumer_uid_hint=None, channel_hint="Default_Display")
    presentation_intent_str = "Display_Field_Overview"
    output_modality_val = OutputModalityEnum.FORMATTED_TEXT
    target_schema_reference: Optional[str] = None

    if l5_field_state_obj.downstream_directives and l5_field_state_obj.downstream_directives.next_action_recommendation_for_L6:
        recommendation = l5_field_state_obj.downstream_directives.next_action_recommendation_for_L6
        if "LLM_Analysis" in recommendation:
            presentation_intent_str = "Prepare_Context_For_LLM_Analysis"
            target_consumer.consumer_type = ConsumerTypeEnum.AGENT_LLM
            output_modality_val = OutputModalityEnum.STRUCTURED_DATA
        elif "Prepare_Summary_For_UI" in recommendation:
            presentation_intent_str = "Display_Field_Summary_For_UI"
            target_consumer.consumer_type = ConsumerTypeEnum.HUMAN_UI
            output_modality_val = OutputModalityEnum.FORMATTED_TEXT
            
    return target_consumer, presentation_intent_str, output_modality_val, target_schema_reference

def _reflect_select_and_prioritize_content_from_madaSeed(mada_seed_input: MadaSeed, target_consumer: PayloadMetadataTarget, presentation_intent_str: str, relevance_policy_ref: str) -> Dict[str, Any]:
    """Selects content from L5 field state and L4 PA context (if intent matches "Reflect_Persona_Alignment_Status")."""
    selected_data: Dict[str, Any] = {}
    l5_field_state_obj = mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L5_field_state_obj

    try:
        selected_data['field_identity'] = {
            "field_instance_uid": l5_field_state_obj.field_instance_uid,
            "field_type": l5_field_state_obj.field_type,
            "field_topic_summary": l5_field_state_obj.field_topic_summary,
            "field_status": l5_field_state_obj.field_status.name if l5_field_state_obj.field_status else None
        }
        selected_data['l5_diagnostics_for_reflection'] = {
            "l5_epistemic_state": l5_field_state_obj.l5_epistemic_state_of_field_processing.name if l5_field_state_obj.l5_epistemic_state_of_field_processing else None,
            "assessed_cynefin_state": l5_field_state_obj.session_maturity.igd_stage_assessment.name if l5_field_state_obj.session_maturity else None, # Placeholder for actual L5 Cynefin
            "session_maturity": l5_field_state_obj.session_maturity,
            "aac_field_readiness": l5_field_state_obj.aac_field_readiness,
            "momentum_profile": l5_field_state_obj.momentum_profile,
            "dialogue_context": l5_field_state_obj.dialogue_context,
            "brave_space_dynamics": l5_field_state_obj.brave_space_dynamics,
            "field_risk_assessment": l5_field_state_obj.field_risk_assessment
        }

        if presentation_intent_str == "Reflect_Persona_Alignment_Status":
            l4_anchor_state_obj = mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L4_anchor_state_obj
            pa_context_from_anchor = l4_anchor_state_obj.persona_alignment_context_engaged
            if pa_context_from_anchor:
                key_findings: List[KeyLevelFindingSummary] = []
                if pa_context_from_anchor.engaged_level_findings and pa_context_from_anchor.engaged_level_findings.P5_Identity:
                    for finding in pa_context_from_anchor.engaged_level_findings.P5_Identity[:1]: # Example: first P5 finding
                         key_findings.append(KeyLevelFindingSummary(level="P5_Identity", finding_summary=finding.description, original_finding_type=finding.finding_type.name))
                
                alignment_gaps_summary: List[str] = []
                if l4_anchor_state_obj.identified_knowledge_gaps_L4:
                    for gap in l4_anchor_state_obj.identified_knowledge_gaps_L4:
                        if gap.gap_type == KnowledgeGapTypeEnum.PA_LEVEL_STATE:
                            alignment_gaps_summary.append(gap.required_info_description)
                
                selected_data['persona_alignment_snapshot'] = ReflectedPAContextSummary(
                    version="0.1.0",
                    source_pa_profile_ref=pa_context_from_anchor.alignment_profile_ref,
                    source_pa_engagement_status=pa_context_from_anchor.engagement_status.name,
                    key_level_findings_summary=key_findings,
                    alignment_gap_summary=alignment_gaps_summary[:1]
                )
    except Exception as e:
        log_internal_error("_reflect_select_content", {"error": str(e)})
        selected_data["error_during_selection"] = True; selected_data["details"] = str(e)
    return selected_data

def _reflect_apply_transformations(selected_data: Dict[str, Any], output_modality_val: OutputModalityEnum, target_schema_ref: Optional[str], transform_policy_ref: str) -> Tuple[Any, Dict[str, Any]]:
    """Baseline: Formats as simple Markdown text if 'Formatted_Text', else returns selected_data."""
    formatted_content: Any = None
    transformation_hr_meta: Dict[str, Any] = {"simplification_level_hint": SimplificationLevelHintEnum.NONE, "potential_fidelity_loss_areas": []}
    try:
        if output_modality_val == OutputModalityEnum.FORMATTED_TEXT:
            text_parts = [f"### Reflection Payload (L6)\n"]; fi = selected_data.get('field_identity', {})
            text_parts.append(f"**Field:** {fi.get('field_topic_summary', 'N/A')} (Status: {fi.get('field_status', 'N/A')})\n")
            l5d = selected_data.get('l5_diagnostics_for_reflection', {})
            if l5d:
                cynefin_domain_name = l5d.get('assessed_cynefin_state', 'Unknown')
                maturity_stage_name = l5d.get('session_maturity').igd_stage_assessment.name if l5d.get('session_maturity') and l5d.get('session_maturity').igd_stage_assessment else 'N/A'
                text_parts.append(f"**L5 Diagnostics:** Cynefin (conceptual)={cynefin_domain_name}, Maturity={maturity_stage_name}\n")
            pas = selected_data.get('persona_alignment_snapshot')
            if pas and isinstance(pas, ReflectedPAContextSummary): text_parts.append(f"**PA Profile Ref:** {pas.source_pa_profile_ref}\n")
            formatted_content = "\n".join(text_parts); transformation_hr_meta["simplification_level_hint"] = SimplificationLevelHintEnum.MINOR_SUMMARIZATION
        elif output_modality_val == OutputModalityEnum.STRUCTURED_DATA: formatted_content = selected_data
        else:
            formatted_content = {"error_message": f"Unsupported output modality for baseline transformation: {output_modality_val.name}"}
            transformation_hr_meta["simplification_level_hint"] = SimplificationLevelHintEnum.HIGH_SIMPLIFICATION
            transformation_hr_meta["potential_fidelity_loss_areas"].append("Unsupported_Modality_Baseline")
    except Exception as e:
        log_internal_error("_reflect_apply_transformations", {"error": str(e)}); formatted_content = {"error_message": f"Transformation error: {str(e)}"}
        transformation_hr_meta["potential_fidelity_loss_areas"].append("Formatting_Process_Error")
    return formatted_content, transformation_hr_meta

def _reflect_adapt_content_perspective(current_payload_content: Any, target_consumer: PayloadMetadataTarget, adaptation_policy_ref: str) -> Any:
    return current_payload_content

def _reflect_apply_filters_redaction(current_payload_content: Any, redaction_policy_ref: str) -> Tuple[Any, RedactionStatus]:
    return current_payload_content, RedactionStatus(version="0.1.0", redaction_applied=False, redaction_policy_ref=redaction_policy_ref)

def _reflect_surface_diagnostics_and_warnings(l5_diagnostics_selected: Dict[str, Any], warning_presentation_policy_ref: str) -> Tuple[BraveSpaceReflection, List[str]]:
    """Returns (BraveSpaceReflection, List[str] for rep_warnings)"""
    bsd = l5_diagnostics_selected.get('brave_space_dynamics') if isinstance(l5_diagnostics_selected.get('brave_space_dynamics'), BraveSpaceDynamics) else None
    dc = l5_diagnostics_selected.get('dialogue_context') if isinstance(l5_diagnostics_selected.get('dialogue_context'), DialogueContext) else None
    
    brave_space_reflection_obj = BraveSpaceReflection(
        version="0.1.0",
        L5_activation_status_hint=bsd.activation_status.name if bsd and bsd.activation_status else None,
        L5_dissent_strength_hint=dc.dissent_strength.name if dc and dc.dissent_strength else None,
        L5_tension_index_hint=bsd.tension_index if bsd else None,
        L6_transformation_dissent_risk_hint=TransformationDissentRiskHintEnum.MINIMAL,
        L6_representation_discomfort_risk_hint=RepresentationDiscomfortRiskHintEnum.MINIMAL_DISCOMFORT
    )
    l6_representation_warnings_list: List[str] = []
    aac_readiness = l5_diagnostics_selected.get('aac_field_readiness') if isinstance(l5_diagnostics_selected.get('aac_field_readiness'), AACFieldReadiness) else None
    if aac_readiness and aac_readiness.die_support_level == AACSupportLevelEnum.NONE:
        l6_representation_warnings_list.append("Low_L5_AAC_DIE_Support_Noted_L6")
    return brave_space_reflection_obj, l6_representation_warnings_list

def _reflect_assess_hr_cynefin_transition(l5_cynefin_state_name_selected: Optional[str], output_modality_val: OutputModalityEnum, simplification_level_val: SimplificationLevelHintEnum) -> Optional[CynefinZoneTransition]:
    l5_domain_name_str = l5_cynefin_state_name_selected or CynefinDomainEnum.UNKNOWN.value
    risk_level_str = "Minimal"; to_domain_hint_str = l5_domain_name_str; rationale: Optional[str] = None
    try:
        if l5_domain_name_str in [CynefinDomainEnum.CHAOTIC.value, CynefinDomainEnum.COMPLEX.value] and \
           simplification_level_val in [SimplificationLevelHintEnum.SIGNIFICANT_ABSTRACTION, SimplificationLevelHintEnum.HIGH_SIMPLIFICATION]:
            risk_level_str = "High"; to_domain_hint_str = CynefinDomainEnum.COMPLICATED.value
            rationale = "High simplification of L5 state may shift perceived Cynefin domain."
        if risk_level_str != "Minimal":
            return CynefinZoneTransition(version="0.1.1", from_domain=l5_domain_name_str, to_formatted_domain_hint=to_domain_hint_str, transition_risk_level=risk_level_str, rationale=rationale)
    except Exception as e:
        log_internal_error("_reflect_assess_hr_cynefin_transition", {"error": str(e)})
        return CynefinZoneTransition(version="0.1.1", from_domain=l5_domain_name_str, to_formatted_domain_hint=l5_domain_name_str, transition_risk_level="Minimal", rationale="Error during transition assessment.")
    return None

def _reflect_validate_final_payload(payload_obj: L6ReflectionPayloadObj, target_schema_ref: Optional[str], output_modality_val: OutputModalityEnum, validation_policy_ref: str) -> bool:
    content_section = payload_obj.payload_content; set_fields = 0; correct_field_set = False
    if output_modality_val == OutputModalityEnum.FORMATTED_TEXT and content_section.formatted_text is not None: set_fields += 1; correct_field_set = True
    elif output_modality_val == OutputModalityEnum.STRUCTURED_DATA and content_section.structured_data is not None: set_fields += 1; correct_field_set = True
    elif output_modality_val == OutputModalityEnum.MULTIMODAL_PACKAGE and content_section.multimodal_package is not None: set_fields += 1; correct_field_set = True
    elif output_modality_val == OutputModalityEnum.API_PAYLOAD and content_section.api_payload is not None: set_fields += 1; correct_field_set = True
    return set_fields == 1 and correct_field_set

def _reflect_determine_final_l6_state(l6_validation_ok: bool, reflection_surface_obj: ReflectionSurface, l6_policies: Dict) -> str:
    if not l6_validation_ok: return L6EpistemicStateEnum.LCL_PRESENTATION_FORMATERROR.value
    if reflection_surface_obj.cynefin_zone_transition and reflection_surface_obj.cynefin_zone_transition.transition_risk_level in ["High", "Critical"]:
        return L6EpistemicStateEnum.LCL_PRESENTATION_HIGHRISKSIMPLIFICATION.value
    if reflection_surface_obj.representation_warning_flags: return L6EpistemicStateEnum.REFLECTION_PREPARED_WITH_WARNINGS.value
    return L6EpistemicStateEnum.REFLECTION_PREPARED.value

def _reflect_assemble_hr_payload_parts(policies: Dict, redaction_obj_model: RedactionStatus, transform_hr_meta_dict: Dict, l5_diagnostics_selected_dict: Dict, brave_space_reflection_obj_l6_model: BraveSpaceReflection, cynefin_transition_assessed_obj_model: Optional[CynefinZoneTransition], persona_alignment_snapshot_obj_model: Optional[ReflectedPAContextSummary]) -> Tuple[TransformationMetadata, ReflectionSurface, Optional[ReflectedPAContextSummary], List[str]]:
    omission_rationale_val = OmissionRationaleCodeEnum.REDACTION_POLICY if redaction_obj_model.redaction_applied else None
    omitted_categories_list_enum = [OmittedContentCategoryEnum(cat) for cat in redaction_obj_model.redacted_categories_hint if cat in OmittedContentCategoryEnum._value2member_map_]
    omitted_content_summary_obj = OmittedContentSummary(version="0.1.1", omission_applied=redaction_obj_model.redaction_applied, omitted_categories=omitted_categories_list_enum, omission_rationale_code=omission_rationale_val)
    transformation_meta_model = TransformationMetadata(version="0.1.1", selection_profile_applied=policies.get("relevance_policy_ref"), transformation_profile_applied=policies.get("transformation_policy_ref"), adaptation_profile_applied=policies.get("adaptation_policy_ref"), redaction_status=redaction_obj_model, simplification_level_hint=SimplificationLevelHintEnum(transform_hr_meta_dict.get("simplification_level_hint", "None")), potential_fidelity_loss_areas=transform_hr_meta_dict.get("potential_fidelity_loss_areas", []), omitted_content_summary=omitted_content_summary_obj)
    l5_cynefin_domain_name_from_selection = l5_diagnostics_selected_dict.get('assessed_cynefin_state', CynefinDomainEnum.UNKNOWN.value)
    try: l5_cynefin_domain_for_reflection = CynefinDomainEnum(l5_cynefin_domain_name_from_selection)
    except ValueError: l5_cynefin_domain_for_reflection = CynefinDomainEnum.UNKNOWN; log_internal_warning("_reflect_assemble_hr_payload_parts", {"warning":f"Invalid Cynefin domain string '{l5_cynefin_domain_name_from_selection}' from L5 selection."})
    l6_rep_warnings = list(set(transformation_meta_model.potential_fidelity_loss_areas))
    if cynefin_transition_assessed_obj_model and cynefin_transition_assessed_obj_model.transition_risk_level in ["High", "Critical"]: l6_rep_warnings.append("HighRisk_Cynefin_Representation_Shift_L6_Assembled")
    reflection_surf_model = ReflectionSurface(version="0.1.2", assessed_cynefin_state=AssessedCynefinState(version="0.1.0", domain=l5_cynefin_domain_for_reflection), cynefin_zone_transition=cynefin_transition_assessed_obj_model, representation_warning_flags=list(set(l6_rep_warnings)), brave_space_reflection=brave_space_reflection_obj_l6_model)
    persona_flags: List[str] = []
    if redaction_obj_model.redaction_applied: persona_flags.append("May_Impact_Trust_Due_To_Redaction_L6_Assembled")
    if transformation_meta_model.simplification_level_hint != SimplificationLevelHintEnum.NONE: persona_flags.append("Simplification_May_Obscure_Context_L6_Assembled")
    return transformation_meta_model, reflection_surf_model, persona_alignment_snapshot_obj_model, persona_flags

# --- Main reflect_boom Process Function ---
def reflect_boom_process(mada_seed_input: MadaSeed) -> MadaSeed:
    current_time_fail_dt = dt.fromisoformat(_reflect_get_current_timestamp_utc().replace('Z', '+00:00'))
    if not _reflect_validate_l5_data_in_madaSeed(mada_seed_input):
        error_detail_msg = "Invalid or incomplete L5 data for L6 processing."
        log_critical_error("reflect_boom_process L5 Data Error", {"trace_id": mada_seed_input.seed_id if mada_seed_input else "Unknown", "error": error_detail_msg})
        if mada_seed_input:
            mada_seed_input.trace_metadata.L6_trace = L6Trace(version_L6_trace_schema="0.1.0", sop_name="lC.SOP.reflect_boom", completion_timestamp_L6=current_time_fail_dt, epistemic_state_L6=L6EpistemicStateEnum.LCL_PRESENTATION_REQUIRES_L5STATE, error_details=error_detail_msg)
            error_l6_payload = L6ReflectionPayloadObj(version="0.1.6", l6_epistemic_state=L6EpistemicStateEnum.LCL_PRESENTATION_REQUIRES_L5STATE, redaction_applied_summary=False, payload_metadata=PayloadMetadata(generation_sop="lC.SOP.reflect_boom", generation_timestamp=current_time_fail_dt, source_trace_id=mada_seed_input.seed_id, presentation_target=PayloadMetadataTarget(consumer_type=ConsumerTypeEnum.SYSTEM_MODULE), presentation_intent="ErrorState_L6_ReqL5", output_modality=OutputModalityEnum.STRUCTURED_DATA, error_details=f"L6 aborted: {error_detail_msg}"), transformation_metadata=TransformationMetadata(redaction_status=RedactionStatus(redaction_applied=False), omitted_content_summary=OmittedContentSummary(omission_applied=False)), reflection_surface=ReflectionSurface(assessed_cynefin_state=AssessedCynefinState(domain=CynefinDomainEnum.UNKNOWN), brave_space_reflection=BraveSpaceReflection()), payload_content=PayloadContent(structured_data={"error": "L6 Error: Invalid L5 input."}))
            mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L6_reflection_payload.L6_reflection_payload_obj = error_l6_payload
        return mada_seed_input

    trace_id = mada_seed_input.seed_id
    l5_field_state_obj = mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L5_field_state_obj
    l6_reflection_payload_obj_draft = L6ReflectionPayloadObj(version="0.1.6", l6_epistemic_state=L6EpistemicStateEnum.LCL_FAILURE_INTERNAL_L6, redaction_applied_summary=False, payload_metadata=PayloadMetadata(generation_sop="lC.SOP.reflect_boom", generation_timestamp=current_time_fail_dt, source_trace_id=trace_id, presentation_target=PayloadMetadataTarget(consumer_type=ConsumerTypeEnum.SYSTEM_MODULE), presentation_intent="InitState_L6", output_modality=OutputModalityEnum.STRUCTURED_DATA), transformation_metadata=TransformationMetadata(redaction_status=RedactionStatus(redaction_applied=False), omitted_content_summary=OmittedContentSummary(omission_applied=False)), reflection_surface=ReflectionSurface(assessed_cynefin_state=AssessedCynefinState(domain=CynefinDomainEnum.UNKNOWN), brave_space_reflection=BraveSpaceReflection()), payload_content=PayloadContent(structured_data={"status":"Initializing L6 Payload"}))
    
    try:
        temp_target_consumer_model, temp_presentation_intent, _, _ = _reflect_determine_presentation_details_from_madaSeed(mada_seed_input, {})
        active_l6_policies = _reflect_resolve_l6_policies_from_madaSeed(mada_seed_input, temp_target_consumer_model.model_dump(), temp_presentation_intent)
        final_target_consumer, final_presentation_intent, final_output_modality, final_target_schema_ref = _reflect_determine_presentation_details_from_madaSeed(mada_seed_input, active_l6_policies)
        content_selected_for_l6 = _reflect_select_and_prioritize_content_from_madaSeed(mada_seed_input, final_target_consumer, final_presentation_intent, active_l6_policies.get('relevance_policy_ref', ''))
        if content_selected_for_l6.get("error_in_selection"): raise ValueError(f"L6 Content selection failed: {content_selected_for_l6.get('details')}")
        payload_main_content, transformation_hr_meta_details_dict = _reflect_apply_transformations(content_selected_for_l6, final_output_modality, final_target_schema_ref, active_l6_policies.get('transformation_policy_ref', ''))
        if isinstance(payload_main_content, dict) and payload_main_content.get("error_message"): raise ValueError(payload_main_content.get("error_message"))
        content_adapted_for_perspective = _reflect_adapt_content_perspective(payload_main_content, final_target_consumer, active_l6_policies.get('adaptation_policy_ref', ''))
        content_after_redaction, redaction_hr_metadata_model = _reflect_apply_filters_redaction(content_adapted_for_perspective, active_l6_policies.get('redaction_policy_ref', ''))
        l5_diagnostics_from_selection = content_selected_for_l6.get('l5_diagnostics_for_reflection', {})
        brave_space_reflection_model, l6_representation_warning_list = _reflect_surface_diagnostics_and_warnings(l5_diagnostics_from_selection, active_l6_policies.get('warning_presentation_policy_ref', ''))
        l5_cynefin_for_transition = l5_diagnostics_from_selection.get('assessed_cynefin_state', CynefinDomainEnum.UNKNOWN.value)
        cynefin_transition_assessment_model = _reflect_assess_hr_cynefin_transition(l5_cynefin_for_transition, final_output_modality, SimplificationLevelHintEnum(transformation_hr_meta_details_dict.get('simplification_level_hint', 'None')))
        hr_transformation_meta_model, hr_reflection_surface_model, reflected_pa_summary_model, persona_flags_list = _reflect_assemble_hr_payload_parts(policies=active_l6_policies, redaction_obj_model=redaction_hr_metadata_model, transform_hr_meta_dict=transformation_hr_meta_details_dict, l5_diagnostics_selected_dict=l5_diagnostics_from_selection, brave_space_reflection_obj_l6_model=brave_space_reflection_model, cynefin_transition_assessed_obj_model=cynefin_transition_assessment_model, persona_alignment_snapshot_obj_model=content_selected_for_l6.get('persona_alignment_snapshot'))
        
        temp_payload_content_model = PayloadContent()
        if final_output_modality == OutputModalityEnum.FORMATTED_TEXT: temp_payload_content_model.formatted_text = content_after_redaction
        elif final_output_modality == OutputModalityEnum.STRUCTURED_DATA: temp_payload_content_model.structured_data = content_after_redaction
        
        temp_l6_payload_for_validation = L6ReflectionPayloadObj(version="0.1.6", l6_epistemic_state=L6EpistemicStateEnum.REFLECTION_PREPARED, redaction_applied_summary=redaction_hr_metadata_model.redaction_applied, payload_metadata=PayloadMetadata(generation_sop="lC.SOP.reflect_boom", generation_timestamp=dt.now(timezone.utc), source_trace_id=trace_id, presentation_target=final_target_consumer, presentation_intent=final_presentation_intent, output_modality=final_output_modality), transformation_metadata=hr_transformation_meta_model, reflection_surface=hr_reflection_surface_model, payload_content=temp_payload_content_model)
        l6_output_validation_ok = _reflect_validate_final_payload(temp_l6_payload_for_validation, final_target_schema_ref, final_output_modality, active_l6_policies.get('output_validation_policy_ref', ''))
        final_l6_epistemic_state_str = _reflect_determine_final_l6_state(l6_output_validation_ok, hr_reflection_surface_model, active_l6_policies)
        final_l6_epistemic_state_enum = L6EpistemicStateEnum(final_l6_epistemic_state_str)
        current_time_for_payload_dt = dt.fromisoformat(_reflect_get_current_timestamp_utc().replace('Z', '+00:00'))
        
        l6_reflection_payload_obj_draft = L6ReflectionPayloadObj(
            version="0.1.6", l6_epistemic_state=final_l6_epistemic_state_enum,
            redaction_applied_summary=redaction_hr_metadata_model.redaction_applied,
            payload_metadata=PayloadMetadata(generation_sop="lC.SOP.reflect_boom", generation_timestamp=current_time_for_payload_dt, source_trace_id=trace_id, source_field_instance_uid=l5_field_state_obj.field_instance_uid, source_field_state_version_ref=l5_field_state_obj.version, presentation_target=final_target_consumer, presentation_intent=final_presentation_intent, output_modality=final_output_modality, target_schema_ref=final_target_schema_ref, L6_processing_confidence=0.75 if l6_output_validation_ok and not final_l6_epistemic_state_enum.name.startswith("LCL") else 0.3),
            transformation_metadata=hr_transformation_meta_model, reflection_surface=hr_reflection_surface_model,
            reflected_pa_context_summary=reflected_pa_summary_model, persona_exposure_flags=persona_flags_list,
            field_diagnostics_summary_hints=FieldDiagnosticsSummaryHints( L5_epistemic_state_hint=l5_diagnostics_from_selection.get('l5_epistemic_state'), maturity_stage_hint=l5_diagnostics_from_selection.get('session_maturity').igd_stage_assessment.name if l5_diagnostics_from_selection.get('session_maturity') and l5_diagnostics_from_selection.get('session_maturity').igd_stage_assessment else None, aac_visibility_score_hint=l5_diagnostics_from_selection.get('aac_field_readiness').aac_visibility_score if l5_diagnostics_from_selection.get('aac_field_readiness') else None),
            payload_content=temp_payload_content_model, supplemental_context_refs=[], next_action_directives=[]
        )
        mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L6_reflection_payload.L6_reflection_payload_obj = l6_reflection_payload_obj_draft
        l6_trace_obj = L6Trace(version_L6_trace_schema="0.1.0", sop_name="lC.SOP.reflect_boom", completion_timestamp_L6=current_time_for_payload_dt, epistemic_state_L6=final_l6_epistemic_state_enum, L6_presentation_target_consumer_type=final_target_consumer.consumer_type, L6_presentation_intent_resolved=final_presentation_intent, L6_output_modality_used=final_output_modality, L6_processing_confidence_score_from_payload=l6_reflection_payload_obj_draft.payload_metadata.L6_processing_confidence, L6_redaction_applied_summary_from_payload=l6_reflection_payload_obj_draft.redaction_applied_summary, L6_simplification_level_hint_applied=hr_transformation_meta_model.simplification_level_hint, L6_cynefin_transition_risk_assessed=hr_reflection_surface_model.cynefin_zone_transition.transition_risk_level if hr_reflection_surface_model.cynefin_zone_transition else None, L6_applied_policy_refs=[active_l6_policies.get(p) for p in active_l6_policies if active_l6_policies.get(p) and isinstance(active_l6_policies.get(p), str)])
        mada_seed_input.trace_metadata.L6_trace = l6_trace_obj
        return mada_seed_input
    except Exception as critical_process_error:
        error_msg = f"Critical L6 Failure: {str(critical_process_error)}"
        log_critical_error("Reflect Boom Process Failed Critically", {"trace_id": trace_id, "error": error_msg})
        current_time_crit_fail_dt = dt.fromisoformat(_reflect_get_current_timestamp_utc().replace('Z', '+00:00'))
        mada_seed_input.trace_metadata.L6_trace = L6Trace(version_L6_trace_schema="0.1.0", sop_name="lC.SOP.reflect_boom", completion_timestamp_L6=current_time_crit_fail_dt, epistemic_state_L6=L6EpistemicStateEnum.LCL_FAILURE_INTERNAL_L6, error_details=error_msg)
        error_l6_payload = L6ReflectionPayloadObj(version="0.1.6", l6_epistemic_state=L6EpistemicStateEnum.LCL_FAILURE_INTERNAL_L6, redaction_applied_summary=False, payload_metadata=PayloadMetadata(generation_sop="lC.SOP.reflect_boom", generation_timestamp=current_time_crit_fail_dt, source_trace_id=trace_id, presentation_target=PayloadMetadataTarget(consumer_type=ConsumerTypeEnum.SYSTEM_MODULE), presentation_intent="ErrorState_L6_Internal", output_modality=OutputModalityEnum.STRUCTURED_DATA, error_details=error_msg), transformation_metadata=TransformationMetadata(redaction_status=RedactionStatus(redaction_applied=False), omitted_content_summary=OmittedContentSummary(omission_applied=False)), reflection_surface=ReflectionSurface(assessed_cynefin_state=AssessedCynefinState(domain=CynefinDomainEnum.UNKNOWN), brave_space_reflection=BraveSpaceReflection()), payload_content=PayloadContent(structured_data={"error": f"L6 Error: {error_msg}"}))
        mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L6_reflection_payload.L6_reflection_payload_obj = error_l6_payload
        return mada_seed_input

if __name__ == '__main__':
    from sop_l1_startle import startle_process
    from sop_l2_frame_click import frame_click_process
    from sop_l3_keymap_click import keymap_click_process
    from sop_l4_anchor_click import anchor_click_process
    from sop_l5_field_click import field_click_process

    print("--- Running sop_l6_reflect_boom.py example ---")
    example_input_event = {"reception_timestamp_utc_iso": "2023-11-01T05:00:00Z", "origin_hint": "Test_Reflect_Input", "data_components": [{"role_hint": "primary_text", "content_handle_placeholder": "Reflect boom test content for L6. This field has some risks.", "size_hint": 50, "type_hint": "text/plain"}]}
    l1_seed = startle_process(example_input_event)
    l2_seed = frame_click_process(l1_seed)
    l3_seed = keymap_click_process(l2_seed)
    l4_seed = anchor_click_process(l3_seed)
    l5_seed = field_click_process(l4_seed)
    if l5_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L5_field_state_obj.session_maturity:
        l5_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L5_field_state_obj.session_maturity.igd_stage_assessment = IGDStageAssessmentEnum.S2_EXPLORING_IDS_INEQUALITIES
    if l5_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L5_field_state_obj.downstream_directives:
        l5_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L5_field_state_obj.downstream_directives.next_action_recommendation_for_L6 = "Prepare_Summary_For_UI"
    print(f"\nL5 Epistemic State: {l5_seed.trace_metadata.L5_trace.epistemic_state_L5.name if l5_seed.trace_metadata.L5_trace.epistemic_state_L5 else 'N/A'}")
    if l5_seed.trace_metadata.L5_trace.epistemic_state_L5.name not in ["FIELD_INSTANTIATED_NEW", "FIELD_UPDATED_EXISTING"]: print("L5 processing did not result in a FIELD_ state suitable for L6, L6 test might not be fully meaningful.")
    print("\nCalling reflect_boom_process with L5 MadaSeed...")
    l6_seed = reflect_boom_process(l5_seed)
    if l6_seed:
        l6_payload_obj = l6_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L4_anchor_state.L5_field_state.L6_reflection_payload.L6_reflection_payload_obj
        print(f"\nL6 Reflection Payload Object Version: {l6_payload_obj.version}")
        print(f"L6 Epistemic State: {l6_payload_obj.l6_epistemic_state.name if l6_payload_obj.l6_epistemic_state else 'N/A'}")
        print(f"L6 Payload Presentation Intent: {l6_payload_obj.payload_metadata.presentation_intent}")
        print(f"L6 Payload Output Modality: {l6_payload_obj.payload_metadata.output_modality.name if l6_payload_obj.payload_metadata.output_modality else 'N/A'}")
        if l6_payload_obj.payload_content.formatted_text: print(f"L6 Formatted Text Content (excerpt): {l6_payload_obj.payload_content.formatted_text[:150]}...")
        if l6_payload_obj.reflection_surface.assessed_cynefin_state: print(f"L6 Reflected Cynefin State (from L5): {l6_payload_obj.reflection_surface.assessed_cynefin_state.domain.name if l6_payload_obj.reflection_surface.assessed_cynefin_state.domain else 'N/A'}")
        if l6_payload_obj.transformation_metadata: print(f"L6 Simplification Level: {l6_payload_obj.transformation_metadata.simplification_level_hint.name if l6_payload_obj.transformation_metadata.simplification_level_hint else 'N/A'}")
        l6_trace_meta = l6_seed.trace_metadata.L6_trace
        print(f"\nL6 Trace Version: {l6_trace_meta.version_L6_trace_schema}")
        print(f"L6 Trace SOP Name: {l6_trace_meta.sop_name}")
        print(f"L6 Trace Epistemic State: {l6_trace_meta.epistemic_state_L6.name if l6_trace_meta.epistemic_state_L6 else 'N/A'}")
    print("\n--- sop_l6_reflect_boom.py example run complete ---")
