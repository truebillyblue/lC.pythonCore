from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Union, Any, Annotated
from enum import Enum

from pydantic import BaseModel, Field, conint, confloat, constr, StringConstraints


# Forward declarations for models that are defined later
class L1StartleContextObj(BaseModel):
    pass

class L2FrameTypeObj(BaseModel):
    pass

class L3SurfaceKeymapObj(BaseModel):
    pass

class L4AnchorStateObj(BaseModel):
    pass

class L5FieldStateObj(BaseModel):
    pass

class L6ReflectionPayloadObj(BaseModel):
    pass

class L7EncodedApplication(BaseModel):
    pass

class L1Trace(BaseModel):
    pass

class L2Trace(BaseModel):
    pass

class L3Trace(BaseModel):
    pass

class L4Trace(BaseModel):
    pass

class L5Trace(BaseModel):
    pass

class L6Trace(BaseModel):
    pass

class L7Trace(BaseModel):
    pass

class SeedQAQC(BaseModel):
    pass


# Enum Definitions from schema

class L1EpistemicStateOfStartleEnum(str, Enum):
    STARTLE_COMPLETE_SIGNALREFS_GENERATED = "Startle_Complete_SignalRefs_Generated"
    LCL_FAILURE_INTERNAL_L1 = "LCL-Failure-Internal_L1"
    LCL_FAILURE_UID_GENERATION_L1 = "LCL-Failure-UID_Generation_L1"

class EncodingStatusL1Enum(str, Enum):
    ASSUMEDUTF8_TEXTHINT = "AssumedUTF8_TextHint"
    DETECTEDBINARY = "DetectedBinary"
    POSSIBLEENCODINGISSUE_L1 = "PossibleEncodingIssue_L1"
    UNKNOWN_L1 = "Unknown_L1"

class L2EpistemicStateOfFramingEnum(str, Enum):
    FRAMED = "Framed"
    LCL_CLARIFY_STRUCTURE = "LCL-Clarify-Structure"
    LCL_DEFER_STRUCTURE = "LCL-Defer-Structure"
    LCL_FAILURE_SIZENOISE = "LCL-Failure-SizeNoise"
    LCL_FAILURE_AMBIGUOUSFRAME = "LCL-Failure-AmbiguousFrame"
    LCL_FAILURE_MISSINGCOMMSCONTEXT = "LCL-Failure-MissingCommsContext"
    LCL_FAILURE_INTERNAL_L2 = "LCL-Failure-Internal_L2"

class InputClassL2Enum(str, Enum):
    PROMPT = "prompt"
    COMMS = "comms"
    MIXED = "mixed"
    UNKNOWN_L2_CLASSIFIED = "unknown_L2_classified"

class TemporalHintProvenanceL2Enum(str, Enum):
    EXPLICIT_CONTENT_L2_PARSED = "explicit_content_L2_parsed"
    EXPLICIT_METADATA_L2_USED = "explicit_metadata_L2_used"
    FALLBACK_L1_CREATION_TIME = "fallback_L1_creation_time"
    PARSING_ERROR_L2 = "parsing_error_L2"

class FieldTemporalContext(BaseModel):
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_ms: Optional[int] = None

class L2ValidationStatusOfFrameEnum(str, Enum):
    SUCCESS_FRAMED = "Success_Framed"
    FAILURE_SIZEORNOISE = "Failure_SizeOrNoise"
    FAILURE_NOSTRUCTUREDETECTED = "Failure_NoStructureDetected"
    FAILURE_AMBIGUOUSSTRUCTURE = "Failure_AmbiguousStructure"
    FAILURE_MISSINGCOMMSCONTEXT = "Failure_MissingCommsContext"

class ContentEncodingStatusL3Enum(str, Enum):
    CONFIRMEDUTF8 = "ConfirmedUTF8"
    BINARYDETECTED = "BinaryDetected"
    POSSIBLEENCODINGISSUE = "PossibleEncodingIssue"
    UNKNOWN = "Unknown"

class QuantifierQualifierTypeEnum(str, Enum):
    QUANTIFIER = "quantifier"
    QUALIFIER = "qualifier"
    
class SentimentPolarityEnum(str, Enum):
    POS = "pos"
    NEG = "neg"
    NEU = "neu"
    MIXED = "mixed"

class PowerDynamicCueTypeEnum(str, Enum):
    HEDGING = "hedging"
    COMMAND = "command"
    PASSIVE = "passive"

class ActorRoleHintEnum(str, Enum):
    SPEAKER = "speaker"
    RECIPIENT = "recipient"

class PriorTraceReferenceTypeEnum(str, Enum):
    TRACE_ID_MENTION = "trace_id_mention"
    RELATIVE_MENTION = "relative_mention"
    TOPIC_LINK = "topic_link"

class L4EpistemicStateOfAnchoringEnum(str, Enum):
    ANCHORED = "Anchored"
    ANCHORED_WITH_GAPS = "Anchored_With_Gaps"
    ANCHORED_LOW_ASSESSABILITY = "Anchored_Low_Assessability"
    LCL_DEFER_IDENTITY = "LCL-Defer-Identity"
    LCL_AMBIGUATE_SENDER = "LCL-Ambiguate-Sender"
    LCL_FRAGMENT_PROJECTION = "LCL-Fragment-Projection"
    LCL_PROBE_CONTEXT = "LCL-Probe-Context"
    LCL_REANCHOR_SELF = "LCL-Reanchor-Self"
    LCL_FAILURE_LOW_ASSESSABILITY = "LCL-Failure_Low_Assessability"
    LCL_FAILURE_PA_CONTEXT = "LCL-Failure-PA-Context"
    LCL_FAILURE_INTERNAL_L4 = "LCL-Failure-Internal_L4"

class PAEngagementStatusEnum(str, Enum):
    FULL_REFERENCE_ENGAGED = "Full_Reference_Engaged"
    PARTIAL_REFERENCE_ENGAGED = "Partial_Reference_Engaged"
    INFERRED_STATE_USED = "Inferred_State_Used"
    ENGAGEMENT_FAILED = "Engagement_Failed"

class FindingTypeEnum(str, Enum):
    STATE_OBSERVATION_L1 = "State_Observation_L1"
    BEHAVIOR_PATTERN_L2 = "Behavior_Pattern_L2"
    CAPABILITY_IDENTIFIED_L3 = "Capability_Identified_L3"
    CAPABILITY_GAP_L3 = "Capability_Gap_L3"
    BELIEF_SURFACED_L4 = "Belief_Surfaced_L4"
    VALUE_ENGAGED_L4 = "Value_Engaged_L4"
    VALUE_CONFLICT_L4 = "Value_Conflict_L4"
    IDENTITY_FACET_ACTIVATED_P5 = "Identity_Facet_Activated_P5"
    ROLE_ASSUMPTION_P5 = "Role_Assumption_P5"
    IDENTITY_CONFLICT_P5 = "Identity_Conflict_P5"
    MISSION_ALIGNMENT_L6 = "Mission_Alignment_L6"
    SOCIAL_ROLE_ENGAGED_L6 = "Social_Role_Engaged_L6"
    INTERPERSONAL_PURPOSE_REFLECTED_L7 = "Interpersonal_Purpose_Reflected_L7"
    BENEFICIARY_IMPACT_L7 = "Beneficiary_Impact_L7"
    COMMUNITY_NORM_REFERENCED_L8 = "Community_Norm_Referenced_L8"
    NETWORK_LINK_L8 = "Network_Link_L8"
    SYSTEMIC_INFLUENCE_OBSERVED_L9 = "Systemic_Influence_Observed_L9"
    GLOBAL_CONTEXT_REF_L9 = "Global_Context_Ref_L9"
    MACROSYSTEM_PARADIGM_HINT_M10 = "Macrosystem_Paradigm_Hint_M10"
    LEVEL_GENERIC_GAP_IDENTIFIED = "Level_Generic_Gap_Identified"

class L4ValidationStatusEnum(str, Enum):
    SUCCESS = "Success"
    WARNING = "Warning"
    FAILURE = "Failure"

class KnowledgeGapTypeEnum(str, Enum):
    ENTITY_RESOLUTION = "entity_resolution"
    CONCEPT_RESOLUTION = "concept_resolution"
    TEMPORAL_CONTEXT = "temporal_context"
    PERSONA_ATTRIBUTE = "persona_attribute"
    RELATIONSHIP_AMBIGUITY = "relationship_ambiguity"
    SCHEMA_MISSING = "schema_missing"
    CONTEXT_MISSING = "context_missing"
    INTENT_UNCLEAR = "intent_unclear"
    PA_LEVEL_STATE = "pa_level_state"
    OTHER = "other"

