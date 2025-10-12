#!/usr/bin/env python3
"""
Test script for the RFC2544 FastMCP Server

This script tests the FastMCP server functionality by importing and testing
the individual functions.
"""

import asyncio
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the actual function implementations (not the decorated tools)
from rfc2544_mcp.server import mcp


async def test_fastmcp_server():
    """Test the FastMCP server functionality."""
    print("Testing RFC2544 FastMCP Server...")
    print("=" * 50)
    
    # Test server configuration
    test_server_addr = "localhost"
    test_server_port = 8080
    
    print(f"Testing with RFC2544 server at: {test_server_addr}:{test_server_port}")
    print()
    
    # Test 1: Check traffic generator status
    print("1. Testing check_trafficgen_status...")
    try:
        result = await check_trafficgen_status(test_server_addr, test_server_port)
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 2: Check if results are available
    print("2. Testing check_results_available...")
    try:
        result = await check_results_available(test_server_addr, test_server_port)
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 3: Get results (if available)
    print("3. Testing get_trafficgen_results...")
    try:
        result = await get_trafficgen_results(test_server_addr, test_server_port)
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 4: Get MAC addresses
    print("4. Testing get_mac_addresses...")
    try:
        result = await get_mac_addresses(test_server_addr, test_server_port)
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Test 5: Stop traffic generator (if running)
    print("5. Testing stop_trafficgen...")
    try:
        result = await stop_trafficgen(test_server_addr, test_server_port)
        print(f"   Result: {result}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    print("Test completed!")


if __name__ == "__main__":
    asyncio.run(test_fastmcp_server())
