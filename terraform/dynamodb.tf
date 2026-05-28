resource "aws_dynamodb_table" "chat_history" {
  name           = "FedCashChatHistory"
  billing_mode   = "PROVISIONED"
  read_capacity  = 5
  write_capacity = 5
  hash_key       = "session_id"

  attribute {
    name = "session_id"
    type = "S"
  }

  tags = {
    Environment = "production"
    Application = "GenAI-PoC"
  }
}
