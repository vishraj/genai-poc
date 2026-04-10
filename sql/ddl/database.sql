
-- FRFS FedCash Training Database - 20260409
-- MOCK DATABASE for GenAI PoC
-- Aurora PostgreSQL 17, serverless


-- notes: feel free to modify this to suite your needs. Notify the team of breaking changes.
-- todo: ER diagram, data model doc, create indexs, create validation queries


-- Assumes Aurora PostreSQL cluster with empty 'trainingdb' database already created by Terraform
-- Create all db objects with the script below:


-- session settings
SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SET timezone = 'America/Los_Angeles';
SHOW timezone;
SELECT NOW();


-- SCHEMA: training
-- Create schema for training database tables [ employee_fact, catalog_fact, curriculum_fact, transcript_fact ]
--
CREATE SCHEMA IF NOT EXISTS training;


-- add a function for updated_at triggers - used by all tables
-- remember to set the timezone in your query sessions too
--
CREATE OR REPLACE FUNCTION training.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- TABLE: employee_fact
-- employees have a job_family. a job_family has a curriculum. a curriculum has courses. an employee has a transcript.
-- 
CREATE TABLE IF NOT EXISTS training.employee_fact (                           -- helpful hints for the model
    row_num BIGINT PRIMARY KEY,                                               -- primary key
    user_id VARCHAR(12),                                                      -- ABC123, foreign key
    first_name VARCHAR(32),                                                   -- George
    middle_name VARCHAR(32),                                                  -- X
    last_name VARCHAR(32),                                                    -- Washington
    email_address VARCHAR(64),                                                -- george.washington@example.com
    district_num VARCHAR(4),                                                  -- 00
    district_letter VARCHAR(2),                                               -- Z
    district_name VARCHAR(32),                                                -- Northern CA
    office_num VARCHAR(4),                                                    -- 1234
    office_name VARCHAR(32),                                                  -- Modesto
    hire_date DATE,                                                           -- date
    team_id VARCHAR(4),                                                       -- 1234
    team_name VARCHAR(32),                                                    -- team001
    team_type_id VARCHAR(64),                                                 -- CYR
    team_type_description VARCHAR(64),                                        -- Receiving
    team_transfer_date DATE,                                                  -- date
    job_family VARCHAR(64),                                                   -- Cash Handler
    department_name VARCHAR(64),                                              -- Cash Operations
    created_at TIMESTAMP WITHOUT TIME ZONE,                                   -- 2025-06-20 12:10:03.123456 
    updated_at TIMESTAMP WITHOUT TIME ZONE                                    -- 2025-06-20 12:10:03.123456 
);


-- PostgreSQL DDL comments - helpful hints for the model
-- Table comment
COMMENT ON TABLE training.employee_fact IS 'Stores employee demographic and organizational data. Employees have a job_family which maps to a curriculum of required courses.';
-- Column comments
COMMENT ON COLUMN training.employee_fact.row_num IS 'Auto-incrementing primary key for the employee record';
COMMENT ON COLUMN training.employee_fact.user_id IS 'Unique employee identifier (e.g. ABC123). Used as a foreign key in transcript_fact.';
COMMENT ON COLUMN training.employee_fact.first_name IS 'Employee first name (e.g. George)';
COMMENT ON COLUMN training.employee_fact.middle_name IS 'Employee middle name or initial (e.g. X)';
COMMENT ON COLUMN training.employee_fact.last_name IS 'Employee last name (e.g. Washington)';
COMMENT ON COLUMN training.employee_fact.email_address IS 'Employee email address (e.g. george.washington@example.com)';
COMMENT ON COLUMN training.employee_fact.district_num IS 'Numeric identifier for the district (e.g. 00)';
COMMENT ON COLUMN training.employee_fact.district_letter IS 'Letter code for the district (e.g. Z)';
COMMENT ON COLUMN training.employee_fact.district_name IS 'Human-readable district name (e.g. Northern CA)';
COMMENT ON COLUMN training.employee_fact.office_num IS 'Numeric identifier for the office location (e.g. 1234)';
COMMENT ON COLUMN training.employee_fact.office_name IS 'Human-readable office name (e.g. Modesto)';
COMMENT ON COLUMN training.employee_fact.hire_date IS 'Date the employee was hired';
COMMENT ON COLUMN training.employee_fact.team_id IS 'Numeric identifier for the team (e.g. 1234)';
COMMENT ON COLUMN training.employee_fact.team_name IS 'Human-readable team name (e.g. team001)';
COMMENT ON COLUMN training.employee_fact.team_type_id IS 'Code identifying the team type (e.g. CYR)';
COMMENT ON COLUMN training.employee_fact.team_type_description IS 'Description of the team type (e.g. Receiving)';
COMMENT ON COLUMN training.employee_fact.team_transfer_date IS 'Date the employee transferred to the current team';
COMMENT ON COLUMN training.employee_fact.job_family IS 'Job family classification (e.g. Cash Handler). Maps to curriculum_fact to determine required courses.';
COMMENT ON COLUMN training.employee_fact.department_name IS 'Department the employee belongs to (e.g. Cash Operations)';
COMMENT ON COLUMN training.employee_fact.created_at IS 'Timestamp when the record was created';
COMMENT ON COLUMN training.employee_fact.updated_at IS 'Timestamp when the record was last updated (auto-set by trigger)';

