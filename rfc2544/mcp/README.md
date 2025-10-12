# RFC2544 MCP Server

A Model Context Protocol (MCP) server for managing RFC2544 traffic generators using FastMCP.

## Features

The MCP server provides the following tools:

1. **stop_trafficgen** - Stop the RFC2544 traffic generator
2. **check_trafficgen_status** - Check if the traffic generator is currently running
3. **get_trafficgen_results** - Get test results if available
4. **check_results_available** - Check if test results are available
5. **get_mac_addresses** - Get MAC addresses from the traffic generator

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management and running.

### Prerequisites

1. Install uv:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Make sure the RFC2544 traffic generator is running and accessible via its REST API (typically on `localhost:8080`).

### Setup

1. Install dependencies:
```bash
uv sync
```

2. Activate the virtual environment:
```bash
source .venv/bin/activate
```

## Usage

### Running the MCP Server

#### Using uv run (Recommended)
```bash
# Run with default settings
uv run rfc2544-mcp

# Run on custom port
uv run rfc2544-mcp --port 8090

# Run on custom host and port
uv run rfc2544-mcp --host 0.0.0.0 --port 8090
```

#### Using the installed script
After installation, you can run:
```bash
rfc2544-mcp --port 8090
```

#### Direct Python execution
```bash
uv run python -m rfc2544_mcp
```

### MCP Client Configuration

To use this MCP server with an MCP client, add the following configuration:

```json
{
  "mcpServers": {
    "rfc2544": {
      "command": "uv",
      "args": ["run", "rfc2544-mcp", "--port", "8090"],
      "cwd": "/path/to/rfc2544/mcp"
    }
  }
}
```

### Tool Parameters

All tools accept the following optional parameters:

- `server_addr` (string): RFC2544 server address (default: "localhost")
- `server_port` (integer): RFC2544 server port (default: 8080)

## Testing

### Unit Testing
Run the test script to verify the MCP server functionality:

```bash
uv run python test_fastmcp.py
```

This will test all the MCP server tools against the RFC2544 REST API.

### Development Testing
For development, you can also run the server in development mode:

```bash
uv run --dev rfc2544-mcp
```

## Tool Descriptions

### stop_trafficgen

Stops the RFC2544 traffic generator by calling the `/trafficgen/stop` endpoint.

**Parameters:**
- `server_addr` (optional): RFC2544 server address
- `server_port` (optional): RFC2544 server port

**Returns:** Success or failure message

### check_trafficgen_status

Checks if the RFC2544 traffic generator is currently running by calling the `/trafficgen/running` endpoint.

**Parameters:**
- `server_addr` (optional): RFC2544 server address
- `server_port` (optional): RFC2544 server port

**Returns:** Status message indicating if the traffic generator is running

### get_trafficgen_results

Retrieves test results from the RFC2544 traffic generator by calling the `/result` endpoint. First checks if results are available.

**Parameters:**
- `server_addr` (optional): RFC2544 server address
- `server_port` (optional): RFC2544 server port

**Returns:** Formatted test results including:
- RX/TX PPS (packets per second)
- RX/TX L1/L2 BPS (bits per second)
- Latency statistics (average, min, max)
- Packet loss statistics

### check_results_available

Checks if test results are available by calling the `/result/available` endpoint.

**Parameters:**
- `server_addr` (optional): RFC2544 server address
- `server_port` (optional): RFC2544 server port

**Returns:** Message indicating if results are available

### get_mac_addresses

Gets MAC addresses from the traffic generator by calling the `/maclist` endpoint.

**Parameters:**
- `server_addr` (optional): RFC2544 server address
- `server_port` (optional): RFC2544 server port

**Returns:** Comma-separated list of MAC addresses

## Error Handling

The MCP server includes comprehensive error handling for:

- Network connectivity issues
- HTTP errors from the RFC2544 server
- Invalid responses
- Missing or malformed data

All errors are returned as error messages in the tool response.

## Dependencies

- `fastmcp`: FastMCP framework for building MCP servers
- `httpx`: HTTP client library for async requests
- `uv`: Modern Python package manager and project runner

## Integration with RFC2544

This MCP server is designed to work with the existing RFC2544 traffic generator REST API. It does not modify the RFC2544 codebase but provides a standardized interface for MCP clients to interact with it.

The server communicates with the following RFC2544 REST endpoints:

- `GET /trafficgen/running` - Check if traffic generator is running
- `GET /trafficgen/stop` - Stop the traffic generator
- `GET /result/available` - Check if results are available
- `GET /result` - Get test results
- `GET /maclist` - Get MAC addresses

## Development

### Project Structure

```
mcp/
├── src/
│   └── rfc2544_mcp/
│       ├── __init__.py
│       ├── server.py          # Main FastMCP server implementation
│       ├── cli.py             # CLI interface
│       └── __main__.py        # Package entry point
├── test_fastmcp.py           # Test script
├── pyproject.toml            # Project configuration
└── README.md                 # This file
```

### Adding New Tools

To add new tools to the MCP server:

1. Add a new function decorated with `@mcp.tool()` in `src/rfc2544_mcp/server.py`
2. Follow the existing pattern for parameter handling and error management
3. Update this README with the new tool description
4. Add tests for the new tool

### Building and Publishing

To build the package:
```bash
uv build
```

To publish to PyPI (if needed):
```bash
uv publish
```
