import boto3
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_users_table():
    """
    Create the users table in DynamoDB if it doesn't exist
    """
    try:
        # Get configuration from environment
        table_name = os.getenv("DYNAMODB_TABLE")
        region = os.getenv("AWS_REGION")
        
        if not table_name or not region:
            raise ValueError("DYNAMODB_TABLE and AWS_REGION must be set in environment")
        
        # Create DynamoDB client
        dynamodb = boto3.client("dynamodb", region_name=region)
        
        # Check if table exists
        existing_tables = dynamodb.list_tables()["TableNames"]
        if table_name in existing_tables:
            print(f"Table {table_name} already exists")
            return
        
        # Create table
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    "AttributeName": "user_id",
                    "KeyType": "HASH"
                }
            ],
            AttributeDefinitions=[
                {
                    "AttributeName": "user_id",
                    "AttributeType": "S"
                }
            ],
            BillingMode="PAY_PER_REQUEST"
        )
        
        print(f"Created table {table_name}")
        return response
        
    except Exception as e:
        print(f"Error creating table: {str(e)}")
        raise

if __name__ == "__main__":
    create_users_table()
