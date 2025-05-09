from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.routes.auth_routes import auth_bp
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app)
    
    jwt = JWTManager(app)

    app.register_blueprint(auth_bp)
    return app
