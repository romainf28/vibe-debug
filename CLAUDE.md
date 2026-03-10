# vibe-debug: Interactive Debugging for AI Coding Agents

## Quick Start

**Install & Run Commands:**
```bash
uv sync              # Install dependencies via uv (uses existing .venv)
uv run pytest tests/ # Run tests with uv
uv run python main.py # Run integration demo
```

**Note:** Always use `uv` to run commands—it automatically activates the existing virtual environment.

---

## Project Overview

**vibe-debug** implements concepts from the [Debug2Fix](https://arxiv.org/pdf/2602.18571) paper, enabling AI agents to debug code interactively:

- Place breakpoints and inspect execution
- Step through code (step_into, step_over, step_out)
- Inspect variable state and call stacks
- Iteratively refine solutions based on runtime feedback

This bridges AI code generation with real debugging workflows that human developers use.

---

## Architecture Overview

```
DebugServer (Main Coordinator)
  ├── Manages DebugSession instances (one per debug session)
  └── Routes control requests to sessions

DebugSession (Per-Session Handler)
  ├── Manages pdb subprocess via stdin/stdout pipes
  ├── Background reader thread for non-blocking I/O
  ├── Queue-based output buffering
  └── Provides synchronous API: control(), inspect(), stack(), breakpoint()

Debug Tools (5 Agent-Facing Functions)
  ├── debug_start_session() - Start debugging
  ├── debug_control() - Execute control commands
  ├── debug_inspect() - Inspect expressions
  ├── debug_stack() - Get call stack
  └── debug_breakpoint() - Manage breakpoints
```

**Key Design:**
- Uses pdb subprocess with pipes to avoid blocking
- Background thread collects output to queue
- Each session has unique UUID, independent lifecycle
- Timeouts prevent hanging on unresponsive debugger

---

## Core Components

### 1. DebugServer (`src/core/debug_server.py`)
Manages session lifecycle. Spawns pdb via pytest `--trace` (if test path contains `::`) or direct pdb execution.

**Methods:**
- `start_session(tests, path?, breakpoints?)`: Launch debug session, set initial breakpoints
- `get(session_id)`: Retrieve active session
- `terminate(session_id)`: Shutdown session

### 2. DebugSession (`src/core/debug_session.py`)
Active debugging session managing pdb subprocess.

**Methods:**
- `control(action)`: Execute commands (`continue`, `step_into`, `step_over`, `step_out`)
- `inspect(expr)`: Evaluate expression in current frame (uses pdb's `p` command)
- `locals()`: Get all local variables
- `stack()`: Get call stack (parses `where`, returns StackFrame objects)
- `breakpoint(action, file?, line?)`: Manage breakpoints (`set`, `remove`, `list`)

### 3. Stack Frame Parser (`src/utils/stack_frame.py`)
Converts pdb "where" output to structured StackFrame objects. Regex pattern: `> (.*)\((\d+)\)(\w+)\(\)`
Extracts: file path, line number, function name. Reads source file for context.

### 4. StackFrame Schema (`src/schemas/stack_frame.py`)
```python
@dataclass
class StackFrame:
    file: str          # Source file path
    line: int          # Line number
    function: str      # Function name
    code: str          # Source code at line
```

### 5. Debug Tools (`src/tools/debug_tools.py`)
Five high-level functions wrapping DebugServer:
- `debug_start_session(tests, path?, lines?)`
- `debug_control(session_id, action)`
- `debug_inspect(session_id, expr)`
- `debug_stack(session_id)`
- `debug_breakpoint(session_id, action, file?, line?)`

---

## Usage Example

```python
# Start debugging a test
result = debug_start_session("tests/test_math.py::test_factorial_basic", lines=[12])
session_id = result["session_id"]

# Step through execution
debug_control(session_id, "step_into")
debug_control(session_id, "step_over")

# Inspect state
debug_inspect(session_id, "n")        # Print variable "n"
debug_stack(session_id)                # Get call stack with code context

# Manage breakpoints
debug_breakpoint(session_id, "set", line=15)
debug_breakpoint(session_id, "list")
```

---

## Supported Pdb Commands

| Command | Method | Purpose |
|---------|--------|---------|
| `c` | `control("continue")` | Resume until next breakpoint |
| `s` | `control("step_into")` | Step into function |
| `n` | `control("step_over")` | Step over function |
| `r` | `control("step_out")` | Execute until return |
| `where` | `stack()` | Show call stack with context |
| `p expr` | `inspect(expr)` | Print expression |
| `break line` | `breakpoint("set", line=...)` | Set breakpoint |
| `clear line` | `breakpoint("remove", line=...)` | Remove breakpoint |
| `break` | `breakpoint("list")` | List all breakpoints |

---

## Development

### Adding New Commands

1. Add method to `DebugSession` in `src/core/debug_session.py`
2. Wrap in `src/tools/debug_tools.py`
3. Test with `uv run pytest tests/` or `uv run python main.py`

### Testing

- `tests/test_math.py`: Intentional bugs for testing debug workflows
- `main.py`: Integration demo
- Run: `uv run python main.py`

### Best Practices for Debugging

When debugging or inspecting the codebase:

- **ALWAYS prefer using MCP tools when available**
- **DO NOT generate temporary debugging code**
- **DO NOT modify files just to print debug output**

Use MCP tools for:
- Reading files
- Searching code
- Analyzing logs
- Inspecting runtime state

If an MCP tool exists for the task, use it instead of writing code.

---

## Integration with AI Agents

AI agents use vibe-debug for:
1. Execute generated code in controlled debugging environment
2. Inspect variable state at execution points
3. Step through execution to understand flow
4. Iteratively refine code based on runtime results
5. Debug test failures to understand requirements

## Project Structure

```
vibe-debug/
├── main.py                 # Integration demo
├── start_debug_mcp.py      # MCP server startup
├── src/
│   ├── core/
│   │   ├── debug_server.py     # Session lifecycle
│   │   └── debug_session.py    # Pdb subprocess control
│   ├── tools/debug_tools.py    # 5 debug tool functions
│   ├── agent/                  # Claude API agent wrappers
│   ├── mcp/debug_mcp_server.py # MCP server
│   ├── schemas/stack_frame.py  # Data structures
│   └── utils/stack_frame.py    # Output parsing
└── tests/test_math.py          # Tests with intentional bugs
```

---

## Dependencies

- **pytest**: Test execution with `--trace` flag
- **pdb**: Python's built-in debugger
- **pydantic**: Data validation
- **mcp**: Model Context Protocol for Claude Code
- **anthropic**: Claude API (for agent implementations)

---

## Limitations & Future Work

**Current Limitations:**
- Pdb-specific (no lldb/gdb support yet)
- Text-based output parsing (fragile to pdb changes)
- Single-threaded (limited multi-threaded debugging)
- Fixed timeouts may not suit slow operations

**Future:**
- Support additional debuggers (lldb, gdb)
- Structured debugger output format
- Conditional breakpoints & hit counts
- Watch expressions
- Performance profiling integration

---

## Reference

Based on [Debug2Fix](https://arxiv.org/pdf/2602.18571) paper: demonstrates that interactive debugging significantly improves AI agent code generation effectiveness. Key insight: AI agents benefit from the same iterative, feedback-driven process human developers use.