class KnowledgeGapPriorityEnum(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"

class L5EpistemicStateOfFieldProcessingEnum(str, Enum):
    FIELD_INSTANTIATED_NEW = "Field_Instantiated_New"
    FIELD_UPDATED_EXISTING = "Field_Updated_Existing"
    FIELD_UPDATE_BLOCKED = "Field_Update_Blocked"
    LCL_FRAGMENT_FIELD = "LCL-Fragment-Field"
    LCL_INVALID_PARTICIPANT = "LCL-Invalid-Participant"
    LCL_POLICY_CONFLICT = "LCL-Policy-Conflict"
    LCL_MODE_INCOMPATIBLE = "LCL-Mode-Incompatible"
    LCL_AAC_UNREADY = "LCL-AAC-Unready"
    LCL_HIGH_RISK = "LCL-High-Risk"
    LCL_FAILURE_INTERNAL_L5 = "LCL-Failure-Internal_L5"

class FieldStatusEnum(str, Enum):
    NEW = "New"
    ACTIVE = "Active"
    STALLED = "Stalled"
    AWAITING_INPUT = "Awaiting_Input"
    RESOLVING_LCL = "Resolving_LCL"
    CLOSED_SUCCESS = "Closed_Success"
    CLOSED_ABANDONED = "Closed_Abandoned"

class ParticipantEngagementReadinessEnum(str, Enum):
    READY = "Ready"
    NOT_READY = "Not_Ready"
    AWAY = "Away"
    UNKNOWN = "Unknown"
    
class DialogueModeEnum(str, Enum):
    MONOLOGUE = "Monologue"
    DISCUSSION = "Discussion"
    DEBATE = "Debate"
    POLITE_EXCHANGE = "Polite_Exchange"
    DIALOGUE_EMERGENT = "Dialogue_Emergent"
    DIALOGUE_SUSTAINED = "Dialogue_Sustained"
    SOPHISTRY_DETECTED = "Sophistry_Detected"
    STALLED_COMMUNICATION = "Stalled_Communication"

class DissentStrengthEnum(str, Enum):
    NONE_OBSERVED = "None_Observed"
    LOW_IMPLICIT = "Low_Implicit"
    MODERATE_EXPRESSED = "Moderate_Expressed"
    HIGH_CONSTRUCTIVE = "High_Constructive"
    HIGH_FRAGMENTING = "High_Fragmenting"
    FRACTURED = "Fractured"

class AACSupportLevelEnum(str, Enum):
    NONE = "None"
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

class DialogueStructureSupportEnum(str, Enum):
    CLOSED = "Closed"
    RESTRICTED = "Restricted"
    OPEN = "Open"
    SCAFFOLDED_FOR_DIALOGUE = "Scaffolded_For_Dialogue"

class EpistemicFlowDirectionEnum(str, Enum):
    CONVERGING = "Converging"
    DIVERGING = "Diverging"
    STAGNANT = "Stagnant"
    EXPLORING = "Exploring"
    REFINING = "Refining"
    CONSOLIDATING = "Consolidating"

class PBIStatusInFieldEnum(str, Enum):
    NEW_IN_FIELD = "New" # Renamed from "New" to avoid conflict
    UNDER_DISCUSSION = "Under_Discussion"
    BLOCKED_IN_FIELD = "Blocked" # Renamed from "Blocked"
    READY_FOR_ACTION = "Ready_For_Action"
    ACTION_IN_PROGRESS = "Action_In_Progress"
    REVIEW_PENDING = "Review_Pending"
    DONE_IN_FIELD = "Done_In_Field"
    DEFERRED_IN_FIELD = "Deferred_In_Field"

class RiskSeverityHintEnum(str, Enum):
    LOW_RISK = "Low" # Renamed from "Low"
    MODERATE_RISK = "Moderate" # Renamed from "Moderate"
    HIGH_RISK = "High" # Renamed from "High"
    CRITICAL_RISK = "Critical" # Renamed from "Critical"

class BraveSpaceActivationStatusEnum(str, Enum):
    INACTIVE = "Inactive"
    MONITORING = "Monitoring"
    ACTIVE_SCAFFOLDING_LIGHT = "Active_Scaffolding_Light"
    ACTIVE_SCAFFOLDING_HEAVY = "Active_Scaffolding_Heavy"
    INTERVENTION_REQUIRED = "Intervention_Required"

class IGDStageAssessmentEnum(str, Enum):
    S0_UNINITIALIZED = "S0_Uninitialized"
    S1_GROUND_SETTING = "S1_Ground_Setting"
    S2_EXPLORING_IDS_INEQUALITIES = "S2_Exploring_IDs_Inequalities"
    S3_ENGAGING_CONTROVERSIAL_ISSUES = "S3_Engaging_Controversial_Issues"
    S4_ALLIANCEBUILDING_ACTIONPLANNING = "S4_AllianceBuilding_ActionPlanning"
    SX_FRACTURED_REGRESSED = "Sx_Fractured_Regressed"

class L6EpistemicStateEnum(str, Enum):
    REFLECTION_PREPARED = "Reflection_Prepared"
    REFLECTION_PREPARED_WITH_WARNINGS = "Reflection_Prepared_With_Warnings"
    LCL_PRESENTATION_FORMATERROR = "LCL-Presentation-FormatError"
    LCL_PRESENTATION_REDACTIONFAILURE = "LCL-Presentation-RedactionFailure"
    LCL_PRESENTATION_HIGHRISKSIMPLIFICATION = "LCL-Presentation-HighRiskSimplification"
    LCL_PRESENTATION_REQUIRES_L5STATE = "LCL-Presentation-RequiresL5State" # Corrected typo
    LCL_FAILURE_INTERNAL_L6 = "LCL-Failure-Internal_L6"

class ConsumerTypeEnum(str, Enum):
    HUMAN_UI = "Human_UI"
    AGENT_GENERIC = "Agent_Generic"
    AGENT_LLM = "Agent_LLM"
    SYSTEM_MODULE = "System_Module"
    EXTERNAL_API = "External_API"
    LOG_ARCHIVE = "Log_Archive"
    GOOGLE_ASSISTANT_USER = "GOOGLE_ASSISTANT_USER" # Added for Google Assistant

class OutputModalityEnum(str, Enum):
    STRUCTURED_DATA = "Structured_Data"
    FORMATTED_TEXT = "Formatted_Text"
    MULTIMODAL_PACKAGE = "Multimodal_Package"
    API_PAYLOAD = "API_Payload"

class OmissionRationaleCodeEnum(str, Enum):
    REDACTION_POLICY = "Redaction_Policy"
    RELEVANCE_FILTERING = "Relevance_Filtering"
    TARGET_SIMPLIFICATION = "Target_Simplification"
    ERROR_DURING_PROCESSING = "Error_During_Processing"
    NULL = None # For nullable enum

class OmittedContentCategoryEnum(str, Enum):
    FULL_FIELD_HISTORY = "Full_Field_History"
    DETAILED_INTERACTION_LOGS = "Detailed_Interaction_Logs"
    LOW_PRIORITY_RISKS = "Low_Priority_Risks"
    INTERNAL_PROCESSING_METADATA = "Internal_Processing_Metadata"
    REDACTED_PII_CATEGORY = "Redacted_PII_Category"
    REDACTED_CONFIDENTIAL_TOPIC = "Redacted_Confidential_Topic"
    COMPLEXITY_REDUCED_DATA = "Complexity_Reduced_Data"
    AMBIGUITY_SOURCE_DETAILS = "Ambiguity_Source_Details"
    FULL_PARTICIPANT_LIST = "Full_Participant_List"
    DETAILED_MOMENTUM_VECTORS = "Detailed_Momentum_Vectors"
    LOW_CONFIDENCE_ASSERTIONS = "Low_Confidence_Assertions"
    OTHER_POLICY_BASED = "Other_Policy_Based"


class CynefinDomainEnum(str, Enum):
    DISORDER = "Disorder"
    CHAOTIC = "Chaotic"
    COMPLEX = "Complex"
    COMPLICATED = "Complicated"
    SIMPLE = "Simple"
    UNKNOWN = "Unknown"

class TransformationDissentRiskHintEnum(str, Enum):
    MINIMAL = "Minimal"
    LOW_RISK_L6 = "Low" # Renamed
    MODERATE_RISK_L6 = "Moderate" # Renamed
    HIGH_RISK_L6 = "High" # Renamed
    
class RepresentationDiscomfortRiskHintEnum(str, Enum):
    MINIMAL_DISCOMFORT = "Minimal" # Renamed
    LOW_DISCOMFORT = "Low" # Renamed
    MODERATE_DISCOMFORT = "Moderate" # Renamed
    HIGH_DISCOMFORT = "High" # Renamed

class SimplificationLevelHintEnum(str, Enum):
    NONE = "None"
    MINOR_SUMMARIZATION = "Minor_Summarization"
    SIGNIFICANT_ABSTRACTION = "Significant_Abstraction"
    HIGH_SIMPLIFICATION = "High_Simplification"

class L7PbiTypeEnum(str, Enum):
    TASK = "task"
    STORY = "story"
    EPIC = "epic"
    INITIATIVE = "initiative"

class L7TemporalPlaneEnum(str, Enum):
    PAST_A = "Past_A"
    PAST_B = "Past_B"
    PAST_C = "Past_C"
    PRESENT = "Present"
    FUTURE_A = "Future_A"
    FUTURE_B = "Future_B"

class L7DimensionalPlaneEnum(str, Enum):
    PERSONAL = "Personal"
    INTERPERSONAL = "Interpersonal"
    GROUP = "Group"
    INTERGROUP = "Intergroup"
    ORGANIZATIONAL = "Organizational"
    INTERORGANIZATIONAL = "Interorganizational"
    ORGFIELD = "OrgField"
    COMMUNITY = "Community"
    GLOBAL = "Global"

class L7RoleTypeEnum(str, Enum):
    FACILITATOR = "facilitator"
    WITNESS = "witness"
    SCAFFOLD = "scaffold"
    CHAMPION = "champion"
    OBSERVER = "observer"

class L7PBIStatusHintEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED_PBI = "blocked" # Renamed
    DEFERRED_PBI = "deferred" # Renamed

class L7OutputConsumerTypeEnum(str, Enum):
    HUMAN_UI_L7 = "Human_UI" # Renamed
    AGENT_LLM_L7 = "Agent_LLM" # Renamed
    SYSTEM_LOG_L7 = "System_Log" # Renamed
    EXTERNAL_API_CALL_L7 = "External_API_Call" # Renamed
    MADA_OBJECT_UPDATE_L7 = "MADA_Object_Update" # Renamed
    ORCHESTRATOR_SIGNAL_L7 = "Orchestrator_Signal" # Renamed

class L7OutputModalityEnum(str, Enum):
    FORMATTED_TEXT_MARKDOWN = "Formatted_Text_Markdown"
    STRUCTURED_DATA_JSON = "Structured_Data_JSON"
    INSTRUCTION_SEQUENCE = "Instruction_Sequence"
    BINARY_DATA_REF = "Binary_Data_Ref"
    SPEECH_TEXT = "SPEECH_TEXT" # Added for Google Assistant / speech responses

class L7DirectiveTypeEnum(str, Enum):
    EXECUTE_SOP = "Execute_SOP"
    REQUEST_USER_INPUT = "Request_User_Input"
    GENERATE_RESPONSE = "Generate_Response"
    UPDATE_STATE = "Update_State"
    LOG_EVENT = "Log_Event"
    QUERY_MADA = "Query_MADA"

class L7EpistemicStateEnum(str, Enum):
    APPLICATION_SUCCESSFUL_SEED_VALID = "Application_Successful_Seed_Valid"
    APPLICATION_SUCCESSFUL_SEED_WARNINGS = "Application_Successful_Seed_Warnings"
    APPLICATION_PARTIAL_SUCCESS_SEED_VALID = "Application_Partial_Success_Seed_Valid"
    APPLICATION_PARTIAL_SUCCESS_SEED_WARNINGS = "Application_Partial_Success_Seed_Warnings"
    LCL_APPLY_EXECUTIONFAILURE = "LCL-Apply-ExecutionFailure"
    LCL_APPLY_POLICYVIOLATION = "LCL-Apply-PolicyViolation"
    LCL_APPLY_RESOURCEUNAVAILABLE = "LCL-Apply-ResourceUnavailable"
    LCL_APPLY_CAPABILITYMISMATCH = "LCL-Apply-CapabilityMismatch"
    LCL_APPLY_AMBIGUOUSINTENT = "LCL-Apply-AmbiguousIntent"
    LCL_SEED_INCOMPLETE = "LCL-Seed-Incomplete"
    LCL_LOOPBACK_TO_L6 = "LCL-Loopback-To-L6"
    LCL_FAILURE_INTERNAL_L7 = "LCL-Failure-Internal_L7"

class SeedIntegrityStatusEnum(str, Enum):
    VALID_COMPLETE = "Valid_Complete"
    VALID_WITH_WARNINGS = "Valid_With_Warnings" # Combined minor/moderate
    INVALID_LCL_SEED_INCOMPLETE = "Invalid_LCL_Seed_Incomplete"
    INVALID_LCL_LOOPBACK_TO_L6_REQUIRED = "Invalid_LCL_Loopback_To_L6_Required" # from L7 trace
    VALID_WITH_WARNINGS_MINOR = "Valid_With_Warnings_Minor" # from QAQC
    VALID_WITH_WARNINGS_MODERATE = "Valid_With_Warnings_Moderate" # from QAQC
    INVALID_REQUIRES_L6_LOOPBACK = "Invalid_Requires_L6_Loopback" # from QAQC
    INVALID_SEED_INCOMPLETE_CRITICAL = "Invalid_Seed_Incomplete_Critical" # from QAQC
    QA_QC_PROCESS_ERROR = "QA_QC_Process_Error" # from QAQC


class QAQCCheckCategoryCodeEnum(str, Enum):
    COMPLETENESS_CHECK_L1 = "Completeness_Check_L1"
    COMPLETENESS_CHECK_L2 = "Completeness_Check_L2"
    COMPLETENESS_CHECK_L3 = "Completeness_Check_L3"
    COMPLETENESS_CHECK_L4 = "Completeness_Check_L4"
    COMPLETENESS_CHECK_L5 = "Completeness_Check_L5"
    COMPLETENESS_CHECK_L6 = "Completeness_Check_L6"
    COMPLETENESS_CHECK_L7 = "Completeness_Check_L7"
    TIMESTAMP_CHRONOLOGY_ACROSS_LAYERS = "Timestamp_Chronology_Across_Layers"
    VERSION_COMPATIBILITY_HINT_ACROSS_LAYERS = "Version_Compatibility_Hint_Across_Layers"
    STRUCTURAL_EXTENSIBILITY_CHECK_GENERIC = "Structural_Extensibility_Check_Generic"
    STRUCTURAL_EXTENSIBILITY_CHECK_L4_GAPS = "Structural_Extensibility_Check_L4_Gaps"
    STRUCTURAL_EXTENSIBILITY_CHECK_L5_OBJECTIVES = "Structural_Extensibility_Check_L5_Objectives"
    L6_PAYLOAD_INTEGRITY_VS_L5_STATE = "L6_Payload_Integrity_Vs_L5_State"
    L6_PAYLOAD_MALFORMED_BY_L7_STD = "L6_Payload_Malformed_By_L7_Std"
    SEMANTIC_CONSISTENCY_HINT_CROSSLAYER = "Semantic_Consistency_Hint_CrossLayer"
    POLICY_ADHERENCE_L7_ACTION = "Policy_Adherence_L7_Action"
    OTHER_INTEGRITY_CHECK = "Other_Integrity_Check"

class QAQCSeverityLevelEnum(str, Enum):
    INFO = "Info"
    WARNING_MINOR = "Warning_Minor"
    WARNING_MODERATE = "Warning_Moderate"
    ERROR_NONBLOCKING_INTEGRITY = "Error_NonBlocking_Integrity"
    ERROR_BLOCKING_INTEGRITY_REQUIRES_LCL = "Error_Blocking_Integrity_Requires_LCL"


# Definition of nested models

class RawSignal(BaseModel):
    raw_input_id: str
    raw_input_signal: str

class SignalComponentMetadataL1(BaseModel):
    component_role_L1: str
    raw_signal_ref_uid_L1: str
    byte_size_hint_L1: Optional[int] = None
    encoding_status_L1: EncodingStatusL1Enum
    media_type_hint_L1: Optional[str] = None

class L1StartleContextObj(BaseModel):
    version: Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]
    L1_epistemic_state_of_startle: L1EpistemicStateOfStartleEnum
    trace_creation_time_L1: datetime
    input_origin_L1: Optional[str] = None
    signal_components_metadata_L1: List[SignalComponentMetadataL1] = Field(..., min_items=1)
    error_details: Optional[str] = None # Added for error cases in MR logic

