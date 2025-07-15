# 🚀 Redshift MCP Server

**A plug-and-play Model Context Protocol (MCP) server for Amazon Redshift. Instantly connect LLMs and AI agents (Claude, ChatGPT, etc.) to your Redshift data — securely, safely, and with zero hassle.**

---

## 🌟 Features
- **Production-ready**: Secure, robust, and easy to deploy
- **MCP Standard**: Exposes Redshift as standardized tools for LLMs/AI
- **Strict Access Modes**: `readonly`, `readwrite`, `admin` (enforced by env var)
- **Auto-connect**: Use environment variables or a `.env` file for seamless startup
- **No code changes needed**: Just configure and run
- **Extensible**: Add new tools or business logic easily
- **Works with Claude Desktop, ChatGPT, and any MCP client**

---

## ⚡ Quickstart

1. **Clone & Install**
   ```bash
   git clone <repo-url>
   cd my-redshift-mcp
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Configure** (recommended: create a `.env` file):
   ```env
   REDSHIFT_HOST=your-cluster.region.redshift.amazonaws.com
   REDSHIFT_DATABASE=mydb
   REDSHIFT_USER=myuser
   REDSHIFT_PASSWORD=mypassword
   REDSHIFT_PORT=5439
   DB_MCP_MODE=readonly
   ```
3. **Run the server**
   ```bash
   ./scripts/run_server.sh
   ```
4. **Connect from your LLM/MCP client** (e.g., Claude Desktop)

---

## 🔗 What is Redshift MCP Server?

Redshift MCP Server is an open-source bridge between Amazon Redshift and modern AI assistants. It lets LLMs securely query, explore, and (optionally) modify your Redshift data using the [Model Context Protocol (MCP)](https://github.com/anthropic-ai/model-context-protocol). Perfect for:
- Data teams enabling AI-powered analytics
- Building AI workflows and automations
- Secure, auditable LLM access to production data

---

## About This Project

This repository provides a **minimal, production-ready MCP server for Amazon Redshift** using the FastMCP framework. It allows LLMs and AI agents to:
- Query Redshift databases (with strict access controls)
- List schemas and tables
- Describe table structures
- (Optionally) insert/update data, depending on configured mode

**Key features:**
- Three access modes: `readonly`, `readwrite`, `admin` (see below)
- Environment variable and `.env` support for easy configuration
- Secure by default: starts in `readonly` mode
- Compatible with Claude Desktop, ChatGPT, and any MCP client
- Easy to extend with new tools or business logic

---

## Features

This MCP server provides the following tools for Redshift database operations:

- **connect_db**: Establish connection to a Redshift cluster (supports environment variables)
- **query**: Execute SELECT queries with optional parameter binding
- **execute**: Run INSERT, UPDATE, DELETE, or DDL statements
- **list_schemas**: List all schemas in the database
- **list_tables**: List tables in a specific schema
- **describe_table**: Get detailed structure of a table
- **disconnect**: Close the database connection

### Auto-Connection Support

The server supports automatic connection on startup using environment variables. If all required environment variables are set, the server will connect automatically when it starts.

---

## Access Modes and Query Safety

The server supports three access modes, controlled by the `DB_MCP_MODE` environment variable:

### 1. **readonly** (default)
- **Allows:** `SELECT`, `SHOW`, `DESCRIBE`, etc.
- **Blocks:** `INSERT`, `UPDATE`, `DELETE`, `DROP`, `TRUNCATE`, `ALTER`, `CREATE`, `GRANT`, `REVOKE`, `COMMENT`, `SET`, `COPY`, `UNLOAD`, `VACUUM`, `ANALYZE`, `MERGE`

### 2. **readwrite**
- **Allows:** `SELECT`, `INSERT`, `UPDATE`, `CREATE`, etc.
- **Blocks:** `DELETE`, `DROP`, `TRUNCATE`, `ALTER`, `GRANT`, `REVOKE`, `COMMENT`, `SET`, `COPY`, `UNLOAD`, `VACUUM`, `ANALYZE`, `MERGE`

### 3. **admin**
- **Allows everything** (no restrictions)

**If a forbidden statement is detected, the server will return a clear error message.**

#### How to Set the Mode
- **Environment variable:** `DB_MCP_MODE=readonly` (or `readwrite`, `admin`)
- **Claude Desktop config:**
  ```json
  "env": {
    "DB_MCP_MODE": "readwrite",
    ...
  }
  ```
- **Shell/local:**
  ```bash
  export DB_MCP_MODE=readonly
  ./run_server.sh
  ```

---

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running the Server

Run the server directly:

```bash
python src/redshift_mcp_server.py
```

Or use the provided scripts:

```bash
./scripts/run_server.sh
# or on Windows:
scripts\run_server.bat
```

By default, the server runs using STDIO transport, which is suitable for integration with MCP clients like Claude Desktop.

### Configuration for Claude Desktop

To use this server with Claude Desktop, add the following configuration to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

#### Option 1: With Environment Variables (Recommended)

```json
{
  "mcpServers": {
    "redshift": {
      "command": "/Users/anshulpatre/Desktop/DB-mcp/my-redshift-mcp/venv/bin/python",
      "args": ["/Users/anshulpatre/Desktop/DB-mcp/my-redshift-mcp/src/redshift_mcp_server.py"],
      "env": {
        "REDSHIFT_HOST": "your-cluster.region.redshift.amazonaws.com",
        "REDSHIFT_DATABASE": "mydb",
        "REDSHIFT_USER": "myuser",
        "REDSHIFT_PASSWORD": "mypassword",
        "REDSHIFT_PORT": "5439",
        "DB_MCP_MODE": "readonly"
      }
    }
  }
}
```

With this configuration, the server will automatically connect to your Redshift database on startup. You won't need to use the `connect_db` tool manually.

#### Option 2: Without Environment Variables

```json
{
  "mcpServers": {
    "redshift": {
      "command": "/Users/anshulpatre/Desktop/DB-mcp/my-redshift-mcp/venv/bin/python",
      "args": ["/Users/anshulpatre/Desktop/DB-mcp/my-redshift-mcp/src/redshift_mcp_server.py"]
    }
  }
}
```

With this configuration, you'll need to use the `connect_db` tool to establish a connection.

### Environment Variables

The server supports the following environment variables:

- `REDSHIFT_HOST`: Redshift cluster endpoint
- `REDSHIFT_DATABASE`: Database name
- `REDSHIFT_USER`: Username
- `REDSHIFT_PASSWORD`: Password
- `REDSHIFT_PORT`: Port number (default: 5439)
- `DB_MCP_MODE`: Access mode (`readonly`, `readwrite`, `admin`)

When these environment variables are set, the server will:
1. Automatically connect on startup
2. Use them as defaults for the `connect_db` tool if no parameters are provided
3. Enforce query/statement restrictions based on the selected mode

---

### Available Tools

#### 1. connect_db
Connect to a Redshift database cluster. If environment variables are set, parameters are optional.

```python
# With explicit parameters
{
  "tool": "connect_db",
  "arguments": {
    "host": "your-cluster.region.redshift.amazonaws.com",
    "database": "mydb",
    "user": "myuser",
    "password": "mypassword",
    "port": 5439
  }
}

