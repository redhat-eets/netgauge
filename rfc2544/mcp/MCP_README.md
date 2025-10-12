# RFC2544 MCP Server

This directory contains an MCP (Model Context Protocol) server for managing the RFC2544 traffic generator. The MCP server provides tools to interact with the RFC2544 REST API through a standardized interface.

## Features

The MCP server provides the following tools:

1. **stop_trafficgen** - Stop the RFC2544 traffic generator
2. **check_trafficgen_status** - Check if the traffic generator is currently running
3. **get_trafficgen_results** - Get test results if available
4. **check_results_available** - Check if test results are available

## Installation

1. Install the required dependencies:
```bash
pip install -r mcp_requirements.txt
```

2. Make sure the RFC2544 traffic generator is running and accessible via its REST API (typically on `localhost:8080`).

## Usage

### Running the MCP Server

The MCP server can be run in two modes:

#### 1. Stdio Transport (Default)
For MCP clients that communicate via stdio:

```bash
python3 mcp_server.py
```

#### 2. SSE Transport (HTTP)
For HTTP-based clients on port 8090:

```bash
python3 mcp_server.py --sse
```

Or with a custom port:

```bash
python3 mcp_server.py --sse 9000
```

#### Using the Shell Script

The provided shell script supports both modes:

```bash
# Stdio transport (default)
./run_mcp_server.sh

# SSE transport on port 8090
./run_mcp_server.sh --sse

# SSE transport on custom port
./run_mcp_server.sh --sse --port 9000

# Show help
./run_mcp_server.sh --help
```

### Configuration

The server can be configured by modifying the default values in `mcp_server.py`:

- `DEFAULT_SERVER_ADDR`: RFC2544 server address (default: "localhost")
- `DEFAULT_SERVER_PORT`: RFC2544 server port (default: 8080)

### MCP Client Configuration

To use this MCP server with an MCP client, add the following configuration to your MCP client config:

#### For Stdio Transport:
```json
{
  "mcpServers": {
    "rfc2544": {
      "command": "python3",
      "args": ["/path/to/rfc2544/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/path/to/rfc2544"
      }
    }
  }
}
```

#### For SSE Transport:
```json
{
  "mcpServers": {
    "rfc2544": {
      "command": "python3",
      "args": ["/path/to/rfc2544/mcp_server.py", "--sse", "8090"],
      "env": {
        "PYTHONPATH": "/path/to/rfc2544"
      }
    }
  }
}
```

#### HTTP Client Access
When running with SSE transport, clients can access the MCP server via HTTP:

- **Base URL**: `http://localhost:8090`
- **List Tools**: `POST /tools/list`
- **Call Tool**: `POST /tools/call`

### Tool Parameters

All tools accept the following optional parameters:

- `server_addr` (string): RFC2544 server address (default: "localhost")
- `server_port` (integer): RFC2544 server port (default: 8080)

## Testing

### Stdio Transport Testing
Run the test script to verify the MCP server functionality:

```bash
python3 test_mcp_server.py
```

This will test all the MCP server tools against the RFC2544 REST API.

### SSE Transport Testing
To test the SSE transport functionality:

1. Start the MCP server with SSE transport:
```bash
python3 mcp_server.py --sse
# or
./run_mcp_server.sh --sse
```

2. In another terminal, run the SSE test client:
```bash
python3 test_sse_client.py
```

This will test all the MCP server tools via HTTP requests.

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

## Error Handling

The MCP server includes comprehensive error handling for:

- Network connectivity issues
- HTTP errors from the RFC2544 server
- Invalid responses
- Missing or malformed data

All errors are returned as error messages in the tool response.

## Dependencies

- `mcp`: Model Context Protocol library
- `httpx`: HTTP client library for async requests
- `asyncio`: Python async I/O library

## Integration with RFC2544

This MCP server is designed to work with the existing RFC2544 traffic generator REST API. It does not modify the RFC2544 codebase but provides a standardized interface for MCP clients to interact with it.

The server communicates with the following RFC2544 REST endpoints:

- `GET /trafficgen/running` - Check if traffic generator is running
- `GET /trafficgen/stop` - Stop the traffic generator
- `GET /result/available` - Check if results are available
- `GET /result` - Get test results
