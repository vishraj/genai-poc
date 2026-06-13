output "rds_endpoint" {
  description = "The endpoint of the RDS Aurora cluster"
  value       = aws_rds_cluster.learningdb.endpoint
}

output "dynamodb_table_name" {
  description = "The name of the DynamoDB table"
  value       = aws_dynamodb_table.chat_history.name
}

