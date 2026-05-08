import json
from utils.aws_clients import aws_manager
from utils.config import Config

class AIService:
    def __init__(self):
        self.model_id = Config.MODEL_ID
        # Handle inference profiles or full ARNs
        self.model_arn = f"arn:aws:bedrock:{Config.AWS_REGION}::foundation-model/{Config.MODEL_ID}"
        _inference_profile_prefixes = ("global.", "us.", "eu.", "ap.")
        if ":" in Config.MODEL_ID or Config.MODEL_ID.startswith(_inference_profile_prefixes):
            self.model_arn = Config.MODEL_ID

    def route_query(self, query: str) -> list:
        """
        Uses Claude to decide which DataService methods to call.
        """
        system_prompt = (
            "You are a Data Router for a corporate training database. "
            "Your ONLY task is to return a JSON list of tool calls. "
            "DO NOT include any text before or after the JSON.\n\n"
            "AVAILABLE TOOLS:\n"
            "1. get_completions_by_job_family()\n"
            "2. get_completions_by_geography(level='office'|'district')\n"
            "3. get_mandatory_completion_rates()\n"
            "4. search_employees(name_query='...') - Use for finding people by first/last name.\n"
            "5. get_employee_transcript(user_id='...') - Use for training history.\n"
            "6. get_compliance_report(user_id='...') - Use for mandatory training gaps.\n\n"
            "--- OUTPUT FORMAT ---\n"
            "Return EXACTLY a JSON list like this: [{\"tool\": \"tool_name\", \"params\": {}}]\n"
            "Example: [{\"tool\": \"search_employees\", \"params\": {\"name_query\": \"James Baker\"}}]"
        )
        
        response = self.generate_response(query, system_prompt)
        
        # Robust cleaning
        clean = response.strip()
        if "```" in clean:
            # Extract content between backticks if they exist
            import re
            match = re.search(r"```(?:json)?\s*(.*?)```", clean, re.DOTALL)
            if match:
                clean = match.group(1).strip()
        
        try:
            return json.loads(clean)
        except Exception as e:
            # Fallback for debugging
            print(f"DEBUG: Router JSON parse error: {e}. Raw response: {response}")
            return []

    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """
        Generic method to invoke Claude 3 via Bedrock.
        """
        try:
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0
            })

            response = aws_manager.bedrock_runtime.invoke_model(
                modelId=self.model_arn,
                body=body
            )

            response_body = json.loads(response.get('body').read())
            return response_body.get('content', [{}])[0].get('text', "")
        except Exception as e:
            return f"Error invoking AI model: {str(e)}"

    def generate_viz_logic(self, user_query: str, data_context: str) -> dict:
        """
        Generates Python code for Streamlit/Plotly visualizations based on user query.
        """
        system_prompt = (
            "You are a Senior Data Analyst. Your goal is to generate Python code for a Streamlit dashboard. "
            "The code should use Plotly for visualizations. "
            "You will be provided with a USER QUERY and a DATA CONTEXT (JSON representation of the data).\n\n"
            "--- OUTPUT FORMAT ---\n"
            "Return a JSON block with THREE fields:\n"
            "1. 'explanation': A brief high-level description of the insight.\n"
            "2. 'summary': A list of 2-3 summarized bullet points (key takeaways) from the data.\n"
            "3. 'code': The Python code to render the chart using st.plotly_chart().\n"
            "Example:\n"
            "{\n"
            "  \"explanation\": \"This chart shows...\",\n"
            "  \"summary\": [\"Point A\", \"Point B\"],\n"
            "  \"code\": \"import plotly.express as px\\nfig = px.bar(...)\\nst.plotly_chart(fig)\"\n"
            "}"
        )

        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        prompt = f"CURRENT TIME: {current_time}\nUSER QUERY: {user_query}\n\nDATA CONTEXT:\n{data_context}"
        
        raw_response = self.generate_response(prompt, system_prompt)
        
        # Clean up markdown fences if present
        clean_response = raw_response.strip()
        if clean_response.startswith("```json"):
            clean_response = clean_response[7:]
        if clean_response.endswith("```"):
            clean_response = clean_response[:-3]
        clean_response = clean_response.strip()
        
        try:
            return json.loads(clean_response)
        except Exception as e:
            return {
                "explanation": f"I received a response but couldn't parse the structure: {str(e)}",
                "code": f"# Raw response from AI:\n# {raw_response}"
            }
