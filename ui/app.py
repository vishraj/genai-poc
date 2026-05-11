import streamlit as st
import pandas as pd
import plotly.express as px
import os
import sys
import json
import importlib
import re
from datetime import datetime

# ── Path Setup ────────────────────────────────────────────────────────────────
_here = os.path.dirname(os.path.abspath(__file__))
_src  = os.path.abspath(os.path.join(_here, "..", "src"))
if _src not in sys.path:
    sys.path.insert(0, _src)

# ── Imports ───────────────────────────────────────────────────────────────────
import services.ai_service as _ai_mod
import mcp_client as _mcp_mod
import services.history_service as _hist_mod

importlib.reload(_ai_mod)
importlib.reload(_mcp_mod)
importlib.reload(_hist_mod)

from services.ai_service import AIService
from mcp_client import UI_MCPClient
from services.history_service import HistoryService

# ── Service Init ──────────────────────────────────────────────────────────────
ai_service = AIService()
mcp_client = UI_MCPClient()
history_service = HistoryService()

# ── Session State Init ───────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "session_id" not in st.session_state:
    st.session_state.session_id = history_service.create_new_session_id()
if "current_title" not in st.session_state:
    st.session_state.current_title = "New Conversation"

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FedCash Training Intelligence",
    page_icon="📊",
    layout="wide",
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stMetric            { background:#1e293b; padding:20px; border-radius:12px; border:1px solid #334155; }
.query-header { font-size: 0.9rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 4px; margin-top: 24px; }
.query-text { font-size: 1.25rem; color: #f8fafc; font-weight: 600; margin-bottom: 20px; padding-bottom: 12px; border-bottom: 1px solid #334155; }
.insight-container { background: #0f172a; border-left: 4px solid #3b82f6; padding: 24px; border-radius: 0 12px 12px 0; margin: 16px 0 24px 0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }
.insight-label { font-size: 0.75rem; color: #3b82f6; text-transform: uppercase; font-weight: 700; letter-spacing: 0.1em; margin-bottom: 8px; }
.insight-content { font-size: 1.05rem; color: #cbd5e1; line-height: 1.6; }
div[data-testid="column"] button { display: flex; justify-content: center; align-items: center; margin: 0 auto; }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("💬 Chat History")
    if st.button("➕ New Conversation", use_container_width=True):
        st.session_state.history = []
        st.session_state.session_id = history_service.create_new_session_id()
        st.session_state.current_title = "New Conversation"
        st.rerun()
    st.divider()
    saved_sessions = history_service.list_sessions()
    for s in saved_sessions:
        sid, title = s['session_id'], s.get('title', 'Untitled')
        col_title, col_del = st.columns([0.8, 0.2])
        if col_title.button(f"📄 {title[:22]}...", key=f"load_{sid}", use_container_width=True):
            session_data = history_service.get_session(sid)
            if session_data:
                st.session_state.history = session_data.get('messages', [])
                st.session_state.session_id = sid
                st.session_state.current_title = title
                st.rerun()
        with col_del:
            if st.button("🗑️", key=f"del_{sid}"):
                history_service.delete_session(sid)
                if st.session_state.session_id == sid:
                    st.session_state.history = []
                    st.session_state.session_id = history_service.create_new_session_id()
                    st.session_state.current_title = "New Conversation"
                st.rerun()

# ── Header + KPI ──────────────────────────────────────────────────────────────
st.title("📊 Training Intelligence Dashboard")
st.caption(f"Strategy & Analysis Hub | Session: {st.session_state.current_title}")

stats_raw = mcp_client.run_tool_sync("get_dashboard_stats", {}) or {}
stats = {}
try:
    stats = json.loads(stats_raw) if isinstance(stats_raw, str) else stats_raw
except:
    stats = {}

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Workforce", stats.get("total_employees", 0))
c2.metric("Completions",     stats.get("completions",     0), delta=stats.get("completion_delta", "0%"))
c3.metric("Active Catalog",  stats.get("catalog_size",    0))
c4.metric("Risk Profile",    f"{stats.get('in_progress', 0)} Enrolled")

st.divider()

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_chat, tab_analytics, tab_compliance = st.tabs(["💬 AI Intelligence", "📈 Performance Trends", "🛡️ Compliance Registry"])

with tab_chat:
    st.subheader("Interactive Data Exploration")
    if st.session_state.history:
        for msg in st.session_state.history:
            if msg["role"] == "user":
                st.markdown(f'<div class="query-header">User Query</div><div class="query-text">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="insight-container"><div class="insight-label">AI Analysis & Insight</div><div class="insight-content">{msg["content"]}</div></div>', unsafe_allow_html=True)
                viz_data = msg.get("viz_data")
                if viz_data:
                    bullets = viz_data.get("summary", [])
                    if bullets:
                        cols = st.columns(len(bullets))
                        for col, pt in zip(cols, bullets): col.info(f"**{pt}**")
                    code = viz_data.get("code", "").strip()
                    if code:
                        try: exec(code)
                        except: pass

    query = st.chat_input("Ask about workforce training, compliance, or trends...")
    if query:
        if not st.session_state.history: st.session_state.current_title = query[:30]
        st.markdown(f'<div class="query-header">User Query</div><div class="query-text">{query}</div>', unsafe_allow_html=True)
        with st.status("Analyzing workforce data...", expanded=True) as status:
            routing_res = ai_service.route_query(query, history=st.session_state.history)
            
            # Check if router returned an error string instead of a list
            if isinstance(routing_res, str) and routing_res.startswith("Error"):
                status.update(label=routing_res, state="error", expanded=True)
                st.stop()
                
            tool_calls = routing_res
            # ── Tool Execution ───────────────────────────────────────────
            data_ctx: dict = {}
            ALLOWED_PARAMS = {
                "get_employee_summary": ["user_id"],
                "get_employee_transcript": ["user_id"],
                "get_compliance_report": ["user_id"],
                "search_courses": ["query_text"],
                "get_dashboard_stats": [],
                "get_completions_by_geography": ["level"],
                "get_mandatory_completion_rates": [],
                "get_completions_by_job_family": [],
                "get_team_training_summary": ["team_name"],
                "search_employees": ["name_query"],
                "search_employees_by_name": ["first_name", "last_name"]
            }

            for call in tool_calls:
                name, params = call.get("tool", ""), call.get("params", {})
                
                # Filter params to avoid "Extra inputs are not permitted"
                if name in ALLOWED_PARAMS:
                    allowed = ALLOWED_PARAMS[name]
                    params = {k: v for k, v in params.items() if k in allowed}
                
                res = mcp_client.run_tool_sync(name, params)
                if isinstance(res, str):
                    try: res = json.loads(res)
                    except: pass
                data_ctx[name] = res
                if name in ("search_employees", "search_employees_by_name") and res:
                    uid = res[0]["user_id"]
                    data_ctx["summary"]    = mcp_client.run_tool_sync("get_employee_summary",    {"user_id": uid})
                    data_ctx["transcript"] = mcp_client.run_tool_sync("get_employee_transcript", {"user_id": uid})
                    data_ctx["compliance"] = mcp_client.run_tool_sync("get_compliance_report",   {"user_id": uid})
            if data_ctx:
                clean_ctx = {k: v for k, v in data_ctx.items() if v is not None}
                viz = ai_service.generate_viz_logic(query, json.dumps(clean_ctx), history=st.session_state.history)
                st.markdown(f'<div class="insight-container"><div class="insight-label">AI Analysis & Insight</div><div class="insight-content">{viz.get("explanation", "")}</div></div>', unsafe_allow_html=True)
                bullets = viz.get("summary", [])
                if bullets:
                    cols = st.columns(len(bullets))
                    for col, pt in zip(cols, bullets): col.info(f"**{pt}**")
                code = viz.get("code", "").strip()
                if code:
                    if "```" in code: code = re.sub(r"```(?:python)?\s*(.*?)```", r"\1", code, flags=re.DOTALL).strip()
                    try: exec(code)
                    except: pass
                st.session_state.history.append({"role": "user", "content": query})
                st.session_state.history.append({"role": "assistant", "content": viz.get("explanation", ""), "viz_data": viz})
                history_service.save_session(st.session_state.session_id, st.session_state.current_title, st.session_state.history)
                status.update(label="Analysis complete ✅", state="complete", expanded=False)
                st.rerun()
            else:
                status.update(label="No records found", state="error", expanded=False)

with tab_analytics:
    st.subheader("Workforce Development Analytics")
    col_a, col_b = st.columns(2)
    with col_a:
        hist_df = pd.DataFrame({"Year": ["2021", "2022", "2023", "2024"], "Completions": [26, 37, 36, 45]})
        fig_line = px.line(hist_df, x="Year", y="Completions", markers=True, title="Annual Progress", template="plotly_dark")
        fig_line.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.8)")
        st.plotly_chart(fig_line, use_container_width=True)
    with col_b:
        geo_raw = mcp_client.run_tool_sync("get_completions_by_geography", {"level": "office"})
        geo_data = {}
        try: geo_data = json.loads(geo_raw) if isinstance(geo_raw, str) else (geo_raw or [])
        except: geo_data = []
        if geo_data:
            df_geo = pd.DataFrame(geo_data).head(10)
            fig_geo = px.bar(df_geo, x="completion_count", y="location", orientation="h", title="Top Performing Offices", template="plotly_dark")
            fig_geo.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.8)", margin=dict(l=200, r=100, t=80, b=50))
            st.plotly_chart(fig_geo, use_container_width=True)

with tab_compliance:
    st.subheader("Mandatory Training Oversight")
    comp_raw = mcp_client.run_tool_sync("get_mandatory_completion_rates", {})
    comp_data = {}
    try: comp_data = json.loads(comp_raw) if isinstance(comp_raw, str) else (comp_raw or [])
    except: comp_data = []
    if comp_data:
        df_comp = pd.DataFrame(comp_data)
        st.dataframe(df_comp, use_container_width=True, hide_index=True)

st.divider()
st.caption(f"System time: {datetime.now():%Y-%m-%d %H:%M:%S} | Persistence: DynamoDB")
