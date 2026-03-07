from dataclasses import dataclass


@dataclass
class StackFrame:
    file: str
    line: int
    function: str
    code: str
