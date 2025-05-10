import boto3
import os
import logging
from datetime import datetime
from botocore.exceptions import BotoCoreError, ClientError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# DynamoDB Configuration
TABLE_NAME = os.getenv("DYNAMODB_TABLE")
REGION = os.getenv("AWS_REGION")

if not TABLE_NAME or not REGION:
    raise ValueError("DYNAMODB_TABLE and AWS_REGION environment variables must be set")

try:
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    table = dynamodb.Table(TABLE_NAME)
except Exception as e:
    logger.error(f"Failed to initialize DynamoDB: {str(e)}")
    raise

def upsert_user(user_info):
    """
    Create or update a user in DynamoDB
    """
    if not user_info.get("sub"):
        raise ValueError("user_info must contain 'sub' field")
    
    try:
        item = {
            "user_id": user_info["sub"],
            "email": user_info["email"],
            "name": user_info["name"],
            "picture": user_info["picture"],
            "last_login": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Upserting user {item['user_id']}")
        table.put_item(Item=item)
        return item
    except (BotoCoreError, ClientError) as e:
        logger.error(f"DynamoDB error: {str(e)}")
        raise RuntimeError(f"Failed to upsert user to DynamoDB: {str(e)}") from e
    except KeyError as e:
        logger.error(f"Missing required field: {str(e)}")
        raise ValueError(f"Missing required field in user_info: {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise

def get_user(user_id):
    """
    Retrieve a user from DynamoDB by user_id
    """
    if not user_id:
        raise ValueError("user_id must not be empty")
        
    try:
        logger.info(f"Getting user {user_id}")
        response = table.get_item(Key={"user_id": user_id})
        return response.get("Item")
    except (BotoCoreError, ClientError) as e:
        logger.error(f"DynamoDB error: {str(e)}")
        raise RuntimeError(f"Failed to retrieve user from DynamoDB: {str(e)}") from e
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise