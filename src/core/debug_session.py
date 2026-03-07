import subprocess
import queue
import uuid
import threading
import time

from typing import Literal

from src.utils.stack_frame import parse_stack


class DebugSession:
    def __init__(self, process: subprocess.Popen, script: str, cwd: str):
        self.id = str(uuid.uuid4())
        self.process = process
        self.script = script
        self.cwd = cwd

        self.output_queue = queue.Queue()
        self.reader_thread = threading.Thread(target=self._reader_loop, daemon=True)

        self.reader_thread.start()

    def _reader_loop(self):
        for line in iter(self.process.stdout.readline, ""):
            self.output_queue.put(line)

    def _wait_for_prompt(self, timeout=5):
        start = time.time()

        buffer = ""

        while time.time() - start < timeout:
            buffer += self._collect(0.1)

            if "(Pdb)" in buffer:
                return buffer

        return buffer

    def _collect(self, timeout=0.2):

        time.sleep(timeout)

        lines = []
        while not self.output_queue.empty():
            lines.append(self.output_queue.get())

        return "".join(lines)

    def _send(self, cmd: str):
        if self.process.poll() is not None:
            return {"event": "terminated", "message": "Debugger process finished"}

        self.process.stdin.write(cmd + "\n")
        self.process.stdin.flush()

        return self._wait_for_prompt()

    def control(
        self, action: Literal["continue", "step_into", "step_over", "step_out", "where"]
    ):
        action_mapping = {
            "continue": "c",
            "step_into": "s",
            "step_over": "n",
            "step_out": "r",
            "where": "where",
        }

        if action not in action_mapping:
            raise ValueError("Invalid action")

        output = self._send(action_mapping[action])

        return {"event": "execution", "action": action, "output": output}

    def inspect(self, expression: str):
        output = self._send(f"p {expression}")

        return {"event": "inspection", "expression": expression, "value": output}

    def locals(self):

        output = self._send("p locals()")

        return {"event": "locals", "data": output}

    def breakpoint(
        self,
        action: Literal["set", "remove", "list"],
        file: str | None = None,
        line: int | None = None,
    ):
        if action == "set":
            cmd = f"break {file}:{line}" if file else f"break {line}"

        elif action == "remove":
            cmd = f"clear {line}"

        elif action == "list":
            cmd = "break"

        else:
            raise ValueError("Invalid breakpoint action")

        output = self._send(cmd)

        return {"event": "breakpoint", "action": action, "output": output}

    def stack(self):

        output = self._send("where")

        frames = parse_stack(output)

        return {"event": "stack", "frames": [f.__dict__ for f in frames]}

    def terminate(self):
        self._send("quit")
        self.process.terminate()

        return {"event": "terminated"}
