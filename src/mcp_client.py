import asyncio
import json
import os
import threading
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class UI_MCPClient:
    def __init__(self):
        # mcp_client.py and mcp_server.py both live in src/
        server_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "mcp_server.py")
        )
        self.server_params = StdioServerParameters(
            command="python",
            args=[server_path],
            env=os.environ.copy(),
        )

    async def call_tool(self, tool_name: str, params: dict):
        """Connects to the MCP server via stdio, calls a tool, and returns the result."""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, params)

                if result.content and len(result.content) > 0:
                    text = result.content[0].text
                    try:
                        return json.loads(text)
                    except (json.JSONDecodeError, ValueError):
                        return text
                return None

    def run_tool_sync(self, tool_name: str, params: dict):
        """
        Synchronous wrapper safe for Streamlit.

        Uses a dedicated thread with its own event loop to avoid conflicts
        with Streamlit's internal async machinery (RuntimeError: loop running).
        """
        result_holder: list = [None]
        error_holder:  list = [None]

        def _run():
            loop = asyncio.new_event_loop()
            try:
                result_holder[0] = loop.run_until_complete(
                    self.call_tool(tool_name, params)
                )
            except Exception as exc:
                error_holder[0] = exc
            finally:
                loop.close()

        thread = threading.Thread(target=_run, daemon=True)
        thread.start()
        thread.join(timeout=30)  # max 30 s per tool call

        if error_holder[0]:
            print(f"[MCP] Error calling '{tool_name}': {error_holder[0]}")
            return None

        return result_holder[0]
