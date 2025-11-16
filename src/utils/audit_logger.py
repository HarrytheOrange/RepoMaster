import json
import os
import time
from datetime import datetime
from typing import Any, Dict, Optional


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _default_log_dir() -> str:
    # Prefer current process working dir logs/ to avoid scattering
    return os.path.join(os.getcwd(), "logs")


def _truncate(text: Any, max_len: int = 4000) -> Any:
    """
    Safely truncate large strings for logging to keep JSONL entries compact.
    Non-strings are returned unchanged.
    """
    if isinstance(text, str) and len(text) > max_len:
        return text[: max_len - 20] + f"...[+{len(text) - max_len} chars]"
    return text


def log_event(
    event_type: str,
    payload: Dict[str, Any],
    work_dir: Optional[str] = None,
    filename: str = "audit.log",
) -> None:
    """
    Append a structured JSON event to a JSONL log file.
    - event_type: short type label, e.g., "llm_interaction", "tool_usage", "agent_state"
    - payload: dict with event data; large strings should be pre-truncated if needed
    - work_dir: if provided, logs to <work_dir>/<filename>, else to ./logs/<filename>
    """
    try:
        base_dir = work_dir if work_dir else _default_log_dir()
        _ensure_dir(base_dir)
        log_path = os.path.join(base_dir, filename)
        record = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "type": event_type,
            **payload,
        }
        # Ensure potentially large fields are truncated just in case
        for key in ("messages", "response", "arguments", "result_preview", "final_answer_preview"):
            if key in record:
                record[key] = _truncate(record[key])
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        # Best-effort logging: never raise
        pass


class Stopwatch:
    """
    Small helper for measuring durations.
    """
    def __init__(self) -> None:
        self._start = time.perf_counter()

    def elapsed(self) -> float:
        return round(time.perf_counter() - self._start, 6)