class TemporalHintL2(BaseModel):
    value: datetime # Assuming this will be parsed to datetime
    provenance: TemporalHintProvenanceL2Enum

class CommunicationContextL2(BaseModel):
    source_agent_uid_L2: Optional[str] = None
    destination_agent_uid_L2: Optional[str] = None
    origin_environment_L2: Optional[str] = None
    interaction_channel_L2: Optional[str] = None

class L2FrameTypeObj(BaseModel):
    version: Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]
    L2_epistemic_state_of_framing: L2EpistemicStateOfFramingEnum
    input_class_L2: Optional[InputClassL2Enum] = None # Made optional to handle LCL states before this is set
    frame_type_L2: Optional[str] = None
    temporal_hint_L2: Optional[TemporalHintL2] = None
    communication_context_L2: Optional[CommunicationContextL2] = None # Made optional for LCL
    L2_validation_status_of_frame: Optional[L2ValidationStatusOfFrameEnum] = None # Made optional for LCL
    L2_anomaly_flags_from_framing: Optional[List[str]] = Field(default_factory=list)
    L2_framing_confidence_score: Optional[confloat(ge=0, le=1)] = None
    error_details: Optional[str] = None # Added for error cases in MR logic

class DetectedLanguage(BaseModel):
    language_code: str
    confidence: confloat(ge=0, le=1)

