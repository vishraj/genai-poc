import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # AWS Configuration
    AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
    MODEL_ID = os.getenv("MODEL_ID", "global.anthropic.claude-sonnet-4-6")
    
    # Optional: explicit IAM user keys
    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    
    # Optional: named AWS profile
    AWS_PROFILE = os.getenv("AWS_PROFILE", "")

    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "")
