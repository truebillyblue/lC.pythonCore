from datetime import datetime as dt, timezone
from typing import List, Dict, Tuple, Any, Optional, Union

from ..schemas.mada_schema import ( # Corrected path
    MadaSeed, L2FrameTypeObj, L3SurfaceKeymapObj, L3Trace,
    DetectedLanguage, ContentEncodingStatusL3Enum, ExplicitMetadata,
    LexicalAffordances, KeywordMention, EntityMentionRaw, NumericalQuantityMention, TemporalExpressionMention, QuantifierQualifierMention, NegationMarker,
    SyntacticHints, EmojiMention, # Ensure EmojiMention is in imports if used in SyntacticHints Pydantic model
    PragmaticAffectiveAffordances, FormalityHint, SentimentHint, PolitenessMarkers, UrgencyMarkers, PowerDynamicMarkers, InteractionPatternAffordance, ShallowGoalIntentAffordance, ActorRoleHint,
    RelationalLinkingMarkers, ExplicitRelationalPhrases, ExplicitReferenceMarkers, UrlMentions, PriorTraceReference,
    StatisticalProperties, StatisticalValue, StatisticalScore, # Ensure StatisticalScore is in imports
    L3Flags, L3FlagDetail, GriceanViolationHints, 
    EncodingStatusL1Enum
)
from pydantic import BaseModel, ValidationError # Added for helper
from typing import Type # Added for helper

import json
import asyncio

from ..services.adk_llm_service import AdkLlmService
from ..services.mock_lc_core_services import mock_lc_mem_core_get_object # Corrected path

# Basic logging function placeholder
# Initialize ADK LLM Service (module level)
try:
    llm_service = AdkLlmService()
except Exception as e:
    # If service initialization fails, log and set to None.
    # Dependent functions will need to handle this.
    print(f"CRITICAL: Failed to initialize AdkLlmService at module level: {e}")
    llm_service = None

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

# --- Generic LLM Interaction Helper ---
async def _call_llm_for_pydantic_model(
    prompt_text: str,
    target_model_type: Type[BaseModel], 
    default_empty_model: BaseModel,
    helper_name_for_logging: str,
    primary_content_str_for_logging: Optional[str] = None,
    l2_frame_type_str_for_logging: Optional[str] = None
) -> BaseModel:
    """
    Generic helper to call LLM, parse response, and validate against a Pydantic model.
    Returns the parsed model or the default_empty_model on any error.
    """
    if not llm_service:
        log_internal_error(helper_name_for_logging, {"error": "AdkLlmService is not available."})
        return default_empty_model

    try:
        # Shorten content string for logging if it's too long
        logged_content = primary_content_str_for_logging
        if logged_content and len(logged_content) > 100:
            logged_content = logged_content[:100] + "..."

        log_internal_info(helper_name_for_logging, {
            "info": f"Sending prompt to LLM for text: '{logged_content if logged_content else 'N/A'}' (Frame type: {l2_frame_type_str_for_logging})",
            # "prompt": prompt_text # Optionally log the full prompt for debugging, can be very verbose
        })
        llm_response_str = await llm_service.prompt_llm(prompt_text)

        if not llm_response_str:
            log_internal_warning(helper_name_for_logging, {"warning": "LLM returned empty response."})
            return default_empty_model
        
        llm_data = json.loads(llm_response_str)

        parsed_model = target_model_type.model_validate(llm_data)
        log_internal_info(helper_name_for_logging, {"info": f"Successfully parsed LLM response for {target_model_type.__name__}."})
        return parsed_model

    except json.JSONDecodeError as e:
        log_internal_warning(helper_name_for_logging, {"warning": f"Failed to parse LLM JSON response for {target_model_type.__name__}: {e}. Response: {llm_response_str}"})
        return default_empty_model
    except ValidationError as e: 
         log_internal_warning(helper_name_for_logging, {"warning": f"LLM response failed Pydantic validation for {target_model_type.__name__}: {e}. Response data was: {llm_response_str}"})
         return default_empty_model
    except RuntimeError as e: 
        log_internal_error(helper_name_for_logging, {"error": f"LLM call failed for {target_model_type.__name__}: {e}"})
        return default_empty_model
    except Exception as e:
        log_internal_error(helper_name_for_logging, {"error": f"Unexpected error in {helper_name_for_logging} for {target_model_type.__name__}: {e}"})
        return default_empty_model

# --- End Generic LLM Interaction Helper ---


