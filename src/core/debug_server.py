from src.core.debug_session import DebugSession
import os
import sys
import subprocess


class DebugServer:
    def __init__(self):
        self.sessions: dict[str, DebugSession] = {}

    def start_session(
        self,
        tests: str,
        path: str | None = None,
        breakpoints: list[int] | None = None,
    ):
        cwd = path or os.getcwd()

        if "::" in tests:
            cmd = [
                "pytest",
                "-s",  # disable output capture
                "--trace",
                tests,
            ]
        else:
            cmd = [sys.executable, "-m", "pdb", tests]

        process = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        session = DebugSession(process, tests, cwd)

        session._wait_for_prompt()

        if breakpoints:
            for line in breakpoints:
                session.breakpoint("set", line=line)

        self.sessions[session.id] = session

        return {"session_id": session.id, "pid": process.pid}

    def get(self, session_id: str) -> DebugSession:

        if session_id not in self.sessions:
            raise ValueError("session not found")

        return self.sessions[session_id]

    def terminate(self, session_id: str):

        session = self.get(session_id)

        session.terminate()

        del self.sessions[session_id]
