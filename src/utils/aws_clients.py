import boto3
from .config import Config

class AWSClientManager:
    def __init__(self):
        if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
            self.session = boto3.Session(
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
                region_name=Config.AWS_REGION,
            )
        elif Config.AWS_PROFILE:
            self.session = boto3.Session(
                profile_name=Config.AWS_PROFILE,
                region_name=Config.AWS_REGION,
            )
        else:
            self.session = boto3.Session(region_name=Config.AWS_REGION)

        self._bedrock_runtime = None

    @property
    def bedrock_runtime(self):
        if self._bedrock_runtime is None:
            self._bedrock_runtime = self.session.client("bedrock-runtime")
        return self._bedrock_runtime

# Singleton instance
aws_manager = AWSClientManager()