async def _keymap_detect_language(primary_content_str: Optional[str], l2_frame_type_str: Optional[str]) -> List[DetectedLanguage]:
    """Detects language using LLM. Returns a list of DetectedLanguage objects."""
    if not primary_content_str or primary_content_str == "[[BINARY_CONTENT_PLACEHOLDER]]" or primary_content_str.strip() == "":
        log_internal_info("Helper:_keymap_detect_language", {"info": "Primary content is empty or placeholder, returning empty list."})
        return []

    # Define a simple Pydantic model for the expected JSON structure from LLM for this function
    # This class is defined locally as it's specific to this function's LLM call.
    class DetectedLanguagesResponse(BaseModel):
        detected_languages: List[DetectedLanguage] = []

    prompt = f"""Please analyze the following text and detect the primary language(s).
Return your response as a VALID JSON object with the following key:
"detected_languages": [{{"language_code": "en", "confidence": 0.9, "language_name": "English (optional)"}}, {{"language_code": "fr", "confidence": 0.7, "language_name": "French (optional)"}}]
If no specific language is confidently detected, return an empty list for "detected_languages".
Ensure confidence is a float between 0.0 and 1.0.

Text to analyze:
---
{primary_content_str}
---
"""
    default_response = DetectedLanguagesResponse(detected_languages=[])
    
    # Type casting here because _call_llm_for_pydantic_model returns BaseModel
    response_model = await _call_llm_for_pydantic_model(
        prompt_text=prompt,
        target_model_type=DetectedLanguagesResponse, # Pass the class itself
        default_empty_model=default_response,      # Pass an instance for default
        helper_name_for_logging="Helper:_keymap_detect_language",
        primary_content_str_for_logging=primary_content_str,
        l2_frame_type_str_for_logging=l2_frame_type_str
    )
    # Ensure response_model is of the expected type before accessing attributes
    if isinstance(response_model, DetectedLanguagesResponse):
        return response_model.detected_languages
    return [] # Fallback if type casting somehow fails or if default was returned and it's not this type.


def _keymap_check_encoding(primary_content_str: Optional[str]) -> ContentEncodingStatusL3Enum:
    if primary_content_str == "[[BINARY_CONTENT_PLACEHOLDER]]":
        return ContentEncodingStatusL3Enum.BINARYDETECTED
    return ContentEncodingStatusL3Enum.CONFIRMEDUTF8

async def _keymap_extract_explicit_meta(primary_content_str: Optional[str], l2_frame_type_str: Optional[str]) -> List[ExplicitMetadata]:
    """Extracts explicit metadata using LLM. Returns a list of ExplicitMetadata objects."""
    if not primary_content_str or primary_content_str == "[[BINARY_CONTENT_PLACEHOLDER]]" or primary_content_str.strip() == "":
        log_internal_info("Helper:_keymap_extract_explicit_meta", {"info": "Primary content is empty or placeholder, returning empty list."})
        return []

    # This Pydantic model is defined locally for the LLM response structure for this specific function.
    class ExplicitMetadataResponse(BaseModel):
        explicit_metadata: List[ExplicitMetadata] = []

    prompt = f"""Please analyze the following text and extract any explicit metadata mentioned.
Explicit metadata refers to data explicitly stated in the text, such as "Author: John Doe", "Date: 2023-01-01", "Source: Web", "Title: My Document".
It is NOT about inferring implicit metadata.
Return your response as a VALID JSON object with the following key:
"explicit_metadata": [{{"metadata_key": "Author", "metadata_value": "John Doe", "confidence": 0.X, "details": "optional context"}}, ...]
If no explicit metadata is found, return an empty list for "explicit_metadata".
Ensure confidence is a float between 0.0 and 1.0.

Consider the L2 frame type for context if provided: {l2_frame_type_str}
Text to analyze:
---
{primary_content_str}
---
"""
    default_response = ExplicitMetadataResponse(explicit_metadata=[])
    
    response_model = await _call_llm_for_pydantic_model(
        prompt_text=prompt,
        target_model_type=ExplicitMetadataResponse,
        default_empty_model=default_response,
        helper_name_for_logging="Helper:_keymap_extract_explicit_meta",
        primary_content_str_for_logging=primary_content_str,
        l2_frame_type_str_for_logging=l2_frame_type_str
    )
    if isinstance(response_model, ExplicitMetadataResponse):
        return response_model.explicit_metadata
    return []


