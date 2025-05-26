import json
import uuid
import os
import shutil # For rmtree
from pathlib import Path
from typing import Optional, Dict, Any, Union, List # Added List for query results
from datetime import datetime, timezone

# Define a base path for the local MADA vault.
# Using lab/.data/ as suggested by user feedback for persistent local data.
# Ensure this path is resolved correctly relative to where the script might be run from,
# or use an absolute path if necessary for consistency.
# For now, let's assume it's relative to the 'lab' directory.
# If 'lab' is the root of the repo, then Path(__file__).resolve().parents[2] / '.data' / 'mada_vault'
# Assuming this service file is in lab/frontends/lc_python_core/services/
MADA_VAULT_DIR = Path(__file__).resolve().parents[3] / '.data' / 'mada_vault'
MADA_VAULT_DIR.mkdir(parents=True, exist_ok=True)

PBI_OBJECT_TYPE = "ProductBacklogItem"
PBI_VAULT_DIR = MADA_VAULT_DIR / "pbis"
PBI_VAULT_DIR.mkdir(parents=True, exist_ok=True)

AGENT_PROFILE_OBJECT_TYPE = "AgentProfile"
AGENT_PROFILE_VAULT_DIR = MADA_VAULT_DIR / "agent_profiles"
AGENT_PROFILE_VAULT_DIR.mkdir(parents=True, exist_ok=True)


# Mock logging functions (can be replaced with a proper logger)
def log_internal_error(func_name: str, params: dict): print(f"ERROR:{func_name}:{params}")
def log_internal_info(func_name: str, params: dict): print(f"INFO:{func_name}:{params}")
# Added missing log_internal_warning, assuming it's needed or was intended
def log_internal_warning(func_name: str, params: dict): print(f"WARNING:{func_name}:{params}")


def mock_lc_mem_core_ensure_uid(object_type: str, context_description: Optional[str] = None, existing_uid_candidate: Optional[str] = None) -> str:
    # Basic CRUX UID structure: urn:crux:uid::[UUIDv4 hex]
    # The original mock didn't include object_type or context in the UID itself, kept it simple.
    if existing_uid_candidate:
        # Basic validation (presence and URN prefix)
        if existing_uid_candidate.startswith("urn:crux:uid::") and len(existing_uid_candidate) > 15:
            log_internal_info("mock_lc_mem_core_ensure_uid", {"message": f"Validated existing UID: {existing_uid_candidate}"})
            return existing_uid_candidate
        else:
            log_internal_error("mock_lc_mem_core_ensure_uid", {"message": f"Invalid existing_uid_candidate format: {existing_uid_candidate}. Generating new."})
    
    new_uuid = uuid.uuid4().hex
    new_uid = f"urn:crux:uid::{new_uuid}"
    log_internal_info("mock_lc_mem_core_ensure_uid", {"message": f"Generated new UID: {new_uid} for object_type: {object_type}"})
    return new_uid

def mock_lc_mem_core_create_object(object_uid: str, object_payload: Dict[str, Any], initial_metadata: Optional[Dict[str, Any]] = None, requesting_persona_context: Optional[Dict[str, Any]] = None) -> bool:
    if not object_uid.startswith("urn:crux:uid::"):
        log_internal_error("mock_lc_mem_core_create_object", {"message": f"Invalid CRUX UID format for create: {object_uid}"})
        return False
    
    # Instead of object_path and metadata_path directly under MADA_VAULT_DIR,
    # create a directory for each UID to store its object and metadata.
    uid_specific_dir_name = object_uid.split('::')[-1]
    uid_specific_dir = MADA_VAULT_DIR / uid_specific_dir_name
    
    try:
        uid_specific_dir.mkdir(parents=True, exist_ok=True)
        
        object_file_path = uid_specific_dir / "object_payload.json"
        metadata_file_path = uid_specific_dir / "metadata.json"

        with open(object_file_path, 'w') as f:
            json.dump(object_payload, f, indent=2)
        
        meta_to_store = initial_metadata if initial_metadata else {}
        meta_to_store['crux_uid'] = object_uid
        meta_to_store['object_type'] = object_payload.get("type", "Unknown") # Example: try to get type from payload
        meta_to_store['created_at'] = datetime.now(timezone.utc).isoformat() # Use timezone.utc
        meta_to_store['version'] = meta_to_store.get('version', "0.1.0") # Default version

        with open(metadata_file_path, 'w') as f:
            json.dump(meta_to_store, f, indent=2)
        
        log_internal_info("mock_lc_mem_core_create_object", {"message": f"Object {object_uid} created successfully at {object_file_path}"})
        return True
    except IOError as e:
        log_internal_error("mock_lc_mem_core_create_object", {"message": f"IOError creating object {object_uid}: {e}"})
        return False
    except Exception as e:
        log_internal_error("mock_lc_mem_core_create_object", {"message": f"Unexpected error creating object {object_uid}: {e}"})
        return False

