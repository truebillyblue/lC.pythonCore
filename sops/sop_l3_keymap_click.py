from datetime import datetime as dt, timezone
from typing import List, Dict, Tuple, Any, Optional, Union

from ..schemas.mada_schema import ( # Corrected path
    MadaSeed, L2FrameTypeObj, L3SurfaceKeymapObj, L3Trace,
    DetectedLanguage, ContentEncodingStatusL3Enum, ExplicitMetadata,
    LexicalAffordances, KeywordMention, EntityMentionRaw, NumericalQuantityMention, TemporalExpressionMention, QuantifierQualifierMention, NegationMarker,
    SyntacticHints, EmojiMention,
    PragmaticAffectiveAffordances, FormalityHint, SentimentHint, PolitenessMarkers, UrgencyMarkers, PowerDynamicMarkers, InteractionPatternAffordance, ShallowGoalIntentAffordance, ActorRoleHint,
    RelationalLinkingMarkers, ExplicitRelationalPhrases, ExplicitReferenceMarkers, UrlMentions, PriorTraceReference,
    StatisticalProperties, StatisticalValue, StatisticalScore,
    L3Flags, L3FlagDetail, GriceanViolationHints, 
    EncodingStatusL1Enum 
)
from ..services.mock_lc_core_services import mock_lc_mem_core_get_object # Corrected path

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

def _keymap_validate_l2_data_in_madaSeed(mada_seed_input: MadaSeed) -> bool:
    """Validates essential L2 data presence within the input MadaSeed for L3 processing."""
    try:
        if not mada_seed_input:
            log_internal_warning("Helper:_keymap_validate_l2_data", {"error": "Input madaSeed is None"})
            return False

        l2_frame_type_obj = mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L2_frame_type_obj
        l2_trace = mada_seed_input.trace_metadata.L2_trace

        if not l2_frame_type_obj or not l2_frame_type_obj.version:
            log_internal_warning("Helper:_keymap_validate_l2_data", {"error": "Missing or invalid L2_frame_type_obj in madaSeed for L3"})
            return False
        if not l2_trace or not l2_trace.epistemic_state_L2:
            log_internal_warning("Helper:_keymap_validate_l2_data", {"error": "Missing or invalid L2_trace in madaSeed for L3"})
            return False
        if not l2_trace.epistemic_state_L2.name.startswith("FRAMED"): # FRAMED
            log_internal_info("Helper:_keymap_validate_l2_data", {"reason": f"L2 state '{l2_trace.epistemic_state_L2.name}' not suitable for L3 keymapping."})
            return False
    except AttributeError as e:
        log_internal_warning("Helper:_keymap_validate_l2_data", {"error": f"AttributeError validating L2 data: {str(e)}"})
        return False
    except Exception as e:
        log_internal_warning("Helper:_keymap_validate_l2_data", {"error": f"Exception validating L2 data: {str(e)}"})
        return False
    return True

def _keymap_get_current_timestamp_utc() -> str:
    """Returns a fixed, unique timestamp string."""
    return "2023-10-28T11:15:00Z"

