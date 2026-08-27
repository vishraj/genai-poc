import json
import uuid
from datetime import datetime
from botocore.exceptions import ClientError
from utils.aws_clients import aws_manager

TABLE_NAME = "FedCashChatHistory"

class HistoryService:
    def __init__(self):
        self.db = aws_manager.dynamodb
        self.table = self.db.Table(TABLE_NAME)
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        """Creates the DynamoDB table if it does not exist."""
        try:
            self.table.table_status
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFoundException':
                print(f"Creating DynamoDB table: {TABLE_NAME}...")
                self.db.create_table(
                    TableName=TABLE_NAME,
                    KeySchema=[
                        {'AttributeName': 'session_id', 'KeyType': 'HASH'}
                    ],
                    AttributeDefinitions=[
                        {'AttributeName': 'session_id', 'AttributeType': 'S'}
                    ],
                    ProvisionedThroughput={
                        'ReadCapacityUnits': 5,
                        'WriteCapacityUnits': 5
                    }
                )
                # Wait for table to be created
                self.table.meta.client.get_waiter('table_exists').wait(TableName=TABLE_NAME)
                print("Table created successfully.")
            else:
                raise

    def save_session(self, session_id: str, title: str, messages: list, user_id: str = ""):
        """Saves or updates a chat session for a specific user_id."""
        try:
            item = {
                'session_id': session_id,
                'title': title,
                'user_id': user_id,
                'updated_at': datetime.now().isoformat(),
                'messages': json.dumps(messages)
            }
            self.table.put_item(Item=item)
        except Exception as e:
            print(f"[HistoryService] Save error: {e}")

    def list_sessions(self, user_id: str = "") -> list:
        """Returns sessions for the specified user_id, sorted by update time (descending)."""
        try:
            response = self.table.scan()
            items = response.get('Items', [])
            if user_id:
                items = [x for x in items if x.get('user_id') == user_id]
            else:
                items = []
            # Sort by updated_at descending
            items.sort(key=lambda x: x.get('updated_at', ''), reverse=True)
            return items
        except Exception as e:
            print(f"[HistoryService] List error: {e}")
            return []

    def get_session(self, session_id: str, user_id: str = "") -> dict:
        """Retrieves a specific session by ID, ensuring user authorization."""
        try:
            response = self.table.get_item(Key={'session_id': session_id})
            item = response.get('Item')
            if item:
                if user_id and item.get('user_id') and item.get('user_id') != user_id:
                    print(f"[HistoryService] Unauthorized session access attempt: {session_id} by {user_id}")
                    return None
                if 'messages' in item:
                    item['messages'] = json.loads(item['messages'])
            return item
        except Exception as e:
            print(f"[HistoryService] Get error: {e}")
            return None

    def delete_session(self, session_id: str):
        """Deletes a session."""
        try:
            self.table.delete_item(Key={'session_id': session_id})
        except Exception as e:
            print(f"[HistoryService] Delete error: {e}")

    def create_new_session_id(self) -> str:
        return str(uuid.uuid4())