# With environment variables set
{
  "tool": "connect_db",
  "arguments": {}
}
```

#### 2. query
Execute SELECT queries to retrieve data.

```python
{
  "tool": "query",
  "arguments": {
    "sql": "SELECT * FROM users WHERE created_at > %s",
    "params": ["2024-01-01"]
  }
}
```

#### 3. execute
Execute data modification or DDL statements.

```python
{
  "tool": "execute",
  "arguments": {
    "sql": "INSERT INTO users (name, email) VALUES (%s, %s)",
    "params": ["John Doe", "john@example.com"]
  }
}
```

#### 4. list_schemas
List all user-created schemas.

```python
{
  "tool": "list_schemas",
  "arguments": {}
}
```

#### 5. list_tables
List tables in a specific schema.

```python
{
  "tool": "list_tables",
  "arguments": {
    "schema": "public"
  }
}
```

#### 6. describe_table
Get detailed information about a table's structure.

```python
{
  "tool": "describe_table",
  "arguments": {
    "table": "users",
    "schema": "public"
  }
}
```

#### 7. disconnect
Close the database connection.

```python
{
  "tool": "disconnect",
  "arguments": {}
}
```

---

## Security Considerations

- **Credentials**: The recommended approach is to use environment variables in the MCP configuration file. This keeps credentials out of your code and tool calls.
- **Permissions**: Use database users with minimal required permissions.
- **Query Safety**: The server uses parameterized queries to prevent SQL injection. Query/statement type is checked and blocked according to the selected mode.
- **Network Security**: Ensure your Redshift cluster is properly secured with VPC and security groups.

## Development

To extend this server:

1. Add new tools using the `@mcp.tool()` decorator
2. Follow the FastMCP documentation for advanced features
3. Test thoroughly with your Redshift cluster

## Troubleshooting

### Connection Issues
- Verify your Redshift cluster endpoint and credentials
- Check network connectivity and security group settings
- Ensure the cluster is active and accepting connections

### Import Errors
- If `redshift-connector` is not available, the server falls back to `psycopg2`
- Install the appropriate connector based on your needs

## License

MIT

## Contributing

Feel free to submit issues or pull requests to improve this MCP server.

---

## 👤 Maintainer

This Redshift MCP Server is maintained and deployed by **Anshul**.