def _keymap_get_primary_content_from_madaSeed(mada_seed_input: MadaSeed) -> Optional[str]:
    """
    Retrieves primary raw signal content using mock_lc_mem_core_get_object.
    Returns content string, "[[BINARY_CONTENT_PLACEHOLDER]]", or None.
    """
    try:
        l1_startle_context = mada_seed_input.seed_content.L1_startle_reflex.L1_startle_context_obj
        
        primary_signal_ref_uid: Optional[str] = None
        primary_component_encoding_status: Optional[EncodingStatusL1Enum] = None

        # Determine the primary signal component UID and its encoding status
        for comp_meta in l1_startle_context.signal_components_metadata_L1:
            if comp_meta.component_role_L1 and 'primary' in comp_meta.component_role_L1.lower():
                primary_signal_ref_uid = comp_meta.raw_signal_ref_uid_L1
                primary_component_encoding_status = comp_meta.encoding_status_L1
                break
        
        # Fallback if no 'primary' role found, take the first component's ref
        if not primary_signal_ref_uid and l1_startle_context.signal_components_metadata_L1:
            primary_signal_ref_uid = l1_startle_context.signal_components_metadata_L1[0].raw_signal_ref_uid_L1
            primary_component_encoding_status = l1_startle_context.signal_components_metadata_L1[0].encoding_status_L1
        
        if primary_signal_ref_uid:
            if primary_component_encoding_status == EncodingStatusL1Enum.DETECTEDBINARY:
                # For binary content, we don't fetch from MADA store for keymapping, return placeholder
                return "[[BINARY_CONTENT_PLACEHOLDER]]"
            else:
                # Call the mock service function to get content from the mock_mada_store
                content = mock_lc_mem_core_get_object(
                    object_uid=primary_signal_ref_uid,
                    default_value=f"Default mock content for UID {primary_signal_ref_uid} (not found in mock_mada_store)"
                )
                # Ensure content is a string, as expected by downstream helpers
                if not isinstance(content, str):
                    log_internal_warning("_keymap_get_primary_content_from_madaSeed", 
                                         {"warning": f"Content for UID {primary_signal_ref_uid} from mock_mada_store is not a string (type: {type(content)}). Using placeholder."})
                    # Attempt to find the original placeholder from raw_signals if content is not string
                    # This part of the logic might be redundant if mock_mada_store always returns strings or the intended content.
                    raw_signals = mada_seed_input.seed_content.raw_signals
                    for rs in raw_signals:
                        if rs.raw_input_id == primary_signal_ref_uid:
                            return str(rs.raw_input_signal) # Fallback to the placeholder in raw_signals
                    return f"Placeholder for non-string content from UID {primary_signal_ref_uid}"
                return content
        else:
            log_internal_warning("_keymap_get_primary_content_from_madaSeed", {"warning": "No primary_signal_ref_uid could be determined to fetch content."})

    except Exception as e:
        log_internal_error("_keymap_get_primary_content_from_madaSeed", {"error": str(e)})
    return None


def _keymap_detect_language(primary_content_str: Optional[str]) -> List[DetectedLanguage]:
    if primary_content_str and primary_content_str != "[[BINARY_CONTENT_PLACEHOLDER]]":
        return [DetectedLanguage(language_code="en", confidence=0.9)]
    return []

def _keymap_check_encoding(primary_content_str: Optional[str]) -> ContentEncodingStatusL3Enum:
    if primary_content_str == "[[BINARY_CONTENT_PLACEHOLDER]]":
        return ContentEncodingStatusL3Enum.BINARYDETECTED
    return ContentEncodingStatusL3Enum.CONFIRMEDUTF8

def _keymap_extract_explicit_meta(primary_content_str: Optional[str], l2_frame_type_str: Optional[str]) -> List[ExplicitMetadata]:
    return []

def _keymap_extract_structure_markers(primary_content_str: Optional[str], l2_frame_type_str: Optional[str]) -> List[str]:
    return []

def _keymap_extract_lexical(primary_content_str: Optional[str], l2_frame_type_str: Optional[str]) -> LexicalAffordances:
    lex_affordances = LexicalAffordances(
        keyword_mentions=[],
        entity_mentions_raw=[],
        numerical_quantity_mentions=[],
        temporal_expression_mentions=[],
        quantifier_qualifier_mentions=[],
        negation_markers=[]
    )
    if primary_content_str and "urgent" in primary_content_str.lower():
        lex_affordances.keyword_mentions.append(KeywordMention(term="urgent", confidence=0.7))
    return lex_affordances

def _keymap_derive_syntactic(primary_content_str: Optional[str], l2_frame_type_str: Optional[str]) -> SyntacticHints:
    return SyntacticHints(
        sentence_type_distribution={},
        pos_tagging_candidate_flag=True if primary_content_str and primary_content_str != "[[BINARY_CONTENT_PLACEHOLDER]]" else False,
        punctuation_analysis={},
        capitalization_analysis={},
        emoji_mentions=[]
    )