async def _keymap_extract_structure_markers(primary_content_str: Optional[str], l2_frame_type_str: Optional[str]) -> List[str]:
    """Extracts content structure markers (e.g., headings, list indicators) using LLM. Returns a list of strings."""
    if not primary_content_str or primary_content_str == "[[BINARY_CONTENT_PLACEHOLDER]]" or primary_content_str.strip() == "":
        log_internal_info("Helper:_keymap_extract_structure_markers", {"info": "Primary content is empty or placeholder, returning empty list."})
        return []

    # This Pydantic model is defined locally for the LLM response structure.
    class StructureMarkersResponse(BaseModel):
        content_structure_markers: List[str] = []
        # Example: markers could be "Heading: Introduction", "List item: *", "Section break: ---"

    prompt = f"""Please analyze the following text and identify explicit content structure markers.
Structure markers include things like headings (e.g., "# Introduction", "## Section 2"), list item indicators (e.g., "* item", "- item", "1. item"),
paragraph breaks (if explicitly marked or inferable, e.g. "---"), or other textual cues that define the document structure.
Focus on markers explicitly present or strongly implied by formatting that can be represented as text.
Return your response as a VALID JSON object with the following key:
"content_structure_markers": ["marker1 text", "marker2 text", ...]
E.g., ["Heading: Introduction", "List item: * Point A", "Separator: ---"]
If no structure markers are found, return an empty list.

Consider the L2 frame type for context if provided: {l2_frame_type_str}
Text to analyze:
---
{primary_content_str}
---
"""
    default_response = StructureMarkersResponse(content_structure_markers=[])
    
    response_model = await _call_llm_for_pydantic_model(
        prompt_text=prompt,
        target_model_type=StructureMarkersResponse,
        default_empty_model=default_response,
        helper_name_for_logging="Helper:_keymap_extract_structure_markers",
        primary_content_str_for_logging=primary_content_str,
        l2_frame_type_str_for_logging=l2_frame_type_str
    )
    if isinstance(response_model, StructureMarkersResponse):
        return response_model.content_structure_markers
    return []


async def _keymap_extract_lexical(primary_content_str: Optional[str], l2_frame_type_str: Optional[str]) -> LexicalAffordances: # Made async
    """
    Extracts lexical affordances from primary content using ADK LLM Service.
    Refactored to use _call_llm_for_pydantic_model.
    """
    default_empty_lex_affordances = LexicalAffordances(
        keyword_mentions=[], entity_mentions_raw=[], numerical_quantity_mentions=[],
        temporal_expression_mentions=[], quantifier_qualifier_mentions=[], negation_markers=[]
    )

    if not primary_content_str or primary_content_str == "[[BINARY_CONTENT_PLACEHOLDER]]" or primary_content_str.strip() == "":
        log_internal_info("Helper:_keymap_extract_lexical", {"info": "Primary content is empty or placeholder, returning empty lexical affordances."})
        return default_empty_lex_affordances

    prompt = f"""Please analyze the following text and extract lexical affordances.
Return your response as a VALID JSON object with the following keys. Do NOT include comments or trailing commas in the JSON:
"keyword_mentions": [{{"term": "example_term", "confidence": 0.X, "details": "optional context"}}, ...],
"entity_mentions_raw": [{{"mention": "Example Mention", "confidence": 0.X, "possible_types": ["type1", "type2"], "details": "optional context"}}, ...],
"numerical_quantity_mentions": [{{"value_string": "123", "value_numeric": 123 (optional), "unit_mention": "kg" (optional), "confidence": 0.X, "details": "optional context"}}, ...],
"temporal_expression_mentions": [{{"expression": "next week", "confidence": 0.X, "possible_interpretations": ["YYYY-MM-DDTHH:MM:SSZ"] (optional), "details": "optional context"}}, ...],
"quantifier_qualifier_mentions": [{{"term": "many", "type": "quantifier/qualifier", "confidence": 0.X, "details": "optional context"}}, ...],
"negation_markers": [{{"term": "not", "scope": "following phrase" (optional), "confidence": 0.X, "details": "optional context"}}, ...]

If a category has no items, return an empty list for that key. Ensure all confidence scores are floats between 0.0 and 1.0.

Text to analyze:
---
{primary_content_str}
---
"""
    # Type casting here because _call_llm_for_pydantic_model returns BaseModel
    # This is safe because if the call fails, it returns default_empty_lex_affordances, which is of the correct type.
    # If it succeeds, it returns an instance of LexicalAffordances.
    result = await _call_llm_for_pydantic_model(
        prompt_text=prompt,
        target_model_type=LexicalAffordances,
        default_empty_model=default_empty_lex_affordances,
        helper_name_for_logging="Helper:_keymap_extract_lexical",
        primary_content_str_for_logging=primary_content_str,
        l2_frame_type_str_for_logging=l2_frame_type_str
    )
    return result # type: ignore


