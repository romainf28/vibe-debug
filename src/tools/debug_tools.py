from src.core.debug_server import DebugServer

debug_server = DebugServer()


def debug_start_session(
    tests: str,
    path: str | None = None,
    lines: list[int] | None = None,
):
    return debug_server.start_session(tests, path=path, breakpoints=lines)


def debug_control(session_id: str, action: str):
    return debug_server.get(session_id).control(action)


def debug_inspect(session_id: str, expr: str):
    return debug_server.get(session_id).inspect(expr)


def debug_stack(session_id: str):
    return debug_server.get(session_id).stack()


def debug_breakpoint(
    session_id: str, action: str, file: str | None = None, line: int | None = None
):
    return debug_server.get(session_id).breakpoint(action, file, line)