def _keymap_derive_pragmatic_affective(lexical_data: LexicalAffordances, syntactic_data: SyntacticHints) -> PragmaticAffectiveAffordances:
    # Baseline: return dict with default/empty values.
    return PragmaticAffectiveAffordances(
        formality_hint=FormalityHint(), 
        sentiment_hint=SentimentHint(), 
        politeness_markers=PolitenessMarkers(), 
        urgency_markers=UrgencyMarkers(),
        power_dynamic_markers=PowerDynamicMarkers(),
        interaction_pattern_affordance=InteractionPatternAffordance(),
        shallow_goal_intent_affordance=ShallowGoalIntentAffordance(),
        actor_role_hint=ActorRoleHint()
    )

def _keymap_extract_relational_linking(primary_content_str: Optional[str]) -> RelationalLinkingMarkers:
    return RelationalLinkingMarkers(
        explicit_relational_phrases=ExplicitRelationalPhrases(detected=[]),
        explicit_reference_markers=ExplicitReferenceMarkers(detected=[]),
        url_mentions=UrlMentions(detected_urls=[]),
        prior_trace_references=[]
    )

def _keymap_calculate_stats(primary_content_str: Optional[str], l2_frame_type_str: Optional[str]) -> Optional[StatisticalProperties]:
    if primary_content_str and primary_content_str != "[[BINARY_CONTENT_PLACEHOLDER]]":
        # Simple token count for baseline
        token_count = len(primary_content_str.split())
        return StatisticalProperties(token_count=StatisticalValue(value=token_count))
    return None

def _keymap_identify_anomalies(working_l3_surface_keymap_obj: L3SurfaceKeymapObj) -> L3Flags:
    # Baseline: return dict with {"low_confidence_overall_flag": {"detected": False}}.
    return L3Flags(
        internal_contradiction_hint=L3FlagDetail(detected=False),
        mixed_affect_signal=L3FlagDetail(detected=False),
        multivalent_cue_detected=L3FlagDetail(detected=False),
        low_confidence_overall_flag=L3FlagDetail(detected=False),
        gricean_violation_hints=GriceanViolationHints(detected=[])
    )

def _keymap_validate_and_determine_outcome(working_l3_surface_keymap_obj: L3SurfaceKeymapObj) -> str: # Returns epistemic state string
    # Baseline: return "Keymapped_Successfully".
    # Future HR: Implement logic based on L3 policies and content of working_l3_surface_keymap_obj
    # For example, if working_l3_surface_keymap_obj.L3_flags.low_confidence_overall_flag.detected:
    #     return "LCL-Clarify-Semantics_L3" 
    return "Keymapped_Successfully"


# --- Main keymap_click Process Function ---

