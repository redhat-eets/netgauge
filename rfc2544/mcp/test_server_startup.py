#!/usr/bin/env python3
"""
Test script for the RFC2544 FastMCP Server startup

This script tests that the FastMCP server can start and list its tools.
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from rfc2544_mcp.server import mcp


async def test_server_startup():
    """Test that the server can start and list tools."""
    print("Testing RFC2544 FastMCP Server startup...")
    print("=" * 50)
    
    try:
        # Test that we can access the server instance
        print(f"Server name: {mcp.name}")
        
        # List available tools
        tools = mcp.list_tools()
        print(f"\nAvailable tools ({len(tools.tools)}):")
        for tool in tools.tools:
            print(f"  - {tool.name}: {tool.description}")
        
        print("\nServer startup test completed successfully!")
        
    except Exception as e:
        print(f"Error during server startup test: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_server_startup())
    sys.exit(0 if success else 1)
