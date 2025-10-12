#!/usr/bin/env python3
"""
MCP Server for RFC2544 Traffic Generator Management

This MCP server provides tools to manage the RFC2544 traffic generator:
- Stop the traffic generator
- Check the traffic generator running state
- Get results if available

The server communicates with the RFC2544 REST API to perform these operations.
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict, List, Optional

import httpx
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.server.sse import sse_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    TextContent,
    Tool,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default RFC2544 server configuration
DEFAULT_SERVER_ADDR = "localhost"
DEFAULT_SERVER_PORT = 8080

# Create the MCP server instance
server = Server("rfc2544-mcp-server")


@server.list_tools()
async def list_tools() -> ListToolsResult:
    """List available tools."""
    tools = [
        Tool(
            name="stop_trafficgen",
            description="Stop the RFC2544 traffic generator",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_addr": {
                        "type": "string",
                        "description": "RFC2544 server address (default: localhost)",
                        "default": DEFAULT_SERVER_ADDR
                    },
                    "server_port": {
                        "type": "integer",
                        "description": "RFC2544 server port (default: 8080)",
                        "default": DEFAULT_SERVER_PORT
                    }
                }
            }
        ),
        Tool(
            name="check_trafficgen_status",
            description="Check if the RFC2544 traffic generator is running",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_addr": {
                        "type": "string",
                        "description": "RFC2544 server address (default: localhost)",
                        "default": DEFAULT_SERVER_ADDR
                    },
                    "server_port": {
                        "type": "integer",
                        "description": "RFC2544 server port (default: 8080)",
                        "default": DEFAULT_SERVER_PORT
                    }
                }
            }
        ),
        Tool(
            name="get_trafficgen_results",
            description="Get RFC2544 test results if available",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_addr": {
                        "type": "string",
                        "description": "RFC2544 server address (default: localhost)",
                        "default": DEFAULT_SERVER_ADDR
                    },
                    "server_port": {
                        "type": "integer",
                        "description": "RFC2544 server port (default: 8080)",
                        "default": DEFAULT_SERVER_PORT
                    }
                }
            }
        ),
        Tool(
            name="check_results_available",
            description="Check if RFC2544 test results are available",
            inputSchema={
                "type": "object",
                "properties": {
                    "server_addr": {
                        "type": "string",
                        "description": "RFC2544 server address (default: localhost)",
                        "default": DEFAULT_SERVER_ADDR
                    },
                    "server_port": {
                        "type": "integer",
                        "description": "RFC2544 server port (default: 8080)",
                        "default": DEFAULT_SERVER_PORT
                    }
                }
            }
        )
    ]
    
    return ListToolsResult(tools=tools)


@server.call_tool()
async def call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls."""
    tool_name = request.name
    arguments = request.arguments or {}
    
    # Extract server configuration from arguments
    server_addr = arguments.get("server_addr", DEFAULT_SERVER_ADDR)
    server_port = arguments.get("server_port", DEFAULT_SERVER_PORT)
    base_url = f"http://{server_addr}:{server_port}"
    
    try:
        if tool_name == "stop_trafficgen":
            result = await stop_trafficgen(base_url)
        elif tool_name == "check_trafficgen_status":
            result = await check_trafficgen_status(base_url)
        elif tool_name == "get_trafficgen_results":
            result = await get_trafficgen_results(base_url)
        elif tool_name == "check_results_available":
            result = await check_results_available(base_url)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        return CallToolResult(
            content=[TextContent(type="text", text=result)]
        )
        
    except Exception as e:
        logger.error(f"Error calling tool {tool_name}: {e}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")],
            isError=True
        )


async def stop_trafficgen(base_url: str) -> str:
    """Stop the traffic generator."""
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


async def check_trafficgen_status(base_url: str) -> str:
    """Check if the traffic generator is running."""
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


async def get_trafficgen_results(base_url: str) -> str:
    """Get test results if available."""
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


async def check_results_available(base_url: str) -> str:
    """Check if test results are available."""
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


async def main():
    """Main entry point for the MCP server."""
    # Check command line arguments to determine transport mode
    if len(sys.argv) > 1 and sys.argv[1] == "--sse":
        # Run with SSE transport on port 8090
        port = 8090
        if len(sys.argv) > 2:
            try:
                port = int(sys.argv[2])
            except ValueError:
                logger.error(f"Invalid port number: {sys.argv[2]}")
                sys.exit(1)
        
        logger.info(f"Starting RFC2544 MCP Server with SSE transport on port {port}")
        await run_sse_server(port)
    else:
        # Run with stdio transport (default)
        logger.info("Starting RFC2544 MCP Server with stdio transport")
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="rfc2544-mcp-server",
                    server_version="1.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=None,
                        experimental_capabilities=None,
                    ),
                ),
            )


async def run_sse_server(port: int = 8090):
    """Run the MCP server with SSE transport."""
    async with sse_server(port=port) as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="rfc2544-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())