from flask import Blueprint, redirect, session, url_for, jsonify
from app.services.oauth_service import get_google_flow, handle_google_callback, GOOGLE_SCOPES
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.dynamo_manager import get_user

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login")
def login():
    try:
        flow, authorization_endpoint = get_google_flow()
        authorization_url, state = flow.authorization_url(
            url=authorization_endpoint,
            prompt="consent",
            access_type="offline",
            include_granted_scopes="true"
        )
        # Store state and scope in session
        session["oauth_state"] = state
        session["oauth_scope"] = GOOGLE_SCOPES
        return redirect(authorization_url)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/callback")
def callback():
    return handle_google_callback()

@auth_bp.route("/logout")
def logout():
    try:
        session.clear()
        return jsonify({"message": "Successfully logged out"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/me")
@jwt_required()
def me():
    try:
        user_id = get_jwt_identity()
        user = get_user(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
            
        return jsonify(user)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