async def _keymap_derive_syntactic(primary_content_str: Optional[str], l2_frame_type_str: Optional[str]) -> SyntacticHints:
    """Derives syntactic hints using LLM."""
    default_empty_hints = SyntacticHints(
        sentence_type_distribution={}, # Default to empty dict
        pos_tagging_candidate_flag=False, # Default to False
        punctuation_analysis={}, # Default to empty dict
        capitalization_analysis={}, # Default to empty dict
        emoji_mentions=[] # Default to empty list
    )
    if not primary_content_str or primary_content_str == "[[BINARY_CONTENT_PLACEHOLDER]]" or primary_content_str.strip() == "":
        log_internal_info("Helper:_keymap_derive_syntactic", {"info": "Primary content is empty or placeholder, returning empty syntactic hints."})
        return default_empty_hints

    prompt = f"""Analyze the text for syntactic hints.
Return your response as a VALID JSON object with the following structure. Do NOT include comments or trailing commas.
Provide counts for distributions and analyses. Set pos_tagging_candidate_flag based on suitability of text for POS tagging.
{{
  "sentence_type_distribution": {{
    "declarative": 0, 
    "interrogative": 0, 
    "exclamatory": 0, 
    "imperative": 0, 
    "other": 0 
  }},
  "pos_tagging_candidate_flag": true,
  "punctuation_analysis": {{ 
    "period_count": 0, 
    "question_mark_count": 0, 
    "exclamation_mark_count": 0, 
    "comma_count": 0, 
    "quote_count": 0,
    "other_punctuation_count": 0
  }},
  "capitalization_analysis": {{ 
    "all_caps_word_count": 0, 
    "sentence_initial_caps_count": 0, 
    "proper_noun_candidate_caps_count": 0 
  }},
  "emoji_mentions": [
    {{"emoji_char": "😊", "count": 1, "description": "smiling face with smiling eyes", "sentiment_hint": "positive", "confidence": 0.8, "details": "optional details"}}
  ]
}}
If a specific hint cannot be determined, use a default value (e.g., 0 for counts, false for flags, empty list/dict as per schema).
Ensure all confidence scores are floats between 0.0 and 1.0.

Text to analyze:
---
{primary_content_str}
---
"""
    # Type casting here for the same reasons as in _keymap_extract_lexical
    result = await _call_llm_for_pydantic_model(
        prompt_text=prompt,
        target_model_type=SyntacticHints,
        default_empty_model=default_empty_hints,
        helper_name_for_logging="Helper:_keymap_derive_syntactic",
        primary_content_str_for_logging=primary_content_str,
        l2_frame_type_str_for_logging=l2_frame_type_str
    )
    return result # type: ignore

async def _keymap_derive_pragmatic_affective(primary_content_str: Optional[str], l2_frame_type_str: Optional[str]) -> PragmaticAffectiveAffordances: # Signature changed
    """Derives pragmatic and affective affordances using LLM."""
    default_empty_affordances = PragmaticAffectiveAffordances(
        formality_hint=FormalityHint(), sentiment_hint=SentimentHint(), politeness_markers=PolitenessMarkers(),
        urgency_markers=UrgencyMarkers(), power_dynamic_markers=PowerDynamicMarkers(),
        interaction_pattern_affordance=InteractionPatternAffordance(),
        shallow_goal_intent_affordance=ShallowGoalIntentAffordance(), actor_role_hint=ActorRoleHint()
    )

    if not primary_content_str or primary_content_str == "[[BINARY_CONTENT_PLACEHOLDER]]" or primary_content_str.strip() == "":
        log_internal_info("Helper:_keymap_derive_pragmatic_affective", {"info": "Primary content is empty or placeholder, returning empty pragmatic/affective affordances."})
        return default_empty_affordances

    prompt = f"""Analyze the text for pragmatic and affective affordances.
Return your response as a VALID JSON object matching the structure of PragmaticAffectiveAffordances. Do NOT include comments or trailing commas.
Example sub-structures (fill all applicable fields based on the text):
{{
  "formality_hint": {{"level": "neutral", "confidence": 0.X, "markers": ["marker1"]}},
  "sentiment_hint": {{"polarity": "positive", "confidence": 0.X, "markers": ["marker1"], "magnitude": 0.X, "scope": "sentence/document"}},
  "politeness_markers": {{"level": "polite", "confidence": 0.X, "markers": ["please", "thank you"]}},
  "urgency_markers": {{"is_urgent": true, "confidence": 0.X, "markers": ["urgent", "asap"], "level": "high"}},
  "power_dynamic_markers": {{"direction": "equal/dominant/submissive", "confidence": 0.X, "markers": ["sir", "I demand"]}},
  "interaction_pattern_affordance": {{"pattern_type": "question-answer/request-acknowledge/statement-elaboration", "confidence": 0.X, "details": "..."}},
  "shallow_goal_intent_affordance": {{"goal_type": "inform/request_action/clarify/social_connect", "confidence": 0.X, "details": "User wants to know X"}},
  "actor_role_hint": {{"roles_identified": ["customer", "support_agent"], "confidence": 0.X, "details": "Customer is asking for help."}}
}}
If a specific affordance is not detected or not applicable, use its default/empty representation (e.g., null for objects, empty list for lists, default values for primitives like false for booleans or 0 for numbers if appropriate for the schema).
Ensure all confidence scores are floats between 0.0 and 1.0.

Text to analyze (consider also frame type: {l2_frame_type_str}):
---
{primary_content_str}
---
"""
    result = await _call_llm_for_pydantic_model(
        prompt_text=prompt,
        target_model_type=PragmaticAffectiveAffordances,
        default_empty_model=default_empty_affordances,
        helper_name_for_logging="Helper:_keymap_derive_pragmatic_affective",
        primary_content_str_for_logging=primary_content_str,
        l2_frame_type_str_for_logging=l2_frame_type_str
    )
    return result # type: ignore

