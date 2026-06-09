# 📊 Training Intelligence Dashboard (GenAI PoC)

A premium, protocol-compliant AI analytics platform designed for workforce training and compliance oversight. This Proof of Concept demonstrates a robust integration of **Model Context Protocol (MCP)**, **Amazon Bedrock**, and **AWS DynamoDB** within a professional Streamlit dashboard.

---

## 🚀 Key Features

- **MCP-Native Architecture**: Decoupled backend services exposed via the Model Context Protocol, ensuring scalability and standardized tool integration.
- **Generative Insights**: Natural language data exploration powered by Claude 4.6 Sonnet on Amazon Bedrock.
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

### 1. Prerequisites

Before starting, ensure you have the following installed and configured:
- **Python 3.13+**
- **uv package manager** (`pip install uv`)
- **Terraform** (to provision AWS resources)
- **AWS CLI** (configured with your AWS credentials)
- **pgAdmin** (to connect to and manage the RDS PostgreSQL database)

**AWS Configuration**:
Configure your AWS credentials using the AWS CLI so that Terraform and the application can access AWS resources:
```bash
aws configure
# Or using AWS SSO: aws sso login --profile <your_profile_name>
```

### 2. Infrastructure Provisioning with Terraform

Use Terraform to automatically provision the required AWS resources, such as DynamoDB tables and IAM roles.

1. Navigate to the terraform directory:
   ```bash
   cd terraform
   ```
2. Initialize Terraform:
   ```bash
   terraform init
   ```
3. Review the infrastructure plan:
   ```bash
   terraform plan
   ```
4. Apply the configuration to create the resources:
   ```bash
   terraform apply
   ```

### 3. Database Setup and Data Population using pgAdmin

Once your RDS PostgreSQL instance is created (either manually or via Terraform), you can connect to it and populate the initial data using **pgAdmin**.

1. **Connect to RDS using pgAdmin**:
   - Open **pgAdmin** and right-click on **Servers** -> **Register** -> **Server...**
   - **General Tab**: Name the server (e.g., `GenAI PoC RDS`).
   - **Connection Tab**: 
     - **Host name/address**: Your RDS Endpoint address.
     - **Port**: `5432`
     - **Maintenance database**: `postgres` (or your initial database name)
     - **Username**: Your master username.
     - **Password**: Your master password.
   - Click **Save**.

2. **Create the Required Schema and Tables**:
   - In pgAdmin, expand your newly registered server and databases. Right-click on your target database and select **Query Tool**.
   - Open the `sql/ddl/create_database_tables.sql` file from this repository, copy its contents, and paste it into the Query Tool.
   - Click the **Execute/Refresh** button (or press `F5`) to create the schema and tables.

3. **Populate the Data**:
   - You can use the provided PowerShell script (`load_database_data.ps1`) to load the CSV data, ensuring you update the connection variables in the script first.
   - Alternatively, you can use pgAdmin's **Import/Export Data** feature on each table to load the respective CSV files located in `sql/ddl/`.

### 4. Application Installation and Execution

1. **Clone and Install Dependencies**:
   Return to the root directory and synchronize the workspace using `uv`:
   ```bash
   cd ..
   uv sync
   ```

2. **Environment Configuration**:
   Create a `.env` file in the root directory. Include your AWS profile, database URL, and model configurations:
   ```env
   # PostgreSQL Connection String (RDS)
   DATABASE_URL="postgresql://<username>:<password>@<your-rds-endpoint>:5432/<database_name>"

   # Amazon Bedrock Configuration
   AWS_REGION=us-east-1
   MODEL_ID=global.anthropic.claude-sonnet-4-6
   AWS_PROFILE=default  # Update if using a different profile
   ```

3. **Start the Streamlit Dashboard**:
   From the project root directory, run:
   ```bash
   uv run streamlit run ui/app.py
   ```
   *Note: The app will automatically connect to DynamoDB and the PostgreSQL database based on your configuration.*

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
