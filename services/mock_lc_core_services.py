import uuid
from typing import Any, Dict

# In-memory store for mock objects
mock_mada_store: Dict[str, Any] = {}
mock_policy_store: Dict[str, Dict[str, Any]] = {}

def mock_lc_mem_core_get_object(object_uid: str, default_value: Any = None) -> Any:
    print(f"[MOCK_MEM_CORE] Getting object: {object_uid}")
    return mock_mada_store.get(object_uid, default_value)

def mock_lc_mem_core_ensure_uid(type_hint: str, context_hint: dict) -> str:
    # This is the same as _startle_generate_crux_uid, kept for conceptual mapping
    # and to centralize UID generation logic if it were to become more complex.
    print(f"[MOCK_MEM_CORE] Ensuring UID for type: {type_hint}, context: {context_hint}")
    return "urn:crux:uid::" + uuid.uuid4().hex

def mock_lc_mem_core_create_object(object_uid: str, payload: dict) -> bool:
    print(f"[MOCK_MEM_CORE] Creating object: {object_uid} with payload: {payload}")
    mock_mada_store[object_uid] = payload
    return True

def mock_lc_gov_core_get_policy(policy_ref: str, default_policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    print(f"[MOCK_GOV_CORE] Getting policy: {policy_ref}")
    # Ensure default_policy is a dict if None is passed but a default is expected by the caller
    effective_default = default_policy if default_policy is not None else {"name": policy_ref, "rules": ["default_mock_rule_for_" + policy_ref]}
    return mock_policy_store.get(policy_ref, effective_default)

# Example: Populate mock store for testing
# For L3's _keymap_get_primary_content_from_madaSeed
mock_mada_store["urn:crux:uid::sample_raw_signal_text_content_for_l3_test"] = "This is sample text content for keymap testing from mock_mada_store."
mock_mada_store["urn:crux:uid::sample_raw_signal_binary_content_for_l3_test"] = "[[BINARY_CONTENT_PLACEHOLDER]]" # As used in L3 helper

# For L7's _apply_resolve_l7_policies
mock_policy_store["L7_ActionSelection_Default_v1.0"] = { # Added .0 as per L7 helper's request
    "name": "L7_ActionSelection_Default_v1.0", 
    "description": "Mocked L7 Action Selection Policy",
    "default_action": "LogAuditRecord_L7_From_Mock_Policy",
    "rules": [
        {"if_intent_contains": "Display", "then_action": "PresentOutput_L7_From_Mock_Policy"},
        {"if_intent_contains": "Update", "then_action": "UpdateMadaObject_L7_From_Mock_Policy"}
    ]
}
mock_policy_store["L7_CapabilityCheck_Default_v1.0"] = {"name": "L7_CapabilityCheck_Default_v1.0", "capabilities_required": ["mock_logging", "mock_mada_access"]}
mock_policy_store["L7_LCLHandling_Default_v1.0"] = {"name": "L7_LCLHandling_Default_v1.0", "default_lcl_action": "Escalate_To_Admin"}
mock_policy_store["L7_SeedQAQC_Default_v1.0"] = {"name": "L7_SeedQAQC_Default_v1.0", "min_required_layers_complete": 6}
mock_policy_store["L7_FinalStatePrecedence_Default_v1.0"] = {"name": "L7_FinalStatePrecedence_Default_v1.0", "precedence": ["L7ActionLCL", "SeedIntegrityLCL", "L7ActionSuccess"]}


if __name__ == '__main__':
    print("--- Mock LC Core Services Initialized ---")
    print("Mock MADA Store:", mock_mada_store)
    print("Mock Policy Store:", mock_policy_store)

    # Example usage:
    test_uid = mock_lc_mem_core_ensure_uid("test_object", {"purpose": "example"})
    print(f"Generated Test UID: {test_uid}")
    
    mock_lc_mem_core_create_object(test_uid, {"data": "my test data"})
    retrieved_obj = mock_lc_mem_core_get_object(test_uid)
    print(f"Retrieved Object for {test_uid}: {retrieved_obj}")
    
    retrieved_unknown = mock_lc_mem_core_get_object("urn:crux:uid::unknown", default_value={"message": "Not Found"})
    print(f"Retrieved Unknown Object: {retrieved_unknown}")

    action_policy = mock_lc_gov_core_get_policy("L7_ActionSelection_Default_v1.0")
    print(f"Retrieved Action Policy: {action_policy}")

    other_policy = mock_lc_gov_core_get_policy("Some_Other_Policy_Ref", default_policy={"rules": ["specific_default"]})
    print(f"Retrieved Other Policy (with specific default): {other_policy}")

    another_policy = mock_lc_gov_core_get_policy("Yet_Another_Policy_Ref") # Will use the general default
    print(f"Retrieved Another Policy (with general default): {another_policy}")
