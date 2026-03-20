-- create the demo tables - [training_fact, employee_fact, difference_fact]
CREATE SCHEMA IF NOT EXISTS demo;

-- training_fact table
DROP TABLE IF EXISTS demo.training_fact;
CREATE TABLE IF NOT EXISTS demo.training_fact (
    row_num bigint primary key,
    department_name varchar(64),
    job_family varchar(64),
    district_id varchar(4),
    user_id varchar(12),
    course_title varchar(256),
    course_number varchar(12),
    class_number varchar(12),
    registration_date date,
    credit_date date,
    enrollment_status varchar(32),
    created_at timestamp without timezone,
    updated_at timestamp without timezone
);

-- create the index
create index if not exists idx_training_fact_user_id on demo.training_fact(row_num);

-- verify data load
select count(*) from demo.training_fact;
select * from demo.training_fact limit 50;

-- employee_fact table
drop table if exists demo.employee_fact;
create table if not exists demo.employee_fact (
    row_num bigint primary key,
    user_id varchar(12),
    first_name varchar(64),
    middle_name varchar(32),
    last_name varchar(64),
    email_address varchar(128),
    district_number varchar(4),
    district_letter varchar(2),
    district_name varchar(32),
    office_number varchar(4),
    office_name varchar(32),
    hire_date date,
    team_id varchar(4),
    team_name varchar(32),
    team_type_id varchar(4),
    team_type_description varchar(64),
    team_transfer_date date,
    job_family varchar(64),
    department_name varchar(64),
    created_at timestamp without timezone,
    updated_at timestamp without timezone
);

-- create the index
create index if not exists idx_demo_employee_fact_user_id on demo.employee_fact(user_id);

-- verify data load
select count(*) from demo.employee_fact;
select * from demo.employee_fact limit 50;

-- difference_fact table
drop table if exists demo.difference_fact;
create table if not exists demo.difference_fact (
    row_num bigint primary key,
    difference_id varchar(12),
    difference_date date,
    deposit_id vachar(12),
    deposit_endpoint_id varchar(12),
    deposit_date date,
    deposit_total decimal,
    deposit_diff decimal,
    difference_type varchar(12),
    difference_denom varchar(4),
    difference_pieces integer,
    difference_amount decimal,
    location_name varchar(32),
    machine_number integer,
    team_id varchar(8),
    operator_id varchar(12),
    created_at timestamp without timezone,
    updated_at timestamp without timezone
);

-- create index
create index if not exists idx_demo_difference_fact_row_num on demo.difference_fact(row_num);

-- validate data load
select count(*) from demo.difference_fact;
select * from demo.difference_fact limit 50;