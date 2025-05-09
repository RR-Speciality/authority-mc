import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "your-secret-key"
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
    GOOGLE_DISCOVERY_URL = os.environ.get("GOOGLE_DISCOVERY_URL")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") or "your-jwt-secret-key"
    AWS_REGION = os.environ.get("AWS_REGION")
    DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE")