output "rds_endpoint" {
  description = "The endpoint of the RDS instance"
  value       = aws_db_instance.learningdb.endpoint
}

output "dynamodb_table_name" {
  description = "The name of the DynamoDB table"
  value       = aws_dynamodb_table.chat_history.name
}

output "iam_access_key_id" {
  description = "The access key ID for the application user"
  value       = aws_iam_access_key.app_user_key.id
}

output "iam_secret_access_key" {
  description = "The secret access key for the application user"
  value       = aws_iam_access_key.app_user_key.secret
  sensitive   = true
}