async def _keymap_extract_relational_linking(primary_content_str: Optional[str], l2_frame_type_str: Optional[str]) -> RelationalLinkingMarkers: # Made async, added l2_frame_type_str
    """Extracts relational linking markers using LLM."""
    default_empty_markers = RelationalLinkingMarkers(
        explicit_relational_phrases=ExplicitRelationalPhrases(detected=[]),
        explicit_reference_markers=ExplicitReferenceMarkers(detected=[]),
        url_mentions=UrlMentions(detected_urls=[]),
        prior_trace_references=[]
    )
    if not primary_content_str or primary_content_str == "[[BINARY_CONTENT_PLACEHOLDER]]" or primary_content_str.strip() == "":
        log_internal_info("Helper:_keymap_extract_relational_linking", {"info": "Primary content is empty or placeholder, returning empty relational markers."})
        return default_empty_markers

    prompt = f"""Analyze the text for relational linking markers.
Return your response as a VALID JSON object matching the RelationalLinkingMarkers structure. Do NOT include comments or trailing commas.
Example structure:
{{
  "explicit_relational_phrases": {{ "detected": [{{"phrase": "because of that", "confidence": 0.X, "type": "causal"}}] }},
  "explicit_reference_markers": {{ "detected": [{{"marker": "the aforementioned", "confidence": 0.X, "refers_to_hint": "previous topic"}}] }},
  "url_mentions": {{ "detected_urls": [{{"url": "http://example.com", "confidence": 0.X, "url_type_hint": "external_link", "link_text_anchor": "optional anchor text"}}] }},
  "prior_trace_references": [{{"reference_text": "as mentioned before", "confidence": 0.X, "referred_trace_id_hint": "previous_turn_id_or_topic", "details": "optional details"}}]
}}
If a category has no items, return an empty list or object as appropriate for the schema.
Ensure all confidence scores are floats between 0.0 and 1.0.

Text to analyze (consider also frame type: {l2_frame_type_str}):
---
{primary_content_str}
---
"""
    result = await _call_llm_for_pydantic_model(
        prompt_text=prompt,
        target_model_type=RelationalLinkingMarkers,
        default_empty_model=default_empty_markers,
        helper_name_for_logging="Helper:_keymap_extract_relational_linking",
        primary_content_str_for_logging=primary_content_str,
        l2_frame_type_str_for_logging=l2_frame_type_str
    )
    return result # type: ignore