class ExplicitMetadata(BaseModel):
    key: str
    value: str
    confidence: confloat(ge=0, le=1)
    source_component_ref: Optional[str] = None # CRUX UID

class KeywordMention(BaseModel):
    term: str
    confidence: float
    potential_synonyms_or_frames: Optional[List[str]] = None
    source_component_ref: Optional[str] = None # CRUX UID

class EntityMentionRaw(BaseModel):
    mention: str
    confidence: float
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    possible_types: Optional[List[str]] = None
    source_component_ref: Optional[str] = None # CRUX UID

class NumericalQuantityMention(BaseModel):
    value_string: str
    confidence: float
    unit_mention: Optional[str] = None
    source_component_ref: Optional[str] = None # CRUX UID

class TemporalExpressionMention(BaseModel):
    expression: str
    confidence: float
    possible_interpretations: Optional[List[str]] = None
    source_component_ref: Optional[str] = None # CRUX UID

class QuantifierQualifierMention(BaseModel):
    term: str
    type: QuantifierQualifierTypeEnum
    confidence: float
    source_component_ref: Optional[str] = None # CRUX UID

class NegationMarker(BaseModel):
    term: str
    confidence: float
    scope_hint_indices: Optional[List[int]] = None
    source_component_ref: Optional[str] = None # CRUX UID

class LexicalAffordances(BaseModel):
    keyword_mentions: List[KeywordMention] = Field(default_factory=list)
    entity_mentions_raw: List[EntityMentionRaw] = Field(default_factory=list)
    numerical_quantity_mentions: List[NumericalQuantityMention] = Field(default_factory=list)
    temporal_expression_mentions: List[TemporalExpressionMention] = Field(default_factory=list)
    quantifier_qualifier_mentions: List[QuantifierQualifierMention] = Field(default_factory=list)
    negation_markers: List[NegationMarker] = Field(default_factory=list)

class EmojiMention(BaseModel):
    emoji: str
    count: int
    potential_sentiment: Optional[str] = None

class SyntacticHints(BaseModel):
    sentence_type_distribution: Optional[dict] = Field(default_factory=dict) # e.g. {"declarative": 5}
    pos_tagging_candidate_flag: bool = False
    punctuation_analysis: Optional[dict] = Field(default_factory=dict)
    capitalization_analysis: Optional[dict] = Field(default_factory=dict)
    emoji_mentions: List[EmojiMention] = Field(default_factory=list)

class FormalityHint(BaseModel):
    score: Optional[float] = None # Made optional based on schema
    confidence: Optional[confloat(ge=0, le=1)] = None # Made optional

class SentimentHint(BaseModel):
    polarity: Optional[SentimentPolarityEnum] = None # Made optional
    score: Optional[float] = None # Made optional
    confidence: Optional[confloat(ge=0, le=1)] = None # Made optional
    contributing_markers: Optional[List[str]] = Field(default_factory=list) # Made optional

class PolitenessMarkers(BaseModel):
    detected_terms: Optional[List[str]] = Field(default_factory=list) # Made optional
    score_hint: Optional[float] = None

class UrgencyMarkers(BaseModel):
    detected_terms: Optional[List[str]] = Field(default_factory=list) # Made optional
    level_hint: Optional[str] = None # Enum: low, medium, high - not strictly enforced here

class PowerDynamicCue(BaseModel):
    cue: Optional[str] = None # Made optional
    type: Optional[PowerDynamicCueTypeEnum] = None # Made optional
    confidence: Optional[confloat(ge=0, le=1)] = None # Made optional
    source_component_ref: Optional[str] = None # CRUX UID

class PowerDynamicMarkers(BaseModel):
    detected_cues: Optional[List[PowerDynamicCue]] = Field(default_factory=list) # Made optional

class InteractionPatternAffordance(BaseModel):
    primary_type: Optional[str] = None
    confidence: Optional[confloat(ge=0, le=1)] = None
    alternative_types: Optional[List[str]] = None

class ShallowGoalIntentAffordance(BaseModel):
    primary_type: Optional[str] = None
    confidence: Optional[confloat(ge=0, le=1)] = None
    alternative_types: Optional[List[str]] = None

class ActorRole(BaseModel):
    role: Optional[ActorRoleHintEnum] = None # Made optional
    mention: Optional[str] = None
    confidence: Optional[confloat(ge=0, le=1)] = None # Made optional

class ActorRoleHint(BaseModel):
    detected_actors: Optional[List[ActorRole]] = Field(default_factory=list) # Made optional

class PragmaticAffectiveAffordances(BaseModel):
    formality_hint: Optional[FormalityHint] = None
    sentiment_hint: Optional[SentimentHint] = None
    politeness_markers: Optional[PolitenessMarkers] = None
    urgency_markers: Optional[UrgencyMarkers] = None
    power_dynamic_markers: Optional[PowerDynamicMarkers] = None
    interaction_pattern_affordance: Optional[InteractionPatternAffordance] = None
    shallow_goal_intent_affordance: Optional[ShallowGoalIntentAffordance] = None
    actor_role_hint: Optional[ActorRoleHint] = None

class ExplicitRelationalPhrases(BaseModel):
    detected: List[str] = Field(default_factory=list)

class ExplicitReferenceMarkers(BaseModel):
    detected: List[str] = Field(default_factory=list)

class UrlMentions(BaseModel):
    detected_urls: List[str] = Field(default_factory=list)

class PriorTraceReference(BaseModel):
    reference_type: PriorTraceReferenceTypeEnum
    reference_value: str
    confidence: confloat(ge=0, le=1)
    source_component_ref: Optional[str] = None # CRUX UID

class RelationalLinkingMarkers(BaseModel):
    explicit_relational_phrases: Optional[ExplicitRelationalPhrases] = None # Made optional based on schema
    explicit_reference_markers: Optional[ExplicitReferenceMarkers] = None # Made optional
    url_mentions: Optional[UrlMentions] = None # Made optional
    prior_trace_references: List[PriorTraceReference] = Field(default_factory=list)

class StatisticalValue(BaseModel):
    value: Optional[Union[int, float]] = None # Allow int or float

class StatisticalScore(BaseModel):
    score: Optional[float] = None

class StatisticalProperties(BaseModel):
    token_count: Optional[StatisticalValue] = None
    sentence_count: Optional[StatisticalValue] = None
    lexical_diversity: Optional[StatisticalScore] = None
    entropy_score: Optional[StatisticalScore] = None

class L3FlagDetail(BaseModel):
    detected: bool = False
    description: Optional[str] = None

class GriceanViolationHints(BaseModel):
     detected: Optional[List[str]] = Field(default_factory=list)

class L3Flags(BaseModel):
    internal_contradiction_hint: Optional[L3FlagDetail] = None
    mixed_affect_signal: Optional[L3FlagDetail] = None
    multivalent_cue_detected: Optional[L3FlagDetail] = None
    low_confidence_overall_flag: Optional[L3FlagDetail] = None
    gricean_violation_hints: Optional[GriceanViolationHints] = None

