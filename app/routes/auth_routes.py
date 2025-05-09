from flask import Blueprint, redirect, session, url_for, jsonify
from app.services.oauth_service import get_google_flow, handle_google_callback
from flask_jwt_extended import jwt_required, get_jwt_identity

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login")
def login():
    flow = get_google_flow()
    authorization_url, state = flow.authorization_url(
        prompt="consent",
        access_type="offline",
        include_granted_scopes="true"
    )
    session["oauth_state"] = state
    return redirect(authorization_url)

@auth_bp.route("/callback")
def callback():
    return handle_google_callback()

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@auth_bp.route("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user_info = session.get("user")
    if not user_info:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(user_info)
