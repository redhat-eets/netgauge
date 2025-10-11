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

# Run the MCP server
echo "Starting RFC2544 MCP Server..."
python3 mcp_server.py
