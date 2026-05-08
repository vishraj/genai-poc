import os
from dotenv import load_dotenv
from typing import Optional
from mcp.server.fastmcp import FastMCP
from services.data_service import DataService

# Load environment variables (e.g., DATABASE_URL)
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("GenAI-PoC-Training-Service")

# Initialize the DataService
data_service = DataService()

@mcp.tool()
def get_employee_summary(user_id: str) -> str:
    """
    Retrieves a comprehensive summary of an employee, including demographic data 
    and transcript status counts (completed, enrolled, dropped).
    
    Args:
        user_id: The unique identifier for the employee (e.g., 'ABC123').
    """
    result = data_service.get_employee_summary(user_id)
    return str(result) if result else "Employee not found."

@mcp.tool()
def get_employee_transcript(user_id: str) -> str:
    """
    Retrieves the full course transcript for a specific employee, 
    including course titles, registration dates, and enrollment status.
    
    Args:
        user_id: The unique identifier for the employee.
    """
    result = data_service.get_employee_transcript(user_id)
    return str(result) if result else "No transcript found for this employee."

@mcp.tool()
def get_compliance_report(user_id: str) -> str:
    """
    Analyzes an employee's compliance with their job family curriculum.
    Identifies which mandatory courses are missing or incomplete.
    
    Args:
        user_id: The unique identifier for the employee.
    """
    result = data_service.get_compliance_report(user_id)
    return str(result)

@mcp.tool()
def search_courses(query_text: str) -> str:
    """
    Searches the training catalog for courses by title or course number.
    
    Args:
        query_text: The search term (e.g., 'Currency', 'Security', or 'C101').
    """
    result = data_service.search_courses(query_text)
    return str(result) if result else "No courses matched your search."

@mcp.tool()
def get_team_training_summary(team_name: str) -> str:
    """
    Aggregates training progress for an entire team, showing completion 
    stats for each team member.
    
    Args:
        team_name: The human-readable name of the team.
    """
    result = data_service.get_team_training_summary(team_name)
    return str(result) if result else "No data found for this team."

@mcp.tool()
def search_employees(name_query: str) -> str:
    """
    Searches for employees by first or last name using a single query string.
    
    Args:
        name_query: The name or partial name to search for.
    """
    result = data_service.search_employees(name_query)
    return str(result) if result else "No employees matched your search."

@mcp.tool()
def search_employees_by_name(first_name: Optional[str] = None, last_name: Optional[str] = None) -> str:
    """
    Searches for employees by first name, last name, or both (case-insensitive).
    At least one parameter must be provided.
    
    Args:
        first_name: The first name or partial first name (optional).
        last_name: The last name or partial last name (optional).
    """
    result = data_service.search_employees_by_name(first_name, last_name)
    return str(result) if result else "No employees matched your search."

@mcp.tool()
def get_completions_by_job_family() -> str:
    """
    Aggregates course completions grouped by Job Family. 
    Useful for visualizing training impact across different roles.
    """
    result = data_service.get_completions_by_job_family()
    return str(result)

@mcp.tool()
def get_completions_by_geography(level: str = 'office') -> str:
    """
    Aggregates course completions grouped by geographic dimension (office or district).
    Useful for regional performance analysis.
    
    Args:
        level: The geographic level ('office' or 'district'). Defaults to 'office'.
    """
    result = data_service.get_completions_by_geography(level)
    return str(result)

@mcp.tool()
def get_mandatory_completion_rates() -> str:
    """
    Calculates the completion rate of mandatory courses for each employee.
    Identifies gaps in regulatory compliance.
    """
    result = data_service.get_mandatory_completion_rates()
    return str(result)

@mcp.tool()
def get_dashboard_stats() -> str:
    """
    Retrieves high-level summary statistics (counts) for the dashboard.
    """
    with data_service._get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM training.employee_fact")
            emp_count = cur.fetchone()['count']
            cur.execute("SELECT count(*) FROM training.transcript_fact WHERE enrollment_status = 'Completed'")
            comp_count = cur.fetchone()['count']
            cur.execute("SELECT count(*) FROM training.catalog_fact")
            course_count = cur.fetchone()['count']
            cur.execute("SELECT count(*) FROM training.transcript_fact WHERE enrollment_status = 'Enrolled'")
            enrolled_count = cur.fetchone()['count']
            return str({
                "total_employees": emp_count,
                "completions": comp_count,
                "catalog_size": course_count,
                "in_progress": enrolled_count
            })

if __name__ == "__main__":
    # Run the server using stdio transport by default
    mcp.run()
