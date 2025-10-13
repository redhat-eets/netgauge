# RFC2544 Traffic Generator MCP Server

A FastMCP server that provides tools to manage the RFC2544 traffic generator via REST API calls.

## Overview

This MCP (Model Context Protocol) server acts as a bridge between MCP clients and the RFC2544 traffic generator REST API. It provides a set of tools to start, stop, monitor, and retrieve results from RFC2544 performance tests.

## Features

- **Start Traffic Generator**: Configure and start RFC2544 tests with customizable parameters
- **Stop Traffic Generator**: Gracefully stop running tests
- **Monitor Status**: Check if the traffic generator is currently running
- **Retrieve Results**: Get formatted test results including performance metrics
- **MAC Address Discovery**: Retrieve MAC addresses from the traffic generator

## Installation

### Prerequisites

- Python 3.8+
- RFC2544 traffic generator REST API server running
- Required Python packages (see `pyproject.toml`)

### Setup

1. Install dependencies:
```bash
cd mcp/rfc2544_mcp
uv sync
```

2. Ensure the RFC2544 REST API server is running on the target host (default: localhost:8080)

## Usage

### Starting the MCP Server

```bash
python server.py
```

The server will start and be ready to accept MCP client connections.

### Available Tools

#### 1. `start_trafficgen`

Start the RFC2544 traffic generator with specified parameters.

**Required Parameters:**
- `l3` (bool, default: False): Whether to use L3 mode (True) or L2 mode (False)
- `device_pairs` (str, default: "0:1"): Device pairs configuration
- `search_runtime` (int, default: 10): Search runtime in seconds
- `validation_runtime` (int, default: 30): Validation runtime in seconds
- `num_flows` (int, default: 1000): Number of flows to generate
- `frame_size` (int, default: 64): Frame size in bytes
- `max_loss_pct` (float, default: 0.002): Maximum packet loss percentage
- `sniff_runtime` (int, default: 10): Sniff runtime in seconds
- `search_granularity` (float, default: 5.0): Search granularity value

**Optional Parameters:**
- `server_addr` (str, default: "localhost"): RFC2544 server address
- `server_port` (int, default: 8080): RFC2544 server port
- `active_device_pairs` (str): Active device pairs
- `traffic_direction` (str): Traffic direction
- `rate_tolerance_failure` (str): Rate tolerance failure setting
- `duplicate_packet_failure` (str): Duplicate packet failure setting
- `negative_packet_loss` (str): Negative packet loss setting
- `send_teaching_warmup` (bool, default: True): Send teaching warmup packets
- `teaching_warmup_packet_type` (str, default: "generic"): Teaching warmup packet type
- `teaching_warmup_packet_rate` (int, default: 10000): Teaching warmup packet rate
- `use_src_ip_flows` (int, default: 1): Use source IP flows (0 or 1)
- `use_dst_ip_flows` (int, default: 1): Use destination IP flows (0 or 1)
- `use_src_mac_flows` (int, default: 0): Use source MAC flows (0 or 1)
- `use_dst_mac_flows` (int, default: 0): Use destination MAC flows (0 or 1)
- `rate_unit` (str, default: "%"): Rate unit
- `rate` (int, default: 50): Rate value
- `one_shot` (int, default: 0): One shot value
- `rate_tolerance` (int, default: 10): Rate tolerance
- `runtime_tolerance` (int, default: 10): Runtime tolerance
- `no_promisc` (bool, default: True): Disable promiscuous mode
- `binary_search_extra_args` (List[str]): Extra arguments for binary search
- `dst_macs` (str): Destination MAC addresses (required for L3 mode)

**Example Usage:**
```python
# L2 mode with defaults
await start_trafficgen()

# L3 mode with custom parameters
await start_trafficgen(
    l3=True,
    dst_macs="00:11:22:33:44:55,00:11:22:33:44:56",
    num_flows=2000,
    frame_size=128
)
```

#### 2. `stop_trafficgen`

Stop the RFC2544 traffic generator.

**Parameters:**
- `server_addr` (str, default: "localhost"): RFC2544 server address
- `server_port` (int, default: 8080): RFC2544 server port

**Example Usage:**
```python
await stop_trafficgen()
```

#### 3. `check_trafficgen_status`

Check if the RFC2544 traffic generator is currently running.

**Parameters:**
- `server_addr` (str, default: "localhost"): RFC2544 server address
- `server_port` (int, default: 8080): RFC2544 server port

**Example Usage:**
```python
await check_trafficgen_status()
```

#### 4. `get_trafficgen_results`

Get RFC2544 test results if available.

**Parameters:**
- `server_addr` (str, default: "localhost"): RFC2544 server address
- `server_port` (int, default: 8080): RFC2544 server port

