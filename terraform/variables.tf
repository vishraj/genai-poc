variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "us-east-1"
}

variable "db_password" {
  description = "Password for the RDS PostgreSQL database"
  type        = string
  sensitive   = true
}

variable "db_username" {
  description = "Username for the RDS PostgreSQL database"
  type        = string
  default     = "postgres"
}
