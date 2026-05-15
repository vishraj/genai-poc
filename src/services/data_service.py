import os
import psycopg2
import re
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
        """
        self.conn_string = conn_string or os.getenv(
            "DATABASE_URL", 
            "dbname='trainingdb' user='postgres' host='localhost' password='yourpassword' port='5432'"
        )

    def _get_connection(self):
        return psycopg2.connect(self.conn_string, cursor_factory=RealDictCursor)

    def resolve_user_id(self, identifier: str) -> Optional[str]:
        """
        Systemic name resolution: handles whitespace, case, 'Name (ID)' format, 
        and first/last name variations.
        """
        if not identifier: return None
        clean_id = str(identifier).strip()
        
        # 0. Handle "Name (ID)" or "ID (Name)" formats commonly produced by LLMs
        if "(" in clean_id:
            match = re.search(r"\(([^)]+)\)", clean_id)
            if match:
                potential_id = match.group(1).strip()
                # Check if the extracted part is likely an ID (alphanumeric, no spaces, short)
                if len(potential_id) <= 12 and " " not in potential_id:
                    with self._get_connection() as conn:
                        with conn.cursor() as cur:
                            cur.execute("SELECT user_id FROM training.employee_fact WHERE user_id ILIKE %s", (potential_id,))
                            if cur.fetchone(): return potential_id.upper()
        
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # 1. Exact ID match (case-insensitive)
                cur.execute("SELECT user_id FROM training.employee_fact WHERE user_id ILIKE %s", (clean_id,))
                res = cur.fetchone()
                if res: return res['user_id']
                
                # 2. Try splitting name into first and last
                parts = clean_id.split()
                if len(parts) >= 2:
                    f, l = parts[0], parts[-1]
                    cur.execute("SELECT user_id FROM training.employee_fact WHERE first_name ILIKE %s AND last_name ILIKE %s LIMIT 1", (f, l))
                    res = cur.fetchone()
                    if res: return res['user_id']
                
                # 3. Fallback to flexible wildcard search on full name variations
                search_val = f"%{clean_id}%"
                search_query = """
                SELECT user_id FROM training.employee_fact 
                WHERE (COALESCE(first_name, '') || ' ' || COALESCE(last_name, '')) ILIKE %s
                   OR (COALESCE(last_name, '') || ' ' || COALESCE(first_name, '')) ILIKE %s
                   OR last_name ILIKE %s
                   OR first_name ILIKE %s
                LIMIT 1;
                """
                cur.execute(search_query, (search_val, search_val, search_val, search_val))
                res = cur.fetchone()
                if res: return res['user_id']
        return None

    def get_total_employees(self) -> int:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM training.employee_fact;")
                return cur.fetchone()['count']

    def get_total_completions(self) -> int:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM training.transcript_fact WHERE enrollment_status = 'Completed';")
                return cur.fetchone()['count']

    def get_catalog_size(self) -> int:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM training.catalog_fact;")
                return cur.fetchone()['count']

    def get_active_enrollments(self) -> int:
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT count(*) FROM training.transcript_fact WHERE enrollment_status = 'Enrolled';")
                return cur.fetchone()['count']

    def get_completion_trend(self) -> str:
        """Calculates completions growth comparing the last two active months."""
        query = """
        WITH monthly_completions AS (
            SELECT 
                DATE_TRUNC('month', registration_date) as month,
                COUNT(*) as count
            FROM training.transcript_fact
            WHERE enrollment_status = 'Completed'
            GROUP BY 1
            ORDER BY 1 DESC
            LIMIT 2
        )
        SELECT count FROM monthly_completions;
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    rows = cur.fetchall()
                    if len(rows) < 2: return "0%"
                    
                    latest = rows[0]['count']
                    previous = rows[1]['count']
                    
                    if previous == 0: return "+100%"
                    delta = ((latest - previous) / previous) * 100
                    return f"{delta:+.1f}%"
        except:
            return "0%"

    def get_employee_summary(self, user_id: str) -> Optional[Dict[str, Any]]:
        resolved_id = self.resolve_user_id(user_id) or user_id
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
                cur.execute(query, (resolved_id,))
                return cur.fetchone()

    def get_employee_transcript(self, user_id: str) -> List[Dict[str, Any]]:
        resolved_id = self.resolve_user_id(user_id) or user_id
        query = """
        SELECT c.course_title, t.course_number, t.registration_date, t.credit_date, t.enrollment_status
        FROM training.transcript_fact t
        JOIN training.catalog_fact c ON t.course_number = c.course_number
        WHERE t.user_id = %s
        ORDER BY t.registration_date DESC;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (resolved_id,))
                return cur.fetchall()

    def get_compliance_report(self, user_id: str) -> Dict[str, Any]:
        resolved_id = self.resolve_user_id(user_id) or user_id
        query = """
        WITH required_courses AS (
            SELECT cf.course_number, c.course_title, cf.course_is_mandatory
            FROM training.employee_fact e
            JOIN training.curriculum_fact cf ON e.job_family = cf.job_family
            JOIN training.catalog_fact c ON cf.course_number = c.course_number
            WHERE e.user_id = %s
        )
        SELECT rc.course_title, rc.course_number, rc.course_is_mandatory, COALESCE(t.enrollment_status, 'Not Started') as status, t.credit_date
        FROM required_courses rc
        LEFT JOIN training.transcript_fact t ON rc.course_number = t.course_number AND t.user_id = %s;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (resolved_id, resolved_id))
                results = cur.fetchall()
                if not results: return {"status": "Error", "message": f"No curriculum found for user {resolved_id}"}
                mandatory_count = sum(1 for r in results if r['course_is_mandatory'])
                completed_mandatory = sum(1 for r in results if r['course_is_mandatory'] and r['status'] == 'Completed')
                missing = [r for r in results if r['course_is_mandatory'] and r['status'] != 'Completed']
                rate = (completed_mandatory / mandatory_count * 100) if mandatory_count > 0 else 100
                return {
                    "user_id": resolved_id, "completion_rate": round(rate, 1),
                    "mandatory_count": mandatory_count, "completed_mandatory": completed_mandatory,
                    "missing_mandatory": missing, "full_report": results
                }

    def search_courses(self, query_text: str) -> List[Dict[str, Any]]:
        sql = "SELECT * FROM training.catalog_fact WHERE course_title ILIKE %s OR course_number ILIKE %s;"
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                search_val = f"%{query_text}%"
                cur.execute(sql, (search_val, search_val))
                return cur.fetchall()

    def get_team_training_summary(self, team_name: str) -> List[Dict[str, Any]]:
        query = """
        SELECT e.first_name, e.last_name, e.user_id, e.job_family, e.team_name,
            COUNT(t.row_num) FILTER (WHERE t.enrollment_status = 'Completed') as completed_count,
            COUNT(t.row_num) FILTER (WHERE t.enrollment_status = 'Enrolled') as in_progress_count,
            COUNT(t.row_num) FILTER (WHERE t.enrollment_status = 'Dropped') as dropped_count
        FROM training.employee_fact e
        LEFT JOIN training.transcript_fact t ON e.user_id = t.user_id
        WHERE e.team_name ILIKE %s OR e.job_family ILIKE %s
        GROUP BY e.user_id, e.first_name, e.last_name, e.job_family, e.team_name ORDER BY completed_count DESC;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (team_name, team_name))
                return cur.fetchall()

    def search_employees(self, name_query: str) -> List[Dict[str, Any]]:
        sql = """
        SELECT user_id, first_name, last_name, team_name, job_family 
        FROM training.employee_fact 
        WHERE first_name ILIKE %s OR last_name ILIKE %s OR (first_name || ' ' || last_name) ILIKE %s;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                search_val = f"%{name_query}%"
                cur.execute(sql, (search_val, search_val, search_val))
                return cur.fetchall()

    def search_employees_by_name(self, first_name: Optional[str] = None, last_name: Optional[str] = None) -> List[Dict[str, Any]]:
        sql = "SELECT user_id, first_name, last_name, team_name, job_family FROM training.employee_fact WHERE 1=1"
        params = []
        if first_name:
            sql += " AND first_name ILIKE %s"; params.append(f"%{first_name}%")
        if last_name:
            sql += " AND last_name ILIKE %s"; params.append(f"%{last_name}%")
        if not params: return []
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, tuple(params))
                return cur.fetchall()

    def get_completions_by_job_family(self) -> List[Dict[str, Any]]:
        query = """
        SELECT e.job_family, COUNT(t.row_num) as completion_count
        FROM training.employee_fact e
        JOIN training.transcript_fact t ON e.user_id = t.user_id
        WHERE t.enrollment_status = 'Completed'
        GROUP BY e.job_family ORDER BY completion_count DESC;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()

    def get_completions_by_geography(self, level: str = 'office') -> List[Dict[str, Any]]:
        column = 'office_name' if level.lower() == 'office' else 'district_name'
        query = f"""
        SELECT e.{column} as location, COUNT(t.row_num) as completion_count
        FROM training.employee_fact e
        JOIN training.transcript_fact t ON e.user_id = t.user_id
        WHERE t.enrollment_status = 'Completed'
        GROUP BY e.{column} ORDER BY completion_count DESC;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()

    def get_mandatory_completion_rates(self) -> List[Dict[str, Any]]:
        query = """
        WITH total_req AS (
            SELECT e.user_id, e.first_name, e.last_name, e.team_name, COUNT(cf.course_number) as req_count
            FROM training.employee_fact e
            JOIN training.curriculum_fact cf ON e.job_family = cf.job_family
            WHERE cf.course_is_mandatory = true GROUP BY e.user_id, e.first_name, e.last_name, e.team_name
        ),
        completed_req AS (
            SELECT t.user_id, COUNT(t.course_number) as comp_count
            FROM training.transcript_fact t
            JOIN training.curriculum_fact cf ON t.course_number = cf.course_number
            JOIN training.employee_fact e ON t.user_id = e.user_id AND e.job_family = cf.job_family
            WHERE cf.course_is_mandatory = true AND t.enrollment_status = 'Completed'
            GROUP BY t.user_id
        )
        SELECT tr.user_id, tr.first_name, tr.last_name, tr.team_name, tr.req_count,
               COALESCE(cr.comp_count, 0) as completed_count,
               ROUND((COALESCE(cr.comp_count, 0)::numeric / tr.req_count) * 100, 1) as completion_rate
        FROM total_req tr
        LEFT JOIN completed_req cr ON tr.user_id = cr.user_id
        ORDER BY completion_rate ASC;
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchall()
