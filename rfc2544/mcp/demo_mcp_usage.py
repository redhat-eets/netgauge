#!/usr/bin/env python3
"""
Demonstration of RFC2544 MCP Server Usage

This script shows how to use the RFC2544 MCP server tools programmatically.
"""

import asyncio
from mcp_server import (
    stop_trafficgen,
    check_trafficgen_status,
    get_trafficgen_results,
    check_results_available
)


async def demo_mcp_usage():
    """Demonstrate MCP server usage."""
    print("RFC2544 MCP Server Usage Demo")
    print("=" * 40)
    
    # Example server configuration
    server_addr = "localhost"
    server_port = 8080
    base_url = f"http://{server_addr}:{server_port}"
    
    print(f"Connecting to RFC2544 server at: {base_url}")
    print()
    
    # 1. Check if traffic generator is running
    print("1. Checking traffic generator status...")
    try:
        status = await check_trafficgen_status(base_url)
        print(f"   {status}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # 2. Check if results are available
    print("2. Checking if results are available...")
    try:
        available = await check_results_available(base_url)
        print(f"   {available}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # 3. Get results if available
    print("3. Getting test results...")
    try:
        results = await get_trafficgen_results(base_url)
        print(f"   {results}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # 4. Stop traffic generator (if running)
    print("4. Stopping traffic generator...")
    try:
        stop_result = await stop_trafficgen(base_url)
        print(f"   {stop_result}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    print("Demo completed!")


if __name__ == "__main__":
    asyncio.run(demo_mcp_usage())