class L3SurfaceKeymapObj(BaseModel):
    version: Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]
    detected_languages: List[DetectedLanguage] = Field(default_factory=list)
    content_encoding_status: Optional[ContentEncodingStatusL3Enum] = None # Made optional
    explicit_metadata: List[ExplicitMetadata] = Field(default_factory=list)
    content_structure_markers: List[str] = Field(default_factory=list)
    lexical_affordances: LexicalAffordances
    syntactic_hints: SyntacticHints
    pragmatic_affective_affordances: PragmaticAffectiveAffordances
    relational_linking_markers: RelationalLinkingMarkers
    statistical_properties: Optional[StatisticalProperties] = None
    L3_flags: L3Flags # Renamed from "l3_flags"
    error_details: Optional[str] = None # Added for error cases in MR logic

class ConsequenceVector(BaseModel):
    immediacy: float
    visibility: float
    delay_ms: Optional[int] = None

class AACAssessabilityMap(BaseModel):
    version: Annotated[str, StringConstraints(pattern=r"^0\.1\.1$")] # Using regex for const
    die_score: float
    consequence_vector: ConsequenceVector
    dialogue_intensity: float
    aac_visibility_score: float

class LevelFindingItem(BaseModel):
    finding_type: FindingTypeEnum
    description: str
    confidence: Optional[confloat(ge=0, le=1)] = None
    source_anchor_component: Optional[str] = None
    related_cues_from_input: List[str] = Field(default_factory=list)
    implication_for_anchoring_note: Optional[str] = None

class EngagedLevelFindings(BaseModel):
    L1_Environment: Optional[List[LevelFindingItem]] = Field(default_factory=list)
    L2_Behavior: Optional[List[LevelFindingItem]] = Field(default_factory=list)
    L3_Capabilities: Optional[List[LevelFindingItem]] = Field(default_factory=list)
    L4_Beliefs_Values: Optional[List[LevelFindingItem]] = Field(default_factory=list)
    P5_Identity: Optional[List[LevelFindingItem]] = Field(default_factory=list)
    L6_Personhood: Optional[List[LevelFindingItem]] = Field(default_factory=list)
    L7_Interpersonal: Optional[List[LevelFindingItem]] = Field(default_factory=list)
    L8_Community: Optional[List[LevelFindingItem]] = Field(default_factory=list)
    L9_Global: Optional[List[LevelFindingItem]] = Field(default_factory=list)
    M10_Macrosystem: Optional[List[LevelFindingItem]] = Field(default_factory=list)

class PersonaAlignmentContextEngaged(BaseModel):
    version: Annotated[str, StringConstraints(pattern=r"^0\.1\.1$")]
    persona_uid: str # CRUX UID
    alignment_profile_ref: str # CRUX UID
    profile_version_ref: Optional[str] = None
    engagement_status: PAEngagementStatusEnum
    B0_P3_boundary_findings: List[dict] = Field(default_factory=list) # Simplified for now
    B11_boundary_findings: List[dict] = Field(default_factory=list) # Simplified
    engaged_level_findings: Optional[EngagedLevelFindings] = None # Made optional

class TraceThreadingContext(BaseModel):
    version: Annotated[str, StringConstraints(pattern=r"^0\.1\.1$")]
    parent_trace_id: Optional[str] = None # CRUX UID
    chain_id: Optional[str] = None # CRUX UID or String
    recursion_depth: Optional[int] = None
    perspective_role_in_chain: Optional[str] = None

class ResolvedEntity(BaseModel):
    mention: Optional[str] = None # Made optional
    resolved_uid: Optional[str] = None
    candidates: Optional[List[Any]] = Field(default_factory=list) # Made optional
    confidence: Optional[confloat(ge=0, le=1)] = None
    resolution_status: Optional[str] = None # Made optional
    source_component_ref: Optional[str] = None
    status_flag: Optional[str] = None # Added from MR logic example

class ResolvedConcept(BaseModel):
    mention: Optional[str] = None # Made optional
    resolved_uid: Optional[str] = None
    candidates: Optional[List[Any]] = Field(default_factory=list) # Made optional
    confidence: Optional[confloat(ge=0, le=1)] = None
    resolution_status: Optional[str] = None # Made optional
    source_component_ref: Optional[str] = None

class CoreferenceLink(BaseModel):
    pronoun_mention: Optional[str] = None # Made optional
    linked_entity_uid: Optional[str] = None # Made optional
    confidence: Optional[confloat(ge=0, le=1)] = None # Made optional

class ResolutionSummary(BaseModel):
    resolved_entities: Optional[List[ResolvedEntity]] = Field(default_factory=list) # Made optional
    resolved_concepts: Optional[List[ResolvedConcept]] = Field(default_factory=list) # Made optional
    coreference_links: Optional[List[CoreferenceLink]] = Field(default_factory=list) # Made optional

class TemporalSummaryL4(BaseModel):
    original_expression: Optional[str] = None # Made optional
    normalized_value: Optional[str] = None # Made optional
    normalization_status: Optional[str] = None # Made optional
    confidence: Optional[confloat(ge=0, le=1)] = None

class RelationshipSummaryL4(BaseModel):
    subject_uid: Optional[str] = None # Made optional
    predicate_hint: Optional[str] = None # Made optional
    object_uid: Optional[str] = None # Made optional
    relationship_type_guess: Optional[str] = None
    confidence: Optional[confloat(ge=0, le=1)] = None # Made optional

class InterpretationSummaryL4(BaseModel):
    primary_interaction_pattern_L4: Optional[str] = None
    confidence: Optional[confloat(ge=0, le=1)] = None # This confidence is for pattern, not goal
    primary_goal_intent_L4: Optional[str] = None
    # primary_goal_intent_L4_confidence: Optional[confloat(ge=0, le=1)] = None # Schema has this separate
    primary_schema_match_L4: Optional[str] = None # CRUX UID
    # primary_schema_match_L4_confidence: Optional[confloat(ge=0, le=1)] = None # Schema has this separate
    overall_relevance_score_L4: Optional[float] = None

class ValidationSummaryL4(BaseModel):
    overall_status_L4: L4ValidationStatusEnum
    key_anomaly_flags_L4: List[str] = Field(default_factory=list)

class IdentifiedKnowledgeGapL4(BaseModel):
    gap_id: str
    gap_type: KnowledgeGapTypeEnum
    required_info_description: str
    related_mention_or_cue: Optional[str] = None
    related_pa_level: Optional[str] = None
    confidence_impact_on_anchor: Optional[confloat(ge=0, le=1)] = None
    priority_hint: Optional[KnowledgeGapPriorityEnum] = None
    potential_resolution_path_hint: Optional[str] = None

class L4AnchorStateObj(BaseModel):
    version: Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")] # e.g. "0.2.17"
    l4_epistemic_state_of_anchoring: Optional[L4EpistemicStateOfAnchoringEnum] = None # Made optional for error states
    overall_anchor_confidence: Optional[confloat(ge=0, le=1)] = None
    AACAssessabilityMap: Optional[AACAssessabilityMap] = None # Made optional for error states
    persona_alignment_context_engaged: Optional[PersonaAlignmentContextEngaged] = None # Made optional
    trace_threading_context: Optional[TraceThreadingContext] = None
    resolution_summary: Optional[ResolutionSummary] = None # Made optional
    temporal_summary_L4: List[TemporalSummaryL4] = Field(default_factory=list)
    relationship_summary_L4: List[RelationshipSummaryL4] = Field(default_factory=list)
    interpretation_summary_L4: Optional[InterpretationSummaryL4] = None # Made optional
    validation_summary_L4: Optional[ValidationSummaryL4] = None # Made optional
    identified_knowledge_gaps_L4: List[IdentifiedKnowledgeGapL4] = Field(default_factory=list)
    error_details: Optional[str] = None # Added for error cases in MR logic
    l4_anchoring_completion_time: Optional[datetime] = None # Added from MR logic example


class ParticipantInteractionStats(BaseModel):
    contribution_count: Optional[int] = None # Made optional
    query_count: Optional[int] = None # Made optional
    dissent_signals_observed: Optional[int] = None # Made optional

class FieldParticipant(BaseModel):
    persona_uid: str # CRUX UID
    role_in_field: str
    engagement_readiness: ParticipantEngagementReadinessEnum
    last_interaction_in_field_time: Optional[datetime] = None
    interaction_stats_in_field: Optional[ParticipantInteractionStats] = None

class InteractionPatternSummary(BaseModel):
    primary_pattern_observed: Optional[str] = None
    participation_balance_metric: Optional[float] = None

