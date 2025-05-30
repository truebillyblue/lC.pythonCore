# learnt.cloud Python Core (`lc_python_core`)

This package contains the Python implementation of core concepts from the learnt.cloud doctrine, focusing on the `madaSeed` data structure and the L1-L7 Standard Operating Procedures (SOPs) as defined in the `/_lC.Core - Common - v0.1.2.2.md` doctrine (located in `../../../1_models/`).

## Purpose

The primary purpose of this package is to provide a functional Python representation of the core epistemic processing pipeline of the learnt.cloud framework. It translates the machine-readable pseudo-code from the doctrine into executable Python code.

This implementation currently includes:
- Pydantic models for the `madaSeed` object and its nested structures.
- Python functions for each of the L1-L7 SOPs (`startle` through `apply_done`).
- Baseline logic and mocked service calls for initial functionality and testing.
The L7 SOP (`sops/sop_l7_apply_done.py`) also demonstrates how to call other agent packages, such as `lc_adk_agent`, as part of its application logic.

## Structure

- **`schemas/`**: Contains `mada_schema.py`, which defines the Pydantic models for the `madaSeed` object and all its constituent parts, based on the v0.3 schema from the doctrine.
- **`sops/`**: Contains Python implementations for each L1-L7 Standard Operating Procedure (e.g., `sop_l1_startle.py`, `sop_l2_frame_click.py`, etc.).
    -   **`meta_sops/`**: A sub-package for higher-level SOPs that may orchestrate multiple core SOPs or service calls.
- **`services/`**: Contains `mock_lc_core_services.py`, which provides in-memory mock implementations for conceptual `lC.Core` service calls used by the SOPs. Full service implementations may reside here in the future. (Note: Some MADA mocks here are superseded by `lc_mem_service.py`).
- **`tests/`**: Contains `unittest` test suites for the schemas and SOP implementations (e.g., `test_sop_l1_l2.py`, `test_sop_l3_l7.py`, `test_lc_mem_service.py`, `test_sop_oia_cycle_management.py`, `test_sop_rdsotm_management.py`, and `test_lc_agent_registry.py`).

### Meta SOPs

Directory: `sops/meta_sops/`

This sub-package contains implementations for higher-level Standard Operating Procedures that orchestrate more complex processes, often involving multiple interactions with `lC.Core` services or other SOPs.

-   **`sop_oia_cycle_management.py`**: Implements functions for managing the lifecycle of an Observe-Interpret-Apply (OIA) cycle. This includes initiating a cycle, adding observations, interpretations, and application details, and tracking its overall state. These functions interact with the `lC.MEM.CORE` service (currently the file-based `lc_mem_service.py`) to persist OIA cycle data as MADA objects. The conceptual doctrine and MADA schema for these OIA cycle objects can be found in `1_models/CoreCommon/OIACycleManagement_SOP.md`.
-   **`sop_rdsotm_management.py`**: Implements functions for managing the lifecycle of r(DSOTM) components (Doctrine, Strategy, Operations, Tactics, Mission, Reality-Inputs) and their overarching cycle linkages. This includes creating components, associating them with cycles, and retrieving their details. These functions interact with the `lC.MEM.CORE` service to persist r(DSOTM) data as MADA objects. The conceptual doctrine and MADA schemas for these objects can be found in `1_models/CoreCommon/RDSOTMManagement_SOP.md`.

## Services Implementation

This package is beginning to implement concrete versions of the `lC.Core` services.

-   **`services/lc_mem_service.py`**: Provides a local file-system-based implementation of the `lC.MEM.CORE` service operations.
    *   **General MADA Objects:** Handles basic CRUD for generic MADA objects (e.g., `ensure_uid`, `create_object`, `get_object`, `update_object`, `delete_object`, and basic `query_objects`). These are stored in UID-named subdirectories under `lab/.data/mada_vault/`.
    *   **Product Backlog Items (PBIs):** Includes specific functions for managing PBI MADA objects:
        - `create_pbi(pbi_data: Dict, ...)`: Creates a new PBI.
        - `get_pbi(pbi_uid: str, ...)`: Retrieves a PBI.
        - `update_pbi(pbi_uid: str, updates: Dict, ...)`: Updates a PBI.
        - `delete_pbi(pbi_uid: str, ...)`: Deletes a PBI.
        - `query_pbis(query_params: Dict, ...)`: Queries PBIs. Supported `query_params` keys:
            - `status` (exact match)
            - `priority` (exact match)
            - `pbi_type` (exact match)
            - `cynefin_domain_context` (exact match)
            - `related_oia_cycle_uid` (checks if provided UID is in PBI's list)
            - `related_rdsotm_cycle_linkage_uid` (checks if provided UID is in PBI's list)
            - `related_rdsotm_component_uid` (checks if provided UID is in PBI's list)
            If `query_params` is empty, all PBIs are returned. Multiple parameters act as an AND condition.
        These PBIs are stored as JSON files within a dedicated `pbis` subdirectory: `lab/.data/mada_vault/pbis/<UID_HEX>/object_payload.json`, with corresponding metadata. The schema for PBIs is documented in `1_models/CoreCommon/PBI_Schema.md`.
    *   **Agent Profiles:** Includes functions (`create_agent_profile`, `get_agent_profile`, `update_agent_profile`, `delete_agent_profile`, `query_agent_profiles`) for managing Agent Profile MADA objects. These profiles define agent characteristics (name, type, model, capabilities, tools) and are stored as JSON files within a dedicated `agent_profiles` subdirectory: `lab/.data/mada_vault/agent_profiles/<UID_HEX>/object_payload.json`, with corresponding metadata. The schema is documented in `1_models/CoreCommon/AgentProfile_Schema.md`.
    *   **Local MADA Vault:** This service stores all data on the local disk. The root vault location is `../../.data/mada_vault/` (relative to the `lc_python_core` directory, meaning it resolves to `lab/.data/mada_vault/` from the repository root). This directory and its subdirectories (like `pbis/`, `agent_profiles/`) are created automatically if they don't exist.
    *   This implementation allows for local development and testing of MADA interactions.
-   **`services/mock_lc_core_services.py`**: Contains older mock functions. Some MADA-related mocks are superseded by `lc_mem_service.py`.

## Relation to `1_models`

The code in this package is a direct Python translation of the concepts, pseudo-code, and schemas detailed in the `../../../1_models/_lC.Core - Common - v0.1.2.2.md` doctrine. Any updates to the pseudo-code or `madaSeed` schema in the doctrine should be reflected here.

## Usage & Testing

This package is designed to be used as a library or a core component within the broader learnt.cloud environment.

To run the included unit tests, navigate to the `./lab/frontends/lc_python_core/` directory and run:

```bash
python -m unittest discover ./tests
```
Or, to run specific test files:
```bash
python -m unittest tests.test_sop_l1_l2
python -m unittest tests.test_sop_l3_l7
python -m unittest tests.test_lc_mem_service
python -m unittest tests.test_sop_oia_cycle_management
python -m unittest tests.test_sop_rdsotm_management
python -m unittest tests.test_lc_pbi_management
python -m unittest tests.test_lc_agent_registry
```

(Ensure your Python environment is set up to resolve imports from the `lc_python_core` package, e.g., by having your PYTHONPATH include the `./lab/frontends/` directory or by installing `lc_python_core` as an editable package if a `setup.py` is added in the future.)