def mock_lc_mem_core_get_object(object_uid: str, version_hint: Optional[str] = None, requesting_persona_context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    if not object_uid.startswith("urn:crux:uid::"):
        log_internal_error("mock_lc_mem_core_get_object", {"message": f"Invalid CRUX UID format for get: {object_uid}"})
        return None
    
    uid_specific_dir = MADA_VAULT_DIR / object_uid.split('::')[-1]
    object_file_path = uid_specific_dir / "object_payload.json"
    # metadata_file_path = uid_specific_dir / "metadata.json" # Metadata could also be returned if needed

    if not object_file_path.exists():
        log_internal_info("mock_lc_mem_core_get_object", {"message": f"Object {object_uid} not found at {object_file_path}"})
        return None
    
    try:
        with open(object_file_path, 'r') as f:
            payload = json.load(f)
        log_internal_info("mock_lc_mem_core_get_object", {"message": f"Object {object_uid} retrieved successfully."})
        return payload
    except IOError as e:
        log_internal_error("mock_lc_mem_core_get_object", {"message": f"IOError reading object {object_uid}: {e}"})
        return None
    except json.JSONDecodeError as e:
        log_internal_error("mock_lc_mem_core_get_object", {"message": f"JSONDecodeError reading object {object_uid}: {e}"})
        return None
    except Exception as e:
        log_internal_error("mock_lc_mem_core_get_object", {"message": f"Unexpected error reading object {object_uid}: {e}"})
        return None

def mock_lc_mem_core_update_object(object_uid: str, updated_object_payload: Dict[str, Any], requesting_persona_context: Optional[Dict[str, Any]] = None, update_metadata: Optional[Dict[str, Any]] = None) -> bool:
    if not object_uid.startswith("urn:crux:uid::"):
        log_internal_error("mock_lc_mem_core_update_object", {"message": f"Invalid CRUX UID format for update: {object_uid}"})
        return False

    uid_specific_dir = MADA_VAULT_DIR / object_uid.split('::')[-1]
    object_file_path = uid_specific_dir / "object_payload.json"
    metadata_file_path = uid_specific_dir / "metadata.json"

    if not object_file_path.exists() or not metadata_file_path.exists():
        log_internal_error("mock_lc_mem_core_update_object", {"message": f"Object {object_uid} not found for update."})
        return False

    try:
        # Update payload
        with open(object_file_path, 'w') as f:
            json.dump(updated_object_payload, f, indent=2)
        
        # Update metadata
        current_meta = {}
        with open(metadata_file_path, 'r') as f:
            current_meta = json.load(f)
        
        current_meta['updated_at'] = datetime.now(timezone.utc).isoformat()
        if update_metadata and 'version' in update_metadata:
            current_meta['version'] = update_metadata['version']
        elif 'version' in current_meta: # Basic increment if version exists
            parts = str(current_meta['version']).split('.')
            if len(parts) == 3 and all(p.isdigit() for p in parts):
                parts[-1] = str(int(parts[-1]) + 1)
                current_meta['version'] = ".".join(parts)
            else: # Non-standard version, just mark updated
                 current_meta['version'] = str(current_meta['version']) + "_updated"
        else:
            current_meta['version'] = "0.1.1" # Default next version from 0.1.0
        
        if update_metadata: # Merge any other metadata provided
            for key, value in update_metadata.items():
                if key not in ['crux_uid', 'created_at', 'updated_at']: # Avoid overwriting critical/managed meta
                    current_meta[key] = value
        
        with open(metadata_file_path, 'w') as f:
            json.dump(current_meta, f, indent=2)

        log_internal_info("mock_lc_mem_core_update_object", {"message": f"Object {object_uid} updated successfully."})
        return True
    except IOError as e:
        log_internal_error("mock_lc_mem_core_update_object", {"message": f"IOError updating object {object_uid}: {e}"})
        return False
    except Exception as e:
        log_internal_error("mock_lc_mem_core_update_object", {"message": f"Unexpected error updating object {object_uid}: {e}"})
        return False
            
def mock_lc_mem_core_delete_object(object_uid: str, requesting_persona_context: Optional[Dict[str, Any]] = None, deletion_rationale: Optional[str] = None) -> bool:
    if not object_uid.startswith("urn:crux:uid::"):
        log_internal_error("mock_lc_mem_core_delete_object", {"message": f"Invalid CRUX UID format for delete: {object_uid}"})
        return False

    uid_specific_dir = MADA_VAULT_DIR / object_uid.split('::')[-1]

    if not uid_specific_dir.exists():
        log_internal_info("mock_lc_mem_core_delete_object", {"message": f"Object directory {uid_specific_dir} for UID {object_uid} not found. Considered deleted."})
        return True # Idempotent delete
    
    try:
        shutil.rmtree(uid_specific_dir)
        log_internal_info("mock_lc_mem_core_delete_object", {"message": f"Object {object_uid} and its directory {uid_specific_dir} deleted successfully. Rationale: {deletion_rationale or 'N/A'}"})
        return True
    except OSError as e:
        log_internal_error("mock_lc_mem_core_delete_object", {"message": f"OSError deleting object directory {uid_specific_dir} for UID {object_uid}: {e}"})
        return False
    except Exception as e:
        log_internal_error("mock_lc_mem_core_delete_object", {"message": f"Unexpected error deleting object {object_uid}: {e}"})
        return False

def mock_lc_mem_core_query_objects(query_parameters: Dict[str, Any], requesting_persona_context: Optional[Dict[str, Any]] = None) -> List[Union[Dict[str, Any], str]]:
    results: List[Union[Dict[str, Any], str]] = []
    
    query_object_type = query_parameters.get("object_type")
    query_uid_list = query_parameters.get("object_uid_list")

    try:
        if query_object_type == PBI_OBJECT_TYPE:
            log_internal_info("mock_lc_mem_core_query_objects", {"message": f"Querying PBIs with params: {query_parameters}"})
            if not PBI_VAULT_DIR.exists():
                return []
            for pbi_uid_dir in PBI_VAULT_DIR.iterdir():
                if not pbi_uid_dir.is_dir():
                    continue
                
                # Construct UID from directory name to fetch PBI data via get_pbi
                pbi_uid_candidate = f"urn:crux:uid::{pbi_uid_dir.name}"
                pbi_data = get_pbi(pbi_uid_candidate) # get_pbi already handles metadata check and returns payload

                if pbi_data:
                    match = True # Assume match until a filter fails
                    
                    # Status filter
                    if "status" in query_params and pbi_data.get("status") != query_params["status"]:
                        match = False
                    
                    # Priority filter
                    if match and "priority" in query_params and pbi_data.get("priority") != query_params["priority"]:
                        match = False

                    # PBI Type filter
                    if match and "pbi_type" in query_params and pbi_data.get("pbi_type") != query_params["pbi_type"]:
                        match = False

                    # Cynefin Domain filter
                    if match and "cynefin_domain_context" in query_params and pbi_data.get("cynefin_domain_context") != query_params["cynefin_domain_context"]:
                        match = False
                    
                    # Related OIA Cycle UID filter
                    if match and "related_oia_cycle_uid" in query_params:
                        if query_params["related_oia_cycle_uid"] not in pbi_data.get("related_oia_cycle_uids", []):
                            match = False
                    
                    # Related RDSOTM Cycle Linkage UID filter
                    if match and "related_rdsotm_cycle_linkage_uid" in query_params:
                        if query_params["related_rdsotm_cycle_linkage_uid"] not in pbi_data.get("related_rdsotm_cycle_linkage_uids", []):
                            match = False

                    # Related RDSOTM Component UID filter
                    if match and "related_rdsotm_component_uid" in query_params:
                        if query_params["related_rdsotm_component_uid"] not in pbi_data.get("related_rdsotm_component_uids", []):
                            match = False
                    
                    if match:
                        results.append(pbi_data)
            # Keep existing logic for other object types or general MADA vault queries
        elif query_object_type and query_object_type != "*":
            log_internal_info("mock_lc_mem_core_query_objects", {"message": f"Querying generic object_type: {query_object_type}"})
            for item in MADA_VAULT_DIR.iterdir(): # Iterate general MADA_VAULT_DIR, not PBI_VAULT_DIR
                if item.is_dir(): 
                    metadata_file = item / "metadata.json"
                    if metadata_file.exists():
                        try:
                            with open(metadata_file, 'r') as f:
                                meta = json.load(f)
                            if meta.get("object_type") == query_object_type:
                                results.append(meta.get("crux_uid", f"urn:crux:uid::{item.name}"))
                        except Exception as e:
                            log_internal_error("mock_lc_mem_core_query_objects", {"message": f"Error reading metadata for {item.name}: {e}"})
        elif query_uid_list and isinstance(query_uid_list, list):
            log_internal_info("mock_lc_mem_core_query_objects", {"message": f"Querying for UIDs in list: {query_uid_list}"})
            for uid in query_uid_list:
                # Determine if it's a PBI UID by checking if its hex part exists in PBI_VAULT_DIR
                # This is a bit heuristic; ideally, object_type would be part of query_uid_list items or context
                uid_hex = uid.split('::')[-1]
                is_pbi_path = PBI_VAULT_DIR / uid_hex
                obj = None
                if is_pbi_path.exists() and is_pbi_path.is_dir(): # Check if it's a PBI by path
                    obj = get_pbi(uid)
                else: # Assume generic MADA object
                    obj = mock_lc_mem_core_get_object(uid)
                
                if obj:
                    results.append(obj)
        elif query_object_type == "*": 
            log_internal_info("mock_lc_mem_core_query_objects", {"message": "Querying for all object UIDs ('*') in general MADA_VAULT_DIR."})
            for item in MADA_VAULT_DIR.iterdir():
                if item.is_dir() and item.name != "pbis": # Exclude PBI vault from general '*' unless specified
                     results.append(f"urn:crux:uid::{item.name}")
        else: # Default or unspecified query
            log_internal_warning("mock_lc_mem_core_query_objects", {"message": f"Unsupported or generic query. Query: {query_parameters}. Consider specifying object_type."})
            # Optionally, list all UIDs from general MADA_VAULT_DIR (excluding pbis)
            for item in MADA_VAULT_DIR.iterdir():
                if item.is_dir() and item.name != "pbis":
                     results.append(f"urn:crux:uid::{item.name}")

    except Exception as e:
        log_internal_error("mock_lc_mem_core_query_objects", {"message": f"Error during query: {e}"})
        return [] # Return empty list on error
        
    log_internal_info("mock_lc_mem_core_query_objects", {"message": f"Query completed. Found {len(results)} results."})
    return results

# END_OF_LC_MEM_SERVICE_FUNCTIONS_SEPARATOR_

# ==============================================================================
# PBI (Product Backlog Item) MANAGEMENT FUNCTIONS
# ==============================================================================

def create_pbi(pbi_data: Dict[str, Any], requesting_persona_context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    pbi_uid_context_desc = pbi_data.get("title", "Untitled PBI")
    pbi_uid = mock_lc_mem_core_ensure_uid(PBI_OBJECT_TYPE, context_description=pbi_uid_context_desc)
    if "ERROR" in pbi_uid:
        log_internal_error("create_pbi", {"message": f"Failed to ensure UID for PBI: {pbi_uid}"})
        return None

    current_time = datetime.now(timezone.utc).isoformat()
    pbi_data_final = pbi_data.copy()
    pbi_data_final["pbi_uid"] = pbi_uid
    pbi_data_final.setdefault("pbi_schema_version", "0.1.0")
    pbi_data_final.setdefault("created_at", current_time)
    pbi_data_final["updated_at"] = current_time
    pbi_data_final.setdefault("status", "New")
    pbi_data_final.setdefault("priority", "Medium")

    uid_hex = pbi_uid.split('::')[-1]
    pbi_specific_dir = PBI_VAULT_DIR / uid_hex
    pbi_specific_dir.mkdir(parents=True, exist_ok=True)
    
    object_file_path = pbi_specific_dir / "object_payload.json"
    metadata_file_path = pbi_specific_dir / "metadata.json"

    try:
        with open(object_file_path, 'w') as f:
            json.dump(pbi_data_final, f, indent=2)
        
        pbi_metadata = {
            "crux_uid": pbi_uid,
            "object_type": PBI_OBJECT_TYPE,
            "pbi_schema_version": pbi_data_final["pbi_schema_version"],
            "created_at": pbi_data_final["created_at"],
            "updated_at": pbi_data_final["updated_at"],
            "title": pbi_data_final.get("title", "Untitled PBI"),
            "status": pbi_data_final.get("status"),
            "priority": pbi_data_final.get("priority")
        }
        with open(metadata_file_path, 'w') as f:
            json.dump(pbi_metadata, f, indent=2)
        
        log_internal_info("create_pbi", {"message": f"PBI {pbi_uid} created successfully."})
        return pbi_uid
    except Exception as e:
        log_internal_error("create_pbi", {"message": f"Error creating PBI {pbi_uid}: {e}"})
        if object_file_path.exists(): object_file_path.unlink(missing_ok=True) # Python 3.8+
        if metadata_file_path.exists(): metadata_file_path.unlink(missing_ok=True)
        if pbi_specific_dir.exists() and not any(pbi_specific_dir.iterdir()): pbi_specific_dir.rmdir()
        return None

def get_pbi(pbi_uid: str, requesting_persona_context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    if not pbi_uid or not pbi_uid.startswith("urn:crux:uid::"):
        log_internal_error("get_pbi", {"message": f"Invalid PBI UID format: {pbi_uid}"})
        return None
    
    uid_hex = pbi_uid.split('::')[-1]
    pbi_dir = PBI_VAULT_DIR / uid_hex
    object_file_path = pbi_dir / "object_payload.json"
    metadata_file_path = pbi_dir / "metadata.json" # To verify object_type

    if not object_file_path.exists() or not metadata_file_path.exists():
        log_internal_info("get_pbi", {"message": f"PBI {pbi_uid} not found."})
        return None
    
    try:
        with open(metadata_file_path, 'r') as f:
            meta = json.load(f)
        if meta.get("object_type") != PBI_OBJECT_TYPE:
            log_internal_error("get_pbi", {"message": f"Object {pbi_uid} is not of type {PBI_OBJECT_TYPE}."})
            return None

        with open(object_file_path, 'r') as f:
            payload = json.load(f)
        log_internal_info("get_pbi", {"message": f"PBI {pbi_uid} retrieved successfully."})
        return payload
    except Exception as e:
        log_internal_error("get_pbi", {"message": f"Error retrieving PBI {pbi_uid}: {e}"})
        return None

def update_pbi(pbi_uid: str, updates: Dict[str, Any], requesting_persona_context: Optional[Dict[str, Any]] = None) -> bool:
    if not pbi_uid or not pbi_uid.startswith("urn:crux:uid::"):
        log_internal_error("update_pbi", {"message": f"Invalid PBI UID format for update: {pbi_uid}"})
        return False

    uid_hex = pbi_uid.split('::')[-1]
    pbi_dir = PBI_VAULT_DIR / uid_hex
    object_file_path = pbi_dir / "object_payload.json"
    metadata_file_path = pbi_dir / "metadata.json"

    if not object_file_path.exists() or not metadata_file_path.exists():
        log_internal_error("update_pbi", {"message": f"PBI {pbi_uid} not found for update."})
        return False

    try:
        with open(object_file_path, 'r') as f:
            current_payload = json.load(f)
        with open(metadata_file_path, 'r') as f:
            current_metadata = json.load(f)

        if current_metadata.get("object_type") != PBI_OBJECT_TYPE:
             log_internal_error("update_pbi", {"message": f"Object {pbi_uid} is not of type {PBI_OBJECT_TYPE}."})
             return False

        # Apply updates to payload
        has_payload_updates = False
        for key, value in updates.items():
            if key not in ["pbi_uid", "created_at", "pbi_schema_version"]: # Protected payload fields
                if current_payload.get(key) != value:
                    current_payload[key] = value
                    has_payload_updates = True
        
        if has_payload_updates or updates.get("status") or updates.get("priority") or updates.get("title"): # Check if metadata relevant fields changed
            current_payload["updated_at"] = datetime.now(timezone.utc).isoformat()
            with open(object_file_path, 'w') as f:
                json.dump(current_payload, f, indent=2)

            # Update metadata file
            current_metadata["updated_at"] = current_payload["updated_at"]
            if updates.get("title"): current_metadata["title"] = updates["title"]
            if updates.get("status"): current_metadata["status"] = updates["status"]
            if updates.get("priority"): current_metadata["priority"] = updates["priority"]
            if updates.get("pbi_schema_version"): current_metadata["pbi_schema_version"] = updates["pbi_schema_version"] # Allow schema version update

            with open(metadata_file_path, 'w') as f:
                json.dump(current_metadata, f, indent=2)
            
            log_internal_info("update_pbi", {"message": f"PBI {pbi_uid} updated successfully."})
        else:
            log_internal_info("update_pbi", {"message": f"No effective updates for PBI {pbi_uid}."})
        return True
        
    except Exception as e:
        log_internal_error("update_pbi", {"message": f"Error updating PBI {pbi_uid}: {e}"})
        return False

def delete_pbi(pbi_uid: str, requesting_persona_context: Optional[Dict[str, Any]] = None) -> bool:
    if not pbi_uid or not pbi_uid.startswith("urn:crux:uid::"):
        log_internal_error("delete_pbi", {"message": f"Invalid PBI UID format for delete: {pbi_uid}"})
        return False

    uid_hex = pbi_uid.split('::')[-1]
    pbi_dir = PBI_VAULT_DIR / uid_hex

    if not pbi_dir.exists():
        log_internal_info("delete_pbi", {"message": f"PBI directory {pbi_dir} for UID {pbi_uid} not found. Considered deleted."})
        return True 

    try:
        shutil.rmtree(pbi_dir)
        log_internal_info("delete_pbi", {"message": f"PBI {pbi_uid} and its directory {pbi_dir} deleted successfully."})
        return True
    except Exception as e:
        log_internal_error("delete_pbi", {"message": f"Error deleting PBI {pbi_uid}: {e}"})
        return False

def query_pbis(query_params: Dict[str, Any], requesting_persona_context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    if not PBI_VAULT_DIR.exists():
        return results

    for pbi_uuid_dir in PBI_VAULT_DIR.iterdir():
        if pbi_uuid_dir.is_dir():
            pbi_uid = f"urn:crux:uid::{pbi_uuid_dir.name}"
            pbi_data = get_pbi(pbi_uid) # This uses the get_pbi function which checks metadata for object_type
            if pbi_data:
                match = True
                # Filter by status
                if "status" in query_params and pbi_data.get("status") != query_params["status"]:
                    match = False
                # Filter by priority
                if match and "priority" in query_params and pbi_data.get("priority") != query_params["priority"]:
                    match = False
                # Add more filters here as needed based on PBI schema and query_params structure
                # e.g., assignee_persona_uids (check if value is in list), tags_keywords (any or all), etc.

                if match:
                    results.append(pbi_data)
    
    log_internal_info("query_pbis", {"message": f"PBI Query completed. Found {len(results)} results for params: {query_params}"})
    return results

# ==============================================================================
# AGENT PROFILE MANAGEMENT FUNCTIONS
# ==============================================================================

def create_agent_profile(profile_data: Dict[str, Any], requesting_persona_context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    profile_uid_context_desc = profile_data.get("agent_name", "Untitled AgentProfile")
    agent_profile_uid = mock_lc_mem_core_ensure_uid(AGENT_PROFILE_OBJECT_TYPE, context_description=profile_uid_context_desc)
    if "ERROR" in agent_profile_uid:
        log_internal_error("create_agent_profile", {"message": f"Failed to ensure UID for AgentProfile: {agent_profile_uid}"})
        return None

    current_time = datetime.now(timezone.utc).isoformat()
    profile_data_final = profile_data.copy()
    profile_data_final["agent_profile_uid"] = agent_profile_uid
    profile_data_final.setdefault("profile_schema_version", "0.1.0")
    profile_data_final.setdefault("created_at", current_time)
    profile_data_final["updated_at"] = current_time
    profile_data_final.setdefault("status", "Development")
    profile_data_final.setdefault("agent_instance_version", "0.1.0")


    uid_hex = agent_profile_uid.split('::')[-1]
    profile_specific_dir = AGENT_PROFILE_VAULT_DIR / uid_hex
    profile_specific_dir.mkdir(parents=True, exist_ok=True)
    
    object_file_path = profile_specific_dir / "object_payload.json"
    metadata_file_path = profile_specific_dir / "metadata.json"

    try:
        with open(object_file_path, 'w') as f:
            json.dump(profile_data_final, f, indent=2)
        
        profile_metadata = {
            "crux_uid": agent_profile_uid,
            "object_type": AGENT_PROFILE_OBJECT_TYPE,
            "profile_schema_version": profile_data_final["profile_schema_version"],
            "created_at": profile_data_final["created_at"],
            "updated_at": profile_data_final["updated_at"],
            "agent_name": profile_data_final.get("agent_name", "Untitled AgentProfile"),
            "agent_type": profile_data_final.get("agent_type"),
            "status": profile_data_final.get("status")
        }
        with open(metadata_file_path, 'w') as f:
            json.dump(profile_metadata, f, indent=2)
        
        log_internal_info("create_agent_profile", {"message": f"AgentProfile {agent_profile_uid} created successfully."})
        return agent_profile_uid
    except Exception as e:
        log_internal_error("create_agent_profile", {"message": f"Error creating AgentProfile {agent_profile_uid}: {e}"})
        if object_file_path.exists(): object_file_path.unlink(missing_ok=True)
        if metadata_file_path.exists(): metadata_file_path.unlink(missing_ok=True)
        if profile_specific_dir.exists() and not any(profile_specific_dir.iterdir()): profile_specific_dir.rmdir()
        return None

def get_agent_profile(agent_profile_uid: str, requesting_persona_context: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    if not agent_profile_uid or not agent_profile_uid.startswith("urn:crux:uid::"):
        log_internal_error("get_agent_profile", {"message": f"Invalid AgentProfile UID format: {agent_profile_uid}"})
        return None
    
    uid_hex = agent_profile_uid.split('::')[-1]
    profile_dir = AGENT_PROFILE_VAULT_DIR / uid_hex
    object_file_path = profile_dir / "object_payload.json"
    metadata_file_path = profile_dir / "metadata.json"

    if not object_file_path.exists() or not metadata_file_path.exists():
        log_internal_info("get_agent_profile", {"message": f"AgentProfile {agent_profile_uid} not found."})
        return None
    
    try:
        with open(metadata_file_path, 'r') as f:
            meta = json.load(f)
        if meta.get("object_type") != AGENT_PROFILE_OBJECT_TYPE:
            log_internal_error("get_agent_profile", {"message": f"Object {agent_profile_uid} is not of type {AGENT_PROFILE_OBJECT_TYPE}."})
            return None

        with open(object_file_path, 'r') as f:
            payload = json.load(f)
        log_internal_info("get_agent_profile", {"message": f"AgentProfile {agent_profile_uid} retrieved successfully."})
        return payload
    except Exception as e:
        log_internal_error("get_agent_profile", {"message": f"Error retrieving AgentProfile {agent_profile_uid}: {e}"})
        return None

def update_agent_profile(agent_profile_uid: str, updates: Dict[str, Any], requesting_persona_context: Optional[Dict[str, Any]] = None) -> bool:
    if not agent_profile_uid or not agent_profile_uid.startswith("urn:crux:uid::"):
        log_internal_error("update_agent_profile", {"message": f"Invalid AgentProfile UID format for update: {agent_profile_uid}"})
        return False

    uid_hex = agent_profile_uid.split('::')[-1]
    profile_dir = AGENT_PROFILE_VAULT_DIR / uid_hex
    object_file_path = profile_dir / "object_payload.json"
    metadata_file_path = profile_dir / "metadata.json"

    if not object_file_path.exists() or not metadata_file_path.exists():
        log_internal_error("update_agent_profile", {"message": f"AgentProfile {agent_profile_uid} not found for update."})
        return False

    try:
        with open(object_file_path, 'r') as f:
            current_payload = json.load(f)
        with open(metadata_file_path, 'r') as f:
            current_metadata = json.load(f)

        if current_metadata.get("object_type") != AGENT_PROFILE_OBJECT_TYPE:
             log_internal_error("update_agent_profile", {"message": f"Object {agent_profile_uid} is not of type {AGENT_PROFILE_OBJECT_TYPE}."})
             return False

        has_payload_updates = False
        for key, value in updates.items():
            if key not in ["agent_profile_uid", "created_at", "profile_schema_version"]: # Protected fields
                if current_payload.get(key) != value:
                    current_payload[key] = value
                    has_payload_updates = True
        
        metadata_updated_fields = ["agent_name", "agent_type", "status", "profile_schema_version", "agent_instance_version"]
        needs_metadata_update = any(updates.get(field) for field in metadata_updated_fields if updates.get(field) != current_metadata.get(field))


        if has_payload_updates or needs_metadata_update:
            current_payload["updated_at"] = datetime.now(timezone.utc).isoformat()
            with open(object_file_path, 'w') as f:
                json.dump(current_payload, f, indent=2)

            current_metadata["updated_at"] = current_payload["updated_at"]
            for field in metadata_updated_fields:
                if updates.get(field) and updates.get(field) != current_metadata.get(field):
                     current_metadata[field] = updates[field]
            
            with open(metadata_file_path, 'w') as f:
                json.dump(current_metadata, f, indent=2)
            
            log_internal_info("update_agent_profile", {"message": f"AgentProfile {agent_profile_uid} updated successfully."})
        else:
            log_internal_info("update_agent_profile", {"message": f"No effective updates for AgentProfile {agent_profile_uid}."})
        return True
        
    except Exception as e:
        log_internal_error("update_agent_profile", {"message": f"Error updating AgentProfile {agent_profile_uid}: {e}"})
        return False

def delete_agent_profile(agent_profile_uid: str, requesting_persona_context: Optional[Dict[str, Any]] = None) -> bool:
    if not agent_profile_uid or not agent_profile_uid.startswith("urn:crux:uid::"):
        log_internal_error("delete_agent_profile", {"message": f"Invalid AgentProfile UID format for delete: {agent_profile_uid}"})
        return False

    uid_hex = agent_profile_uid.split('::')[-1]
    profile_dir = AGENT_PROFILE_VAULT_DIR / uid_hex

    if not profile_dir.exists():
        log_internal_info("delete_agent_profile", {"message": f"AgentProfile directory {profile_dir} for UID {agent_profile_uid} not found. Considered deleted."})
        return True 

    try:
        shutil.rmtree(profile_dir)
        log_internal_info("delete_agent_profile", {"message": f"AgentProfile {agent_profile_uid} and its directory {profile_dir} deleted successfully."})
        return True
    except Exception as e:
        log_internal_error("delete_agent_profile", {"message": f"Error deleting AgentProfile {agent_profile_uid}: {e}"})
        return False

def query_agent_profiles(query_params: Dict[str, Any], requesting_persona_context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    if not AGENT_PROFILE_VAULT_DIR.exists():
        return results

    for profile_uuid_dir in AGENT_PROFILE_VAULT_DIR.iterdir():
        if profile_uuid_dir.is_dir():
            profile_uid = f"urn:crux:uid::{profile_uuid_dir.name}"
            profile_data = get_agent_profile(profile_uid) # Uses get_agent_profile which checks object_type
            if profile_data:
                match = True
                
                if "agent_type" in query_params and profile_data.get("agent_type") != query_params["agent_type"]:
                    match = False
                
                if match and "capabilities" in query_params:
                    required_caps = query_params["capabilities"]
                    if isinstance(required_caps, str): # Single capability string
                        required_caps = [required_caps]
                    
                    agent_caps = profile_data.get("capabilities", [])
                    if not all(req_cap in agent_caps for req_cap in required_caps):
                        match = False
                
                if match:
                    results.append(profile_data)
    
    log_internal_info("query_agent_profiles", {"message": f"AgentProfile Query completed. Found {len(results)} results for params: {query_params}"})
    return results

# END_OF_LC_MEM_SERVICE_FUNCTIONS_SEPARATOR_