class ActiveGovernance(BaseModel):
    policy_set_refs: List[str] = Field(default_factory=list) # CRUX UID
    norm_set_ref: Optional[str] = None
    applicable_schema_refs: List[str] = Field(default_factory=list) # CRUX UID
    brave_space_rules_ref: Optional[str] = None

class DialogueContext(BaseModel):
    current_dialogue_mode: DialogueModeEnum
    dissent_strength: DissentStrengthEnum
    sophistry_flag_L5: bool = False

class AACFieldReadiness(BaseModel):
    die_support_level: AACSupportLevelEnum
    consequence_tracking_enabled: bool
    dialogue_structure_support: DialogueStructureSupportEnum

class AxisMomentum(BaseModel):
    position_estimate: Optional[float] = None # Made optional
    velocity_estimate: Optional[float] = None # Made optional
    tendency_assessment: Optional[str] = None # Made optional
    flow_vector_assessment: Optional[str] = None

class MomentumProfile(BaseModel):
    axis1_power_participation: Optional[AxisMomentum] = None
    axis2_competition_community: Optional[AxisMomentum] = None
    axis3_hoarding_sustainability: Optional[AxisMomentum] = None
    overall_epistemic_flow_direction: Optional[EpistemicFlowDirectionEnum] = None

class LinkedBacklogItem(BaseModel):
    pbi_uid: str # CRUX UID
    status_in_field: PBIStatusInFieldEnum
    relevance_to_current_trace: Optional[float] = None

class WorkManagement(BaseModel):
    current_wip_count: int
    wip_limit_policy_ref: Optional[str] = None
    sequence_hints_for_next: List[str] = Field(default_factory=list) # CRUX UID of PBI
    monitoring_flags_from_L5: List[str] = Field(default_factory=list)

class RiskIndicator(BaseModel):
    risk_type_code: Optional[str] = None # Made optional
    description: Optional[str] = None # Made optional
    severity_hint: Optional[RiskSeverityHintEnum] = None # Made optional

class LCLForecastForField(BaseModel):
    predicted_lcl_state: Optional[str] = None # Made optional
    confidence: Optional[confloat(ge=0, le=1)] = None # Made optional
    contributing_factors: Optional[List[str]] = Field(default_factory=list) # Made optional

class FieldRiskAssessment(BaseModel):
    risk_indicators: List[RiskIndicator] = Field(default_factory=list)
    lcl_forecast_for_field: List[LCLForecastForField] = Field(default_factory=list)

class BraveSpaceDynamics(BaseModel):
    activation_status: BraveSpaceActivationStatusEnum
    tension_index: Optional[float] = None
    active_scaffolds: List[str] = Field(default_factory=list) # Identifier of active scaffold/protocol
    scaffold_recommendation_for_next: Optional[str] = None

class SharedTarget(BaseModel):
    target_id: Optional[str] = None # Made optional
    description: Optional[str] = None # Made optional
    status: Optional[str] = None # Made optional

class FieldObjectives(BaseModel):
    primary_intent_summary: Optional[str] = None
    shared_targets: List[SharedTarget] = Field(default_factory=list)

class CurrentTraceSOPProvenance(BaseModel):
    processed_trace_id: str # CRUX UID
    sop_executed_at_L5: Annotated[str, StringConstraints(pattern=r"^lC\.SOP\.field_click$")]
    field_state_version_before_this_update: Optional[str] = None
    key_changes_by_this_trace: List[str] = Field(default_factory=list)

class FieldMaturity(BaseModel): # Renamed from "SessionMaturity" to match MR logic example
    igd_stage_assessment: IGDStageAssessmentEnum
    readiness_for_L6_reflection_flag: bool
    assessment_rationale_summary: Optional[str] = None

class DownstreamDirectives(BaseModel):
    presentation_context_hint_for_L6: Optional[str] = None
    next_action_recommendation_for_L6: Optional[str] = None
    required_capabilities_hint_for_L6: List[str] = Field(default_factory=list)

class L5FieldStateObj(BaseModel):
    version: Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")] # e.g. "0.2.0"
    l5_epistemic_state_of_field_processing: Optional[L5EpistemicStateOfFieldProcessingEnum] = None # Made optional for error states
    overall_field_stability_score_hint: Optional[confloat(ge=0, le=1)] = None
    field_instance_uid: Optional[str] = None # CRUX UID, made optional for error states
    field_type: Optional[str] = None
    field_tags: List[str] = Field(default_factory=list)
    field_topic_summary: Optional[str] = None
    field_status: Optional[FieldStatusEnum] = None # Made optional
    related_field_uids: List[str] = Field(default_factory=list) # CRUX UID
    field_temporal_context: Optional[FieldTemporalContext] = None
    field_participants: List[FieldParticipant] = Field(default_factory=list)
    interaction_pattern_summary: Optional[InteractionPatternSummary] = None
    active_governance: Optional[ActiveGovernance] = None
    dialogue_context: Optional[DialogueContext] = None # Made optional
    aac_field_readiness: Optional[AACFieldReadiness] = None # Made optional
    momentum_profile: Optional[MomentumProfile] = None
    linked_backlog_items: List[LinkedBacklogItem] = Field(default_factory=list)
    new_backlog_items_generated_by_trace: List[str] = Field(default_factory=list) # CRUX UID
    work_management: Optional[WorkManagement] = None # Made optional
    field_risk_assessment: Optional[FieldRiskAssessment] = None
    brave_space_dynamics: Optional[BraveSpaceDynamics] = None # Made optional
    field_objectives: Optional[FieldObjectives] = Field(default_factory=dict)
    current_trace_sop_provenance: Optional[CurrentTraceSOPProvenance] = None # Made optional
    session_maturity: Optional[FieldMaturity] = None # Renamed from field_maturity in schema, made optional
    downstream_directives: Optional[DownstreamDirectives] = Field(default_factory=dict)
    error_details: Optional[str] = None # Added for error cases in MR logic
    l5_field_processing_completion_time: Optional[datetime] = None # Added from MR logic example

class PayloadMetadataTarget(BaseModel):
    consumer_type: ConsumerTypeEnum
    consumer_uid_hint: Optional[str] = None
    channel_hint: Optional[str] = None

class PayloadMetadata(BaseModel):
    generation_sop: Annotated[str, StringConstraints(pattern=r"^lC\.SOP\.reflect_boom$")]
    generation_timestamp: datetime
    source_trace_id: str # CRUX UID
    source_field_instance_uid: Optional[str] = None # CRUX UID, made optional as not in all MR logic paths
    source_field_state_version_ref: Optional[str] = None
    presentation_target: PayloadMetadataTarget
    presentation_intent: str
    output_modality: OutputModalityEnum
    target_schema_ref: Optional[str] = None # CRUX UID or string ref
    L6_processing_confidence: Optional[confloat(ge=0, le=1)] = None
    error_details: Optional[str] = None # Added from MR logic example

class RedactionStatus(BaseModel):
    version: Optional[Annotated[str, StringConstraints(pattern=r"^0\.1\.0$")]] = None # Made optional
    redaction_applied: bool
    redaction_policy_ref: Optional[str] = None
    redacted_categories_hint: List[str] = Field(default_factory=list)

class OmittedContentSummary(BaseModel):
    version: Optional[Annotated[str, StringConstraints(pattern=r"^0\.1\.1$")]] = None # Made optional
    omission_applied: bool
    omitted_categories: List[OmittedContentCategoryEnum] = Field(default_factory=list)
    omission_rationale_code: Optional[OmissionRationaleCodeEnum] = None


class TransformationMetadata(BaseModel):
    version: Optional[Annotated[str, StringConstraints(pattern=r"^0\.1\.1$")]] = None # Made optional
    selection_profile_applied: Optional[str] = None
    transformation_profile_applied: Optional[str] = None
    adaptation_profile_applied: Optional[str] = None
    redaction_status: RedactionStatus
    simplification_level_hint: SimplificationLevelHintEnum = SimplificationLevelHintEnum.NONE
    potential_fidelity_loss_areas: List[str] = Field(default_factory=list)
    omitted_content_summary: OmittedContentSummary

class AssessedCynefinState(BaseModel):
    version: Optional[Annotated[str, StringConstraints(pattern=r"^0\.1\.0$")]] = None # Made optional
    domain: CynefinDomainEnum
    rationale_hint: Optional[str] = None
    confidence_score: Optional[confloat(ge=0, le=1)] = None

class CynefinZoneTransition(BaseModel):
    version: Optional[Annotated[str, StringConstraints(pattern=r"^0\.1\.1$")]] = None # Made optional
    from_domain: str
    to_formatted_domain_hint: str
    transition_risk_level: str # Not an enum in schema, but has fixed values in MR
    rationale: Optional[str] = None