**Returns:** Formatted test results including:
- RX/TX PPS (packets per second)
- RX/TX L1/L2 BPS (bits per second)
- Latency statistics (average, min, max)
- Packet loss statistics

**Example Usage:**
```python
await get_trafficgen_results()
```

#### 5. `check_results_available`

Check if RFC2544 test results are available.

**Parameters:**
- `server_addr` (str, default: "localhost"): RFC2544 server address
- `server_port` (int, default: 8080): RFC2544 server port

**Example Usage:**
```python
await check_results_available()
```

#### 6. `get_mac_addresses`

Get MAC addresses from the RFC2544 traffic generator.

**Parameters:**
- `server_addr` (str, default: "localhost"): RFC2544 server address
- `server_port` (int, default: 8080): RFC2544 server port

**Example Usage:**
```python
await get_mac_addresses()
```

## Configuration

### Default Server Settings

- **Server Address**: localhost
- **Server Port**: 8080

These can be overridden by passing custom values to any tool.

### Common Test Scenarios

#### Basic L2 Throughput Test
```python
await start_trafficgen(
    l3=False,
    device_pairs="0:1",
    num_flows=1000,
    frame_size=64,
    max_loss_pct=0.002
)
```

#### L3 Latency Test
```python
await start_trafficgen(
    l3=True,
    dst_macs="00:11:22:33:44:55,00:11:22:33:44:56",
    num_flows=10000,
    frame_size=128,
    max_loss_pct=0.001
)
```

#### High-Volume Test
```python
await start_trafficgen(
    num_flows=50000,
    frame_size=1518,
    search_runtime=60,
    validation_runtime=120
)
```

## Error Handling

The server provides detailed error messages for common issues:

- **Connection Errors**: When unable to connect to the RFC2544 REST API server
- **HTTP Errors**: When the REST API returns error status codes
- **Validation Errors**: When required parameters are missing (e.g., `dst_macs` for L3 mode)

## Integration

This MCP server can be integrated with any MCP-compatible client, including:

- Claude Desktop
- Custom MCP clients
- CI/CD pipelines for automated testing
- Monitoring and alerting systems

### MCP Configuration

To use this server with an MCP client, add the following configuration to your `mcp.json` file:

```json
{
  "mcpServers": {
    "rfc2544-trafficgen": {
      "command": "uv",
      "args": ["run", "--with", "mcp[cli]", "mcp", "run", "path/to/netgauge/mcp/rfc2544_mcp/server.py"]
    }
  }
}
```

**Configuration Options:**

- **command**: The Python interpreter to use (can be `python`, `python3`, or full path)
- **args**: Arguments to pass to the server script
- **cwd**: Working directory (update the path to match your installation)
- **env**: Environment variables (PYTHONPATH ensures proper module resolution)

**Alternative Configurations:**

1. **Using uv (recommended for development):**
```json
{
  "mcpServers": {
    "rfc2544-trafficgen": {
      "command": "uv",
      "args": ["run", "--with", "mcp[cli]", "mcp", "run", "path/to/netgauge/mcp/rfc2544_mcp/server.py"]
    }
  }
}
```

2. **Using virtual environment:**
```json
{
  "mcpServers": {
    "rfc2544-trafficgen": {
      "command": "/path/to/venv/bin/python",
      "args": ["server.py"],
      "cwd": "/path/to/netgauge/mcp/rfc2544_mcp"
    }
  }
}
```

3. **With custom server settings:**
```json
{
  "mcpServers": {
    "rfc2544-trafficgen": {
      "command": "python",
      "args": ["server.py"],
      "cwd": "/path/to/netgauge/mcp/rfc2544_mcp",
      "env": {
        "PYTHONPATH": "/path/to/netgauge/mcp/rfc2544_mcp",
        "RFC2544_SERVER_ADDR": "192.168.1.100",
        "RFC2544_SERVER_PORT": "8080"
      }
    }
  }
}
```

**Claude Desktop Integration:**

1. Copy the configuration to your Claude Desktop MCP settings file
2. Restart Claude Desktop
3. The RFC2544 tools will be available in Claude's tool selection

**Custom Client Integration:**

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def main():
    server_params = StdioServerParameters(
        command="python",
        args=["server.py"],
        cwd="/path/to/netgauge/mcp/rfc2544_mcp"
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the session
            await session.initialize()
            
            # Use the tools
            result = await session.call_tool(
                "start_trafficgen",
                {"l3": False, "num_flows": 1000}
            )
            print(result)

## Troubleshooting

### Common Issues

1. **Connection Refused**: Ensure the RFC2544 REST API server is running
2. **Port Already in Use**: Check if another instance is running on the same port
3. **Missing Results**: Verify the test completed successfully before requesting results
4. **L3 Mode Errors**: Ensure `dst_macs` is provided when `l3=True`

### Debug Mode

Enable debug logging by setting the log level:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

See the main project LICENSE file for license information.