async def _keymap_calculate_stats(primary_content_str: Optional[str], l2_frame_type_str: Optional[str]) -> Optional[StatisticalProperties]:
    """Calculates statistical properties using LLM, with a fallback for token count."""
    
    # Basic fallback: calculate token count if content exists
    basic_fallback_stats = StatisticalProperties()
    if primary_content_str and primary_content_str != "[[BINARY_CONTENT_PLACEHOLDER]]" and primary_content_str.strip() != "":
        basic_fallback_stats.token_count = StatisticalValue(value=len(primary_content_str.split()), calculation_method="simple_whitespace_split_python")
    else: # No content, no stats
        log_internal_info("Helper:_keymap_calculate_stats", {"info": "Primary content is empty or placeholder, returning None for stats."})
        return None # Return None if no content

    prompt = f"""Analyze the following text and provide statistical properties.
Return your response as a VALID JSON object matching the StatisticalProperties structure. Do NOT include comments or trailing commas.
Example structure:
{{
  "token_count": {{"value": 150, "confidence": 0.9, "calculation_method": "LLM_estimate_whitespace_split_like"}},
  "sentence_count": {{"value": 5, "confidence": 0.8, "calculation_method": "LLM_estimate"}},
  "word_frequency": [{{"word": "example", "count": 3, "details": "appears frequently"}}],
  "lexical_density_score": {{"score_value": 0.45, "confidence": 0.7, "scale_description": "0_to_1_less_to_more_dense"}},
  "readability_scores": [
    {{"score_name": "Flesch_Kincaid_Grade_Level", "score_value": 8.5, "confidence": 0.7}},
    {{"score_name": "Gunning_Fog_Index", "score_value": 10.2, "confidence": 0.6}}
  ],
  "sentiment_distribution_overall": {{ "positive_score": 0.6, "negative_score": 0.1, "neutral_score": 0.3, "confidence": 0.8 }}
}}
If a specific statistic cannot be reliably calculated, omit its key or use a null/default value as appropriate for the schema.
Ensure confidence scores are floats between 0.0 and 1.0.

Text to analyze (consider also frame type: {l2_frame_type_str}):
---
{primary_content_str}
---
"""
    # The _call_llm_for_pydantic_model will return 'basic_fallback_stats' if the LLM call or parsing fails.
    llm_derived_stats_model = await _call_llm_for_pydantic_model(
        prompt_text=prompt,
        target_model_type=StatisticalProperties,
        default_empty_model=basic_fallback_stats, # Fallback on LLM error
        helper_name_for_logging="Helper:_keymap_calculate_stats",
        primary_content_str_for_logging=primary_content_str,
        l2_frame_type_str_for_logging=l2_frame_type_str
    )

    # Ensure it's the correct type, although our helper should guarantee it or the default.
    if not isinstance(llm_derived_stats_model, StatisticalProperties):
         # This case should ideally not be reached if _call_llm_for_pydantic_model works as expected
        log_internal_warning("Helper:_keymap_calculate_stats", {"warning": "LLM call returned unexpected model type, returning basic_fallback_stats."})
        return basic_fallback_stats if basic_fallback_stats.token_count else None


    # If LLM returns a valid StatisticalProperties model, but it's essentially empty (e.g. just default values from Pydantic)
    # or if it specifically missed token_count, ensure our Python-calculated token_count is present.
    if not llm_derived_stats_model.token_count and basic_fallback_stats.token_count:
        llm_derived_stats_model.token_count = basic_fallback_stats.token_count
        log_internal_info("Helper:_keymap_calculate_stats", {"info": "LLM-derived stats did not include token_count, Python-calculated token_count was used/added."})
    
    # If the resulting model is empty (no token_count even after fallback logic), return None
    if not llm_derived_stats_model.token_count and not llm_derived_stats_model.sentence_count and not llm_derived_stats_model.word_frequency: # etc. for other fields
         log_internal_info("Helper:_keymap_calculate_stats", {"info": "LLM-derived stats and fallback are empty, returning None."})
         return None
         
    return llm_derived_stats_model