def keymap_click_process(mada_seed_input: MadaSeed) -> MadaSeed:
    """
    Processes the madaSeed object from L2 (frame_click) to populate L3 surface keymap information.
    """
    current_time_fail_dt = dt.fromisoformat(_keymap_get_current_timestamp_utc().replace('Z', '+00:00'))

    if not _keymap_validate_l2_data_in_madaSeed(mada_seed_input):
        error_detail_msg = "Invalid or incomplete L2 data in input madaSeed for L3 processing."
        log_critical_error("keymap_click_process L2 Data Error", {"trace_id": mada_seed_input.seed_id if mada_seed_input else "Unknown", "error": error_detail_msg})
        
        if mada_seed_input:
            mada_seed_input.trace_metadata.L3_trace = L3Trace(
                version_L3_trace_schema="0.1.0", sop_name="lC.SOP.keymap_click",
                completion_timestamp_L3=current_time_fail_dt,
                epistemic_state_L3="LCL-Failure-Internal_L3", # L3 specific LCL
                error_details=error_detail_msg
            )
            mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj = L3SurfaceKeymapObj(
                version="0.1.1", 
                lexical_affordances={}, syntactic_hints={}, pragmatic_affective_affordances={}, relational_linking_markers={}, L3_flags={}, # Required empty sub-models
                error_details=f"L3 aborted: {error_detail_msg}"
            )
        return mada_seed_input

    trace_id = mada_seed_input.seed_id
    l2_frame_type_obj = mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L2_frame_type_obj
    
    # Initialize L3_surface_keymap_obj with version
    working_l3_surface_keymap_obj = L3SurfaceKeymapObj(version="0.1.1", lexical_affordances={}, syntactic_hints={}, pragmatic_affective_affordances={}, relational_linking_markers={}, L3_flags={}) # Ensure required sub-models are initialized
    
    try:
        input_frame_type_from_l2 = l2_frame_type_obj.frame_type_L2
        primary_content_for_l3 = _keymap_get_primary_content_from_madaSeed(mada_seed_input)

        if primary_content_for_l3 is None and (input_frame_type_from_l2 is None or "binary" not in input_frame_type_from_l2.lower()):
            # Only raise if not explicitly binary and content is None
            # If it's binary placeholder, some helpers can still run.
             if primary_content_for_l3 != "[[BINARY_CONTENT_PLACEHOLDER]]":
                raise ValueError("Missing primary text content for L3 keymapping and not identified as binary.")

        # --- Populate surface_map (working_l3_surface_keymap_obj) ---
        working_l3_surface_keymap_obj.detected_languages = _keymap_detect_language(primary_content_for_l3)
        working_l3_surface_keymap_obj.content_encoding_status = _keymap_check_encoding(primary_content_for_l3)
        working_l3_surface_keymap_obj.explicit_metadata = _keymap_extract_explicit_meta(primary_content_for_l3, input_frame_type_from_l2)
        working_l3_surface_keymap_obj.content_structure_markers = _keymap_extract_structure_markers(primary_content_for_l3, input_frame_type_from_l2)
        
        lexical_data = _keymap_extract_lexical(primary_content_for_l3, input_frame_type_from_l2)
        working_l3_surface_keymap_obj.lexical_affordances = lexical_data
        
        syntactic_data = _keymap_derive_syntactic(primary_content_for_l3, input_frame_type_from_l2)
        working_l3_surface_keymap_obj.syntactic_hints = syntactic_data
        
        working_l3_surface_keymap_obj.pragmatic_affective_affordances = _keymap_derive_pragmatic_affective(lexical_data, syntactic_data)
        working_l3_surface_keymap_obj.relational_linking_markers = _keymap_extract_relational_linking(primary_content_for_l3)
        working_l3_surface_keymap_obj.statistical_properties = _keymap_calculate_stats(primary_content_for_l3, input_frame_type_from_l2)
        working_l3_surface_keymap_obj.L3_flags = _keymap_identify_anomalies(working_l3_surface_keymap_obj)

        # --- Validate surface_map & Determine L3 Outcome ---
        final_l3_epistemic_state_str = _keymap_validate_and_determine_outcome(working_l3_surface_keymap_obj)
        
        # --- Update madaSeed object with L3 contributions ---
        mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj = working_l3_surface_keymap_obj

        # --- Populate L3_trace ---
        current_time_l3_final_dt = dt.fromisoformat(_keymap_get_current_timestamp_utc().replace('Z', '+00:00'))
        
        primary_lang_code = None
        if working_l3_surface_keymap_obj.detected_languages:
            primary_lang_code = working_l3_surface_keymap_obj.detected_languages[0].language_code

        low_conf_flag = False
        if working_l3_surface_keymap_obj.L3_flags and working_l3_surface_keymap_obj.L3_flags.low_confidence_overall_flag:
             low_conf_flag = working_l3_surface_keymap_obj.L3_flags.low_confidence_overall_flag.detected


        l3_trace_obj = L3Trace(
            version_L3_trace_schema="0.1.0", 
            sop_name="lC.SOP.keymap_click", 
            completion_timestamp_L3=current_time_l3_final_dt,
            epistemic_state_L3=final_l3_epistemic_state_str, # This should be an enum if defined, or string
            L3_primary_language_detected_code=primary_lang_code,
            L3_content_encoding_status_determined=working_l3_surface_keymap_obj.content_encoding_status,
            L3_generated_flags_summary={"low_confidence_overall_flagged": low_conf_flag }
        )
        mada_seed_input.trace_metadata.L3_trace = l3_trace_obj
        
        return mada_seed_input

    except Exception as critical_process_error:
        error_msg = f"Critical L3 Failure: {str(critical_process_error)}"
        log_critical_error("Keymap Click Process Failed Critically", {"trace_id": trace_id, "error": error_msg})
        
        current_time_crit_fail_dt = dt.fromisoformat(_keymap_get_current_timestamp_utc().replace('Z', '+00:00'))
        
        mada_seed_input.trace_metadata.L3_trace = L3Trace(
             version_L3_trace_schema="0.1.0", sop_name="lC.SOP.keymap_click",
             completion_timestamp_L3=current_time_crit_fail_dt, 
             epistemic_state_L3="LCL-Failure-Internal_L3",
             error_details=error_msg
        )
        mada_seed_input.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj = L3SurfaceKeymapObj(
            version="0.1.1", 
            lexical_affordances={}, syntactic_hints={}, pragmatic_affective_affordances={}, relational_linking_markers={}, L3_flags={}, # Required empty
            error_details=error_msg
        )
        return mada_seed_input

