from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, origins=[
        "http://localhost:5173",
        "http://192.168.1.4:5173",
        "http://172.31.192.1:5173"
    ], supports_credentials=True)
    
    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)

    from app.routes.auth_routes import auth_bp
    from app.routes.rol_routes import rol_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(rol_bp, url_prefix='/api')
    

    return app
