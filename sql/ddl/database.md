
# training database
FRFS GenAI training app database

## Schema: database.sql

Mock database schema containing 4 tables
- employee_fact
- catalog_fact
- curriculum_fact
- transcript_fact


## Mock data: csv files

All four CSV files are populated with referentially consistent synthetic data:  
employee_fact_data.csv — 100 employees across 5 job families, 10 districts, 20 offices  
catalog_fact_data.csv — 10 courses (currency processing, counterfeit detection, compliance, etc.)  
curriculum_fact_data.csv — 22 rows mapping 3-5 courses per job family with mandatory/optional flags  
transcript_fact_data.csv — 436 transcript records, one per employee-course assignment, with ~70% Completed, ~20% Enrolled, ~10% Dropped. Credit dates are only populated for completed courses.  
All foreign keys (user_id, course_number, job_family) are consistent across tables.  


