from flask import Flask, send_from_directory
from app.config import Config
from app.extensions import db
from app.routes.contrato_routes import contrato_bp
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    # Carpeta pública para los contratos generados
    CONTRATO_FOLDER = os.path.join(os.getcwd(), "archivos", "contratos")

    # Inicializar extensiones
    db.init_app(app)

    # Registrar Blueprints
    app.register_blueprint(contrato_bp)

    return app
