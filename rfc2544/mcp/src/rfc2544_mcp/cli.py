#!/usr/bin/env python3
"""CLI for the RFC2544 MCP Server."""

import argparse
import sys
from .server import mcp


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="RFC2544 MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  rfc2544-mcp                    # Run with stdio transport
  rfc2544-mcp --help            # Show this help
        """
    )
    
    args = parser.parse_args()
    
    try:
        # FastMCP runs with stdio by default
        mcp.run()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
