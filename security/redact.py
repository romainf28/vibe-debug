import os
from typing import Any

ENV_VALUES = set(os.environ.values())
MAX_LEN = 500

def safe_repr(value:Any) -> str:
    """Truncates long values for LLM readability"""
    text = repr(value)

    if len(text) > MAX_LEN:
        return text[:MAX_LEN]+"...<truncated>"
    
    return text

def redact(object: Any):