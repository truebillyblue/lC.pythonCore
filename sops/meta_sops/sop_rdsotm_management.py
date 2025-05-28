from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import uuid # For component IDs if not full CRUX UIDs yet

from lc_python_core.services.lc_mem_service import ( # Adjusted for potential deeper structure if meta_sops is a sub-package
    mock_lc_mem_core_ensure_uid,
    mock_lc_mem_core_create_object,
    mock_lc_mem_core_get_object,
    mock_lc_mem_core_update_object
)

# Mock logging functions
def log_internal_error(func_name: str, params: dict): print(f"ERROR:{func_name}:{params}")
def log_internal_info(func_name: str, params: dict): print(f"INFO:{func_name}:{params}")
def log_internal_warning(func_name: str, params: dict): print(f"WARNING:{func_name}:{params}")


RDSOTM_CYCLE_LINKAGE_TYPE = "RDSOTMCycleLinkage"
RDSOTM_COMPONENT_BASE_TYPE = "RDSOTMComponent" # Generic, specific type will be in rdsotm_component_type
TEXT_DOCUMENT_TYPE = "TextDocument" # For storing content

def _get_current_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def initiate_rdsotm_cycle(name: Optional[str] = "Default RDSOTM Cycle") -> Optional[str]:
    cycle_linkage_uid = mock_lc_mem_core_ensure_uid(
        RDSOTM_CYCLE_LINKAGE_TYPE, 
        context_description=name
    )
    if "ERROR" in cycle_linkage_uid:
        log_internal_error("initiate_rdsotm_cycle", {"message": f"Failed to ensure UID: {cycle_linkage_uid}"})
        return None

    current_time = _get_current_utc_iso()
    cycle_linkage_data = {
        "cycle_linkage_uid": cycle_linkage_uid,
        "cycle_linkage_version": "0.1.0",
        "cycle_name": name,
        "status": "Active",
        "created_at": current_time,
        "last_updated_at": current_time,
        "reality_input_refs": [], "doctrine_ref": None, "strategy_refs": [],
        "operations_refs": [], "tactics_refs": [], "mission_refs": [],
        "oia_cycle_refs": []
    }
    if mock_lc_mem_core_create_object(cycle_linkage_uid, cycle_linkage_data, {"object_type": RDSOTM_CYCLE_LINKAGE_TYPE, "name": name}):
        return cycle_linkage_uid
    else:
        log_internal_error("initiate_rdsotm_cycle", {"message": f"Failed to create RDSOTM cycle linkage object for UID: {cycle_linkage_uid}"})
        return None

