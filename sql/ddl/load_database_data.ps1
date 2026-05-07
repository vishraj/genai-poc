# PowerShell script to load synthetic data into RDS PostgreSQL
# This script uses the psql \copy command for high-performance loading.
# Requires: psql (PostgreSQL client) installed and in your PATH.

# --- Configuration ---
$DB_HOST = "learningdb.cxe8g06806dj.us-east-1.rds.amazonaws.com"
$DB_PORT = "5432"
$DB_NAME = "trainingdb"
$DB_USER = "postgres"

# Optional: Set PGPASSWORD environment variable if you want to avoid being prompted
$env:PGPASSWORD = 'vGbD6l2k4KuI8n7Gq7wb'

Write-Host "--- Starting Data Load for $DB_NAME ---" -ForegroundColor Cyan

# Define the files and target tables in correct dependency order
$data_files = @(
    @{ Table = "training.employee_fact"; File = "employee_fact_data.csv" },
    @{ Table = "training.catalog_fact";  File = "catalog_fact_data.csv" },
    @{ Table = "training.curriculum_fact"; File = "curriculum_fact_data.csv" },
    @{ Table = "training.transcript_fact"; File = "transcript_fact_data.csv" }
)

foreach ($item in $data_files) {
    $table = $item.Table
    $file = $item.File
    
    Write-Host "Loading $file into $table..." -NoNewline
    
    # Construct the psql command
    # \copy is a psql meta-command that runs a COPY FROM STDIN under the hood, 
    # which works even if the user doesn't have superuser permissions on RDS.
    $copy_cmd = "\copy $table FROM '$file' WITH (FORMAT csv, HEADER true, ENCODING 'UTF8')"
    
    & psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -c $copy_cmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host " [SUCCESS]" -ForegroundColor Green
    } else {
        Write-Host " [FAILED]" -ForegroundColor Red
        Write-Error "Failed to load $file. Check connection or data format."
        break
    }
}

Write-Host "--- Data Load Complete ---" -ForegroundColor Cyan