-- TRIGGER: set_updated_at
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON training.employee_fact
    FOR EACH ROW
    EXECUTE FUNCTION training.update_updated_at_column();




-- TABLE: catalog_fact
-- catalog contains all courses
--
CREATE TABLE IF NOT EXISTS training.catalog_fact (                            -- helpful hints for the model
    row_num BIGINT PRIMARY KEY,                                               -- primary key
    course_title VARCHAR(256),                                                -- Introduction to Currency...
    course_number VARCHAR(12),                                                -- 123456789012, foreign key
    class_number VARCHAR(12),                                                 -- 123456789012
    created_at TIMESTAMP WITHOUT TIME ZONE,                                   -- 2025-06-20 12:10:03.123456 
    updated_at TIMESTAMP WITHOUT TIME ZONE                                    -- 2025-06-20 12:10:03.123456 
);


-- PostgreSQL DDL comments - helpful hints for the model
-- Table comment
COMMENT ON TABLE training.catalog_fact IS 'Contains all available training courses. Each course has a unique course_number referenced by curriculum_fact and transcript_fact.';
-- Column comments
COMMENT ON COLUMN training.catalog_fact.row_num IS 'Auto-incrementing primary key for the catalog record';
COMMENT ON COLUMN training.catalog_fact.course_title IS 'Full title of the training course (e.g. Introduction to Currency...)';
COMMENT ON COLUMN training.catalog_fact.course_number IS 'Unique course identifier (e.g. 123456789012). Used as a foreign key in curriculum_fact and transcript_fact.';
COMMENT ON COLUMN training.catalog_fact.class_number IS 'Class number associated with the course (e.g. 123456789012)';
COMMENT ON COLUMN training.catalog_fact.created_at IS 'Timestamp when the record was created';
COMMENT ON COLUMN training.catalog_fact.updated_at IS 'Timestamp when the record was last updated (auto-set by trigger)';


-- TRIGGER: set_updated_at
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON training.catalog_fact
    FOR EACH ROW
    EXECUTE FUNCTION training.update_updated_at_column();




-- TABLE: curriculum_fact
-- curriculums map course_numbers to job_family 
-- e.g. an employee with job_family = 'Cash Handler' must take course_number 123456789012, etc.
--
CREATE TABLE IF NOT EXISTS training.curriculum_fact (                         -- helpful hints for the model
    row_num BIGINT PRIMARY KEY,                                               -- primary key
    job_family VARCHAR(64),                                                   -- Cash Operations, foreign key
    course_number VARCHAR(12),                                                -- 123456789012, foreign key
    course_is_mandatory BOOLEAN,                                              -- TRUE 
    created_at TIMESTAMP WITHOUT TIME ZONE,                                   -- 2025-06-20 12:10:03.123456 
    updated_at TIMESTAMP WITHOUT TIME ZONE                                    -- 2025-06-20 12:10:03.123456 
);


