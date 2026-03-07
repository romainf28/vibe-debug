from src.schemas.stack_frame import StackFrame
import re

STACK_PATTERN = re.compile(r"> (.*)\((\d+)\)(\w+)\(\)")


def parse_stack(output: str) -> list[StackFrame]:

    frames = []

    for line in output.splitlines():
        m = STACK_PATTERN.search(line)
        if m:
            file_path = m.group(1)
            line_no = int(m.group(2))
            func = m.group(3)

            # Read the code line from file if possible
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    code_line = lines[line_no - 1].strip()
            except Exception:
                code_line = ""

            frames.append(
                StackFrame(file=file_path, line=line_no, function=func, code=code_line)
            )

    return frames
