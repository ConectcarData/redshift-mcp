"""
Simple Redshift MCP Server using FastMCP

A minimal MCP server that provides basic Redshift database operations.
"""
import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
import logging
from dataclasses import dataclass

load_dotenv()

# Ensure DB_MCP_MODE is set to 'readonly' by default if not defined externally
if 'DB_MCP_MODE' not in os.environ:
    os.environ['DB_MCP_MODE'] = 'readonly'

try:
    import redshift_connector
except ImportError:
    import psycopg2 as redshift_connector

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastMCP server instance
mcp = FastMCP("Redshift MCP Server", host='0.0.0.0', port='8000')

# Connection state
@dataclass
class ConnectionState:
    conn: Optional[Any] = None
    cursor: Optional[Any] = None
    host: Optional[str] = None
    database: Optional[str] = None
    user: Optional[str] = None

# Global connection state
connection_state = ConnectionState()

# --- MODE ENFORCEMENT ---

def get_mcp_mode() -> str:
    """Get the current MCP mode from environment variable (readonly, readwrite, admin)."""
    mode = os.getenv('DB_MCP_MODE', 'readonly').lower()
    if mode not in ('readonly', 'readwrite', 'admin'):
        mode = 'readonly'
    return mode

FORBIDDEN_READONLY = [
    'insert', 'update', 'delete', 'drop', 'truncate', 'alter', 'create', 'grant', 'revoke', 'comment', 'set', 'copy', 'unload', 'vacuum', 'analyze', 'merge'
]
FORBIDDEN_READWRITE = [
    'delete', 'drop', 'truncate', 'alter', 'grant', 'revoke', 'comment', 'set', 'copy', 'unload', 'vacuum', 'analyze', 'merge'
]


def is_forbidden(sql: str, mode: str) -> Optional[str]:
    """Check if the SQL statement is forbidden in the current mode. Returns reason if forbidden, else None."""
    sql_trim = sql.strip().lower()
    # Only check the first word (command)
    first_word = sql_trim.split()[0] if sql_trim else ''
    if mode == 'readonly':
        if first_word in FORBIDDEN_READONLY:
            return f"'{first_word.upper()}' statements are not allowed in readonly mode."
    elif mode == 'readwrite':
        if first_word in FORBIDDEN_READWRITE:
            return f"'{first_word.upper()}' statements are not allowed in readwrite mode."
    # admin: allow everything
    return None


def get_env_connection_params() -> Dict[str, Any]:
    """Get connection parameters from environment variables if available."""
    params = {}
    
    # Check for environment variables
    if os.getenv('REDSHIFT_HOST'):
        params['host'] = os.getenv('REDSHIFT_HOST')
    if os.getenv('REDSHIFT_DATABASE'):
        params['database'] = os.getenv('REDSHIFT_DATABASE')
    if os.getenv('REDSHIFT_USER'):
        params['user'] = os.getenv('REDSHIFT_USER')
    if os.getenv('REDSHIFT_PASSWORD'):
        params['password'] = os.getenv('REDSHIFT_PASSWORD')
    if os.getenv('REDSHIFT_PORT'):
        params['port'] = int(os.getenv('REDSHIFT_PORT'))
    
    return params

async def auto_connect():
    """Automatically connect using environment variables if available."""
    env_params = get_env_connection_params()
    
    # Check if we have all required parameters
    required = ['host', 'database', 'user', 'password']
    if all(key in env_params for key in required):
        logger.info("Auto-connecting using environment variables...")
        result = await connect_db(**env_params)
        if result.get('status') == 'connected':
            logger.info(f"Successfully connected to {env_params['host']}/{env_params['database']}")
        else:
            logger.warning(f"Auto-connection failed: {result.get('error')}")
    else:
        logger.info("Environment variables not configured for auto-connection. Use connect_db tool to connect.")