if __name__ == '__main__':
    # Need to import startle and frame_click to generate input for keymap_click
    from sop_l1_startle import startle_process
    from sop_l2_frame_click import frame_click_process

    print("--- Running sop_l3_keymap_click.py example ---")

    # 1. Create L1 MadaSeed
    example_input_event = {
        "reception_timestamp_utc_iso": "2023-10-29T08:00:00Z",
        "origin_hint": "Test_Keymap_Input",
        "data_components": [
            {"role_hint": "primary_text", "content_handle_placeholder": "This is an urgent test message for keymap.", "size_hint": 40, "type_hint": "text/plain"}
        ]
    }
    l1_seed = startle_process(example_input_event)

    # 2. Create L2 MadaSeed
    l2_seed = frame_click_process(l1_seed)
    print(f"\nL2 Epistemic State: {l2_seed.trace_metadata.L2_trace.epistemic_state_L2.name if l2_seed.trace_metadata.L2_trace.epistemic_state_L2 else 'N/A'}")
    if l2_seed.trace_metadata.L2_trace.epistemic_state_L2.name != "FRAMED":
         print("L2 processing did not result in FRAMED state, L3 test might not be meaningful.")
    
    # 3. Pass L2 MadaSeed to keymap_click_process
    print("\nCalling keymap_click_process with L2 MadaSeed...")
    l3_seed = keymap_click_process(l2_seed)

    # print("\nL3 MadaSeed (keymap_click_process output):")
    # print(l3_seed.json(indent=2, exclude_none=True))

    if l3_seed:
        print(f"\nL3 Surface Keymap Object Version: {l3_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj.version}")
        print(f"L3 Detected Language: {l3_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj.detected_languages}")
        print(f"L3 Keyword 'urgent' found: {'urgent' in [kw.term for kw in l3_seed.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj.lexical_affordances.keyword_mentions]}")
        
        print(f"\nL3 Trace Version: {l3_seed.trace_metadata.L3_trace.version_L3_trace_schema}")
        print(f"L3 Trace SOP Name: {l3_seed.trace_metadata.L3_trace.sop_name}")
        print(f"L3 Trace Epistemic State: {l3_seed.trace_metadata.L3_trace.epistemic_state_L3}")

    # Test with binary content hint from L1
    example_input_event_binary = {
        "reception_timestamp_utc_iso": "2023-10-29T08:05:00Z",
        "origin_hint": "Test_Keymap_Binary_Input",
        "data_components": [
            {"role_hint": "primary_binary_data", "content_handle_placeholder": "some_binary_data_ref", "size_hint": 500, "type_hint": "application/octet-stream"}
        ]
    }
    l1_seed_bin = startle_process(example_input_event_binary)
    l2_seed_bin = frame_click_process(l1_seed_bin)
    print("\nCalling keymap_click_process with L2 MadaSeed (Binary Hint)...")
    l3_seed_bin = keymap_click_process(l2_seed_bin)
    if l3_seed_bin:
        print(f"L3 Content Encoding (Binary): {l3_seed_bin.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj.content_encoding_status.name}")
        print(f"L3 Detected Languages (Binary): {l3_seed_bin.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj.detected_languages}")

    print("\n--- sop_l3_keymap_click.py example run complete ---")