def create_rdsotm_component(
    cycle_linkage_uid: str, 
    component_type: str, # e.g., "Doctrine", "Strategy"
    name: str, 
    description: str, 
    content_text: str, 
    related_component_uids: Optional[List[str]] = None,
    specific_fields: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    
    # 1. Store the content_text as a separate MADA object
    content_context_desc = f"Content for {component_type}: {name}"
    content_mada_uid = mock_lc_mem_core_ensure_uid(TEXT_DOCUMENT_TYPE, context_description=content_context_desc)
    if "ERROR" in content_mada_uid:
        log_internal_error("create_rdsotm_component", {"message": f"Failed to ensure UID for content: {content_mada_uid}"})
        return None
    
    content_payload = {"text_content": content_text, "original_component_name": name}
    if not mock_lc_mem_core_create_object(content_mada_uid, content_payload, {"object_type": TEXT_DOCUMENT_TYPE, "name": content_context_desc}):
        log_internal_error("create_rdsotm_component", {"message": f"Failed to create content MADA object for {name}"})
        return None

    # 2. Create the RDSOTM component object
    component_uid_desc = f"{component_type} component: {name}"
    component_uid = mock_lc_mem_core_ensure_uid(RDSOTM_COMPONENT_BASE_TYPE, context_description=component_uid_desc)
    if "ERROR" in component_uid:
        log_internal_error("create_rdsotm_component", {"message": f"Failed to ensure UID for component: {component_uid}"})
        # Ideally, should also handle cleanup of the content_mada_object if it was created
        return None

    current_time = _get_current_utc_iso()
    component_data = {
        "component_uid": component_uid,
        "component_version": "0.1.0",
        "rdsotm_component_type": component_type,
        "name": name,
        "description_summary": description,
        "content_mada_uid": content_mada_uid,
        "status": "Draft",
        "created_at": current_time,
        "last_updated_at": current_time,
        "linked_cycle_linkage_uids": [cycle_linkage_uid],
        "related_component_uids": related_component_uids or []
    }
    if specific_fields:
        component_data.update(specific_fields)

    if not mock_lc_mem_core_create_object(component_uid, component_data, {"object_type": RDSOTM_COMPONENT_BASE_TYPE, "rdsotm_type": component_type, "name": name}):
        log_internal_error("create_rdsotm_component", {"message": f"Failed to create RDSOTM component object for {name}"})
        # Ideally, cleanup content and component UID MADA objects
        return None

    # 3. Update the RDSOTMCycleLinkage object
    cycle_data = mock_lc_mem_core_get_object(cycle_linkage_uid)
    if not cycle_data:
        log_internal_error("create_rdsotm_component", {"message": f"Failed to retrieve cycle linkage {cycle_linkage_uid} to update."})
        # Component created, but linkage failed. Caller needs to be aware.
        return component_uid # Return component UID but signal error elsewhere or handle cleanup

    link_field_map = {
        "Doctrine": "doctrine_ref", # Note: schema has this as Optional[str], not List
        "Strategy": "strategy_refs", "Operations": "operations_refs",
        "Tactics": "tactics_refs", "Mission": "mission_refs",
        "RealityInput": "reality_input_refs"
    }
    
    link_field = link_field_map.get(component_type)
    if link_field:
        if isinstance(cycle_data.get(link_field), list):
            if component_uid not in cycle_data[link_field]:
                cycle_data[link_field].append(component_uid)
        elif link_field == "doctrine_ref": # Special handling for single doctrine_ref
             cycle_data[link_field] = component_uid
        else: # Field might not exist or is not a list and not doctrine_ref
             cycle_data[link_field] = [component_uid] if component_type != "Doctrine" else component_uid


        cycle_data["last_updated_at"] = current_time
        if not mock_lc_mem_core_update_object(cycle_linkage_uid, cycle_data):
            log_internal_error("create_rdsotm_component", {"message": f"Failed to update cycle linkage {cycle_linkage_uid} with new component."})
            # Component created, but linkage update failed.
    else:
        log_internal_warning("create_rdsotm_component", {"message": f"Unknown component type '{component_type}' for cycle linkage."})


    return component_uid

def get_rdsotm_component(component_uid: str, include_content: bool = False) -> Optional[Dict[str, Any]]:
    component_data = mock_lc_mem_core_get_object(component_uid)
    if not component_data:
        log_internal_info("get_rdsotm_component", {"message": f"Component {component_uid} not found."})
        return None
    
    if include_content and component_data.get("content_mada_uid"):
        content_payload = mock_lc_mem_core_get_object(component_data["content_mada_uid"])
        if content_payload:
            component_data["embedded_content"] = content_payload.get("text_content", "Content not in expected format or missing.")
        else:
            component_data["embedded_content"] = "Failed to retrieve content."
    return component_data

def update_rdsotm_component(component_uid: str, updates: Dict[str, Any], new_content_text: Optional[str] = None) -> bool:
    component_data = mock_lc_mem_core_get_object(component_uid)
    if not component_data:
        log_internal_error("update_rdsotm_component", {"message": f"Component {component_uid} not found for update."})
        return False

    has_updates = False
    for key, value in updates.items():
        if key not in ["component_uid", "created_at", "content_mada_uid", "rdsotm_component_type"]: # Protected fields
            if component_data.get(key) != value:
                component_data[key] = value
                has_updates = True
    
    if new_content_text is not None:
        content_mada_uid = component_data.get("content_mada_uid")
        if content_mada_uid:
            content_payload = {"text_content": new_content_text, "original_component_name": component_data.get("name")}
            if not mock_lc_mem_core_update_object(content_mada_uid, content_payload):
                log_internal_error("update_rdsotm_component", {"message": f"Failed to update content MADA object {content_mada_uid} for component {component_uid}."})
                # Continue to update component metadata even if content update fails, or decide to fail all
            else:
                has_updates = True # Content was updated
        else: # No existing content object, create one
            content_context_desc = f"Content for {component_data.get('rdsotm_component_type')}: {component_data.get('name')}"
            new_content_uid = mock_lc_mem_core_ensure_uid(TEXT_DOCUMENT_TYPE, context_description=content_context_desc)
            content_payload = {"text_content": new_content_text, "original_component_name": component_data.get("name")}
            if mock_lc_mem_core_create_object(new_content_uid, content_payload, {"object_type": TEXT_DOCUMENT_TYPE, "name": content_context_desc}):
                component_data["content_mada_uid"] = new_content_uid
                has_updates = True
            else:
                log_internal_error("update_rdsotm_component", {"message": f"Failed to create new content MADA object for component {component_uid}."})


    if has_updates:
        component_data["last_updated_at"] = _get_current_utc_iso()
        return mock_lc_mem_core_update_object(component_uid, component_data)
    
    log_internal_info("update_rdsotm_component", {"message": f"No effective updates for component {component_uid}."})
    return True # No changes, but operation is "successful" in that sense

def get_rdsotm_cycle_details(cycle_linkage_uid: str, resolve_component_summaries: bool = False) -> Optional[Dict[str, Any]]:
    cycle_data = mock_lc_mem_core_get_object(cycle_linkage_uid)
    if not cycle_data:
        log_internal_info("get_rdsotm_cycle_details", {"message": f"RDSOTM Cycle Linkage {cycle_linkage_uid} not found."})
        return None

    if resolve_component_summaries:
        for ref_type in ["reality_input_refs", "strategy_refs", "operations_refs", "tactics_refs", "mission_refs", "oia_cycle_refs"]:
            summary_key = f"{ref_type}_summaries"
            cycle_data[summary_key] = []
            for comp_uid in cycle_data.get(ref_type, []):
                comp = get_rdsotm_component(comp_uid) # Not including content here for summary
                if comp:
                    cycle_data[summary_key].append({"uid": comp_uid, "name": comp.get("name"), "type": comp.get("rdsotm_component_type"), "status": comp.get("status")})
        
        # Handle single doctrine_ref
        if cycle_data.get("doctrine_ref"):
            doc_uid = cycle_data["doctrine_ref"]
            doc_comp = get_rdsotm_component(doc_uid)
            if doc_comp:
                 cycle_data["doctrine_ref_summary"] = {"uid": doc_uid, "name": doc_comp.get("name"), "type": doc_comp.get("rdsotm_component_type"), "status": doc_comp.get("status")}

    return cycle_data

# Note: link_components_in_cycle is more complex as it involves graph-like relationships.
# For a file-based system, this might involve updating lists in multiple component files.
# A simpler version might just update the RDSOTMCycleLinkage object if the relationships are primarily hub-spoke from the cycle.
# For now, this function will be a placeholder.
def link_components_in_cycle(cycle_linkage_uid: str, source_comp_uid: str, target_comp_uid: str, link_type: str) -> bool:
    log_internal_warning("link_components_in_cycle", {"message": "Placeholder: Not fully implemented for file-based backend."})
    # Basic: update related_component_uids in source and target if they exist
    source_obj = get_rdsotm_component(source_comp_uid)
    target_obj = get_rdsotm_component(target_comp_uid)
    updated = False
    if source_obj:
        source_obj.setdefault("related_component_uids", []).append(target_comp_uid)
        if mock_lc_mem_core_update_object(source_comp_uid, source_obj): updated = True
    if target_obj:
        target_obj.setdefault("related_component_uids", []).append(source_comp_uid)
        if mock_lc_mem_core_update_object(target_comp_uid, target_obj): updated = True
    return updated
