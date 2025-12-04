from flask import Flask, send_from_directory
from app.config import Config
from app.extensions import db
from app.routes.orden_instalacion_routes import ordenes_bp
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    # Carpeta pública para los contratos generados
    ORDENES_FOLDER = os.path.join(os.getcwd(), "archivos", "ordenes")

    # Inicializar extensiones
    db.init_app(app)

    # Registrar Blueprints
    app.register_blueprint(ordenes_bp)

    return app
