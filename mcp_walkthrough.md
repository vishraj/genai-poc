# MCP Server Walkthrough: GenAI PoC Training Service

You have successfully exposed the `DataService` as an MCP server. This allows AI clients (like Claude Desktop) to use your database functions as tools.

## 1. Verify Installation
Ensure you have the required packages installed:
```powershell
uv sync
```

## 2. Configuration
The server uses the `DATABASE_URL` from the `.env` file in the root directory. Update it with your RDS endpoint and credentials:
```env
DATABASE_URL="postgresql://[user]:[password]@[rds-endpoint]:5432/[dbname]"
```

## 3. Registering the Server
To use this server with an MCP client (e.g., Claude Desktop), add it to your configuration file.

### For Claude Desktop:
Edit your `claude_desktop_config.json` (usually found in `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "training-data": {
      "command": "D:/vishwak.rajgopalan/.local/bin/uv.exe",
      "args": [
        "run",
        "--project",
        "d:/vishwak.rajgopalan/projects/GithubProjects/genai-poc",
        "d:/vishwak.rajgopalan/projects/GithubProjects/genai-poc/src/mcp_server.py"
      ]
    }
  }
}
```

> [!TIP]
> Claude Desktop often requires the **absolute path** to the `uv` executable to start the server correctly. 

## 4. Running/Testing Locally
You can test if the server starts correctly by running:
```powershell
uv run src/mcp_server.py
```
It should start and wait for input (stdio transport).

## 5. Available Tools
The following tools are now available to your AI:
- `get_employee_summary`: Get overview of an employee.
- `get_employee_transcript`: Get full course history.
- `get_compliance_report`: Check if an employee is compliant.
- `search_courses`: Find courses in the catalog.
- `get_team_training_summary`: Get team-level stats.
- `search_employees`: Search for employees by name.
