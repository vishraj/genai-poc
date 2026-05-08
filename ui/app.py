import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import sys
import json
from datetime import datetime

# Add the src/ui directory to the path so we can import services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from services.ai_service import AIService
from mcp_client import UI_MCPClient

# Initialize Services
mcp_client = UI_MCPClient()
ai_service = AIService()

# --- Page Configuration ---
st.set_page_config(
    page_title="FedCash Training | Pure MCP",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Premium Look ---
st.markdown("""
    <style>
    .main {
        background-color: transparent;
    }
    [data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 12px;
    }
    .stSidebar {
        background-color: #1e293b;
    }
    .stSidebar [data-testid="stMarkdownContainer"] p {
        color: #cbd5e1;
    }
    .stButton>button {
        background-color: #3b82f6;
        color: white;
        border-radius: 8px;
        border: none;
        padding: 10px 24px;
    }
    .stTextInput>div>div>input {
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.image("https://www.federalreserve.gov/images/fed-logo-small.png", width=100)
    st.title("Admin Console")
    st.markdown("---")
    
    st.subheader("Protocol Status")
    st.success("Mode: Pure MCP (Host)")
    st.info("The UI is communicating with the backend via formal MCP CallTool requests.")

# --- Header ---
st.title("📊 Training Intelligence Dashboard")
st.markdown("#### Real-time insights powered by Model Context Protocol (MCP)")

# --- Key Metrics Row ---
col1, col2, col3, col4 = st.columns(4)

# Fetch stats via MCP Tool
with st.spinner("Fetching protocol stats..."):
    stats = mcp_client.run_tool_sync("get_dashboard_stats", {})
    if isinstance(stats, str): # Handle string response from MCP
        import ast
        stats = ast.literal_eval(stats)
    
    if not stats:
        stats = {"total_employees": 0, "completions": 0, "catalog_size": 0, "in_progress": 0}

with col1:
    st.metric("Total Employees", stats.get("total_employees", 0))
with col2:
    st.metric("Course Completions", stats.get("completions", 0), delta="12% vs last month")
with col3:
    st.metric("Catalog Size", stats.get("catalog_size", 0))
with col4:
    st.metric("In-Progress", stats.get("in_progress", 0), delta="-5%", delta_color="inverse")

st.markdown("---")

# --- Tabbed Interface ---
tab1, tab2, tab3 = st.tabs(["💬 AI Insights", "📈 Visual Analytics", "🛡️ Compliance Registry"])

# --- Tab 1: AI Insights (LLM Generated Viz) ---
with tab1:
    st.header("Ask your Data")
    st.markdown("Enter a natural language query below. Claude will route your request through the **MCP Server**.")
    
    query = st.text_input("Example: 'Show me completion rates by job family' or 'Show me the transcript for James Baker'", 
                         placeholder="Type your request here...")
    
    if query:
        st.info(f"AI is routing query: '{query}'...")
        
        # 1. Determine data context based on query (AGENTIC ROUTING via MCP)
        with st.spinner("Analyzing query intent..."):
            tool_calls = ai_service.route_query(query)
            
        data_context_map = {}
        if tool_calls:
            st.caption(f"AI decided to use MCP tools: {', '.join([c.get('tool') for c in tool_calls])}")
            
        for call in tool_calls:
            tool_name = str(call.get('tool')).strip()
            params = call.get('params', {})
            
            try:
                # CALL THE TOOL VIA MCP
                result = mcp_client.run_tool_sync(tool_name, params)
                
                # Convert string result (from mcp server) back to list/dict for context
                if isinstance(result, str) and result.startswith("["):
                    import ast
                    result = ast.literal_eval(result)
                
                data_context_map[tool_name] = result
                
                # Special Case: If we found employees, automatically get transcripts too
                if tool_name == "search_employees" and result:
                    user_id = result[0]['user_id']
                    st.caption(f"MCP discovered employee: {result[0].get('first_name')} {result[0].get('last_name')} ({user_id})")
                    data_context_map["transcript"] = mcp_client.run_tool_sync("get_employee_transcript", {"user_id": user_id})
                    data_context_map["compliance"] = mcp_client.run_tool_sync("get_compliance_report", {"user_id": user_id})

            except Exception as e:
                st.error(f"MCP Tool Execution Error ({tool_name}): {e}")

        data_context = json.dumps(data_context_map) if data_context_map else ""
        
        # 2. Call AI Service to generate visualization
        if data_context and data_context != "{}":
            with st.spinner("Generating visualization via Amazon Bedrock..."):
                response = ai_service.generate_viz_logic(query, data_context)
                
                st.subheader("AI Insight")
                st.write(response.get('explanation', 'No explanation provided.'))
                
                summary = response.get('summary', [])
                if summary:
                    for point in summary:
                        st.markdown(f"* {point}")
                
                # Execute the generated code
                try:
                    code = response.get('code', '').strip()
                    if code:
                        if code.startswith("```python"): code = code[9:]
                        if code.startswith("```"): code = code[3:]
                        if code.endswith("```"): code = code[:-3]
                        st.markdown("---")
                        exec(code.strip())
                except Exception as e:
                    st.error(f"Failed to render visualization: {e}")
                    st.code(code)
        else:
            st.warning("The MCP server returned no data for this query.")

# --- Tab 2: Visual Analytics ---
with tab2:
    st.header("Analytics Overview")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Completion Trends")
        yearly_data = {'Year': ['2020', '2021', '2022', '2023', '2024'], 'Completions': [23, 26, 37, 36, 45]}
        df_yearly = pd.DataFrame(yearly_data)
        fig_line = px.line(df_yearly, x='Year', y='Completions', markers=True, title="Annual Completion Volume")
        st.plotly_chart(fig_line, use_container_width=True)
        
    with c2:
        st.subheader("Office Performance")
        geo_data_str = mcp_client.run_tool_sync("get_completions_by_geography", {"level": "office"})
        import ast
        geo_data = ast.literal_eval(geo_data_str) if isinstance(geo_data_str, str) else []
        df_geo = pd.DataFrame(geo_data).head(10)
        if not df_geo.empty:
            fig_geo = px.bar(df_geo, x='completion_count', y='location', orientation='h',
                             title="Top 10 Offices by Completion", color='completion_count')
            st.plotly_chart(fig_geo, use_container_width=True)

# --- Tab 3: Compliance Registry ---
with tab3:
    st.header("Mandatory Training Compliance")
    
    data_str = mcp_client.run_tool_sync("get_mandatory_completion_rates", {})
    import ast
    data = ast.literal_eval(data_str) if isinstance(data_str, str) else []
    df_comp = pd.DataFrame(data)
    
    if not df_comp.empty:
        non_compliant = df_comp[df_comp['completion_rate'] < 100]
        st.warning(f"Found {len(non_compliant)} employees with incomplete mandatory training.")
        st.dataframe(df_comp, use_container_width=True, hide_index=True)

# --- Footer ---
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Architecture: Pure MCP Host")
