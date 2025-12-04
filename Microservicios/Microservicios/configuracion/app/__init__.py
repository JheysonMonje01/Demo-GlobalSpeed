from flask import Flask
from app.extensions import db
from app.routes.empresa_routes import empresa_bp
from app.routes.configuracion_routes import config_bp
from app.routes.mikrotik_routes import mikrotik_bp
from app.config import Config
from flask_cors import CORS
from app.routes.interface_routes import interface_bp
from app.routes.olt_comandos_routes import olt_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)

    app.register_blueprint(empresa_bp, url_prefix='/api')
    app.register_blueprint(config_bp, url_prefix='/api')
    app.register_blueprint(mikrotik_bp, url_prefix='/mikrotik')
    app.register_blueprint(interface_bp)
    app.register_blueprint(olt_bp)


    return app
