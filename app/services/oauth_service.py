import os
import requests
import logging
from flask import session, redirect, url_for, request, jsonify, current_app
from oauthlib.oauth2 import WebApplicationClient
from requests_oauthlib import OAuth2Session
from app.config import Config
from app.utils.dynamo_manager import upsert_user, get_user
from flask_jwt_extended import create_access_token

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Allow OAuth over HTTP for development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Define Google OAuth2 scopes
GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "openid"
]

client = WebApplicationClient(Config.GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    try:
        return requests.get(Config.GOOGLE_DISCOVERY_URL).json()
    except Exception as e:
        logger.error(f"Failed to fetch Google provider configuration: {str(e)}")
        raise RuntimeError("Failed to fetch Google provider configuration") from e

def get_google_flow():
    try:
        provider_cfg = get_google_provider_cfg()
        authorization_endpoint = provider_cfg["authorization_endpoint"]
        
        # Get the callback URL
        callback_url = url_for("auth.callback", _external=True)
        logger.debug(f"Callback URL: {callback_url}")
        
        flow = OAuth2Session(
            client_id=Config.GOOGLE_CLIENT_ID,
            redirect_uri=callback_url,
            scope=GOOGLE_SCOPES
        )
        
        return flow, authorization_endpoint
    except Exception as e:
        logger.error(f"Failed to create OAuth flow: {str(e)}")
        raise

def fetch_token(flow):
    try:
        provider_cfg = get_google_provider_cfg()
        token_url = provider_cfg.get("token_endpoint")
        if not token_url:
            raise RuntimeError("Failed to get token endpoint from provider configuration")
        
        logger.debug(f"Fetching token from {token_url}")
        logger.debug(f"Request URL: {request.url}")
        
        # Get original scopes from session
        original_scope = session.get('oauth_scope')
        logger.debug(f"Original scope: {original_scope}")
        
        token = flow.fetch_token(
            token_url=token_url,
            client_secret=Config.GOOGLE_CLIENT_SECRET,
            authorization_response=request.url,
            include_client_id=True
        )
        
        logger.debug(f"Token received: {token.keys()}")
        return token
        
    except Exception as e:
        logger.error(f"Failed to fetch OAuth token: {str(e)}")
        raise RuntimeError(f"Failed to fetch OAuth token: {str(e)}") from e

def fetch_user_info(flow):
    try:
        userinfo_endpoint = get_google_provider_cfg().get("userinfo_endpoint")
        if not userinfo_endpoint:
            raise RuntimeError("Failed to get userinfo endpoint from provider configuration")
        
        logger.debug(f"Fetching user info from {userinfo_endpoint}")
        resp = flow.get(userinfo_endpoint)
        
        if resp.status_code != 200:
            raise RuntimeError(f"Failed to get user info: {resp.status_code}")
        
        user_info = resp.json()
        logger.debug(f"User info received: {user_info.keys()}")
        return user_info
        
    except Exception as e:
        logger.error(f"Failed to fetch user info: {str(e)}")
        raise RuntimeError("Failed to fetch user info") from e

def store_user_session(user_info):
    try:
        if not user_info.get("sub"):
            raise ValueError("Invalid user info: missing sub")
        
        # Store in DynamoDB
        upsert_user(user_info)
        
        # Create JWT token
        access_token = create_access_token(identity=user_info["sub"])
        
        # Store in session
        session["user"] = user_info
        
        return access_token
    except Exception as e:
        logger.error(f"Failed to store user session: {str(e)}")
        raise RuntimeError("Failed to store user session") from e

def handle_google_callback():
    try:
        # Verify state
        stored_state = session.get("oauth_state")
        received_state = request.args.get("state")
        
        logger.debug(f"Stored state: {stored_state}")
        logger.debug(f"Received state: {received_state}")
        
        if stored_state != received_state:
            logger.error("State mismatch")
            return jsonify({"error": "Invalid state parameter"}), 400
        
        # Get OAuth2 flow
        flow, _ = get_google_flow()
        
        # Fetch token
        token = fetch_token(flow)
        
        # Get user info
        user_info = fetch_user_info(flow)
        
        # Store session and create JWT
        access_token = store_user_session(user_info)
        
        return jsonify({
            "access_token": access_token,
            "user": user_info
        })
    except Exception as e:
        logger.error(f"Callback error: {str(e)}")
        return jsonify({"error": str(e)}), 500
