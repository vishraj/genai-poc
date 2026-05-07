# Gen AI POC

A Proof of Concept project exploring Generative AI capabilities.

## Project Structure

```
genai-poc/
├── src/            # Backend source code (Python, API logic, AI integrations)
├── ui/             # Streamlit frontend application
├── terraform/      # Infrastructure-as-Code for cloud resources
└── sql/            # SQL scripts for database setup and queries
```

## Getting Started

### Prerequisites
- Python 3.10+
- Terraform CLI
- AWS CLI (or relevant cloud provider CLI)

### Setup

1. **Install uv** (if not already installed)
   Follow instructions at [astral.sh/uv](https://astral.sh/uv).

2. **Install Dependencies**
   ```bash
   uv sync
   ```

3. **Run UI (Streamlit)**
   ```bash
   uv run streamlit run ui/app.py
   ```

3. **Infrastructure**
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

4. **Database**
    - Run scripts in `sql/` in the order indicated by their filename prefix.

## MCP Server
This project exposes its data services via a Model Context Protocol (MCP) server. 

### To run the MCP server:
```bash
uv run src/mcp_server.py
```

See [mcp_walkthrough.md](./mcp_walkthrough.md) for detailed configuration instructions for Claude Desktop and other MCP clients.

