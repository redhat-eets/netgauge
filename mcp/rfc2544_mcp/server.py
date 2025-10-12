#!/usr/bin/env python3
"""
FastMCP Server for RFC2544 Traffic Generator Management

This FastMCP server provides tools to manage the RFC2544 traffic generator:
- Stop the traffic generator
- Check the traffic generator running state
- Get results if available

The server communicates with the RFC2544 REST API to perform these operations.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

import httpx
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default RFC2544 server configuration
DEFAULT_SERVER_ADDR = "localhost"
DEFAULT_SERVER_PORT = 8080

# Create the FastMCP server instance
mcp = FastMCP("RFC2544 Traffic Generator MCP Server")


@mcp.tool()
async def stop_trafficgen(
    server_addr: str = DEFAULT_SERVER_ADDR,
    server_port: int = DEFAULT_SERVER_PORT
) -> str:
    """Stop the RFC2544 traffic generator.
    
    Args:
        server_addr: RFC2544 server address (default: localhost)
        server_port: RFC2544 server port (default: 8080)
    
    Returns:
        Success or failure message
    """
    base_url = f"http://{server_addr}:{server_port}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/trafficgen/stop")
            response.raise_for_status()
            result = response.json()
            
            if result:
                return "Traffic generator stopped successfully"
            else:
                return "Failed to stop traffic generator"
                
        except httpx.RequestError as e:
            raise Exception(f"Failed to connect to RFC2544 server: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error from RFC2544 server: {e}")


@mcp.tool()
async def check_trafficgen_status(
    server_addr: str = DEFAULT_SERVER_ADDR,
    server_port: int = DEFAULT_SERVER_PORT
) -> str:
    """Check if the RFC2544 traffic generator is running.
    
    Args:
        server_addr: RFC2544 server address (default: localhost)
        server_port: RFC2544 server port (default: 8080)
    
    Returns:
        Status message indicating if the traffic generator is running
    """
    base_url = f"http://{server_addr}:{server_port}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/trafficgen/running")
            response.raise_for_status()
            result = response.json()
            
            if result:
                return "Traffic generator is currently running"
            else:
                return "Traffic generator is not running"
                
        except httpx.RequestError as e:
            raise Exception(f"Failed to connect to RFC2544 server: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error from RFC2544 server: {e}")


@mcp.tool()
async def get_trafficgen_results(
    server_addr: str = DEFAULT_SERVER_ADDR,
    server_port: int = DEFAULT_SERVER_PORT
) -> str:
    """Get RFC2544 test results if available.
    
    Args:
        server_addr: RFC2544 server address (default: localhost)
        server_port: RFC2544 server port (default: 8080)
    
    Returns:
        Formatted test results including:
        - RX/TX PPS (packets per second)
        - RX/TX L1/L2 BPS (bits per second)
        - Latency statistics (average, min, max)
        - Packet loss statistics
    """
    base_url = f"http://{server_addr}:{server_port}"
    
    async with httpx.AsyncClient() as client:
        try:
            # First check if results are available
            response = await client.get(f"{base_url}/result/available")
            response.raise_for_status()
            available = response.json()
            
            if not available:
                return "Test results are not available"
            
            # Get the results
            response = await client.get(f"{base_url}/result")
            response.raise_for_status()
            results = response.json()
            
            if not results:
                return "No test results found"
            
            # Format the results nicely
            formatted_results = []
            formatted_results.append("RFC2544 Test Results:")
            formatted_results.append("=" * 50)
            
            for port, stats in results.items():
                formatted_results.append(f"\nPort {port} Statistics:")
                formatted_results.append(f"  RX PPS: {stats.get('rx_pps', 'N/A'):.2f}")
                formatted_results.append(f"  TX PPS: {stats.get('tx_pps', 'N/A'):.2f}")
                formatted_results.append(f"  RX L1 BPS: {stats.get('rx_l1_bps', 'N/A'):.2f}")
                formatted_results.append(f"  RX L2 BPS: {stats.get('rx_l2_bps', 'N/A'):.2f}")
                formatted_results.append(f"  TX L1 BPS: {stats.get('tx_l1_bps', 'N/A'):.2f}")
                formatted_results.append(f"  TX L2 BPS: {stats.get('tx_l2_bps', 'N/A'):.2f}")
                formatted_results.append(f"  Average Latency: {stats.get('rx_latency_average', 'N/A'):.2f} μs")
                formatted_results.append(f"  Min Latency: {stats.get('rx_latency_minimum', 'N/A'):.2f} μs")
                formatted_results.append(f"  Max Latency: {stats.get('rx_latency_maximum', 'N/A'):.2f} μs")
                formatted_results.append(f"  Lost Packets: {stats.get('rx_lost_packets', 'N/A')}")
                formatted_results.append(f"  Lost Packets %: {stats.get('rx_lost_packets_pct', 'N/A'):.4f}%")
            
            formatted_results.append("\n" + "=" * 50)
            formatted_results.append("Raw JSON Results:")
            formatted_results.append(json.dumps(results, indent=2))
            
            return "\n".join(formatted_results)
            
        except httpx.RequestError as e:
            raise Exception(f"Failed to connect to RFC2544 server: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error from RFC2544 server: {e}")


@mcp.tool()
async def check_results_available(
    server_addr: str = DEFAULT_SERVER_ADDR,
    server_port: int = DEFAULT_SERVER_PORT
) -> str:
    """Check if RFC2544 test results are available.
    
    Args:
        server_addr: RFC2544 server address (default: localhost)
        server_port: RFC2544 server port (default: 8080)
    
    Returns:
        Message indicating if results are available
    """
    base_url = f"http://{server_addr}:{server_port}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/result/available")
            response.raise_for_status()
            result = response.json()
            
            if result:
                return "Test results are available"
            else:
                return "Test results are not available"
                
        except httpx.RequestError as e:
            raise Exception(f"Failed to connect to RFC2544 server: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error from RFC2544 server: {e}")


@mcp.tool()
async def get_mac_addresses(
    server_addr: str = DEFAULT_SERVER_ADDR,
    server_port: int = DEFAULT_SERVER_PORT
) -> str:
    """Get MAC addresses from the RFC2544 traffic generator.
    
    Args:
        server_addr: RFC2544 server address (default: localhost)
        server_port: RFC2544 server port (default: 8080)
    
    Returns:
        Comma-separated list of MAC addresses
    """
    base_url = f"http://{server_addr}:{server_port}"
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{base_url}/maclist")
            response.raise_for_status()
            result = response.json()
            
            if result:
                return f"Traffic generator MAC addresses: {result}"
            else:
                return "No MAC addresses found"
                
        except httpx.RequestError as e:
            raise Exception(f"Failed to connect to RFC2544 server: {e}")
        except httpx.HTTPStatusError as e:
            raise Exception(f"HTTP error from RFC2544 server: {e}")


if __name__ == "__main__":
    mcp.run()

