#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Check if environment variables are set
if [ -n "$REDSHIFT_HOST" ]; then
    echo "✓ Using environment variables for Redshift connection"
    echo "  Host: $REDSHIFT_HOST"
    echo "  Database: $REDSHIFT_DATABASE"
    echo "  User: $REDSHIFT_USER"
else
    echo "ℹ️  No environment variables set. Use connect_db tool to connect."
fi

# Run the Redshift MCP server
echo ""
echo "Starting Redshift MCP Server..."
python src/redshift_mcp_server.py 