async def _keymap_identify_anomalies(primary_content_str: Optional[str], l2_frame_type_str: Optional[str], working_l3_surface_keymap_obj: L3SurfaceKeymapObj) -> L3Flags: # Made async, added context params
    """Identifies anomalies using LLM, with context from prior analysis."""
    default_empty_flags = L3Flags(
        internal_contradiction_hint=L3FlagDetail(detected=False),
        mixed_affect_signal=L3FlagDetail(detected=False),
        multivalent_cue_detected=L3FlagDetail(detected=False),
        low_confidence_overall_flag=L3FlagDetail(detected=False),
        gricean_violation_hints=GriceanViolationHints(detected=[])
    )
    if not primary_content_str or primary_content_str == "[[BINARY_CONTENT_PLACEHOLDER]]" or primary_content_str.strip() == "":
        log_internal_info("Helper:_keymap_identify_anomalies", {"info": "Primary content is empty or placeholder, returning default flags."})
        # Potentially analyze working_l3_surface_keymap_obj for anomalies even without primary_content, but for now, require content.
        return default_empty_flags

    context_summary = "No additional L3 context provided."
    if working_l3_surface_keymap_obj:
        try:
            # Safely access attributes, providing defaults if parts of the structure are missing
            lex_affordances = working_l3_surface_keymap_obj.lexical_affordances
            kw_summary = ""
            if lex_affordances and lex_affordances.keyword_mentions:
                kw_summary = "Keywords: " + ", ".join([kw.term for kw in lex_affordances.keyword_mentions[:3]])

            prag_affordances = working_l3_surface_keymap_obj.pragmatic_affective_affordances
            sentiment_polarity = "N/A"
            sentiment_confidence = "N/A"
            if prag_affordances and prag_affordances.sentiment_hint:
                sentiment_polarity = prag_affordances.sentiment_hint.polarity or "N/A" # Handle None polarity
                sentiment_confidence = prag_affordances.sentiment_hint.confidence if prag_affordances.sentiment_hint.confidence is not None else "N/A"
            
            prag_summary = f"Sentiment: {sentiment_polarity} (Conf: {sentiment_confidence})"
            context_summary = f"Prior L3 Analysis Context: {kw_summary}. {prag_summary}."
            if not kw_summary and prag_summary == "Sentiment: N/A (Conf: N/A)": # If both are empty/default
                 context_summary = "No specific lexical or sentiment context from L3 so far."

        except AttributeError as ae: # Catch specific attribute errors if structures are unexpectedly missing
            log_internal_warning("Helper:_keymap_identify_anomalies", {"warning": f"AttributeError generating context summary: {ae}"})
        except Exception as e: # Catch any other error during summary generation
            log_internal_warning("Helper:_keymap_identify_anomalies", {"warning": f"Error generating context summary: {e}"})


    prompt = f"""Analyze the following text for potential anomalies, considering the provided L3 context summary.
Return your response as a VALID JSON object matching the L3Flags structure. Do NOT include comments or trailing commas.
Example structure:
{{
  "internal_contradiction_hint": {{"detected": true, "confidence": 0.X, "explanation": "States X then states Not X", "details": "optional details"}},
  "mixed_affect_signal": {{"detected": false, "confidence": 0.X, "explanation": "Positive words with negative tone", "details": "optional details"}},
  "multivalent_cue_detected": {{"detected": true, "confidence": 0.X, "explanation": "Word 'fine' could mean good or bad", "details": "optional details"}},
  "low_confidence_overall_flag": {{"detected": false, "confidence": 0.X, "explanation": "Set this to true if multiple other anomalies are detected or overall confidence in interpretation is low"}},
  "gricean_violation_hints": {{ 
    "detected": [
        {{"violation_type": "maxim_of_quality", "confidence": 0.X, "explanation": "Seems unsure or speculative", "details": "optional details"}},
        {{"violation_type": "maxim_of_quantity", "confidence": 0.X, "explanation": "Too much or too little information", "details": "optional details"}}
    ],
    "summary_explanation": "optional overall summary of gricean violations"
  }}
}}
If a specific anomaly is not detected, set "detected" to false.
Ensure all confidence scores are floats between 0.0 and 1.0.

L3 Context Summary: {context_summary}
Text to analyze (consider also frame type: {l2_frame_type_str}):
---
{primary_content_str}
---
"""
    flags_model = await _call_llm_for_pydantic_model(
        prompt_text=prompt,
        target_model_type=L3Flags,
        default_empty_model=default_empty_flags,
        helper_name_for_logging="Helper:_keymap_identify_anomalies",
        primary_content_str_for_logging=primary_content_str,
        l2_frame_type_str_for_logging=l2_frame_type_str
    )
    
    # Ensure correct type for static analysis, though helper should guarantee it or default.
    if not isinstance(flags_model, L3Flags):
        return default_empty_flags # Should not happen if helper works

    # Post-processing: if multiple anomalies are detected with high confidence, set low_confidence_overall_flag
    num_detected_anomalies = 0
    # Check main flags
    if flags_model.internal_contradiction_hint and flags_model.internal_contradiction_hint.detected: num_detected_anomalies +=1
    if flags_model.mixed_affect_signal and flags_model.mixed_affect_signal.detected: num_detected_anomalies +=1
    if flags_model.multivalent_cue_detected and flags_model.multivalent_cue_detected.detected: num_detected_anomalies +=1
    # Check Gricean violations
    if flags_model.gricean_violation_hints and flags_model.gricean_violation_hints.detected:
        num_detected_anomalies += len(flags_model.gricean_violation_hints.detected)

    if num_detected_anomalies >= 2: # Arbitrary threshold
        if not flags_model.low_confidence_overall_flag: # Ensure it exists
            flags_model.low_confidence_overall_flag = L3FlagDetail(detected=False) # Initialize if somehow missing
        if not flags_model.low_confidence_overall_flag.detected: # Only update if not already detected by LLM
            flags_model.low_confidence_overall_flag.detected = True
            current_explanation = flags_model.low_confidence_overall_flag.explanation if flags_model.low_confidence_overall_flag.explanation else ""
            flags_model.low_confidence_overall_flag.explanation = (current_explanation + " (Auto-set by L3 SOP due to multiple anomalies detected)").strip()
            flags_model.low_confidence_overall_flag.confidence = flags_model.low_confidence_overall_flag.confidence or 0.75 # Set confidence if not already set
            log_internal_info("Helper:_keymap_identify_anomalies", {"info": "Auto-set low_confidence_overall_flag due to multiple detected anomalies."})
        
    return flags_model

