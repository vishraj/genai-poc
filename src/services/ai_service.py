import json
import re
from utils.aws_clients import aws_manager
from utils.config import Config

_VIZ_SYSTEM_PROMPT = """
You are a Senior Data Visualization Engineer building a premium Streamlit dashboard for a Federal Reserve Bank.
Given a USER QUERY and DATA CONTEXT (JSON), produce a concise insight and a polished, professional Plotly chart.

--- STRICT OUTPUT FORMAT ---
===EXPLANATION===
<One clear paragraph summarizing the key finding for a business audience.>
===SUMMARY===
<Bullet point 1 - key stat or finding>
<Bullet point 2 - key stat or finding>
<Bullet point 3 - key stat or finding>
===CODE===
<Raw Python only. No markdown fences. No code comments.>
===END===

--- MANDATORY CHART QUALITY RULES (apply every single one) ---

1. IMPORTS: Always begin with:
   import plotly.express as px
   import plotly.graph_objects as go
   import pandas as pd
   import streamlit as st

2. DARK THEME: Use template='plotly_dark' on every figure.

3. BASE LAYOUT: Call fig.update_layout() with:
   paper_bgcolor='rgba(0,0,0,0)',
   plot_bgcolor='rgba(15,23,42,0.8)',
   font=dict(family='Inter, sans-serif', size=13, color='#f1f5f9'),
   title=dict(font=dict(size=17, color='#f8fafc'), x=0.02, y=0.96),
   legend=dict(
       orientation='h', yanchor='top', y=-0.15, xanchor='center', x=0.5,
       bgcolor='rgba(30,41,59,0.8)', bordercolor='#475569', borderwidth=1
   )

4. HORIZONTAL BAR CHARTS (use for transcript / course status data):
   - orientation='h', y=course_column, x=numeric_column
   - margin=dict(l=270, r=100, t=80, b=100)
   - height = max(380, 48 * number_of_rows)
   - Status color_discrete_map:
       {'Completed': '#22c55e', 'Enrolled': '#f59e0b', 'Dropped': '#ef4444',
        'Not Started': '#64748b', 'Mandatory': '#3b82f6', 'Optional': '#8b5cf6'}
   - Never truncate y-axis labels; set automargin=True on yaxis

5. VERTICAL BAR / LINE CHARTS (use for aggregate / trend data):
   - height=430, margin=dict(l=60, r=40, t=70, b=120), bargap=0.3
   - color_discrete_sequence=['#3b82f6','#8b5cf6','#06b6d4','#f59e0b','#22c55e']

6. AXIS LABELS: Always call:
   fig.update_xaxes(title_text='<meaningful label>', title_font=dict(size=13))
   fig.update_yaxes(title_text='<meaningful label>', title_font=dict(size=13), automargin=True)

7. DATA: Build a pd.DataFrame entirely from the context JSON inside the code block.
   All variables must be self-contained — do not reference external variables.

8. RENDER: End every code block with:
   st.plotly_chart(fig, use_container_width=True)

9. WHEN TO SKIP THE CHART (CRITICAL):
   - DO NOT generate a chart for purely descriptive or categorical lists (e.g., course catalog search results, employee directories, descriptive summaries).
   - ONLY generate a chart if there is a meaningful numeric metric to visualize (e.g., completion counts, percentages, progress over time, or aggregate stats).
   - If the data is a list of items with only categorical info (names, titles, dates, descriptions) and no quantitative metric, leave CODE empty before ===END===.
   - For descriptive results, focus on providing a rich EXPLANATION and a bulleted SUMMARY instead.
"""


