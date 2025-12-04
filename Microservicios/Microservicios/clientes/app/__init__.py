from flask import Flask
from app.config import Config
from app.db import db
from app.routes import persona_bp
from flask_cors import CORS
from app.routes import cliente_bp
from app.routes import tecnico_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, origins=[
        "http://localhost:5173",
        "http://192.168.1.4:5173",
        "http://172.31.192.1:5173"
    ], supports_credentials=True)

    db.init_app(app)

    app.register_blueprint(persona_bp, url_prefix='/api')
    app.register_blueprint(cliente_bp)
    app.register_blueprint(tecnico_bp)

    return app
