import os
import requests
from flask import session, redirect, url_for, request
from oauthlib.oauth2 import WebApplicationClient
from requests_oauthlib import OAuth2Session
from app.config import Config
from app.utils.dynamo_manager import upsert_user
from flask_jwt_extended import create_access_token

client = WebApplicationClient(Config.GOOGLE_CLIENT_ID)

def get_google_provider_cfg():
    try:
        return requests.get(Config.GOOGLE_DISCOVERY_URL).json()
    except Exception as e:
        raise RuntimeError("Failed to fetch Google provider configuration") from e

def get_google_flow():
    return OAuth2Session(
        client_id=Config.GOOGLE_CLIENT_ID,
        redirect_uri=url_for("auth.callback", _external=True),
        scope=["openid", "email", "profile"]
    )

def fetch_token(flow):
    token_url = get_google_provider_cfg().get("token_endpoint")
    try:
        flow.fetch_token(
            token_url=token_url,
            authorization_response=request.url,
            client_secret=Config.GOOGLE_CLIENT_SECRET
        )
    except Exception as e:
        raise RuntimeError("Failed to fetch token from Google") from e

def fetch_user_info(flow):
    userinfo_endpoint = get_google_provider_cfg().get("userinfo_endpoint")
    try:
        resp = flow.get(userinfo_endpoint)
        return resp.json()
    except Exception as e:
        raise RuntimeError("Failed to fetch user info from Google") from e

def store_user_session(user_info):
    access_token = create_access_token(identity=user_info["sub"])
    session["access_token"] = access_token
    session["user"] = {
        "user_id": user_info["sub"],
        "email": user_info["email"],
        "name": user_info["name"],
        "picture": user_info["picture"]
    }
    return access_token

def handle_google_callback():
    flow = get_google_flow()
    fetch_token(flow)
    user_info = fetch_user_info(flow)

    if not user_info.get("email_verified"):
        return {"error": "Email not verified"}, 400

    store_user_session(user_info)
    upsert_user(user_info)
    return redirect("/")
