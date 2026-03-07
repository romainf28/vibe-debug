import json
import time
from src.core.debug_server import DebugServer


def pretty(x):
    print(json.dumps(x, indent=2))


def main():

    print("=== Debug Tool Integration Test ===\n")

    server = DebugServer()

    # ------------------------------------------------
    # 1. Start debugging session
    # ------------------------------------------------

    print("Starting debug session...")

    result = server.start_session(
        tests="tests/test_math.py::test_factorial_basic",
        path=".",
        breakpoints=[10],
    )

    pretty(result)

    session_id = result["session_id"]
    session = server.get(session_id)

    print("\nSession ID:", session_id)

    time.sleep(1)

    # ------------------------------------------------
    # 2. Verify process started
    # ------------------------------------------------

    print("\nChecking debugger process...")

    alive = session.process.poll() is None

    print("Debugger running:", alive)

    if not alive:
        print("Debugger failed to start")
        return

    # ------------------------------------------------
    # 3. Read initial debugger output
    # ------------------------------------------------

    print("\nInitial debugger output:")
    output = session._collect()
    print(output)

    # ------------------------------------------------
    # 4. Get stack frames
    # ------------------------------------------------

    print("\nRequesting stack frames...")

    stack = session.stack()

    pretty(stack)

    # ------------------------------------------------
    # 5. Step into code
    # ------------------------------------------------

    print("\nStepping into code...")

    step = session.control("step_into")

    pretty(step)

    # ------------------------------------------------
    # 6. Inspect variable
    # ------------------------------------------------

    print("\nInspecting variable 'n'")

    inspect = session.inspect("n")

    pretty(inspect)

    # ------------------------------------------------
    # 7. Show locals
    # ------------------------------------------------

    print("\nLocal variables")

    locals_data = session.locals()

    pretty(locals_data)

    # ------------------------------------------------
    # 8. Continue execution
    # ------------------------------------------------

    print("\nContinuing execution...")

    cont = session.control("continue")

    pretty(cont)

    # ------------------------------------------------
    # 9. Terminate session
    # ------------------------------------------------

    print("\nTerminating session...")

    session.terminate()

    print("Done.")


if __name__ == "__main__":
    main()
