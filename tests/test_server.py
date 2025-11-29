"""
Test script for Redshift MCP Server

This script demonstrates how to test the MCP server functionality.
"""
import asyncio
import json
from src.redshift_mcp_server import (
    connect_db, query, execute, list_schemas, 
    list_tables, describe_table, disconnect
)

async def test_redshift_mcp():
    """Test the Redshift MCP server tools"""
    
    print("Testing Redshift MCP Server\n")
    
    # Test 1: Connect to database
    print("1. Testing database connection...")
    # Replace with your actual Redshift credentials
    connection_result = await connect_db(
        host="",
        database="",
        user="",
        password="",
        port=5439
    )
    print(f"Connection result: {json.dumps(connection_result, indent=2)}\n")
    
    if connection_result.get("status") != "connected":
        print("Failed to connect. Please check your credentials.")
        return
    
    # Test 2: List schemas
    print("2. Testing list_schemas...")
    schemas_result = await list_schemas()
    print(f"Schemas: {json.dumps(schemas_result, indent=2)}\n")
    
    # Test 3: List tables
    print("3. Testing list_tables...")
    tables_result = await list_tables(schema="public")
    print(f"Tables in public schema: {json.dumps(tables_result, indent=2)}\n")
    
    # Test 4: Create a test table (if needed)
    print("4. Testing execute (CREATE TABLE)...")
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS test_mcp_table (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    create_result = await execute(create_table_sql)
    print(f"Create table result: {json.dumps(create_result, indent=2)}\n")
    
    # Test 5: Insert test data
    print("5. Testing execute (INSERT)...")
    insert_result = await execute(
        "INSERT INTO test_mcp_table (id, name) VALUES (%s, %s)",
        [1, "Test Record"]
    )
    print(f"Insert result: {json.dumps(insert_result, indent=2)}\n")
    
    # Test 6: Query data
    print("6. Testing query...")
    query_result = await query("SELECT * FROM test_mcp_table")
    print(f"Query result: {json.dumps(query_result, indent=2)}\n")
    
    # Test 7: Describe table
    print("7. Testing describe_table...")
    describe_result = await describe_table(table="test_mcp_table", schema="public")
    print(f"Table structure: {json.dumps(describe_result, indent=2)}\n")
    
    # Test 8: Clean up (optional)
    print("8. Cleaning up test table...")
    cleanup_result = await execute("DROP TABLE IF EXISTS test_mcp_table")
    print(f"Cleanup result: {json.dumps(cleanup_result, indent=2)}\n")
    
    # Test 9: Disconnect
    print("9. Testing disconnect...")
    disconnect_result = await disconnect()
    print(f"Disconnect result: {json.dumps(disconnect_result, indent=2)}\n")
    
    print("All tests completed!")

if __name__ == "__main__":
    # Run the async test function
    asyncio.run(test_redshift_mcp()) 