@mcp.tool()
async def connect_db(
    host: Optional[str] = None,
    database: Optional[str] = None,
    user: Optional[str] = None,
    password: Optional[str] = None,
    port: Optional[int] = None
) -> Dict[str, Any]:
    """
    Connect to a Redshift database.
    
    If parameters are not provided, will attempt to use environment variables:
    - REDSHIFT_HOST
    - REDSHIFT_DATABASE
    - REDSHIFT_USER
    - REDSHIFT_PASSWORD
    - REDSHIFT_PORT
    
    Args:
        host: Redshift cluster endpoint (optional if env var set)
        database: Database name (optional if env var set)
        user: Username (optional if env var set)
        password: Password (optional if env var set)
        port: Port number (default: 5439)
    
    Returns:
        Connection status and details
    """
    global connection_state
    
    # Get environment variables
    env_params = get_env_connection_params()
    
    # Use provided parameters or fall back to environment variables
    host = host or env_params.get('host')
    database = database or env_params.get('database')
    user = user or env_params.get('user')
    password = password or env_params.get('password')
    port = port or env_params.get('port', 5439)
    
    # Validate required parameters
    if not all([host, database, user, password]):
        missing = []
        if not host: missing.append('host (or REDSHIFT_HOST env var)')
        if not database: missing.append('database (or REDSHIFT_DATABASE env var)')
        if not user: missing.append('user (or REDSHIFT_USER env var)')
        if not password: missing.append('password (or REDSHIFT_PASSWORD env var)')
        
        return {
            "status": "error",
            "error": f"Missing required parameters: {', '.join(missing)}"
        }
    
    try:
        # Close existing connection if any
        if connection_state.conn:
            connection_state.conn.close()
        
        # Create new connection
        connection_state.conn = redshift_connector.connect(
            host=host,
            database=database,
            user=user,
            password=password,
            port=port
        )
        connection_state.cursor = connection_state.conn.cursor()
        connection_state.host = host
        connection_state.database = database
        connection_state.user = user
        
        return {
            "status": "connected",
            "host": host,
            "database": database,
            "user": user
        }
    except Exception as e:
        logger.error(f"Connection failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@mcp.tool()
async def query(sql: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
    """
    Execute a SELECT query on the Redshift database.
    
    Args:
        sql: SQL query to execute
        params: Optional query parameters for prepared statements
    
    Returns:
        Query results as list of dictionaries
    """
    mode = get_mcp_mode()
    forbidden_reason = is_forbidden(sql, mode)
    if forbidden_reason:
        return {"status": "error", "error": forbidden_reason}
    if not connection_state.conn:
        # Try auto-connect if not connected
        await auto_connect()
        if not connection_state.conn:
            return {"error": "Not connected to database. Use connect_db or set environment variables."}
    
    try:
        cursor = connection_state.cursor
        
        # Execute query with or without parameters
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        
        # Fetch results
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        
        # Convert to list of dictionaries
        results = []
        for row in rows:
            results.append(dict(zip(columns, row)))
        
        return {
            "status": "success",
            "row_count": len(results),
            "columns": columns,
            "data": results
        }
    except Exception as e:
        logger.error(f"Query failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@mcp.tool()
async def execute(sql: str, params: Optional[List[Any]] = None) -> Dict[str, Any]:
    """
    Execute INSERT, UPDATE, DELETE, or DDL statements.
    
    Args:
        sql: SQL statement to execute
        params: Optional parameters for prepared statements
    
    Returns:
        Execution status and affected rows
    """
    mode = get_mcp_mode()
    forbidden_reason = is_forbidden(sql, mode)
    if forbidden_reason:
        return {"status": "error", "error": forbidden_reason}
    if not connection_state.conn:
        # Try auto-connect if not connected
        await auto_connect()
        if not connection_state.conn:
            return {"error": "Not connected to database. Use connect_db or set environment variables."}
    
    try:
        cursor = connection_state.cursor
        
        # Execute statement
        if params:
            cursor.execute(sql, params)
        else:
            cursor.execute(sql)
        
        # Commit the transaction
        connection_state.conn.commit()
        
        return {
            "status": "success",
            "rows_affected": cursor.rowcount if hasattr(cursor, 'rowcount') else -1
        }
    except Exception as e:
        # Rollback on error
        if connection_state.conn:
            connection_state.conn.rollback()
        logger.error(f"Execute failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@mcp.tool()
async def list_schemas() -> Dict[str, Any]:
    """
    List all schemas in the Redshift database.
    
    Returns:
        List of schema names
    """
    if not connection_state.conn:
        # Try auto-connect if not connected
        await auto_connect()
        if not connection_state.conn:
            return {"error": "Not connected to database. Use connect_db or set environment variables."}
    
    try:
        cursor = connection_state.cursor
        cursor.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('pg_catalog', 'information_schema')
            ORDER BY schema_name
        """)
        
        schemas = [row[0] for row in cursor.fetchall()]
        
        return {
            "status": "success",
            "schemas": schemas
        }
    except Exception as e:
        logger.error(f"List schemas failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@mcp.tool()
async def list_tables(schema: str = "public") -> Dict[str, Any]:
    """
    List tables in a specific schema.
    
    Args:
        schema: Schema name (default: "public")
    
    Returns:
        List of table names in the schema
    """
    if not connection_state.conn:
        # Try auto-connect if not connected
        await auto_connect()
        if not connection_state.conn:
            return {"error": "Not connected to database. Use connect_db or set environment variables."}
    
    try:
        cursor = connection_state.cursor
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = %s 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """, (schema,))
        
        tables = [row[0] for row in cursor.fetchall()]
        
        return {
            "status": "success",
            "schema": schema,
            "tables": tables
        }
    except Exception as e:
        logger.error(f"List tables failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@mcp.tool()
async def describe_table(table: str, schema: str = "public") -> Dict[str, Any]:
    """
    Get the structure of a specific table.
    
    Args:
        table: Table name
        schema: Schema name (default: "public")
    
    Returns:
        Table structure including columns, types, and constraints
    """
    if not connection_state.conn:
        # Try auto-connect if not connected
        await auto_connect()
        if not connection_state.conn:
            return {"error": "Not connected to database. Use connect_db or set environment variables."}
    
    try:
        cursor = connection_state.cursor
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                numeric_precision,
                numeric_scale,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """, (schema, table))
        
        columns = []
        for row in cursor.fetchall():
            col_info = {
                "name": row[0],
                "type": row[1],
                "nullable": row[5] == 'YES',
                "default": row[6]
            }
            
            # Add length/precision info if applicable
            if row[2]:  # character_maximum_length
                col_info["length"] = row[2]
            elif row[3]:  # numeric_precision
                col_info["precision"] = row[3]
                if row[4]:  # numeric_scale
                    col_info["scale"] = row[4]
            
            columns.append(col_info)
        
        return {
            "status": "success",
            "schema": schema,
            "table": table,
            "columns": columns
        }
    except Exception as e:
        logger.error(f"Describe table failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }

@mcp.tool()
async def disconnect() -> Dict[str, str]:
    """
    Disconnect from the Redshift database.
    
    Returns:
        Disconnection status
    """
    global connection_state
    
    try:
        if connection_state.conn:
            connection_state.conn.close()
            connection_state.conn = None
            connection_state.cursor = None
            connection_state.host = None
            connection_state.database = None
            connection_state.user = None
        
        return {"status": "disconnected"}
    except Exception as e:
        logger.error(f"Disconnect failed: {str(e)}")
        return {"status": "error", "error": str(e)}

# Main entry point
if __name__ == "__main__":
    # Try auto-connect when running directly
    import asyncio
    asyncio.run(auto_connect())
    
    # Run the server
    mcp.run(transport="streamable-http")
