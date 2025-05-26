from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import uuid # For generating observation_id etc. if not full CRUX UIDs yet for components

# Assuming lc_mem_service is now the primary way to interact with MADA (file-based)
from lc_python_core.services.lc_mem_service import (
    mock_lc_mem_core_ensure_uid,
    mock_lc_mem_core_create_object,
    mock_lc_mem_core_get_object,
    mock_lc_mem_core_update_object
)
# For Enums or Pydantic models if we define them for OIA components
# from ...schemas.oia_cycle_schema import OIACycleState, ObservationComponent, etc. 
# For now, we'll work with dicts based on the JSON schema proposed.

# Mock logging functions (can be replaced with a proper logger)
def log_internal_error(func_name: str, params: dict): print(f"ERROR:{func_name}:{params}")
def log_internal_info(func_name: str, params: dict): print(f"INFO:{func_name}:{params}")

OIA_CYCLE_OBJECT_TYPE = "OIACycleState"

def _get_current_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def _generate_component_id(prefix: str) -> str:
    # Generates a simple unique ID for components within an OIA cycle
    # For full CRUX compliance, these could also be full UIDs if components are separate MADA objects
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def initiate_oia_cycle(name: Optional[str] = None, initial_focus_prompt: Optional[str] = None, related_trace_id: Optional[str] = None) -> Optional[str]:
    oia_cycle_uid = mock_lc_mem_core_ensure_uid(OIA_CYCLE_OBJECT_TYPE, context_description=name or "New OIA Cycle")
    if "ERROR" in oia_cycle_uid: # Basic error check from ensure_uid mock
        log_internal_error("initiate_oia_cycle", {"message": f"Failed to ensure UID: {oia_cycle_uid}"})
        return None

    current_time = _get_current_utc_iso()
    oia_cycle_state = {
        "oia_cycle_uid": oia_cycle_uid,
        "oia_cycle_version": "0.1.0",
        "oia_cycle_name": name,
        "status": "Initiated",
        "created_at": current_time,
        "last_updated_at": current_time,
        "related_trace_ids": [related_trace_id] if related_trace_id else [],
        "observations": [],
        "interpretations": [],
        "applications": [],
        "current_focus_prompt": initial_focus_prompt,
        "log": [{"timestamp": current_time, "event_type": "CycleInitiated", "details": f"Cycle initiated with name: {name}"}]
    }

    if mock_lc_mem_core_create_object(oia_cycle_uid, oia_cycle_state, initial_metadata={"object_type": OIA_CYCLE_OBJECT_TYPE, "name": name}):
        return oia_cycle_uid
    else:
        log_internal_error("initiate_oia_cycle", {"message": f"Failed to create OIA cycle object for UID: {oia_cycle_uid}"})
        return None

def _add_oia_component(oia_cycle_uid: str, component_type: str, component_data: Dict[str, Any]) -> Optional[str]:
    oia_cycle_state_dict = mock_lc_mem_core_get_object(oia_cycle_uid)
    if not oia_cycle_state_dict:
        log_internal_error(f"_add_oia_component ({component_type})", {"message": f"OIA cycle {oia_cycle_uid} not found."})
        return None

    component_id = _generate_component_id(component_type.lower()[:3])
    component_data[f"{component_type.lower()}_id"] = component_id # e.g., observation_id
    component_data[f"{component_type.lower()}_at"] = _get_current_utc_iso() # e.g., observed_at

    oia_cycle_state_dict.setdefault(f"{component_type.lower()}s", []).append(component_data)
    
    # Update status based on component type
    if component_type == "Observation":
        oia_cycle_state_dict["status"] = "Observing"
    elif component_type == "Interpretation":
        oia_cycle_state_dict["status"] = "Interpreting"
    elif component_type == "Application":
        oia_cycle_state_dict["status"] = "Applying" # Or Completed_Applied if this is the final state for the action

    current_time = _get_current_utc_iso()
    oia_cycle_state_dict["last_updated_at"] = current_time
    oia_cycle_state_dict.setdefault("log", []).append({
        "timestamp": current_time,
        "event_type": f"{component_type}Added",
        "details": f"{component_type} {component_id} added."
    })

    if mock_lc_mem_core_update_object(oia_cycle_uid, oia_cycle_state_dict):
        return component_id
    else:
        log_internal_error(f"_add_oia_component ({component_type})", {"message": f"Failed to update OIA cycle {oia_cycle_uid}."})
        return None

def add_observation_to_cycle(oia_cycle_uid: str, summary: str, data_source_mada_uid: Optional[str] = None, raw_observation_ref: Optional[str] = None) -> Optional[str]:
    observation_data = {
        "summary": summary,
        "data_source_mada_uid": data_source_mada_uid,
        "raw_observation_ref": raw_observation_ref
    }
    return _add_oia_component(oia_cycle_uid, "Observation", observation_data)

def add_interpretation_to_cycle(oia_cycle_uid: str, summary: str, timeless_principles_extracted: Optional[List[str]] = None, incongruence_flags: Optional[List[str]] = None, references_observation_ids: Optional[List[str]] = None) -> Optional[str]:
    interpretation_data = {
        "summary": summary,
        "timeless_principles_extracted": timeless_principles_extracted or [],
        "incongruence_flags": incongruence_flags or [],
        "references_observation_ids": references_observation_ids or []
    }
    return _add_oia_component(oia_cycle_uid, "Interpretation", interpretation_data)

def add_application_to_cycle(oia_cycle_uid: str, summary_of_action_taken_or_planned: str, target_mada_uid: Optional[str] = None, outcome_mada_seed_trace_id: Optional[str] = None, references_interpretation_ids: Optional[List[str]] = None) -> Optional[str]:
    application_data = {
        "summary_of_action_taken_or_planned": summary_of_action_taken_or_planned,
        "target_mada_uid": target_mada_uid,
        "outcome_mada_seed_trace_id": outcome_mada_seed_trace_id,
        "references_interpretation_ids": references_interpretation_ids or []
    }
    # After adding an application, the cycle might be considered "Completed_Applied" or loop back to "Observing"
    # This logic can be refined in update_oia_cycle_status or here.
    # For now, _add_oia_component sets it to "Applying".
    return _add_oia_component(oia_cycle_uid, "Application", application_data)

def update_oia_cycle_status(oia_cycle_uid: str, new_status: str, log_message: str) -> bool:
    oia_cycle_state_dict = mock_lc_mem_core_get_object(oia_cycle_uid)
    if not oia_cycle_state_dict:
        log_internal_error("update_oia_cycle_status", {"message": f"OIA cycle {oia_cycle_uid} not found."})
        return False

    oia_cycle_state_dict["status"] = new_status
    current_time = _get_current_utc_iso()
    oia_cycle_state_dict["last_updated_at"] = current_time
    oia_cycle_state_dict.setdefault("log", []).append({
        "timestamp": current_time,
        "event_type": "StatusUpdate",
        "details": log_message
    })

    return mock_lc_mem_core_update_object(oia_cycle_uid, oia_cycle_state_dict)

def get_oia_cycle_state(oia_cycle_uid: str) -> Optional[Dict[str, Any]]:
    state = mock_lc_mem_core_get_object(oia_cycle_uid)
    if not state:
         log_internal_info("get_oia_cycle_state", {"message": f"OIA Cycle {oia_cycle_uid} not found."})
         return None
    return state
