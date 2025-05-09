import boto3
import os
from datetime import datetime
from botocore.exceptions import BotoCoreError, ClientError

TABLE_NAME = os.getenv("DYNAMODB_TABLE")
REGION = os.getenv("AWS_REGION")

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(TABLE_NAME)


def upsert_user(user_info):
    try:
        table.put_item(Item={
            "user_id": user_info["sub"],
            "email": user_info["email"],
            "name": user_info["name"],
            "picture": user_info["picture"],
            "last_login": datetime.utcnow().isoformat()
        })
    except (BotoCoreError, ClientError) as e:
        raise RuntimeError("Failed to upsert user to DynamoDB") from e


def get_user(user_id):
    try:
        response = table.get_item(Key={"user_id": user_id})
        return response.get("Item")
    except (BotoCoreError, ClientError) as e:
        raise RuntimeError("Failed to retrieve user from DynamoDB") from e