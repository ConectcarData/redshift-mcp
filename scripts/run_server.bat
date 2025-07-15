@echo off

REM Activate the virtual environment
call venv\Scripts\activate

REM Run the Redshift MCP server
echo Starting Redshift MCP Server...
python redshift_mcp_server.py 