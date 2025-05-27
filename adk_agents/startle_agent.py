
from typing import List, Optional, Dict, Any, ClassVar
from pydantic import BaseModel, Field
from google.adk.agents import Agent
from lc_python_core.schemas.mada_schema import (
    MadaSeed,
    RawSignal,
    SignalComponentMetadataL1,
    EncodingStatusL1Enum,
    L1StartleContextObj,
)
from lc_python_core.services.lc_mem_service import write_mada_object
import time, os

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

    def _startle_generate_crux_uid(self, category: str, context: Dict[str, Any]) -> str:
        import uuid
        uid = f"{category}_{uuid.uuid4().hex[:8]}"
        log(f"[UID] Generated {uid} for category={category}")
        return uid

    def _startle_create_initial_madaSeed_shell(self, seed_id: str, trace_id: str, raw_signals: List[RawSignal]) -> MadaSeed:
        log(f"[Shell] Creating MadaSeed shell with trace_id={trace_id}")
        return MadaSeed(
            seed_id=seed_id,
            trace_id=trace_id,
            seed_content={
                "L1_startle_reflex": {
                    "raw_signals": [s.model_dump() for s in raw_signals],
                    "L1_startle_context_obj": None
                }
            }
        )

    def _startle_process_input_components(self, components: List[DataComponent], trace_id_for_context: str):
        raw_signals = []
        signal_meta = []

        for comp in components:
            log(f"[Component] Processing: {comp}")
            if not comp.content_handle_placeholder or not isinstance(comp.content_handle_placeholder, str) or comp.content_handle_placeholder.strip() == "":
                log("[Component] Skipped empty or invalid content")
                continue

            content = comp.content_handle_placeholder
            try:
                byte_size = len(content.encode("utf-8"))
            except Exception as enc_err:
                log(f"[EncodingError] Could not encode content: {enc_err}")
                continue

            signal_id = self._startle_generate_crux_uid("raw_signal", {"trace_id": trace_id_for_context, "role": comp.role_hint})
            raw_signals.append(RawSignal(
                raw_input_id=signal_id,
                raw_input_signal=content
            ))

            signal_meta.append(SignalComponentMetadataL1(
                component_role_L1=comp.role_hint,
                raw_signal_ref_uid_L1=signal_id,
                byte_size_hint_L1=byte_size,
                encoding_status_L1=EncodingStatusL1Enum.UNKNOWN_L1,
                media_type_hint_L1=comp.type_hint
            ))

        return raw_signals, signal_meta

    async def run(self, ctx):
        log("[StartleAgent] run() invoked")
        try:
            log(f"[Session] Keys: {list(ctx.session.state.keys())}")
            input_event = ctx.session.state.get("input_event", {})
            log(f"[InputEvent] Raw: {input_event}")

            try:
                parsed_input = self.model.model_validate(input_event)
                log(f"[Validation] Parsed: {parsed_input}")
            except Exception as parse_err:
                log(f"[ValidationError] {parse_err}")
                raise

            input_origin = parsed_input.origin_hint
            trace_id = self._startle_generate_crux_uid("trace_id", {})
            log(f"[TraceID] {trace_id}")

            raw_signals, signal_meta = self._startle_process_input_components(parsed_input.data_components, trace_id)
            log(f"[Processed] Signals: {len(raw_signals)}, Metadata: {len(signal_meta)}")

            if not signal_meta:
                log("[Fallback] Injecting default signal_meta")
                fallback_uid = self._startle_generate_crux_uid("fallback", {"trace_id": trace_id})
                signal_meta.append(SignalComponentMetadataL1(
                    component_role_L1="fallback",
                    raw_signal_ref_uid_L1=fallback_uid,
                    byte_size_hint_L1=0,
                    encoding_status_L1=EncodingStatusL1Enum.UNKNOWN_L1,
                    media_type_hint_L1=None
                ))
                raw_signals.append(RawSignal(
                    raw_input_id=fallback_uid,
                    raw_input_signal="[[AUTO_FALLBACK_SIGNAL]]"
                ))

            seed = self._startle_create_initial_madaSeed_shell(trace_id, trace_id, raw_signals)
            seed.seed_content["L1_startle_reflex"]["L1_startle_context_obj"] = L1StartleContextObj(
                trace_metadata={"origin_hint": input_origin},
                signal_components_metadata_L1=[m.model_dump() for m in signal_meta]
            ).model_dump()

            ctx.session.state["mada_seed_output"] = seed.model_dump()
            ctx.session.state["trace_id"] = trace_id
            log(f"[Done] Seed written. trace_id={trace_id}")

        except Exception as e:
            log(f"[CriticalError] {e}")
            fallback = self._startle_create_initial_madaSeed_shell("ERROR_SEED_ID", "ERROR_TRACE_ID", [])
            log(f"[FallbackDump] {fallback.model_dump()}")
            ctx.session.state["mada_seed_output"] = fallback.model_dump()
            ctx.session.state["trace_id"] = f"ERROR_ADK_EXECUTION_{type(e).__name__}"
            log(f"[Trace] Error trace_id set: {ctx.session.state['trace_id']}")
