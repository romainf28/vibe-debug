#!/usr/bin/env python
"""Script to start the vibe-debug MCP server for Claude Code integration."""

import asyncio
from src.mcp.debug_mcp_server import main

if __name__ == "__main__":
    asyncio.run(main())