class BraveSpaceReflection(BaseModel):
    version: Optional[Annotated[str, StringConstraints(pattern=r"^0\.1\.0$")]] = None # Made optional
    L5_activation_status_hint: Optional[str] = None
    L5_dissent_strength_hint: Optional[str] = None
    L5_tension_index_hint: Optional[float] = None
    L6_transformation_dissent_risk_hint: TransformationDissentRiskHintEnum = TransformationDissentRiskHintEnum.MINIMAL
    L6_representation_discomfort_risk_hint: RepresentationDiscomfortRiskHintEnum = RepresentationDiscomfortRiskHintEnum.MINIMAL_DISCOMFORT

class ReflectionSurface(BaseModel):
    version: Optional[Annotated[str, StringConstraints(pattern=r"^0\.1\.2$")]] = None # Made optional
    assessed_cynefin_state: AssessedCynefinState
    cynefin_zone_transition: Optional[CynefinZoneTransition] = None
    representation_warning_flags: List[str] = Field(default_factory=list)
    brave_space_reflection: BraveSpaceReflection

class KeyLevelFindingSummary(BaseModel):
    level: str
    finding_summary: str
    original_finding_type: Optional[str] = None
    relevance_score_to_intent: Optional[confloat(ge=0, le=1)] = None

class ReflectedPAContextSummary(BaseModel):
    version: Optional[Annotated[str, StringConstraints(pattern=r"^0\.1\.0$")]] = None # Made optional
    source_pa_profile_ref: Optional[str] = None # CRUX UID
    source_pa_engagement_status: Optional[str] = None
    key_level_findings_summary: List[KeyLevelFindingSummary] = Field(default_factory=list)
    alignment_gap_summary: List[str] = Field(default_factory=list)

class FieldDiagnosticsSummaryHints(BaseModel):
    version: Optional[Annotated[str, StringConstraints(pattern=r"^0\.1\.0$")]] = None # Made optional
    L5_epistemic_state_hint: Optional[str] = None
    maturity_stage_hint: Optional[str] = None
    aac_visibility_score_hint: Optional[confloat(ge=0, le=1)] = None

class MultimodalPackageItem(BaseModel):
    content_type: str
    content_ref: str # CRUX UID or String
    description: Optional[str] = None
    rendering_hint: Optional[str] = None

class PayloadContent(BaseModel):
    version: Optional[Annotated[str, StringConstraints(pattern=r"^0\.1\.1$")]] = None # Made optional
    structured_data: Optional[dict] = None
    formatted_text: Optional[str] = None
    multimodal_package: Optional[List[MultimodalPackageItem]] = None
    api_payload: Optional[Union[dict, str]] = None
    # oneOf constraint is handled by Pydantic's Union and manual validation if needed

class NextActionDirective(BaseModel):
    directive_type: L7DirectiveTypeEnum # Corrected from schema, was L6
    target_sop_or_param: Optional[str] = None # CRUX UID or String
    context_hint: Optional[str] = None

class L6ReflectionPayloadObj(BaseModel):
    version: Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")] # e.g. "0.1.6"
    l6_epistemic_state: Optional[L6EpistemicStateEnum] = None # Made optional for error states
    redaction_applied_summary: bool
    payload_metadata: PayloadMetadata
    transformation_metadata: TransformationMetadata
    reflection_surface: ReflectionSurface
    reflected_pa_context_summary: Optional[ReflectedPAContextSummary] = None
    persona_exposure_flags: Optional[List[str]] = Field(default_factory=list)
    field_diagnostics_summary_hints: Optional[FieldDiagnosticsSummaryHints] = None
    payload_content: PayloadContent
    supplemental_context_refs: List[str] = Field(default_factory=list) # CRUX UID
    next_action_directives: List[NextActionDirective] = Field(default_factory=list)

class AlignmentVector(BaseModel):
    temporal_plane: L7TemporalPlaneEnum
    dimensional_plane: L7DimensionalPlaneEnum
    alignment_pivot: str

class ParticipationRole(BaseModel):
    persona_uid: str
    role_type: L7RoleTypeEnum

class PBIEntry(BaseModel):
    pbi_uid: str # CRUX UID
    pbi_type: L7PbiTypeEnum
    summary: str
    alignment_vector: AlignmentVector
    participation_roles: Optional[List[ParticipationRole]] = Field(default_factory=list) # Made optional
    subtask_refs: Optional[List[str]] = Field(default_factory=list) # Made optional
    status_hint: L7PBIStatusHintEnum = L7PBIStatusHintEnum.PENDING

class L7Backlog(BaseModel):
    version: Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]
    single_loop: Optional[List[PBIEntry]] = Field(default_factory=list) # Made optional
    double_loop: Optional[List[PBIEntry]] = Field(default_factory=list) # Made optional
    triple_loop: Optional[List[PBIEntry]] = Field(default_factory=list) # Made optional

class SeedOption(BaseModel):
    option_id: str
    label: str
    action_type: str
    action_params: Optional[dict] = None

class SeedOptions(BaseModel):
    version: Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]
    prompt_for_next_action: Optional[str] = None
    options: List[SeedOption]
    allow_free_text_input_for_other: bool = False
    default_option_id: Optional[str] = None

class SeedOutputItem(BaseModel):
    output_UID: str # CRUX UID
    target_consumer_hint: dict # Simplified, define L7OutputConsumerHint if needed
    output_modality: L7OutputModalityEnum
    content: Union[str, dict, list]
    seed_options: Optional[SeedOptions] = None

class L7EncodedApplication(BaseModel):
    version_L7_payload: Optional[Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]] = "0.1.1" # Corrected: Added as field
    L7_backlog: Optional[L7Backlog] = None # Made optional based on MR logic
    seed_outputs: Optional[List[SeedOutputItem]] = Field(default_factory=list) # Made optional
    # Based on MR logic, application_receipt fields are part of L7_trace or seed_QA_QC

# Nested content models
class L1StartleReflex(BaseModel):
    L1_startle_context_obj: L1StartleContextObj
    L2_frame_type: L2FrameTypeObj # Placeholder for L2FrameType

class L2FrameType(BaseModel):
    L2_frame_type_obj: L2FrameTypeObj
    L3_surface_keymap: L3SurfaceKeymapObj # Placeholder for L3SurfaceKeymap

class L3SurfaceKeymap(BaseModel):
    L3_surface_keymap_obj: L3SurfaceKeymapObj
    L4_anchor_state: L4AnchorStateObj # Placeholder for L4AnchorState

class L4AnchorState(BaseModel):
    L4_anchor_state_obj: L4AnchorStateObj
    L5_field_state: L5FieldStateObj # Placeholder for L5FieldState

class L5FieldState(BaseModel):
    L5_field_state_obj: L5FieldStateObj
    L6_reflection_payload: L6ReflectionPayloadObj # Placeholder for L6ReflectionPayload

class L6ReflectionPayload(BaseModel):
    L6_reflection_payload_obj: L6ReflectionPayloadObj
    L7_encoded_application: L7EncodedApplication


# Top-level seed_content
class SeedContent(BaseModel):
    raw_signals: List[RawSignal]
    L1_startle_reflex: L1StartleReflex

# Trace metadata models
class L1Trace(BaseModel):
    version_L1_trace_schema: Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]
    sop_name: Annotated[str, StringConstraints(pattern=r"^lC\.SOP\.startle$")]
    completion_timestamp_L1: datetime # Renamed from completion_timestamp_l1
    epistemic_state_L1: L1EpistemicStateOfStartleEnum
    L1_trace_creation_time_from_context: datetime # Renamed
    L1_input_origin_from_context: Optional[str] = None # Renamed
    L1_signal_component_count: conint(ge=1) # Renamed
    L1_generated_trace_id: Optional[str] = None # Added from MR logic
    L1_generated_raw_signal_ref_uids_summary: Optional[dict] = None # Added from MR logic
    L1_applied_policy_refs: List[str] = Field(default_factory=list)
    error_detail: Optional[str] = None # Added for error states in MR logic

