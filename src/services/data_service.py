import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional

class DataService:
    """
    Service for querying the Training database. 
    Provides joined, business-oriented data for the FedCash Training GenAI PoC.
    """

    def __init__(self, conn_string: Optional[str] = None):
        """
        Initializes the DataService.
        
        Args:
            conn_string: Connection string for PostgreSQL. 
                        Defaults to DATABASE_URL environment variable.
        """
        self.conn_string = conn_string or os.getenv(
            "DATABASE_URL", 
            "dbname='trainingdb' user='postgres' host='localhost' password='yourpassword' port='5432'"
        )

    def _get_connection(self):
        return psycopg2.connect(self.conn_string, cursor_factory=RealDictCursor)

    def get_employee_summary(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a comprehensive summary of an employee, including demographic data and transcript status counts.
        
        Args:
            user_id: The unique identifier for the employee (e.g., 'ABC123').
            
        Returns:
            A dictionary containing employee details and completion stats, or None if not found.
        """
        query = """
        SELECT 
            e.*,
            (SELECT count(*) FROM training.transcript_fact t WHERE t.user_id = e.user_id AND t.enrollment_status = 'Completed') as completed_count,
            (SELECT count(*) FROM training.transcript_fact t WHERE t.user_id = e.user_id AND t.enrollment_status = 'Enrolled') as enrolled_count,
            (SELECT count(*) FROM training.transcript_fact t WHERE t.user_id = e.user_id AND t.enrollment_status = 'Dropped') as dropped_count
        FROM training.employee_fact e
        WHERE e.user_id = %s;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id,))
                return cur.fetchone()

    def get_employee_transcript(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves the full course transcript for a specific employee with human-readable course titles.
        
        Args:
            user_id: The unique identifier for the employee.
            
        Returns:
            A list of transcript records including course titles and enrollment status.
        """
        query = """
        SELECT 
            c.course_title,
            t.course_number,
            t.registration_date,
            t.credit_date,
            t.enrollment_status
        FROM training.transcript_fact t
        JOIN training.catalog_fact c ON t.course_number = c.course_number
        WHERE t.user_id = %s
        ORDER BY t.registration_date DESC;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id,))
                return cur.fetchall()

    def get_compliance_report(self, user_id: str) -> Dict[str, Any]:
        """
        Analyzes an employee's compliance with their job family curriculum.
        Identifies which mandatory courses are missing or incomplete.
        
        Args:
            user_id: The unique identifier for the employee.
            
        Returns:
            A dictionary with compliance status, full curriculum details, and missing mandatory courses.
        """
        query = """
        WITH required_courses AS (
            SELECT 
                cf.course_number,
                c.course_title,
                cf.course_is_mandatory
            FROM training.employee_fact e
            JOIN training.curriculum_fact cf ON e.job_family = cf.job_family
            JOIN training.catalog_fact c ON cf.course_number = c.course_number
            WHERE e.user_id = %s
        )
        SELECT 
            rc.course_title,
            rc.course_number,
            rc.course_is_mandatory,
            COALESCE(t.enrollment_status, 'Not Started') as status,
            t.credit_date
        FROM required_courses rc
        LEFT JOIN training.transcript_fact t ON rc.course_number = t.course_number AND t.user_id = %s;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (user_id, user_id))
                results = cur.fetchall()
                
                mandatory_missing = [r for r in results if r['course_is_mandatory'] and r['status'] != 'Completed']
                return {
                    "user_id": user_id,
                    "is_compliant": len(mandatory_missing) == 0,
                    "total_required": len(results),
                    "missing_mandatory_count": len(mandatory_missing),
                    "curriculum_details": results,
                    "missing_mandatory_list": mandatory_missing
                }

    def search_courses(self, query_text: str) -> List[Dict[str, Any]]:
        """
        Searches the training catalog for courses by title.
        
        Args:
            query_text: The search term (e.g., 'Currency' or 'Security').
            
        Returns:
            A list of matching courses.
        """
        sql = "SELECT * FROM training.catalog_fact WHERE course_title ILIKE %s OR course_number ILIKE %s;"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                search_val = f"%{query_text}%"
                cur.execute(sql, (search_val, search_val))
                return cur.fetchall()

    def get_team_training_summary(self, team_name: str) -> List[Dict[str, Any]]:
        """
        Aggregates training progress for an entire team.
        
        Args:
            team_name: The human-readable name of the team.
            
        Returns:
            A list of employees with their aggregate completion statistics.
        """
        query = """
        SELECT 
            e.first_name,
            e.last_name,
            e.user_id,
            e.job_family,
            COUNT(t.row_num) FILTER (WHERE t.enrollment_status = 'Completed') as completed_count,
            COUNT(t.row_num) FILTER (WHERE t.enrollment_status = 'Enrolled') as in_progress_count,
            COUNT(t.row_num) FILTER (WHERE t.enrollment_status = 'Dropped') as dropped_count
        FROM training.employee_fact e
        LEFT JOIN training.transcript_fact t ON e.user_id = t.user_id
        WHERE e.team_name = %s
        GROUP BY e.user_id, e.first_name, e.last_name, e.job_family
        ORDER BY completed_count DESC;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (team_name,))
                return cur.fetchall()

    def search_employees(self, name_query: str) -> List[Dict[str, Any]]:
        """
        Searches for employees by first or last name.
        
        Args:
            name_query: The name or partial name to search for.
            
        Returns:
            A list of matching employees.
        """
        sql = "SELECT user_id, first_name, last_name, team_name, job_family FROM training.employee_fact WHERE first_name ILIKE %s OR last_name ILIKE %s;"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                search_val = f"%{name_query}%"
                cur.execute(sql, (search_val, search_val))
                return cur.fetchall()
