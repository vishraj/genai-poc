import os
import json
from dotenv import load_dotenv
from typing import Optional
from decimal import Decimal
from datetime import date, datetime
from mcp.server.fastmcp import FastMCP
from services.data_service import DataService

# Load environment variables (e.g., DATABASE_URL)
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("GenAI-PoC-Training-Service")

# Initialize the DataService
data_service = DataService()

def mcp_serialize(data):
    """Helper to serialize data for MCP with Decimal and date support."""
    return json.dumps(data, default=lambda o: float(o) if isinstance(o, Decimal) else str(o))

@mcp.tool()
def get_employee_summary(user_id: str) -> str:
    """
    Retrieves a comprehensive summary of an employee.
    
    Args:
        user_id: The employee's ID (e.g. 'ABC123') OR their full name (e.g. 'David Hill').
    """
    result = data_service.get_employee_summary(user_id)
    return mcp_serialize(result) if result else "{}"

@mcp.tool()
def get_employee_transcript(user_id: str) -> str:
    """
    Retrieves the full course transcript for a specific employee.
    
    Args:
        user_id: The employee's ID (e.g. 'ABC123') OR their full name (e.g. 'David Hill').
    """
    result = data_service.get_employee_transcript(user_id)
    return mcp_serialize(result) if result else "[]"

@mcp.tool()
def get_compliance_report(user_id: str) -> str:
    """
    Analyzes an employee's compliance with their job family curriculum.
    
    Args:
        user_id: The employee's ID (e.g. 'ABC123') OR their full name (e.g. 'David Hill').
    """
    result = data_service.get_compliance_report(user_id)
    return mcp_serialize(result)

@mcp.tool()
def search_courses(query_text: str) -> str:
    """
    Searches the training catalog for courses by title or course number.
    """
    result = data_service.search_courses(query_text)
    return mcp_serialize(result) if result else "[]"

@mcp.tool()
def get_dashboard_stats() -> str:
    """
    Returns high-level training KPIs: total employees, total completions, 
    catalog size, and active enrollments.
    """
    stats = {
        "total_employees": data_service.get_total_employees(),
        "completions": data_service.get_total_completions(),
        "catalog_size": data_service.get_catalog_size(),
        "in_progress": data_service.get_active_enrollments()
    }
    return json.dumps(stats)

@mcp.tool()
def get_completions_by_geography(level: str = 'office') -> str:
    """
    Aggregates completions by 'office' or 'district'.
    """
    result = data_service.get_completions_by_geography(level)
    return mcp_serialize(result) if result else "[]"

@mcp.tool()
def get_mandatory_completion_rates() -> str:
    """
    Returns a list of all employees and their % completion of mandatory courses.
    """
    result = data_service.get_mandatory_completion_rates()
    return mcp_serialize(result) if result else "[]"

@mcp.tool()
def get_completions_by_job_family() -> str:
    """
    Aggregates course completions grouped by Job Family.
    """
    result = data_service.get_completions_by_job_family()
    return mcp_serialize(result) if result else "[]"

@mcp.tool()
def get_team_training_summary(team_name: str) -> str:
    """
    Aggregates training progress for an entire team.
    """
    result = data_service.get_team_training_summary(team_name)
    return mcp_serialize(result) if result else "[]"

@mcp.tool()
def search_employees(name_query: str) -> str:
    """
    Searches for employees by first or last name.
    """
    result = data_service.search_employees(name_query)
    return mcp_serialize(result) if result else "[]"

@mcp.tool()
def search_employees_by_name(first_name: Optional[str] = None, last_name: Optional[str] = None) -> str:
    """
    Precise search for employees by first and/or last name.
    """
    result = data_service.search_employees_by_name(first_name, last_name)
    return mcp_serialize(result) if result else "[]"

if __name__ == "__main__":
    mcp.run()