def _keymap_validate_and_determine_outcome(working_l3_surface_keymap_obj: L3SurfaceKeymapObj) -> str: # Returns epistemic state string
    # Baseline: return "Keymapped_Successfully".
    # Future HR: Implement logic based on L3 policies and content of working_l3_surface_keymap_obj
    # For example, if working_l3_surface_keymap_obj.L3_flags.low_confidence_overall_flag.detected:
    #     return "LCL-Clarify-Semantics_L3" 
    return "Keymapped_Successfully"


# --- Main keymap_click Process Function ---

async def keymap_click_process(mada_seed_input: MadaSeed) -> MadaSeed: # Made async
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
        # All helper calls below need to be awaited if they are async.
        
        # _keymap_detect_language is now async
        working_l3_surface_keymap_obj.detected_languages = await _keymap_detect_language(primary_content_for_l3, input_frame_type_from_l2)
        
        working_l3_surface_keymap_obj.content_encoding_status = _keymap_check_encoding(primary_content_for_l3) # Stays sync
        
        # _keymap_extract_explicit_meta will be async (in a later patch)
        working_l3_surface_keymap_obj.explicit_metadata = _keymap_extract_explicit_meta(primary_content_for_l3, input_frame_type_from_l2) # Stays sync for now
        
        # _keymap_extract_structure_markers will be async (in a later patch)
        working_l3_surface_keymap_obj.content_structure_markers = _keymap_extract_structure_markers(primary_content_for_l3, input_frame_type_from_l2) # Stays sync for now
        
        lexical_data = await _keymap_extract_lexical(primary_content_for_l3, input_frame_type_from_l2) # Already async, refactored to helper
        working_l3_surface_keymap_obj.lexical_affordances = lexical_data
        
        syntactic_data = await _keymap_derive_syntactic(primary_content_for_l3, input_frame_type_from_l2) # Now async, uses LLM & helper
        working_l3_surface_keymap_obj.syntactic_hints = syntactic_data
        
        # _keymap_derive_pragmatic_affective will be async and use primary_content_for_l3 (in a later patch)
        # For now, its signature and call site remain unchanged.
        working_l3_surface_keymap_obj.pragmatic_affective_affordances = _keymap_derive_pragmatic_affective(lexical_data, syntactic_data) # Stays sync for now
        
        # _keymap_extract_relational_linking will be async (in a later patch)
        working_l3_surface_keymap_obj.relational_linking_markers = _keymap_extract_relational_linking(primary_content_for_l3) # Stays sync for now
        
        # _keymap_calculate_stats will be async (in a later patch)
        working_l3_surface_keymap_obj.statistical_properties = _keymap_calculate_stats(primary_content_for_l3, input_frame_type_from_l2) # Stays sync for now
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
    # frame_click_process is synchronous
    l2_seed = frame_click_process(l1_seed) 
    print(f"\nL2 Epistemic State: {l2_seed.trace_metadata.L2_trace.epistemic_state_L2.name if l2_seed.trace_metadata.L2_trace.epistemic_state_L2 else 'N/A'}")
    if l2_seed.trace_metadata.L2_trace.epistemic_state_L2.name != "FRAMED": # FRAMED
         print("L2 processing did not result in FRAMED state, L3 test might not be meaningful.")
    
    # 3. Pass L2 MadaSeed to keymap_click_process (now async)
    print("\nCalling keymap_click_process with L2 MadaSeed...")
    # Use asyncio.run() to execute the async keymap_click_process
    if llm_service: # Only run if service initialized
        l3_seed = asyncio.run(keymap_click_process(l2_seed))
    else:
        print("Skipping keymap_click_process run because AdkLlmService failed to initialize.")
        l3_seed = l2_seed # Or some other appropriate fallback MadaSeed

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
    l2_seed_bin = frame_click_process(l1_seed_bin) # sync
    print("\nCalling keymap_click_process with L2 MadaSeed (Binary Hint)...")
    if llm_service: # Only run if service initialized
        l3_seed_bin = asyncio.run(keymap_click_process(l2_seed_bin)) # async
    else:
        print("Skipping keymap_click_process run (binary) because AdkLlmService failed to initialize.")
        l3_seed_bin = l2_seed_bin # Or some other appropriate fallback MadaSeed
        
    if l3_seed_bin and l3_seed_bin.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj: # Check if L3_surface_keymap_obj exists
        print(f"L3 Content Encoding (Binary): {l3_seed_bin.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj.content_encoding_status.name}")
        print(f"L3 Detected Languages (Binary): {l3_seed_bin.seed_content.L1_startle_reflex.L2_frame_type.L3_surface_keymap.L3_surface_keymap_obj.detected_languages}")

    print("\n--- sop_l3_keymap_click.py example run complete ---")
