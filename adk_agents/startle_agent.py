import time
import os
from typing import List, Optional, Dict, Any, ClassVar
from pydantic import BaseModel, Field
from google.adk.agents import Agent
from datetime import datetime, timezone

from lc_python_core.schemas.mada_schema import (
    MadaSeed,
    RawSignal,
    SignalComponentMetadataL1,
    EncodingStatusL1Enum,
    L1StartleContextObj,
    L1EpistemicStateOfStartleEnum,
    SeedContent,
    L1StartleReflex,
    L2FrameTypeObj,
    L2EpistemicStateOfFramingEnum,
    InputClassL2Enum,
    TemporalHintProvenanceL2Enum,
    L2ValidationStatusOfFrameEnum,
    L3SurfaceKeymapObj,
    ContentEncodingStatusL3Enum,
    LexicalAffordances,
    SyntacticHints,
    PragmaticAffectiveAffordances,
    RelationalLinkingMarkers,
    L3Flags,
    L4AnchorStateObj,
    L4EpistemicStateOfAnchoringEnum,
    AACAssessabilityMap,
    ConsequenceVector,
    PersonaAlignmentContextEngaged,
    PAEngagementStatusEnum,
    TraceThreadingContext,
    ResolutionSummary,
    InterpretationSummaryL4,
    ValidationSummaryL4,
    L4ValidationStatusEnum,
    L5FieldStateObj,
    L5EpistemicStateOfFieldProcessingEnum,
    FieldStatusEnum,
    FieldParticipant,
    ParticipantEngagementReadinessEnum,
    DialogueContext,
    DialogueModeEnum,
    DissentStrengthEnum,
    AACFieldReadiness,
    AACSupportLevelEnum,
    DialogueStructureSupportEnum,
    WorkManagement,
    FieldMaturity, 
    IGDStageAssessmentEnum,
    L6ReflectionPayloadObj,
    L6EpistemicStateEnum,
    PayloadMetadata,
    ConsumerTypeEnum,
    OutputModalityEnum,
    TransformationMetadata,
    RedactionStatus,
    OmittedContentSummary,
    OmissionRationaleCodeEnum, 
    OmittedContentCategoryEnum, 
    SimplificationLevelHintEnum,
    ReflectionSurface,
    AssessedCynefinState,
    CynefinDomainEnum,
    BraveSpaceReflection,
    TransformationDissentRiskHintEnum,
    RepresentationDiscomfortRiskHintEnum,
    PayloadContent,
    L7EncodedApplication,
    L7EpistemicStateEnum, 
    SeedQAQC,
    SeedIntegrityStatusEnum,
    QAQCCheckCategoryCodeEnum,
    QAQCSeverityLevelEnum,
    IntegrityFinding,
    TraceMetadata,
    L1Trace,
    L2Trace,
    L3Trace,
    L4Trace,
    L5Trace,
    L6Trace,
    L7Trace,
    TemporalHintL2, 
    CommunicationContextL2, 
    DetectedLanguage, 
    KeywordMention, 
    EntityMentionRaw, 
    NumericalQuantityMention, 
    TemporalExpressionMention, 
    QuantifierQualifierMention, 
    QuantifierQualifierTypeEnum, 
    NegationMarker, 
    EmojiMention, 
    FormalityHint, 
    SentimentHint, 
    SentimentPolarityEnum, 
    PolitenessMarkers, 
    UrgencyMarkers, 
    PowerDynamicCue, 
    PowerDynamicCueTypeEnum, 
    PowerDynamicMarkers, 
    InteractionPatternAffordance, 
    ShallowGoalIntentAffordance, 
    ActorRole, 
    ActorRoleHintEnum, 
    ActorRoleHint, 
    ExplicitRelationalPhrases, 
    ExplicitReferenceMarkers, 
    UrlMentions, 
    PriorTraceReference, 
    PriorTraceReferenceTypeEnum, 
    StatisticalProperties, 
    StatisticalValue, 
    StatisticalScore, 
    L3FlagDetail, 
    GriceanViolationHints, 
    FindingTypeEnum, 
    LevelFindingItem, 
    EngagedLevelFindings, 
    ResolvedEntity, 
    ResolvedConcept, 
    CoreferenceLink, 
    TemporalSummaryL4, 
    RelationshipSummaryL4, 
    IdentifiedKnowledgeGapL4, 
    KnowledgeGapTypeEnum, 
    KnowledgeGapPriorityEnum, 
    FieldTemporalContext, 
    ParticipantInteractionStats, 
    InteractionPatternSummary, 
    ActiveGovernance, 
    MomentumProfile, 
    AxisMomentum, 
    EpistemicFlowDirectionEnum, 
    LinkedBacklogItem, 
    PBIStatusInFieldEnum, 
    RiskIndicator, 
    RiskSeverityHintEnum, 
    LCLForecastForField, 
    FieldRiskAssessment, 
    BraveSpaceDynamics, 
    BraveSpaceActivationStatusEnum, 
    FieldObjectives, 
    SharedTarget, 
    CurrentTraceSOPProvenance, 
    DownstreamDirectives, 
    PayloadMetadataTarget, 
    CynefinZoneTransition, 
    KeyLevelFindingSummary, 
    ReflectedPAContextSummary, 
    FieldDiagnosticsSummaryHints, 
    MultimodalPackageItem, 
    NextActionDirective, 
    L7DirectiveTypeEnum, 
    L7Backlog, 
    PBIEntry, 
    L7PbiTypeEnum, 
    AlignmentVector, 
    L7TemporalPlaneEnum, 
    L7DimensionalPlaneEnum, 
    ParticipationRole, 
    L7RoleTypeEnum, 
    L7PBIStatusHintEnum, 
    SeedOptions, 
    SeedOption, 
    SeedOutputItem, 
    L7OutputConsumerTypeEnum, 
    L7OutputModalityEnum, 
    SummaryOfChecksPerformed, 
    L2FrameType, 
    L3SurfaceKeymap, 
    L4AnchorState, 
    L5FieldState, 
    L6ReflectionPayload, 
)