class L2Trace(BaseModel):
    version_L2_trace_schema: Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]
    sop_name: Annotated[str, StringConstraints(pattern=r"^lC\.SOP\.frame_click$")]
    completion_timestamp_L2: datetime # Renamed
    epistemic_state_L2: L2EpistemicStateOfFramingEnum
    L2_input_class_determined_in_trace: Optional[InputClassL2Enum] = None # Renamed
    L2_frame_type_determined_in_trace: Optional[str] = None # Renamed
    L2_temporal_hint_provenance_in_trace: Optional[TemporalHintProvenanceL2Enum] = None # Renamed
    L2_communication_context_summary: Optional[dict] = None # Added from MR logic
    L2_validation_status_in_trace: Optional[L2ValidationStatusOfFrameEnum] = None # Renamed
    L2_anomaly_flags_count: Optional[int] = None # Added from MR logic
    L2_applied_policy_refs: List[str] = Field(default_factory=list)
    error_detail: Optional[str] = None # Added for error states in MR logic
    error_details: Optional[str] = None # Added for error states in MR logic (consistency)

class L3Trace(BaseModel):
    version_L3_trace_schema: Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]
    sop_name: Annotated[str, StringConstraints(pattern=r"^lC\.SOP\.keymap_click$")]
    completion_timestamp_L3: datetime # Renamed
    epistemic_state_L3: Optional[str] = None # Enum: Keymapped_Successfully, LCL-Clarify-Semantics_L3 etc.
    L3_primary_language_detected_code: Optional[str] = None # Renamed
    L3_content_encoding_status_determined: Optional[ContentEncodingStatusL3Enum] = None # Renamed
    L3_lexical_affordances_summary: Optional[dict] = None # Added from MR logic
    L3_generated_flags_summary: Optional[dict] = None # Renamed
    L3_applied_policy_refs: List[str] = Field(default_factory=list)
    error_details: Optional[str] = None # Added for error states in MR logic

class L4Trace(BaseModel):
    version_L4_trace_schema: Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]
    sop_name: Annotated[str, StringConstraints(pattern=r"^lC\.SOP\.anchor_click$")]
    completion_timestamp_L4: datetime # Renamed
    epistemic_state_L4: L4EpistemicStateOfAnchoringEnum
    L4_pa_profile_engaged_ref_in_trace: Optional[str] = None # CRUX UID, Renamed
    L4_pa_engagement_status_in_trace: Optional[PAEngagementStatusEnum] = None # Added from MR logic
    L4_aac_visibility_score_from_anchor_state: Optional[confloat(ge=0, le=1)] = None # Renamed
    L4_overall_anchor_confidence_from_anchor_state: Optional[confloat(ge=0, le=1)] = None # Renamed
    L4_knowledge_gaps_identified_count: Optional[int] = None # Added from MR logic
    L4_applied_policy_refs: List[str] = Field(default_factory=list)
    error_details: Optional[str] = None # Added for error states in MR logic

class L5Trace(BaseModel):
    version_L5_trace_schema: Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]
    sop_name: Annotated[str, StringConstraints(pattern=r"^lC\.SOP\.field_click$")]
    completion_timestamp_L5: datetime # Renamed
    epistemic_state_L5: L5EpistemicStateOfFieldProcessingEnum
    L5_field_instance_uid_processed: Optional[str] = None # CRUX UID, Renamed
    L5_field_status_after_update: Optional[FieldStatusEnum] = None # Renamed
    L5_dialogue_mode_assessed_in_trace: Optional[DialogueModeEnum] = None # Renamed
    L5_dissent_strength_assessed_in_trace: Optional[DissentStrengthEnum] = None # Renamed
    L5_igd_stage_assessed_in_trace: Optional[IGDStageAssessmentEnum] = None # Renamed
    L5_risk_level_summary_in_trace: Optional[str] = None # Renamed
    L5_applied_policy_refs: List[str] = Field(default_factory=list)
    L5_new_pbis_generated_count: Optional[int] = None # Added from MR logic
    error_details: Optional[str] = None # Added for error states in MR logic

class L6Trace(BaseModel):
    version_L6_trace_schema: Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]
    sop_name: Annotated[str, StringConstraints(pattern=r"^lC\.SOP\.reflect_boom$")]
    completion_timestamp_L6: datetime # Renamed
    epistemic_state_L6: L6EpistemicStateEnum
    L6_presentation_target_consumer_type: Optional[ConsumerTypeEnum] = None # Renamed
    L6_presentation_intent_resolved: Optional[str] = None # Renamed
    L6_output_modality_used: Optional[OutputModalityEnum] = None # Renamed
    L6_processing_confidence_score_from_payload: Optional[confloat(ge=0, le=1)] = None # Renamed
    L6_redaction_applied_summary_from_payload: Optional[bool] = None # Renamed
    L6_simplification_level_hint_applied: Optional[SimplificationLevelHintEnum] = None # Renamed
    L6_cynefin_transition_risk_assessed: Optional[str] = None # Renamed, not enum in schema
    L6_applied_policy_refs: List[str] = Field(default_factory=list)
    error_details: Optional[str] = None # Added from MR logic


class L7TraceActionExecutionSummary(BaseModel): # Added from MR logic example
    primary_action_type_executed: Optional[str] = None
    action_execution_status: Optional[str] = None # Enum: Success, Failure, Partial_Success
    action_related_lcl_trigger: Optional[str] = None

class L7Trace(BaseModel):
    version_L7_trace_schema: Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]
    sop_name: Annotated[str, StringConstraints(pattern=r"^lC\.SOP\.apply_done$")]
    completion_timestamp_L7: datetime # Renamed
    epistemic_state_L7: L7EpistemicStateEnum
    L7_application_intent_resolved: Optional[str] = None # Renamed
    summary_seed_integrity_status_from_receipt: Optional[SeedIntegrityStatusEnum] = None # Renamed
    summary_outcome_confidence_from_receipt: Optional[confloat(ge=0, le=1)] = None # Renamed
    L7_summary_flags_for_orchestration: Optional[dict] = None # Renamed
    L7_applied_policy_refs: List[str] = Field(default_factory=list)
    L7_action_execution_summary: Optional[L7TraceActionExecutionSummary] = None # Added from MR logic
    error_details: Optional[str] = None # Added for error states in MR logic

class TraceMetadata(BaseModel):
    trace_id: str # CRUX UID
    L1_trace: L1Trace
    L2_trace: L2Trace
    L3_trace: L3Trace
    L4_trace: L4Trace
    L5_trace: L5Trace
    L6_trace: L6Trace
    L7_trace: L7Trace

class IntegrityFinding(BaseModel):
    finding_id: str
    check_category_code: QAQCCheckCategoryCodeEnum
    target_layer_or_component: str
    description_of_finding: str
    severity_level: QAQCSeverityLevelEnum
    applied_policy_ref_for_check: Optional[str] = None
    recommended_action_hint: Optional[str] = None

class SummaryOfChecksPerformed(BaseModel): # Added from schema
    total_checks_defined_in_policy: Optional[int] = None
    total_checks_executed: Optional[int] = None
    checks_passed: Optional[int] = None
    checks_with_warnings: Optional[int] = None
    checks_failed_non_blocking: Optional[int] = None
    checks_failed_blocking: Optional[int] = None

class SeedQAQC(BaseModel):
    version_seed_qa_qc_schema: Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]
    overall_seed_integrity_status: SeedIntegrityStatusEnum
    qa_qc_assessment_timestamp: datetime
    summary_of_checks_performed: Optional[SummaryOfChecksPerformed] = None # Added from schema
    integrity_findings: List[IntegrityFinding] = Field(default_factory=list)
    error_details: Optional[str] = None # Added for error states in MR logic (consistency)

# Top-level madaSeed model
class MadaSeed(BaseModel):
    version: Annotated[str, StringConstraints(pattern=r"^\d+\.\d+\.\d+$")]
    seed_id: str # CRUX UID
    seed_content: SeedContent
    trace_metadata: TraceMetadata
    seed_QA_QC: SeedQAQC # Renamed from seed_QA_QC
    seed_completion_timestamp: Optional[datetime] = None # Made optional as it's set by L7

# Update forward references
L1StartleReflex.update_forward_refs()
L2FrameType.update_forward_refs()
L3SurfaceKeymap.update_forward_refs()
L4AnchorState.update_forward_refs()
L5FieldState.update_forward_refs()
L6ReflectionPayload.update_forward_refs()

# If __name__ == "__main__": section for basic validation example
if __name__ == "__main__":
    # Example of how to create a MadaSeed instance (partially filled for brevity)
    # This requires filling in all required fields according to the structure.
    # Due to the complexity, a full valid example is too long for here.
    # This is just to show the top-level structure.
    try:
        print("Pydantic models for madaSeed schema defined successfully.")
        print("To use, import these models and populate them with data.")
        # Example: test_data = MadaSeed(version="0.3.0", seed_id="urn:crux:uid::testseed1", ...)
        # You would need to construct all nested objects.
    except Exception as e:
        print(f"Error defining models: {e}")
