from flask import Flask
from app.config import Config
from app.extensions import db, ma
from app.routes.plan_routes import plan_bp
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    # Inicializar extensiones
    db.init_app(app)
    ma.init_app(app)

    # Registrar Blueprints
    app.register_blueprint(plan_bp, url_prefix='/planes')

    return app
