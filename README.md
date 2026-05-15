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
- **Python 3.10+**
- **AWS Credentials** (configured with Bedrock and DynamoDB access)
- **PostgreSQL Database** (with the `training` schema populated)

### Installation

1. **Install dependencies** (using `uv`):
   ```bash
   uv sync
   ```

2. **Environment Configuration**:
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/trainingdb
   AWS_REGION=us-east-1
   MODEL_ID=anthropic.claude-3-5-sonnet-20240620-v1:0
   ```

### Running the Application

1. **Start the Dashboard**:
   ```bash
   uv run streamlit run ui/app.py
   ```
   *The app will automatically initialize the DynamoDB `FedCashChatHistory` table on its first run.*

2. **Standalone MCP Server** (for use with Claude Desktop):
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
