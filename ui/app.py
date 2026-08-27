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
@st.cache_resource
def get_services():
    return AIService(), UI_MCPClient(), HistoryService()

ai_service, mcp_client, history_service = get_services()

# ── Session State Init ───────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "role" not in st.session_state:
    st.session_state.role = "Guest"
if "office" not in st.session_state:
    st.session_state.office = None

if "history" not in st.session_state:
    st.session_state.history = []
if "session_id" not in st.session_state:
    st.session_state.session_id = history_service.create_new_session_id()
if "current_title" not in st.session_state:
    st.session_state.current_title = "New Conversation"
if "model_choice" not in st.session_state:
    st.session_state.model_choice = "Claude Sonnet 4.6"
if "temperature" not in st.session_state:
    st.session_state.temperature = 0.0
if "top_p" not in st.session_state:
    st.session_state.top_p = 0.9
if "top_k" not in st.session_state:
    st.session_state.top_k = 250
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FedCash Skills Navigator",
    page_icon="🧭",
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
.user-card { background: #0f172a; border: 1px solid #334155; padding: 14px; border-radius: 10px; margin-bottom: 16px; }
.role-badge { display: inline-block; padding: 4px 10px; font-size: 0.75rem; font-weight: 700; border-radius: 6px; text-transform: uppercase; margin-top: 4px; }
.badge-officer { background: #1e3a8a; color: #93c5fd; border: 1px solid #3b82f6; }
.badge-admin { background: #065f46; color: #a7f3d0; border: 1px solid #10b981; }
.badge-emp { background: #7c2d12; color: #fdba74; border: 1px solid #f97316; }
.badge-guest { background: #334155; color: #cbd5e1; border: 1px solid #475569; }
div[data-testid="column"] button { display: flex; justify-content: center; align-items: center; margin: 0 auto; }
div[data-testid="InputInstructions"], small[data-testid="stInputInstruction"], .stForm [data-testid="stInputInstruction"], [data-testid="stFormInstructions"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

import bcrypt

AUTH_FILE = os.path.abspath(os.path.join(_here, "..", "config", "users_auth.json"))

def load_users_auth():
    if os.path.exists(AUTH_FILE):
        try:
            with open(AUTH_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def verify_user_credentials(user_id: str, plain_password: str):
    clean_id = user_id.strip().upper()
    auth_data = load_users_auth()
    
    if clean_id not in auth_data:
        return False, f"User ID '{clean_id}' not found."
    
    stored_hash = auth_data[clean_id].get("password_hash", "")
    if not stored_hash:
        return False, "Password credentials missing for user."
    
    try:
        if bcrypt.checkpw(plain_password.encode('utf-8'), stored_hash.encode('utf-8')):
            return True, "Success"
        else:
            return False, "Incorrect password."
    except Exception as e:
        return False, f"Verification failed: {e}"

# ── User Resolution & Auth Helper ──────────────────────────────────────────────
DEMO_USERS = {
    "OFF001": {
        "user_id": "OFF001",
        "first_name": "Alex",
        "last_name": "Officer",
        "job_family": "Officer",
        "office_name": "San Francisco",
        "department_name": "Training & Development",
        "email_address": "alex.officer@example.com"
    },
    "LAD001": {
        "user_id": "LAD001",
        "first_name": "Marcus",
        "last_name": "Vance",
        "job_family": "Learning Admin",
        "office_name": "Los Angeles",
        "department_name": "Cash Operations",
        "email_address": "marcus.vance@example.com"
    },
    "EMP001": {
        "user_id": "EMP001",
        "first_name": "Evan",
        "last_name": "Park",
        "job_family": "Cash Handler",
        "office_name": "Los Angeles",
        "department_name": "Cash Operations",
        "email_address": "evan.park@example.com"
    }
}

def resolve_user(uid: str):
    clean_id = uid.strip().upper()
    try:
        raw_res = mcp_client.run_tool_sync("get_employee_summary", {"user_id": clean_id})
        res = json.loads(raw_res) if isinstance(raw_res, str) else raw_res
        if res and isinstance(res, dict) and "user_id" in res:
            return res
    except Exception:
        pass
    
    if clean_id in DEMO_USERS:
        return DEMO_USERS[clean_id]
    return None

# ── Logged In Session Details ─────────────────────────────────────────────────
curr_user = st.session_state.current_user or {}
role = st.session_state.role
user_id = curr_user.get("user_id", "")
first_name = curr_user.get("first_name", "")
last_name = curr_user.get("last_name", "")
office_name = curr_user.get("office_name", "")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🔐 User Authentication")
    
    if st.session_state.authenticated:
        if role == "Officer":
            badge_class, badge_text = "badge-officer", "🛡️ Officer (All 5 Cities)"
        elif role == "Learning Admin":
            badge_class, badge_text = "badge-admin", f"📊 Learning Admin ({office_name})"
        else:
            badge_class, badge_text = "badge-emp", "👤 Employee (Self Scope)"

        st.markdown(f"""
        <div class="user-card">
            <div style="font-weight: 700; font-size: 1.1rem; color: #f8fafc;">👤 {first_name} {last_name}</div>
            <div style="color: #94a3b8; font-size: 0.85rem;">ID: {user_id} | Office: {office_name}</div>
            <div class="role-badge {badge_class}">{badge_text}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.current_user = None
            st.session_state.role = "Guest"
            st.session_state.office = None
            st.session_state.history = []
            st.session_state.session_id = history_service.create_new_session_id()
            st.session_state.current_title = "New Conversation"
            st.rerun()
    else:
        st.caption("Enter your credentials to log in:")
        with st.form("sidebar_login_form"):
            user_input = st.text_input("🔑 User ID / Username", placeholder="e.g. OFF001, LAD001, EMP001")
            pass_input = st.text_input("🔒 Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Log In ➔", use_container_width=True)
            if submitted:
                if not user_input:
                    st.error("Please enter a User ID.")
                elif not pass_input:
                    st.error("Please enter a Password.")
                else:
                    valid, msg = verify_user_credentials(user_input, pass_input)
                    if valid:
                        user_info = resolve_user(user_input)
                        if user_info:
                            st.session_state.authenticated = True
                            st.session_state.current_user = user_info
                            st.session_state.role = user_info.get("job_family", "Employee")
                            st.session_state.office = user_info.get("office_name", "Unknown")
                            st.session_state.history = []
                            st.session_state.session_id = history_service.create_new_session_id()
                            st.session_state.current_title = "New Conversation"
                            st.rerun()
                        else:
                            st.error("User profile could not be retrieved.")
                    else:
                        st.error(f"⚠️ {msg}")

    st.divider()

    st.header("Navigation")
    if st.button("📊 Summary Statistics", use_container_width=True):
        st.session_state.current_page = "Dashboard"
        st.rerun()

    if st.button("➕ New Conversation", use_container_width=True):
        st.session_state.history = []
        st.session_state.session_id = history_service.create_new_session_id()
        st.session_state.current_title = "New Conversation"
        st.session_state.current_page = "Chat"
        st.rerun()

    st.divider()
    
    st.title("💬 Chat History")
    saved_sessions = history_service.list_sessions(user_id=user_id if st.session_state.authenticated else "")
    for s in saved_sessions:
        sid, title = s['session_id'], s.get('title', 'Untitled')
        col_title, col_del = st.columns([0.8, 0.2])
        if col_title.button(f"📄 {title[:22]}...", key=f"load_{sid}", use_container_width=True):
            session_data = history_service.get_session(sid, user_id=user_id if st.session_state.authenticated else "")
            if session_data:
                st.session_state.history = session_data.get('messages', [])
                st.session_state.session_id = sid
                st.session_state.current_title = title
                st.session_state.current_page = "Chat"
                st.rerun()
        with col_del:
            if st.button("🗑️", key=f"del_{sid}"):
                history_service.delete_session(sid)
                if st.session_state.session_id == sid:
                    st.session_state.history = []
                    st.session_state.session_id = history_service.create_new_session_id()
                    st.session_state.current_title = "New Conversation"
                    st.session_state.current_page = "Dashboard"
                st.rerun()

    st.divider()

    with st.expander("⚙️ Model Settings"):
        with st.form("model_settings_form"):
            model_options = ["Claude Sonnet 4.6", "Claude Opus 4.7"]
            model_ids = {
                "Claude Sonnet 4.6": "global.anthropic.claude-sonnet-4-6",
                "Claude Opus 4.7": "global.anthropic.claude-opus-4-7"
            }
            try:
                default_index = model_options.index(st.session_state.model_choice)
            except ValueError:
                default_index = 0
                
            new_model_choice = st.selectbox("Model", model_options, index=default_index)
            new_temperature = st.slider("Temperature", 0.0, 1.0, float(st.session_state.temperature), 0.1)
            new_top_p = st.slider("Top P", 0.0, 1.0, float(st.session_state.top_p), 0.05)
            new_top_k = st.number_input("Top K", 1, 500, int(st.session_state.top_k), 10)

            if st.form_submit_button("Apply Settings"):
                st.session_state.model_choice = new_model_choice
                st.session_state.temperature = new_temperature
                st.session_state.top_p = new_top_p
                st.session_state.top_k = new_top_k
                st.rerun()

# Apply settings to ai_service
ai_service.set_model(model_ids.get(st.session_state.model_choice, "global.anthropic.claude-sonnet-4-6"))
ai_service.temperature = st.session_state.temperature
ai_service.top_p = st.session_state.top_p
ai_service.top_k = st.session_state.top_k

@st.cache_data(ttl=300)
def fetch_dashboard_stats():
    stats_raw = mcp_client.run_tool_sync("get_dashboard_stats", {}) or {}
    try:
        return json.loads(stats_raw) if isinstance(stats_raw, str) else stats_raw
    except:
        return {}

@st.fragment
def render_chat():
    if not st.session_state.authenticated:
        st.warning("🔒 Please log in via the sidebar using your User ID (e.g., OFF001, LAD001, or EMP001) to use the AI Chat Navigator.")
        return

    if st.session_state.history:
        for msg in st.session_state.history:
            if msg["role"] == "user":
                st.markdown(f'<div class="query-header">User Query</div><div class="query-text">{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                formatted_msg = re.sub(r'\*{2,}([^*]+)\*{2,}', r'<b>\1</b>', msg["content"])
                st.markdown(f'<div class="insight-container"><div class="insight-label">AI Analysis & Insight</div><div class="insight-content">{formatted_msg}</div></div>', unsafe_allow_html=True)
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

    if role == "Officer":
        placeholder = "Ask about workforce training across all 5 cities..."
    elif role == "Learning Admin":
        placeholder = f"Ask about workforce training in {office_name}..."
    else:
        placeholder = f"Ask about your personal courses, completion rates, or compliance..."

    query = st.chat_input(placeholder)
    if query:
        banned_words = ["fuck", "shit", "bitch", "asshole", "stupid", "idiot", "hack", "drop table", "dumb"]
        query_lower = query.lower()
        if any(bad_word in query_lower for bad_word in banned_words):
            st.error("⚠️ Query blocked: Your request contains inappropriate or out-of-scope language.")
            return

        if not st.session_state.history: 
            st.session_state.current_title = query[:30]
        st.markdown(f'<div class="query-header">User Query</div><div class="query-text">{query}</div>', unsafe_allow_html=True)
        with st.status("Analyzing workforce data...", expanded=True) as status:
            scoped_query = query
            if role == "Learning Admin":
                scoped_query += f" (Note: User is Learning Admin for office '{office_name}')"
            elif role not in ("Officer", "Learning Admin"):
                scoped_query += f" (Note: Query for employee '{user_id}' only)"

            routing_res = ai_service.route_query(scoped_query, history=st.session_state.history)
            
            if isinstance(routing_res, str) and routing_res.startswith("Error"):
                status.update(label=routing_res, state="error", expanded=True)
                st.stop()
                
            tool_calls = routing_res
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
                "search_employees_by_name": ["first_name", "last_name"],
                "get_mandatory_completions_by_geography": ["level"],
                "get_mandatory_completions_by_job_family": []
            }

            for call in tool_calls:
                name, params = call.get("tool", ""), call.get("params", {})
                if name in ALLOWED_PARAMS:
                    allowed = ALLOWED_PARAMS[name]
                    params = {k: v for k, v in params.items() if k in allowed}
                
                # ── RBAC Guard: Employee Role (Self Scope Only) ────────────────
                if role not in ("Officer", "Learning Admin"):
                    # Block employee lookups, team summaries, or multi-user lists for regular employees
                    if name in ("search_employees", "search_employees_by_name", "get_team_training_summary", "get_mandatory_completion_rates", "get_completions_by_geography", "get_mandatory_completions_by_geography"):
                        data_ctx["access_denied"] = f"Access Denied: As an Employee ({user_id}), you are only authorized to access your own course transcript and compliance data. Access to other employees' records or office analytics is restricted."
                        continue
                    # Force user_id to logged-in employee for transcript/summary/compliance tools
                    if name in ("get_employee_summary", "get_employee_transcript", "get_compliance_report"):
                        params["user_id"] = user_id

                # ── RBAC Guard: Learning Admin Role (Assigned Office Scope Only) ──
                elif role == "Learning Admin":
                    if name == "get_mandatory_completion_rates":
                        res_raw = mcp_client.run_tool_sync(name, params)
                        try:
                            parsed_res = json.loads(res_raw) if isinstance(res_raw, str) else res_raw
                            if isinstance(parsed_res, list):
                                parsed_res = [r for r in parsed_res if r.get("office_name") == office_name]
                            data_ctx[name] = parsed_res
                        except Exception:
                            data_ctx[name] = res_raw
                        continue

                res = mcp_client.run_tool_sync(name, params)
                if isinstance(res, str):
                    try: res = json.loads(res)
                    except: pass
                data_ctx[name] = res

                # Ensure secondary searches obey RBAC boundaries
                if name in ("search_employees", "search_employees_by_name") and res:
                    if isinstance(res, list) and len(res) > 0 and isinstance(res[0], dict) and "user_id" in res[0]:
                        target_uid = res[0]["user_id"]
                        target_office = res[0].get("office_name", "")
                        if role == "Officer" or (role == "Learning Admin" and target_office == office_name) or target_uid == user_id:
                            data_ctx["summary"]    = mcp_client.run_tool_sync("get_employee_summary",    {"user_id": target_uid})
                            data_ctx["transcript"] = mcp_client.run_tool_sync("get_employee_transcript", {"user_id": target_uid})
                            data_ctx["compliance"] = mcp_client.run_tool_sync("get_compliance_report",   {"user_id": target_uid})
                        else:
                            data_ctx.pop(name, None)
                            data_ctx["access_denied"] = f"Access Denied: You do not have authorization to view training records for employee '{target_uid}' in office '{target_office}'."

            if data_ctx:
                clean_ctx = {k: v for k, v in data_ctx.items() if v is not None}
                viz = ai_service.generate_viz_logic(query, json.dumps(clean_ctx), history=st.session_state.history)
                formatted_viz = re.sub(r'\*{2,}([^*]+)\*{2,}', r'<b>\1</b>', viz.get("explanation", ""))
                st.markdown(f'<div class="insight-container"><div class="insight-label">AI Analysis & Insight</div><div class="insight-content">{formatted_viz}</div></div>', unsafe_allow_html=True)
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
                history_service.save_session(st.session_state.session_id, st.session_state.current_title, st.session_state.history, user_id=user_id if st.session_state.authenticated else "")
                status.update(label="Analysis complete ✅", state="complete", expanded=False)
                st.rerun()
            else:
                status.update(label="No records found", state="error", expanded=False)

st.warning("⚠️ **Disclaimer:** All data presented in this application is mock data generated for demonstration purposes.")

if st.session_state.current_page == "Dashboard":
    st.title("🧭 FedCash Skills Navigator")
    
    # ── Default / Public & Officer View: System-Wide Dashboard ───────────────────
    if role in ("Officer", "Guest"):
        st.caption("Strategy & Analysis Hub | High-Level KPIs")
        stats = fetch_dashboard_stats()
        c1, c2 = st.columns(2)
        c1.metric("Total Workforce", stats.get("total_employees", 100))
        c2.metric("Active Catalog",  stats.get("catalog_size",    10))

        st.divider()
        st.header("Summary Statistics")
        
        geo_raw = mcp_client.run_tool_sync("get_completions_by_geography", {"level": "office"})
        geo_data = json.loads(geo_raw) if isinstance(geo_raw, str) else (geo_raw or [])
        
        jf_raw = mcp_client.run_tool_sync("get_completions_by_job_family", {})
        jf_data = json.loads(jf_raw) if isinstance(jf_raw, str) else (jf_raw or [])

        mgeo_raw = mcp_client.run_tool_sync("get_mandatory_completions_by_geography", {"level": "office"})
        mgeo_data = json.loads(mgeo_raw) if isinstance(mgeo_raw, str) else (mgeo_raw or [])

        mjf_raw = mcp_client.run_tool_sync("get_mandatory_completions_by_job_family", {})
        mjf_data = json.loads(mjf_raw) if isinstance(mjf_raw, str) else (mjf_raw or [])

        c_chart1, c_chart2 = st.columns(2)
        with c_chart1:
            if geo_data:
                df_geo = pd.DataFrame(geo_data)
                fig_geo = px.pie(df_geo, values="completion_count", names="location", title="Course Completions by Office", template="plotly_dark")
                fig_geo.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.8)", margin=dict(l=20, r=20, t=50, b=50))
                st.plotly_chart(fig_geo, use_container_width=True)
                
            if mgeo_data:
                df_mgeo = pd.DataFrame(mgeo_data)
                fig_mgeo = px.pie(df_mgeo, values="completion_count", names="location", title="Mandatory Completions by Office", template="plotly_dark")
                fig_mgeo.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.8)", margin=dict(l=20, r=20, t=50, b=50))
                st.plotly_chart(fig_mgeo, use_container_width=True)

        with c_chart2:
            if jf_data:
                df_jf = pd.DataFrame(jf_data)
                fig_jf = px.pie(df_jf, values="completion_count", names="job_family", title="Course Completions by Job Family", template="plotly_dark")
                fig_jf.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.8)", margin=dict(l=20, r=20, t=50, b=50))
                st.plotly_chart(fig_jf, use_container_width=True)

            if mjf_data:
                df_mjf = pd.DataFrame(mjf_data)
                fig_mjf = px.pie(df_mjf, values="completion_count", names="job_family", title="Mandatory Completions by Job Family", template="plotly_dark")
                fig_mjf.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,23,42,0.8)", margin=dict(l=20, r=20, t=50, b=50))
                st.plotly_chart(fig_mjf, use_container_width=True)

        st.divider()
        st.header("🛡️ Compliance Registry")
        comp_raw = mcp_client.run_tool_sync("get_mandatory_completion_rates", {})
        comp_data = json.loads(comp_raw) if isinstance(comp_raw, str) else (comp_raw or [])
        if comp_data:
            df_comp = pd.DataFrame(comp_data)
            st.dataframe(df_comp, use_container_width=True, hide_index=True)

    elif role == "Learning Admin":
        st.caption(f"Office Management Hub | {office_name} Office Scope")
        
        comp_raw = mcp_client.run_tool_sync("get_mandatory_completion_rates", {})
        comp_data = json.loads(comp_raw) if isinstance(comp_raw, str) else (comp_raw or [])
        
        office_comp = [r for r in comp_data if r.get("office_name") == office_name] if isinstance(comp_data, list) else []
        
        c1, c2, c3 = st.columns(3)
        c1.metric(f"Workforce ({office_name})", len(office_comp) if office_comp else 20)
        c2.metric("Active Office Catalog", 10)
        avg_rate = round(sum(r.get("completion_rate", 0) for r in office_comp) / len(office_comp), 1) if office_comp else 85.0
        c3.metric("Avg Office Compliance Rate", f"{avg_rate}%")

        st.divider()
        st.header(f"🛡️ {office_name} Compliance Registry")
        if office_comp:
            df_office_comp = pd.DataFrame(office_comp)
            st.dataframe(df_office_comp, use_container_width=True, hide_index=True)

    else:
        # Employee Self Portal
        st.caption(f"Personal Learning Portal | {first_name} {last_name} ({user_id})")
        
        emp_summary_raw = mcp_client.run_tool_sync("get_employee_summary", {"user_id": user_id})
        emp_summary = json.loads(emp_summary_raw) if isinstance(emp_summary_raw, str) else (emp_summary_raw or {})
        
        emp_comp_raw = mcp_client.run_tool_sync("get_compliance_report", {"user_id": user_id})
        emp_comp = json.loads(emp_comp_raw) if isinstance(emp_comp_raw, str) else (emp_comp_raw or {})
        
        emp_trans_raw = mcp_client.run_tool_sync("get_employee_transcript", {"user_id": user_id})
        emp_trans = json.loads(emp_trans_raw) if isinstance(emp_trans_raw, str) else (emp_trans_raw or [])

        c1, c2, c3 = st.columns(3)
        c1.metric("Completed Courses", emp_summary.get("completed_count", 2))
        c2.metric("Active Enrollments", emp_summary.get("enrolled_count", 1))
        c3.metric("Mandatory Compliance Rate", f"{emp_comp.get('completion_rate', 100.0)}%")

        st.divider()
        st.header("📄 My Course Transcripts")
        if emp_trans:
            df_trans = pd.DataFrame(emp_trans)
            st.dataframe(df_trans, use_container_width=True, hide_index=True)

        st.divider()
        st.header("🎯 Required Curriculum Breakdown")
        full_report = emp_comp.get("full_report", [])
        if full_report:
            df_rep = pd.DataFrame(full_report)
            st.dataframe(df_rep, use_container_width=True, hide_index=True)

elif st.session_state.current_page == "Chat":
    st.title("💬 Skills Navigator AI Chat")
    if st.session_state.authenticated:
        st.caption(f"Session: {st.session_state.current_title} | Logged in as: {first_name} {last_name} ({role})")
    else:
        st.caption("Public AI Navigator")
    render_chat()
