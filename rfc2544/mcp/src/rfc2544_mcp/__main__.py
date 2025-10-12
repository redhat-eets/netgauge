#!/usr/bin/env python3
"""Main entry point for the RFC2544 MCP Server."""

from .server import mcp

if __name__ == "__main__":
    mcp.run()
