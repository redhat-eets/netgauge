#!/bin/bash
# Run the RFC2544 MCP Server

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the script directory
cd "$SCRIPT_DIR"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

# Check if required packages are installed
python3 -c "import httpx, mcp" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    pip install httpx mcp
fi

# Parse command line arguments
MODE="stdio"
PORT=8090

while [[ $# -gt 0 ]]; do
    case $1 in
        --sse)
            MODE="sse"
            shift
            ;;
        --http)
            MODE="http"
            shift
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [--sse|--http] [--port PORT]"
            echo ""
            echo "Options:"
            echo "  --sse        Run with SSE transport (default: stdio)"
            echo "  --http       Run with HTTP transport (FastAPI)"
            echo "  --port PORT  Port for SSE/HTTP transport (default: 8090)"
            echo "  --help, -h   Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Run with stdio transport"
            echo "  $0 --sse             # Run with SSE transport on port 8090"
            echo "  $0 --http            # Run with HTTP transport on port 8090"
            echo "  $0 --http --port 9000 # Run with HTTP transport on port 9000"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Run the MCP server
if [ "$MODE" = "sse" ]; then
    echo "Starting RFC2544 MCP Server with SSE transport on port $PORT..."
    python3 mcp_server.py --sse $PORT
elif [ "$MODE" = "http" ]; then
    echo "Starting RFC2544 HTTP MCP Server on port $PORT..."
    python3 http_mcp_server.py $PORT
else
    echo "Starting RFC2544 MCP Server with stdio transport..."
    python3 mcp_server.py
fi