class AIService:
    def __init__(self):
        self.model_id = Config.MODEL_ID
        self.temperature = 0.0
        self.top_p = 0.9
        self.top_k = 250
        self._resolve_arn()

    def set_model(self, model_id: str):
        self.model_id = model_id
        self._resolve_arn()

    def _resolve_arn(self):
        self.model_arn = f"arn:aws:bedrock:{Config.AWS_REGION}::foundation-model/{self.model_id}"
        _inference_profile_prefixes = ("global.", "us.", "eu.", "ap.")
        if ":" in self.model_id or self.model_id.startswith(_inference_profile_prefixes):
            self.model_arn = self.model_id

    # ── 1. QUERY ROUTER ──────────────────────────────────────────────────────
    def route_query(self, query: str, history: list = None) -> list:
        """
        Uses Claude to decide which MCP tools to call.
        Returns a list of {tool, params} dicts.
        """
        system_prompt = (
            "You are a Data Router for a corporate training database. "
            "Your ONLY task is to return a JSON list of tool calls. "
            "DO NOT include any text before or after the JSON.\n\n"
            "AVAILABLE TOOLS:\n"
            "1. get_dashboard_stats() - High-level counts of employees, courses, and completions.\n"
            "2. get_completions_by_job_family() - Aggregate completion counts grouped by role/job family.\n"
            "3. get_completions_by_geography(level='office'|'district') - Aggregate completions by region or office.\n"
            "4. get_mandatory_completion_rates() - List of employees with their mandatory training % completion.\n"
            "5. search_employees(name_query='...') - Find employees by name (first, last, or full name).\n"
            "6. search_employees_by_name(first_name='...', last_name='...') - More precise search when names are known separately.\n"
            "7. get_employee_summary(user_id='...') - Demographic summary and high-level training counts.\n"
            "8. get_employee_transcript(user_id='...') - Full list of all courses taken by the employee.\n"
            "9. get_compliance_report(user_id='...') - Analysis of mandatory course completion vs curriculum. Use this for 'compliance report' or 'missing courses' queries.\n"
            "10. search_courses(query_text='...') - Find courses in the catalog by title or number.\n"
            "11. get_team_training_summary(team_name='...') - Aggregated progress for everyone on a specific team.\n\n"
            "--- CRITICAL GUIDELINES ---\n"
            "- If a query asks for a 'compliance report', 'mandatory status', or 'missing courses', YOU MUST USE tool 9.\n"
            "- If a query asks for a 'transcript' or 'history', use tool 8.\n"
            "- If a query is about a SPECIFIC person, pass their name or ID directly to 'user_id'.\n"
            "- ONLY include the necessary parameters defined in the tools. DO NOT add extra parameters.\n"
            "- If multiple people match a name, the system will resolve the best match automatically.\n"
            "- If a query is about AGGREGATE trends or metrics, use tools 2, 3, or 4.\n"
            "- If a query is about a TEAM, use tool 11.\n\n"
            "--- OUTPUT FORMAT ---\n"
            "Return EXACTLY a JSON list: [{\"tool\": \"tool_name\", \"params\": {\"param_name\": \"value\"}}]\n"
        )

        # Copy history and keep only role and content to avoid Bedrock validation errors
        messages = []
        if history:
            for msg in history:
                messages.append({"role": msg.get("role", ""), "content": msg.get("content", "")})
        messages.append({"role": "user", "content": query})

        response = self.generate_response(messages, system_prompt)

        # Strip markdown fences if the LLM wraps the JSON in them
        clean = response.strip()
        if "```" in clean:
            match = re.search(r"```(?:json)?\s*(.*?)```", clean, re.DOTALL)
            if match:
                clean = match.group(1).strip()

        try:
            return json.loads(clean)
        except Exception as e:
            print(f"[AIService] Router parse error: {e}. Raw: {response}")
            return []

    # ── 2. VISUALIZATION GENERATOR ───────────────────────────────────────────
    def generate_viz_logic(self, user_query: str, data_context: str, history: list = None) -> dict:
        """
        Generates a professional Plotly chart and insight using a delimiter-based
        output format (avoids JSON-escaping issues with multi-line Python code).
        """
        history_str = json.dumps(history) if history else "none"
        prompt = (
            f"USER QUERY: {user_query}\n\n"
            f"CONVERSATION HISTORY:\n{history_str}\n\n"
            f"DATA CONTEXT:\n{data_context}"
        )

        messages = [{"role": "user", "content": prompt}]
        raw = self.generate_response(messages, _VIZ_SYSTEM_PROMPT).strip()

        # ── Parse delimiter sections ─────────────────────────────────────────
        def _extract(text: str, start_tag: str, end_tag: str) -> str:
            try:
                s = text.index(start_tag) + len(start_tag)
                e = text.index(end_tag, s)
                return text[s:e].strip()
            except ValueError:
                return ""

        explanation = _extract(raw, "===EXPLANATION===", "===SUMMARY===")
        summary_raw = _extract(raw, "===SUMMARY===",    "===CODE===")
        code        = _extract(raw, "===CODE===",       "===END===")

        summary = [ln.lstrip("•-* ") for ln in summary_raw.splitlines() if ln.strip()]

        if not explanation:
            explanation = "The AI returned an unexpected format."
            code = f"st.text({repr(raw)})"

        return {"explanation": explanation, "summary": summary, "code": code}

    # ── 3. BEDROCK INVOCATION ────────────────────────────────────────────────
    def generate_response(self, messages: list, system_prompt: str = "") -> str:
        """Generic Claude 3 invocation via Amazon Bedrock."""
        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "system": system_prompt,
                "messages": messages,
                "temperature": self.temperature,
                "top_k": self.top_k,
            }

            response = aws_manager.bedrock_runtime.invoke_model(
                modelId=self.model_arn,
                body=json.dumps(body),
            )

            response_body = json.loads(response.get("body").read())
            return response_body.get("content", [{}])[0].get("text", "")
        except Exception as e:
            return f"Error invoking AI model: {str(e)}"