LOG_PATH = "Q:/pinokio/api/learnt.cloud/logs" 
os.makedirs(LOG_PATH, exist_ok=True)
LOG_FILE = os.path.join(LOG_PATH, f"startle_{int(time.time())}.log")

def log(message: str):
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(message.strip() + "\n")

class DataComponent(BaseModel):
    role_hint: str
    content_handle_placeholder: str
    size_hint: int
    type_hint: str

class StartleInputModel(BaseModel):
    reception_timestamp_utc_iso: str
    origin_hint: Optional[str] = "UNKNOWN_ORIGIN"
    data_components: List[DataComponent] = Field(..., min_items=1)

class StartleAgent(Agent):
    name: str = "StartleAgent"
    model: ClassVar = StartleInputModel

    def _startle_generate_crux_uid(self, category: str, context: Optional[Dict[str, Any]] = None) -> str:
        import uuid
        uid = f"urn:crux:uid::{category}:{uuid.uuid4().hex[:12]}"
        log(f"[UID] Generated {uid} for category={category}")
        return uid

    def _create_double_fallback_mada_seed(self, seed_id: str, trace_id: str, original_error_type: str, original_error_msg: str, fallback_error_type: str, fallback_error_msg: str) -> MadaSeed:
        log(f"[DoubleFallback] Creating double fallback MadaSeed for seed_id={seed_id}, trace_id={trace_id}")
        now = datetime.now(timezone.utc)
        double_error_summary = f"DOUBLE_FALLBACK: OriginalError: {original_error_type} - {original_error_msg}, FallbackError: {fallback_error_type} - {fallback_error_msg}"

        fallback_raw_signal_id = self._startle_generate_crux_uid("double_fallback_raw_signal")
        raw_signals = [RawSignal(raw_input_id=fallback_raw_signal_id, raw_input_signal=double_error_summary)]

        l1_signal_meta_uid = self._startle_generate_crux_uid("double_fallback_signal_meta")
        l1_startle_context_obj = L1StartleContextObj(
            version="0.1.0",
            L1_epistemic_state_of_startle=L1EpistemicStateOfStartleEnum.LCL_FAILURE_INTERNAL_L1,
            trace_creation_time_L1=now,
            signal_components_metadata_L1=[SignalComponentMetadataL1(
                component_role_L1="double_fallback_error_signal",
                raw_signal_ref_uid_L1=l1_signal_meta_uid,
                byte_size_hint_L1=len(double_error_summary.encode('utf-8')),
                encoding_status_L1=EncodingStatusL1Enum.UNKNOWN_L1,
                media_type_hint_L1="text/plain"
            )],
            error_details=double_error_summary,
            input_origin_L1="DOUBLE_FALLBACK_GENERATION"
        )

        l2_frame_type_obj_instance = L2FrameTypeObj(version="0.1.0", L2_epistemic_state_of_framing=L2EpistemicStateOfFramingEnum.LCL_FAILURE_INTERNAL_L2, error_details=double_error_summary)
        
        # Create L3-L7 ...Obj instances primarily for TraceMetadata in this double fallback
        l3_surface_keymap_obj_instance = L3SurfaceKeymapObj(version="0.1.0", lexical_affordances=LexicalAffordances(), syntactic_hints=SyntacticHints(), pragmatic_affective_affordances=PragmaticAffectiveAffordances(), relational_linking_markers=RelationalLinkingMarkers(), L3_flags=L3Flags(low_confidence_overall_flag=L3FlagDetail(detected=True)), error_details=double_error_summary)
        l4_anchor_state_obj_instance = L4AnchorStateObj(
            version="0.2.17", 
            l4_epistemic_state_of_anchoring=L4EpistemicStateOfAnchoringEnum.LCL_FAILURE_INTERNAL_L4,
            overall_anchor_confidence=0.0, # Default
            AACAssessabilityMap=None, # Explicitly None
            persona_alignment_context_engaged=None, # Explicitly None
            trace_threading_context=None, # Explicitly None
            resolution_summary=None, # Explicitly None
            interpretation_summary_L4=None, # Explicitly None
            validation_summary_L4=ValidationSummaryL4( # Required
                overall_status_L4=L4ValidationStatusEnum.FAILURE, 
                key_anomaly_flags_L4=["DoubleFallbackCreation_L4AnchorStateObj_Minimal"]
            ),
            error_details=double_error_summary,
            l4_anchoring_completion_time=now 
        )
        l5_field_state_obj_instance = L5FieldStateObj(version="0.2.0", l5_epistemic_state_of_field_processing=L5EpistemicStateOfFieldProcessingEnum.LCL_FAILURE_INTERNAL_L5, error_details=double_error_summary, field_participants=[FieldParticipant(persona_uid=self._startle_generate_crux_uid("double_fallback_participant"), role_in_field="placeholder_error_role", engagement_readiness=ParticipantEngagementReadinessEnum.UNKNOWN)])
        l6_reflection_payload_obj_instance = L6ReflectionPayloadObj(version="0.1.6", l6_epistemic_state=L6EpistemicStateEnum.LCL_FAILURE_INTERNAL_L6, redaction_applied_summary=False, payload_metadata=PayloadMetadata(generation_sop="lC.SOP.reflect_boom", generation_timestamp=now, source_trace_id=trace_id, presentation_target=PayloadMetadataTarget(consumer_type=ConsumerTypeEnum.SYSTEM_MODULE), presentation_intent="double_fallback_error_reporting", output_modality=OutputModalityEnum.STRUCTURED_DATA), transformation_metadata=TransformationMetadata(version="0.1.1", redaction_status=RedactionStatus(version="0.1.0", redaction_applied=False), omitted_content_summary=OmittedContentSummary(version="0.1.1", omission_applied=False, omitted_categories=[], omission_rationale_code=OmissionRationaleCodeEnum.NULL)), reflection_surface=ReflectionSurface(version="0.1.2", assessed_cynefin_state=AssessedCynefinState(version="0.1.0",domain=CynefinDomainEnum.DISORDER), brave_space_reflection=BraveSpaceReflection(version="0.1.0", L6_transformation_dissent_risk_hint=TransformationDissentRiskHintEnum.MINIMAL, L6_representation_discomfort_risk_hint=RepresentationDiscomfortRiskHintEnum.MINIMAL_DISCOMFORT)), payload_content=PayloadContent(version="0.1.1", structured_data={"error": double_error_summary}), error_details=double_error_summary)
        l7_encoded_application_instance = L7EncodedApplication(version_L7_payload="0.1.1")

        # The container chain (l2_frame_type_container etc.) is built for potential TraceMetadata use,
        # but SeedContent.L1_startle_reflex.L2_frame_type will use L2FrameTypeObj directly.
        
        seed_content = SeedContent(
            raw_signals=raw_signals,
            L1_startle_reflex=L1StartleReflex(
                L1_startle_context_obj=l1_startle_context_obj, # Corrected variable name
                L2_frame_type=l2_frame_type_obj_instance 
            )
        )

        trace_metadata = TraceMetadata(
            trace_id=trace_id,
            L1_trace=L1Trace(version_L1_trace_schema="0.1.0", sop_name="lC.SOP.startle", completion_timestamp_L1=now, epistemic_state_L1=L1EpistemicStateOfStartleEnum.LCL_FAILURE_INTERNAL_L1, L1_trace_creation_time_from_context=now, L1_signal_component_count=1, error_detail=double_error_summary),
            L2_trace=L2Trace(version_L2_trace_schema="0.1.0", sop_name="lC.SOP.frame_click", completion_timestamp_L2=now, epistemic_state_L2=l2_frame_type_obj_instance.L2_epistemic_state_of_framing, error_detail=double_error_summary), # Use obj_instance
            L3_trace=L3Trace(version_L3_trace_schema="0.1.0", sop_name="lC.SOP.keymap_click", completion_timestamp_L3=now, epistemic_state_L3="LCL-Failure-Internal_L3_Double_Fallback", error_details=double_error_summary),
            L4_trace=L4Trace(version_L4_trace_schema="0.1.0", sop_name="lC.SOP.anchor_click", completion_timestamp_L4=now, epistemic_state_L4=L4EpistemicStateOfAnchoringEnum.LCL_FAILURE_INTERNAL_L4, error_details=double_error_summary),
            L5_trace=L5Trace(version_L5_trace_schema="0.1.0", sop_name="lC.SOP.field_click", completion_timestamp_L5=now, epistemic_state_L5=L5EpistemicStateOfFieldProcessingEnum.LCL_FAILURE_INTERNAL_L5, error_details=double_error_summary),
            L6_trace=L6Trace(version_L6_trace_schema="0.1.0", sop_name="lC.SOP.reflect_boom", completion_timestamp_L6=now, epistemic_state_L6=L6EpistemicStateEnum.LCL_FAILURE_INTERNAL_L6, error_details=double_error_summary),
            L7_trace=L7Trace(version_L7_trace_schema="0.1.0", sop_name="lC.SOP.apply_done", completion_timestamp_L7=now, epistemic_state_L7=L7EpistemicStateEnum.LCL_FAILURE_INTERNAL_L7, error_details=double_error_summary)
        )

        seed_qa_qc = SeedQAQC(
            version_seed_qa_qc_schema="0.1.0",
            overall_seed_integrity_status=SeedIntegrityStatusEnum.INVALID_SEED_INCOMPLETE_CRITICAL,
            qa_qc_assessment_timestamp=now,
            summary_of_checks_performed=SummaryOfChecksPerformed(total_checks_defined_in_policy=0,total_checks_executed=0,checks_passed=0,checks_with_warnings=0,checks_failed_non_blocking=0,checks_failed_blocking=0),
            integrity_findings=[IntegrityFinding(
                finding_id=self._startle_generate_crux_uid("double_fallback_finding"),
                check_category_code=QAQCCheckCategoryCodeEnum.OTHER_INTEGRITY_CHECK,
                target_layer_or_component="MadaSeed_DoubleFallback_Overall",
                description_of_finding=double_error_summary,
                severity_level=QAQCSeverityLevelEnum.ERROR_BLOCKING_INTEGRITY_REQUIRES_LCL
            )],
            error_details=double_error_summary
        )

        return MadaSeed(
            version="0.3.0",
            seed_id=seed_id,
            seed_content=seed_content,
            trace_metadata=trace_metadata,
            seed_QA_QC=seed_qa_qc,
            seed_completion_timestamp=now
        )

    def _startle_create_initial_madaSeed_shell(self, seed_id: str, trace_id: str, raw_signals: List[RawSignal]) -> MadaSeed:
        log(f"[Shell] Creating MadaSeed shell with seed_id={seed_id}, trace_id={trace_id}")
        now = datetime.now(timezone.utc)

        signal_components_metadata_L1: List[SignalComponentMetadataL1] = []
        if raw_signals:
            for rs in raw_signals:
                signal_components_metadata_L1.append(SignalComponentMetadataL1(
                    component_role_L1="raw_input_component",
                    raw_signal_ref_uid_L1=rs.raw_input_id,
                    byte_size_hint_L1=len(rs.raw_input_signal.encode('utf-8')) if rs.raw_input_signal else 0,
                    encoding_status_L1=EncodingStatusL1Enum.ASSUMEDUTF8_TEXTHINT,
                    media_type_hint_L1="text/plain"
                ))
        else:
            default_raw_signal_id = self._startle_generate_crux_uid("raw_signal_placeholder")
            raw_signals.append(RawSignal(raw_input_id=default_raw_signal_id, raw_input_signal="[[EMPTY_INITIAL_SIGNAL]]"))
            signal_components_metadata_L1.append(SignalComponentMetadataL1(
                component_role_L1="placeholder_component",
                raw_signal_ref_uid_L1=default_raw_signal_id,
                byte_size_hint_L1=len(raw_signals[0].raw_input_signal.encode('utf-8')),
                encoding_status_L1=EncodingStatusL1Enum.ASSUMEDUTF8_TEXTHINT,
                media_type_hint_L1="text/plain"
            ))

        l1_startle_context = L1StartleContextObj(
            version="0.1.0",
            L1_epistemic_state_of_startle=L1EpistemicStateOfStartleEnum.STARTLE_COMPLETE_SIGNALREFS_GENERATED,
            trace_creation_time_L1=now,
            input_origin_L1="UNKNOWN_ORIGIN_SHELL",
            signal_components_metadata_L1=signal_components_metadata_L1
        )

        l2_frame_type_obj = L2FrameTypeObj(
            version="0.1.0",
            L2_epistemic_state_of_framing=L2EpistemicStateOfFramingEnum.LCL_FAILURE_INTERNAL_L2,
            input_class_L2=InputClassL2Enum.UNKNOWN_L2_CLASSIFIED,
            frame_type_L2="placeholder_frame_type",
            temporal_hint_L2=TemporalHintL2(value=now, provenance=TemporalHintProvenanceL2Enum.FALLBACK_L1_CREATION_TIME),
            communication_context_L2=CommunicationContextL2(source_agent_uid_L2="placeholder_source_agent_uid", destination_agent_uid_L2="placeholder_destination_agent_uid", origin_environment_L2="placeholder_origin_environment", interaction_channel_L2="placeholder_interaction_channel"),
            L2_validation_status_of_frame=L2ValidationStatusOfFrameEnum.FAILURE_NOSTRUCTUREDETECTED,
            L2_anomaly_flags_from_framing=[],
            L2_framing_confidence_score=0.0
        )
        
        l3_obj_for_trace = L3SurfaceKeymapObj(version="0.1.0", detected_languages=[DetectedLanguage(language_code="en", confidence=0.5)], content_encoding_status=ContentEncodingStatusL3Enum.UNKNOWN, lexical_affordances=LexicalAffordances(), syntactic_hints=SyntacticHints(), pragmatic_affective_affordances=PragmaticAffectiveAffordances(), relational_linking_markers=RelationalLinkingMarkers(), L3_flags=L3Flags(low_confidence_overall_flag=L3FlagDetail(detected=True)))
        l4_obj_for_trace = L4AnchorStateObj(version="0.2.17", l4_epistemic_state_of_anchoring=L4EpistemicStateOfAnchoringEnum.LCL_FAILURE_INTERNAL_L4, overall_anchor_confidence=0.0, AACAssessabilityMap=AACAssessabilityMap(version="0.1.1", die_score=0.0, consequence_vector=ConsequenceVector(immediacy=0.0, visibility=0.0), dialogue_intensity=0.0, aac_visibility_score=0.0), persona_alignment_context_engaged=PersonaAlignmentContextEngaged(version="0.1.1", persona_uid="placeholder_persona_uid", alignment_profile_ref="placeholder_alignment_profile_ref", engagement_status=PAEngagementStatusEnum.ENGAGEMENT_FAILED), trace_threading_context=TraceThreadingContext(version="0.1.1"))
        l5_obj_for_trace = L5FieldStateObj(version="0.2.0", l5_epistemic_state_of_field_processing=L5EpistemicStateOfFieldProcessingEnum.LCL_FAILURE_INTERNAL_L5, field_instance_uid=self._startle_generate_crux_uid("field_instance_trace_ph"), field_participants=[FieldParticipant(persona_uid="placeholder_trace_participant", role_in_field="observer", engagement_readiness=ParticipantEngagementReadinessEnum.UNKNOWN)], dialogue_context=DialogueContext(current_dialogue_mode=DialogueModeEnum.MONOLOGUE, dissent_strength=DissentStrengthEnum.NONE_OBSERVED), work_management=WorkManagement(current_wip_count=0), session_maturity=FieldMaturity(igd_stage_assessment=IGDStageAssessmentEnum.S0_UNINITIALIZED, readiness_for_L6_reflection_flag=False))
        l6_obj_for_trace = L6ReflectionPayloadObj(version="0.1.6", l6_epistemic_state=L6EpistemicStateEnum.LCL_FAILURE_INTERNAL_L6, redaction_applied_summary=False, payload_metadata=PayloadMetadata(generation_sop="lC.SOP.reflect_boom", generation_timestamp=now, source_trace_id=trace_id, presentation_target=PayloadMetadataTarget(consumer_type=ConsumerTypeEnum.SYSTEM_MODULE), presentation_intent="initial_shell_representation_trace", output_modality=OutputModalityEnum.STRUCTURED_DATA), transformation_metadata=TransformationMetadata(version="0.1.1", redaction_status=RedactionStatus(version="0.1.0", redaction_applied=False), omitted_content_summary=OmittedContentSummary(version="0.1.1", omission_applied=False)), reflection_surface=ReflectionSurface(version="0.1.2", assessed_cynefin_state=AssessedCynefinState(version="0.1.0", domain=CynefinDomainEnum.DISORDER), brave_space_reflection=BraveSpaceReflection(version="0.1.0")), payload_content=PayloadContent(version="0.1.1", structured_data={"message": "Initial MadaSeed Shell for Trace"}))

        seed_content = SeedContent(
            raw_signals=raw_signals,
            L1_startle_reflex=L1StartleReflex(
                L1_startle_context_obj=l1_startle_context,
                L2_frame_type=l2_frame_type_obj 
            )
        )

        trace_metadata = TraceMetadata(
            trace_id=trace_id,
            L1_trace=L1Trace(version_L1_trace_schema="0.1.0", sop_name="lC.SOP.startle", completion_timestamp_L1=now, epistemic_state_L1=l1_startle_context.L1_epistemic_state_of_startle, L1_trace_creation_time_from_context=l1_startle_context.trace_creation_time_L1, L1_input_origin_from_context=l1_startle_context.input_origin_L1, L1_signal_component_count=len(l1_startle_context.signal_components_metadata_L1), L1_generated_trace_id=trace_id, L1_applied_policy_refs=[]),
            L2_trace=L2Trace(version_L2_trace_schema="0.1.0", sop_name="lC.SOP.frame_click", completion_timestamp_L2=now, epistemic_state_L2=l2_frame_type_obj.L2_epistemic_state_of_framing, L2_input_class_determined_in_trace=l2_frame_type_obj.input_class_L2, L2_frame_type_determined_in_trace=l2_frame_type_obj.frame_type_L2, L2_temporal_hint_provenance_in_trace=l2_frame_type_obj.temporal_hint_L2.provenance if l2_frame_type_obj.temporal_hint_L2 else None, L2_validation_status_in_trace=l2_frame_type_obj.L2_validation_status_of_frame, L2_applied_policy_refs=[]),
            L3_trace=L3Trace(version_L3_trace_schema="0.1.0", sop_name="lC.SOP.keymap_click", completion_timestamp_L3=now, epistemic_state_L3="Keymapped_Successfully_Shell_Placeholder", L3_primary_language_detected_code=l3_obj_for_trace.detected_languages[0].language_code if l3_obj_for_trace.detected_languages else "N/A", L3_content_encoding_status_determined=l3_obj_for_trace.content_encoding_status, L3_applied_policy_refs=[]),
            L4_trace=L4Trace(version_L4_trace_schema="0.1.0", sop_name="lC.SOP.anchor_click", completion_timestamp_L4=now, epistemic_state_L4=l4_obj_for_trace.l4_epistemic_state_of_anchoring, L4_pa_profile_engaged_ref_in_trace=l4_obj_for_trace.persona_alignment_context_engaged.persona_uid if l4_obj_for_trace.persona_alignment_context_engaged else None, L4_aac_visibility_score_from_anchor_state=l4_obj_for_trace.AACAssessabilityMap.aac_visibility_score if l4_obj_for_trace.AACAssessabilityMap else None, L4_overall_anchor_confidence_from_anchor_state=l4_obj_for_trace.overall_anchor_confidence, L4_applied_policy_refs=[]),
            L5_trace=L5Trace(version_L5_trace_schema="0.1.0", sop_name="lC.SOP.field_click", completion_timestamp_L5=now, epistemic_state_L5=l5_obj_for_trace.l5_epistemic_state_of_field_processing, L5_field_instance_uid_processed=l5_obj_for_trace.field_instance_uid, L5_field_status_after_update=l5_obj_for_trace.field_status, L5_dialogue_mode_assessed_in_trace=l5_obj_for_trace.dialogue_context.current_dialogue_mode if l5_obj_for_trace.dialogue_context else None, L5_dissent_strength_assessed_in_trace=l5_obj_for_trace.dialogue_context.dissent_strength if l5_obj_for_trace.dialogue_context else None, L5_igd_stage_assessed_in_trace=l5_obj_for_trace.session_maturity.igd_stage_assessment if l5_obj_for_trace.session_maturity else None, L5_applied_policy_refs=[]),
            L6_trace=L6Trace(version_L6_trace_schema="0.1.0", sop_name="lC.SOP.reflect_boom", completion_timestamp_L6=now, epistemic_state_L6=l6_obj_for_trace.l6_epistemic_state, L6_presentation_target_consumer_type=l6_obj_for_trace.payload_metadata.presentation_target.consumer_type, L6_presentation_intent_resolved=l6_obj_for_trace.payload_metadata.presentation_intent, L6_output_modality_used=l6_obj_for_trace.payload_metadata.output_modality, L6_processing_confidence_score_from_payload=l6_obj_for_trace.payload_metadata.L6_processing_confidence, L6_redaction_applied_summary_from_payload=l6_obj_for_trace.redaction_applied_summary, L6_simplification_level_hint_applied=l6_obj_for_trace.transformation_metadata.simplification_level_hint, L6_applied_policy_refs=[]),
            L7_trace=L7Trace(version_L7_trace_schema="0.1.0", sop_name="lC.SOP.apply_done", completion_timestamp_L7=now, epistemic_state_L7=L7EpistemicStateEnum.LCL_FAILURE_INTERNAL_L7, L7_application_intent_resolved="initial_shell_application", summary_seed_integrity_status_from_receipt=SeedIntegrityStatusEnum.VALID_WITH_WARNINGS, summary_outcome_confidence_from_receipt=0.0, L7_summary_flags_for_orchestration={}, L7_applied_policy_refs=[])
        )

        seed_qa_qc = SeedQAQC(
            version_seed_qa_qc_schema="0.1.0", 
            overall_seed_integrity_status=SeedIntegrityStatusEnum.VALID_WITH_WARNINGS_MINOR, 
            qa_qc_assessment_timestamp=now,
            summary_of_checks_performed=SummaryOfChecksPerformed(total_checks_defined_in_policy=0,total_checks_executed=0,checks_passed=0,checks_with_warnings=0,checks_failed_non_blocking=0,checks_failed_blocking=0),
            integrity_findings=[IntegrityFinding(finding_id=self._startle_generate_crux_uid("finding"),check_category_code=QAQCCheckCategoryCodeEnum.OTHER_INTEGRITY_CHECK,target_layer_or_component="MadaSeedShell",description_of_finding="Initial MadaSeed shell created, not fully populated.",severity_level=QAQCSeverityLevelEnum.INFO)]
        )

        mada_seed = MadaSeed(
            version="0.3.0", 
            seed_id=seed_id,
            seed_content=seed_content,
            trace_metadata=trace_metadata,
            seed_QA_QC=seed_qa_qc, 
            seed_completion_timestamp=now 
        )
        log(f"[Shell] MadaSeed shell created successfully for seed_id={seed_id}")
        return mada_seed

    def _startle_process_input_components(self, components: List[DataComponent], trace_id_for_context: str):
        raw_signals = []
        for comp_idx, comp in enumerate(components):
            log(f"[Component] Processing: {comp.role_hint}")
            if not comp.content_handle_placeholder or not isinstance(comp.content_handle_placeholder, str) or comp.content_handle_placeholder.strip() == "":
                log("[Component] Skipped empty or invalid content")
                continue
            content = comp.content_handle_placeholder
            signal_id = self._startle_generate_crux_uid("raw_signal", {"trace_id": trace_id_for_context, "role": comp.role_hint, "index": comp_idx})
            raw_signals.append(RawSignal(raw_input_id=signal_id,raw_input_signal=content))
        log(f"[RawSignals] Generated {len(raw_signals)} raw signals.")
        return raw_signals

    async def run(self, ctx):
        log("[StartleAgent] run() invoked")
        try:
            log(f"[Session] Keys: {list(ctx.state.keys())}")
            input_event = ctx.state.get("input_event", {})
            log(f"[InputEvent] Raw: {input_event}")

            try:
                parsed_input = self.model.model_validate(input_event)
                log(f"[Validation] Parsed: {parsed_input}")
            except Exception as parse_err:
                log(f"[ValidationError] {parse_err}")
                raise

            seed_id = self._startle_generate_crux_uid("seed")
            trace_id = self._startle_generate_crux_uid("trace")
            log(f"[IDs] Generated seed_id={seed_id}, trace_id={trace_id}")

            raw_signals = self._startle_process_input_components(parsed_input.data_components, trace_id)
            log(f"[ProcessedInput] Raw Signals Count: {len(raw_signals)}")

            seed = self._startle_create_initial_madaSeed_shell(seed_id=seed_id, trace_id=trace_id, raw_signals=raw_signals)
            
            if seed.seed_content.L1_startle_reflex.L1_startle_context_obj and parsed_input.origin_hint:
                seed.seed_content.L1_startle_reflex.L1_startle_context_obj.input_origin_L1 = parsed_input.origin_hint
                log(f"[ContextUpdate] Updated L1_startle_context_obj.input_origin_L1 to {parsed_input.origin_hint}")

            ctx.state["mada_seed_output"] = seed.model_dump(exclude_none=True)
            ctx.state["trace_id"] = trace_id 
            ctx.state["seed_id"] = seed_id 

            log(f"[Done] MadaSeed created and written to session state. seed_id={seed_id}, trace_id={trace_id}")

        except Exception as e:
            log(f"[CriticalError] An unhandled exception occurred in StartleAgent.run: {type(e).__name__} - {e}")
            error_seed_id = self._startle_generate_crux_uid("error_seed")
            error_trace_id = self._startle_generate_crux_uid("error_trace")
            error_raw_signal_id = self._startle_generate_crux_uid("error_raw_signal")
            error_raw_signals = [RawSignal(raw_input_id=error_raw_signal_id, raw_input_signal=f"Error: {type(e).__name__} - {e}")]
            
            try:
                fallback_seed = self._startle_create_initial_madaSeed_shell(seed_id=error_seed_id,trace_id=error_trace_id,raw_signals=error_raw_signals)
                if fallback_seed.seed_content.L1_startle_reflex.L1_startle_context_obj:
                    fallback_seed.seed_content.L1_startle_reflex.L1_startle_context_obj.L1_epistemic_state_of_startle = L1EpistemicStateOfStartleEnum.LCL_FAILURE_INTERNAL_L1
                    fallback_seed.seed_content.L1_startle_reflex.L1_startle_context_obj.error_details = f"StartleAgent.run CriticalError: {type(e).__name__} - {e}"
                if fallback_seed.trace_metadata.L1_trace:
                    fallback_seed.trace_metadata.L1_trace.epistemic_state_L1 = L1EpistemicStateOfStartleEnum.LCL_FAILURE_INTERNAL_L1
                    fallback_seed.trace_metadata.L1_trace.error_detail = f"StartleAgent.run CriticalError: {type(e).__name__} - {e}"
                log(f"[Fallback] Created fallback MadaSeed due to error. seed_id={error_seed_id}")
                ctx.state["mada_seed_output"] = fallback_seed.model_dump(exclude_none=True)
            except Exception as fe: 
                log(f"[CriticalDoubleFallbackError] Initial shell creation failed: {type(e).__name__} - {e}. Then, fallback shell creation also failed: {type(fe).__name__} - {fe}")
                double_fallback_seed = self._create_double_fallback_mada_seed(seed_id=error_seed_id,trace_id=error_trace_id,original_error_type=type(e).__name__,original_error_msg=str(e),fallback_error_type=type(fe).__name__,fallback_error_msg=str(fe))
                ctx.state["mada_seed_output"] = double_fallback_seed.model_dump(exclude_none=True)
                log(f"[DoubleFallback] Double fallback MadaSeed created and set. seed_id={error_seed_id}")

            ctx.state["trace_id"] = f"ERROR_ADK_EXECUTION_{type(e).__name__}_{error_trace_id}"
            ctx.state["seed_id"] = error_seed_id
            log(f"[Trace] Error trace_id set: {ctx.state['trace_id']}")
