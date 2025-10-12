#!/usr/bin/env python3
"""
Test script for the RFC2544 MCP Server

This script tests the MCP server functionality by making direct HTTP calls
to the RFC2544 REST API endpoints that the MCP server wraps.
"""

import asyncio
import json
import sys
from mcp_server import (
    stop_trafficgen,
    check_trafficgen_status,
    get_trafficgen_results,
    check_results_available
)


async def test_mcp_server():
    """Test the MCP server functionality."""
    print("Testing RFC2544 MCP Server...")
    print("=" * 50)
    
    # Test server configuration
    test_base_url = "http://localhost:8080"
    
    print(f"Testing with RFC2544 server at: {test_base_url}")
    print()
    
    # Test 1: Check traffic generator status
    print("1. Testing check_trafficgen_status...")
    try:
        result = await check_trafficgen_status(test_base_url)
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 2: Check if results are available
    print("2. Testing check_results_available...")
    try:
        result = await check_results_available(test_base_url)
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 3: Get results (if available)
    print("3. Testing get_trafficgen_results...")
    try:
        result = await get_trafficgen_results(test_base_url)
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 4: Stop traffic generator (if running)
    print("4. Testing stop_trafficgen...")
    try:
        result = await stop_trafficgen(test_base_url)
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    print("Test completed!")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())