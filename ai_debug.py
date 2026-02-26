import os
import inspect
from datetime import datetime
from threading import Lock
import json

from security.redact import redact

_lock = Lock()

AI_DEBUG_FILE = os.getenv("AI_DEBUG_FILE", "ai_debug.jsonl")


def ai_breakpoint(label=None, capture_vars=None, capture_attrs=None):
    if os.getenv("AI_DEBUG") != 1:
        return

    locals_dict = inspect.currentframe().f_back.f_locals

    state = {}
    for key in capture_vars or []:
        if key in locals_dict:
            value = locals_dict[key]

            if capture_attrs and key in capture_attrs and hasattr(value, "__dict__"):
                attrs_to_capture = capture_attrs[key]
                sub_state = {}
                for attr in attrs_to_capture:
                    attr_value = getattr(value, attr, "<missing>")
                    sub_state[attr] = redact(attr_value)
                state[key] = sub_state
            else:
                state[key] = redact(value)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "label": label,
        "state": state,
    }

    with _lock:
        with open(AI_DEBUG_FILE, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
