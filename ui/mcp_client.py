import asyncio
import os
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class UI_MCPClient:
    def __init__(self):
        # Path to your mcp_server.py
        server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'mcp_server.py'))
        self.server_params = StdioServerParameters(
            command="python",
            args=[server_path],
            env=os.environ.copy()
        )

    async def call_tool(self, tool_name: str, params: dict):
        """
        Connects to the MCP server, calls a tool, and returns the result.
        """
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, params)
                
                # MCP tools return a list of content objects (usually text)
                if result.content and len(result.content) > 0:
                    import json
                    try:
                        # Attempt to parse the text content back into a dict for the UI
                        return json.loads(result.content[0].text)
                    except:
                        return result.content[0].text
                return None

    def run_tool_sync(self, tool_name: str, params: dict):
        """
        Synchronous wrapper for Streamlit compatibility.
        """
        try:
            return asyncio.run(self.call_tool(tool_name, params))
        except Exception as e:
            print(f"MCP Client Error: {e}")
            return None
