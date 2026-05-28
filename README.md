# 📊 Training Intelligence Dashboard (GenAI PoC)

A premium, protocol-compliant AI analytics platform designed for workforce training and compliance oversight. This Proof of Concept demonstrates a robust integration of **Model Context Protocol (MCP)**, **Amazon Bedrock**, and **AWS DynamoDB** within a professional Streamlit dashboard.

---

## 🚀 Key Features

- **MCP-Native Architecture**: Decoupled backend services exposed via the Model Context Protocol, ensuring scalability and standardized tool integration.
- **Generative Insights**: Natural language data exploration powered by Claude 3.5 Sonnet on Amazon Bedrock.
- **Persistent Conversations**: Full chat history persistence using **AWS DynamoDB**, allowing users to save, load, and manage multiple analysis sessions.
- **Smart Name Resolution & Semantic Matching**: Automatic conversion of human names into internal identifiers, and intelligent query mapping that bridges the gap between natural language (e.g. "teams") and database schemas (e.g. "job families").
- **High-Performance UI**: Optimized Streamlit rendering using `@st.cache_resource` for service connections, `@st.cache_data` for heavy queries, batched form inputs, and `st.fragment` for instantaneous, localized chat updates without full-page reloads.
- **Executive Dashboards**: High-fidelity visualizations (Plotly) and executive summaries optimized for dark-mode professional environments.
- **Automated Compliance Analysis**: Real-time gap analysis for mandatory training curriculums across the workforce.

---

## 🏗️ Project Structure

```text
genai-poc/
├── src/
│   ├── mcp_server.py      # FastMCP Server (exposes tools)
│   ├── mcp_client.py      # Thread-safe UI Client for Streamlit
│   ├── services/
│   │   ├── ai_service.py      # Routing logic & Viz generation
│   │   ├── data_service.py    # PostgreSQL query engine & Name resolution
│   │   └── history_service.py # DynamoDB persistence layer
│   └── utils/             # AWS/Config utilities
├── ui/
│   └── app.py             # Streamlit Dashboard application
├── terraform/             # Cloud Infrastructure (DynamoDB, IAM)
└── sql/                   # DDL & Data Ingestion scripts
```

---

## 🛠️ Getting Started

### Prerequisites
- **Python 3.13+** (Required)
- **uv** package manager (`pip install uv`)
- **AWS CLI** (for AWS credential configuration)
- **PostgreSQL Client (`psql`)** (installed and added to your PATH to run database setup scripts)

### Installation & Configuration

1. **Clone and Install dependencies**:
   Ensure you have `uv` installed, then synchronize the workspace:
   ```bash
   uv sync
   ```

2. **AWS Keys & Credentials Setup**:
   The application requires access to Amazon Bedrock and AWS DynamoDB. Configure your AWS credentials using the AWS CLI:
   ```bash
   # Standard IAM credentials
   aws configure
   
   # Or using AWS SSO
   aws sso login --profile <your_profile_name>
   ```

3. **Environment Configuration**:
   Create a `.env` file in the root directory of the project. Include your AWS profile, database URL, and model configurations:
   ```env
   # PostgreSQL Connection String (RDS)
   DATABASE_URL="postgresql://postgres:vGbD6l2k4KuI8n7Gq7wb@learningdb.cxe8g06806dj.us-east-1.rds.amazonaws.com:5432/trainingdb"

   # Amazon Bedrock Configuration
   AWS_REGION=us-east-1
   MODEL_ID=global.anthropic.claude-sonnet-4-6
   AWS_PROFILE=sso_profile  # Remove or change this if using a different profile/default credentials
   ```

### Database Setup (RDS PostgreSQL)

All the required files for the RDS PostgreSQL setup are located in the `sql/ddl` folder. Follow these steps to initialize the database:

1. **Navigate to the DDL directory**:
   ```bash
   cd sql/ddl
   ```

2. **Create the Schema and Tables**:
   Run the SQL script using your `psql` client to create the `training` schema and required tables (`employee_fact`, `catalog_fact`, `curriculum_fact`, `transcript_fact`):
   ```bash
   psql -h learningdb.cxe8g06806dj.us-east-1.rds.amazonaws.com -p 5432 -U postgres -d trainingdb -f create_database_tables.sql
   ```
   *(You will be prompted for the database password).*

3. **Load Synthetic Data**:
   A PowerShell script is provided to efficiently load the CSV data into your RDS instance using `psql \copy`.
   ```powershell
   .\load_database_data.ps1
   ```
   This will populate the database with synthetic employees, course catalogs, and training transcripts.

### Running the Application

1. **Start the Streamlit Dashboard**:
   From the project root directory, run:
   ```bash
   uv run streamlit run ui/app.py
   ```
   *Note: The app will automatically initialize the DynamoDB `FedCashChatHistory` table on its first run to store conversation history.*

2. **Standalone MCP Server** (Optional, for use with Claude Desktop):
   ```bash
   uv run python src/mcp_server.py
   ```

---

## 🧪 Technology Stack

- **Frontend**: Streamlit (Dashboard & Chat Interface)
- **AI Backend**: Amazon Bedrock (Claude 4.6 Sonnet)
- **Database**: PostgreSQL (Structured Data), AWS DynamoDB (Chat History)
- **Communication**: Model Context Protocol (MCP) via FastMCP
- **Visualization**: Plotly Express (Professional Dark Theme)

---

## 🛡️ Compliance & Safety

This PoC uses a restrictive `exec()` pattern for AI-generated charts, isolated within the UI layer. For production environments, it is recommended to transition to a structured chart-config JSON approach or a sandboxed execution environment.
