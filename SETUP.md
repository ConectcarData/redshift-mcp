# Redshift MCP Server - Quick Setup Guide

This guide will help you set up, run, and test the Redshift MCP Server project.

---

## 1. Clone the Repository

```bash
git clone <your-repo-url>
cd my-redshift-mcp
```

---

## 2. Create and Activate a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

---

## 3. Install Required Packages

```bash
pip install -r requirements.txt
```

---

## 4. Configure Environment Variables (Recommended)

Create a `.env` file in the project root (same folder as `README.md`) with your Redshift credentials and desired mode:

```
REDSHIFT_HOST=your-cluster.region.redshift.amazonaws.com
REDSHIFT_DATABASE=mydb
REDSHIFT_USER=myuser
REDSHIFT_PASSWORD=mypassword
REDSHIFT_PORT=5439
DB_MCP_MODE=readonly
```

> The provided `scripts/run_server.sh` will automatically load this `.env` file if present.

---

## 5. Run the Server

### macOS/Linux:
```bash
./scripts/run_server.sh
```

### Windows:
```cmd
scripts\run_server.bat
```

---

## 6. Run the Test Script

To test the server logic (not the MCP protocol), run:

```bash
python tests/test_server.py
```

- Make sure your `.env` file or environment variables are set with valid Redshift credentials.
- The test script will connect, create a table, insert data, query, and clean up.

---

## 7. Directory Structure

```
my-redshift-mcp/
├── src/                       # Main server code
│   └── redshift_mcp_server.py
├── tests/                     # Test scripts
│   └── test_server.py
├── scripts/                   # Run scripts
│   ├── run_server.sh
│   └── run_server.bat
├── .env                       # (not committed) Redshift credentials
├── .gitignore
├── README.md
├── SETUP.md
├── requirements.txt
├── claude_desktop_config_example.json
├── venv/                      # (not committed)
```

---

## 8. Notes
- The server supports `.env` for easy local development.
- For Claude Desktop or production, set environment variables in your config or deployment system.
- The default mode is `readonly` for safety.

---

**You're ready to use and test the Redshift MCP Server!** 