-- PostgreSQL DDL comments - helpful hints for the model
-- Table comment
COMMENT ON TABLE training.curriculum_fact IS 'Maps course_numbers to job_family classifications. Defines which courses are required (mandatory or optional) for each job family.';
-- Column comments
COMMENT ON COLUMN training.curriculum_fact.row_num IS 'Auto-incrementing primary key for the curriculum record';
COMMENT ON COLUMN training.curriculum_fact.job_family IS 'Job family classification (e.g. Cash Operations). Foreign key linking to employee_fact.job_family.';
COMMENT ON COLUMN training.curriculum_fact.course_number IS 'Course identifier (e.g. 123456789012). Foreign key linking to catalog_fact.course_number.';
COMMENT ON COLUMN training.curriculum_fact.course_is_mandatory IS 'Whether the course is mandatory (TRUE) or optional (FALSE) for the job family';
COMMENT ON COLUMN training.curriculum_fact.created_at IS 'Timestamp when the record was created';
COMMENT ON COLUMN training.curriculum_fact.updated_at IS 'Timestamp when the record was last updated (auto-set by trigger)';


-- TRIGGER: set_updated_at
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON training.curriculum_fact
    FOR EACH ROW
    EXECUTE FUNCTION training.update_updated_at_column();




-- TABLE: transcript_fact
-- transcript contains 1 record for each course assigned to an employee
-- 
CREATE TABLE IF NOT EXISTS training.transcript_fact (                         -- helpful hints for the model
    row_num BIGINT PRIMARY KEY,                                               -- primary key
    user_id VARCHAR(12),                                                      -- ABC123  // L0BCW01 / 123456789
    course_number VARCHAR(12),                                                -- 123456789012
    registration_date DATE,                                                   -- 2024-07-02
    credit_date DATE,                                                         -- 2024-08-15
    enrollment_status VARCHAR(32),                                            -- Completed, Dropped, Enrolled
    created_at TIMESTAMP WITHOUT TIME ZONE,                                   -- 2025-06-20 12:10:03.123456 
    updated_at TIMESTAMP WITHOUT TIME ZONE                                    -- 2025-06-20 12:10:03.123456 
);


-- PostgreSQL DDL comments - helpful hints for the model
-- Table comment
COMMENT ON TABLE training.transcript_fact IS 'Transcript records tracking each course assigned to an employee. Contains one record per employee-course combination with enrollment status and completion dates.';
-- Column comments
COMMENT ON COLUMN training.transcript_fact.row_num IS 'Auto-incrementing primary key for the transcript record';
COMMENT ON COLUMN training.transcript_fact.user_id IS 'Employee identifier (e.g. ABC123). Foreign key linking to employee_fact.user_id.';
COMMENT ON COLUMN training.transcript_fact.course_number IS 'Course identifier (e.g. 123456789012). Foreign key linking to catalog_fact.course_number.';
COMMENT ON COLUMN training.transcript_fact.registration_date IS 'Date the employee registered for the course (e.g. 2024-07-02)';
COMMENT ON COLUMN training.transcript_fact.credit_date IS 'Date the employee received credit for completing the course (e.g. 2024-08-15)';
COMMENT ON COLUMN training.transcript_fact.enrollment_status IS 'Current enrollment status (e.g. Completed, Dropped, Enrolled)';
COMMENT ON COLUMN training.transcript_fact.created_at IS 'Timestamp when the record was created';
COMMENT ON COLUMN training.transcript_fact.updated_at IS 'Timestamp when the record was last updated (auto-set by trigger)';


-- TRIGGER: set_updated_at
CREATE TRIGGER set_updated_at
    BEFORE UPDATE ON training.transcript_fact
    FOR EACH ROW
    EXECUTE FUNCTION training.update_updated_at_column();


-- Aurora PostgreSQL Extensions
--
-- aws_s3 extension - optional
-- Enable aws_s3 extension for S3 data import (Aurora PostgreSQL feature)
-- Aurora cluster must have an IAM role with S3 import permissions on your S3 bucket
CREATE EXTENSION IF NOT EXISTS aws_s3 CASCADE;

