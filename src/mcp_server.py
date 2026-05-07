import os
from dotenv import load_dotenv
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
    Searches for employees by first or last name.
    
    Args:
        name_query: The name or partial name to search for.
    """
    result = data_service.search_employees(name_query)
    return str(result) if result else "No employees matched your search."

if __name__ == "__main__":
    # Run the server using stdio transport by default
    mcp.run()
