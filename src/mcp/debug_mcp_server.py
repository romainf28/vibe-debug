"""MCP server that exposes debug tools to Claude Code."""

import json

from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent, ServerCapabilities, ToolsCapability
import mcp.server.stdio
from mcp.server import Server

from src.tools.debug_tools import (
    debug_start_session,
    debug_control,
    debug_inspect,
    debug_stack,
    debug_breakpoint,
)

# Create MCP server
server = Server("vibe-debug")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available debug tools."""
    return [
        Tool(
            name="debug_start_session",
            description="Start a new debugging session for a test or script. Returns a session ID that can be used with other debug tools.",
            inputSchema={
                "type": "object",
                "properties": {
                    "tests": {
                        "type": "string",
                        "description": "Test path (pytest format like 'tests/test_math.py::test_factorial_basic') or script path to debug",
                    },
                    "path": {
                        "type": "string",
                        "description": "Optional path to working directory",
                    },
                    "lines": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Optional list of line numbers to set breakpoints at on start",
                    },
                },
                "required": ["tests"],
            },
        ),
        Tool(
            name="debug_control",
            description="Execute a control command during debugging to navigate through code execution (continue, step_into, step_over, step_out, or where for stack trace).",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The debug session ID returned from debug_start_session",
                    },
                    "action": {
                        "type": "string",
                        "enum": [
                            "continue",
                            "step_into",
                            "step_over",
                            "step_out",
                            "where",
                        ],
                        "description": "The control action to execute",
                    },
                },
                "required": ["session_id", "action"],
            },
        ),
        Tool(
            name="debug_inspect",
            description="Inspect the value of a variable or expression in the current execution frame.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The debug session ID returned from debug_start_session",
                    },
                    "expr": {
                        "type": "string",
                        "description": "Python expression to evaluate (e.g., 'n', 'n * 2', 'len(lst)', 'result')",
                    },
                },
                "required": ["session_id", "expr"],
            },
        ),
        Tool(
            name="debug_stack",
            description="Get the current call stack showing all frames with file paths, line numbers, function names, and code context.",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The debug session ID returned from debug_start_session",
                    },
                },
                "required": ["session_id"],
            },
        ),
        Tool(
            name="debug_breakpoint",
            description="Manage breakpoints in the debug session (set new breakpoints, remove existing ones, or list all breakpoints).",
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "The debug session ID returned from debug_start_session",
                    },
                    "action": {
                        "type": "string",
                        "enum": ["set", "remove", "list"],
                        "description": "Breakpoint action: 'set' to create, 'remove' to delete, 'list' to show all",
                    },
                    "file": {
                        "type": "string",
                        "description": "File path (required for 'set' and 'remove' actions)",
                    },
                    "line": {
                        "type": "integer",
                        "description": "Line number (required for 'set' and 'remove' actions)",
                    },
                },
                "required": ["session_id", "action"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls and dispatch to debug functions."""
    try:
        if name == "debug_start_session":
            result = debug_start_session(
                tests=arguments["tests"],
                path=arguments.get("path"),
                lines=arguments.get("lines"),
            )
        elif name == "debug_control":
            result = debug_control(
                session_id=arguments["session_id"],
                action=arguments["action"],
            )
        elif name == "debug_inspect":
            result = debug_inspect(
                session_id=arguments["session_id"],
                expr=arguments["expr"],
            )
        elif name == "debug_stack":
            result = debug_stack(session_id=arguments["session_id"])
        elif name == "debug_breakpoint":
            result = debug_breakpoint(
                session_id=arguments["session_id"],
                action=arguments["action"],
                file=arguments.get("file"),
                line=arguments.get("line"),
            )
        else:
            raise ValueError(f"Unknown tool: {name}")

        # Convert result to string if it's a dict
        result_str = json.dumps(result) if isinstance(result, dict) else str(result)
        return [TextContent(type="text", text=result_str)]

    except Exception as e:
        error_msg = f"Error calling {name}: {str(e)}"
        return [TextContent(type="text", text=error_msg)]


async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="vibe-debug",
                server_version="1.0.0",
                capabilities=ServerCapabilities(tools=ToolsCapability()),
            ),
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
