#!/usr/bin/env python3
"""
Test client for RFC2544 MCP Server with SSE transport

This script tests the MCP server functionality when running with SSE transport.
"""

import asyncio
import json
import httpx
from typing import Dict, Any


async def test_sse_mcp_server():
    """Test the MCP server with SSE transport."""
    print("Testing RFC2544 MCP Server with SSE transport...")
    print("=" * 50)
    
    # MCP server configuration
    mcp_server_url = "http://localhost:8090"
    
    print(f"Connecting to MCP server at: {mcp_server_url}")
    print()
    
    async with httpx.AsyncClient() as client:
        try:
            # Test 1: List available tools
            print("1. Testing list_tools...")
            try:
                response = await client.post(
                    f"{mcp_server_url}/tools/list",
                    json={}
                )
                response.raise_for_status()
                tools = response.json()
                print(f"   Available tools: {[tool['name'] for tool in tools.get('tools', [])]}")
            except Exception as e:
                print(f"   Error: {e}")
            print()
            
            # Test 2: Check traffic generator status
            print("2. Testing check_trafficgen_status...")
            try:
                response = await client.post(
                    f"{mcp_server_url}/tools/call",
                    json={
                        "name": "check_trafficgen_status",
                        "arguments": {
                            "server_addr": "localhost",
                            "server_port": 8080
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                print(f"   Result: {result}")
            except Exception as e:
                print(f"   Error: {e}")
            print()
            
            # Test 3: Check if results are available
            print("3. Testing check_results_available...")
            try:
                response = await client.post(
                    f"{mcp_server_url}/tools/call",
                    json={
                        "name": "check_results_available",
                        "arguments": {
                            "server_addr": "localhost",
                            "server_port": 8080
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                print(f"   Result: {result}")
            except Exception as e:
                print(f"   Error: {e}")
            print()
            
            # Test 4: Get results
            print("4. Testing get_trafficgen_results...")
            try:
                response = await client.post(
                    f"{mcp_server_url}/tools/call",
                    json={
                        "name": "get_trafficgen_results",
                        "arguments": {
                            "server_addr": "localhost",
                            "server_port": 8080
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                print(f"   Result: {result}")
            except Exception as e:
                print(f"   Error: {e}")
            print()
            
            # Test 5: Stop traffic generator
            print("5. Testing stop_trafficgen...")
            try:
                response = await client.post(
                    f"{mcp_server_url}/tools/call",
                    json={
                        "name": "stop_trafficgen",
                        "arguments": {
                            "server_addr": "localhost",
                            "server_port": 8080
                        }
                    }
                )
                response.raise_for_status()
                result = response.json()
                print(f"   Result: {result}")
            except Exception as e:
                print(f"   Error: {e}")
            print()
            
        except httpx.RequestError as e:
            print(f"Failed to connect to MCP server: {e}")
            print("Make sure the MCP server is running with SSE transport:")
            print("  python3 mcp_server.py --sse")
            print("  or")
            print("  ./run_mcp_server.sh --sse")
    
    print("Test completed!")


if __name__ == "__main__":
    asyncio.run(test_sse_mcp_server())

