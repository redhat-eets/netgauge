#!/usr/bin/env python3
"""
FastMCP Server for RFC2544 Traffic Generator Management

This FastMCP server provides tools to manage the RFC2544 traffic generator:
- Start the traffic generator with configurable parameters
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
async def start_trafficgen(
    l3: bool = False,
    device_pairs: str = "0:1",
    search_runtime: int = 10,
    validation_runtime: int = 30,
    num_flows: int = 1000,
    frame_size: int = 64,
    max_loss_pct: float = 0.002,
    sniff_runtime: int = 10,
    search_granularity: float = 5.0,
    server_addr: str = DEFAULT_SERVER_ADDR,
    server_port: int = DEFAULT_SERVER_PORT,
    active_device_pairs: Optional[str] = None,
    traffic_direction: Optional[str] = None,
    rate_tolerance_failure: Optional[str] = None,
    duplicate_packet_failure: Optional[str] = None,
    negative_packet_loss: Optional[str] = None,
    send_teaching_warmup: Optional[bool] = True,
    teaching_warmup_packet_type: Optional[str] = "generic",
    teaching_warmup_packet_rate: Optional[int] = 10000,
    use_src_ip_flows: Optional[int] = 1,
    use_dst_ip_flows: Optional[int] = 1,
    use_src_mac_flows: Optional[int] = 0,
    use_dst_mac_flows: Optional[int] = 0,
    rate_unit: Optional[str] = "%",
    rate: Optional[int] = 50,
    one_shot: Optional[int] = 0,
    rate_tolerance: Optional[int] = 10,
    runtime_tolerance: Optional[int] = 10,
    no_promisc: Optional[bool] = True,
    binary_search_extra_args: Optional[List[str]] = None,
    dst_macs: Optional[str] = None
) -> str:
    """Start the RFC2544 traffic generator with specified parameters.
    
    Args:
        l3: Whether to use L3 mode (True) or L2 mode (False) (default: False)
        device_pairs: Device pairs configuration (default: "0,1")
        search_runtime: Search runtime in seconds (default: 10)
        validation_runtime: Validation runtime in seconds (default: 30)
        num_flows: Number of flows to generate (default: 1000)
        frame_size: Frame size in bytes (default: 64)
        max_loss_pct: Maximum packet loss percentage (default: 0.002)
        sniff_runtime: Sniff runtime in seconds (default: 10)
        search_granularity: Search granularity value (default: 5.0)
        server_addr: RFC2544 server address (default: localhost)
        server_port: RFC2544 server port (default: 8080)
        active_device_pairs: Active device pairs (optional)
        traffic_direction: Traffic direction (optional)
        rate_tolerance_failure: Rate tolerance failure setting (optional)
        duplicate_packet_failure: Duplicate packet failure setting (optional)
        negative_packet_loss: Negative packet loss setting (optional)
        send_teaching_warmup: Send teaching warmup packets (optional)
        teaching_warmup_packet_type: Teaching warmup packet type (optional)
        teaching_warmup_packet_rate: Teaching warmup packet rate (optional)
        use_src_ip_flows: Use source IP flows (0 or 1, default: 1)
        use_dst_ip_flows: Use destination IP flows (0 or 1, default: 1)
        use_src_mac_flows: Use source MAC flows (0 or 1, default: 0)
        use_dst_mac_flows: Use destination MAC flows (0 or 1, default: 0)
        rate_unit: Rate unit (optional)
        rate: Rate value (optional)
        one_shot: One shot value (optional)
        rate_tolerance: Rate tolerance (optional)
        runtime_tolerance: Runtime tolerance (optional)
        no_promisc: Disable promiscuous mode (optional)
        binary_search_extra_args: Extra arguments for binary search (optional)
        dst_macs: Destination MAC addresses (required for L3 mode)
    
    Returns:
        Success or failure message
    """
    base_url = f"http://{server_addr}:{server_port}"
    
    # Build the request payload
    payload = {
        "l3": l3,
        "device_pairs": device_pairs,
        "search_runtime": search_runtime,
        "validation_runtime": validation_runtime,
        "num_flows": num_flows,
        "frame_size": frame_size,
        "max_loss_pct": max_loss_pct,
        "sniff_runtime": sniff_runtime,
        "search_granularity": search_granularity
    }
    
    # Add optional parameters if provided
    optional_params = {
        "active_device_pairs": active_device_pairs,
        "traffic_direction": traffic_direction,
        "rate_tolerance_failure": rate_tolerance_failure,
        "duplicate_packet_failure": duplicate_packet_failure,
        "negative_packet_loss": negative_packet_loss,
        "send_teaching_warmup": send_teaching_warmup,
        "teaching_warmup_packet_type": teaching_warmup_packet_type,
        "teaching_warmup_packet_rate": teaching_warmup_packet_rate,
        "use_src_ip_flows": use_src_ip_flows,
        "use_dst_ip_flows": use_dst_ip_flows,
        "use_src_mac_flows": use_src_mac_flows,
        "use_dst_mac_flows": use_dst_mac_flows,
        "rate_unit": rate_unit,
        "rate": rate,
        "one_shot": one_shot,
        "rate_tolerance": rate_tolerance,
        "runtime_tolerance": runtime_tolerance,
        "no_promisc": no_promisc,
        "binary_search_extra_args": binary_search_extra_args
    }
    
    # Add optional parameters that are not None
    for key, value in optional_params.items():
        if value is not None:
            # Convert boolean flow parameters to integers as expected by the REST API
            if key in ["use_src_ip_flows", "use_dst_ip_flows", "use_src_mac_flows", "use_dst_mac_flows"]:
                payload[key] = int(value)
            else:
                payload[key] = value
    
    # Add dst_macs for L3 mode
    if l3 and dst_macs is not None:
        payload["dst_macs"] = dst_macs
    elif l3 and dst_macs is None:
        raise Exception("dst_macs is required when l3=True")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{base_url}/trafficgen/start", json=payload)
            response.raise_for_status()
            result = response.json()
            
            if result:
                return "Traffic generator started successfully"
            else:
                return "Failed to start traffic generator"
                
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

@mcp.prompt(
    name="rfc2544-test",
    description="Start rfc2544 trafficgen, wait for it to complete and display the result. Usage: /run-rfc2544-test ip port"
)
async def rfc2544_test(arguments: str) -> str:
    parts = [p.strip() for p in arguments.split(":")]
    ip = parts[0] if len(parts) > 0 else None
    port = parts[1] if len(parts) > 1 else 8080

    if not ip or not port:
        return "Error: Usage: /run-rfc2544-test ip:port"

    return f"""
    Use start_trafficgen with these exact details:
    - server_addr: {ip}
    - server_port: {port}
    - use the default values for other parameters

    After the trafficgen started, use check_trafficgen_status every 5 second until the trafficgen is not running anymore; display the result when it is available
    """
    
    
if __name__ == "__main__":
    mcp.run()

