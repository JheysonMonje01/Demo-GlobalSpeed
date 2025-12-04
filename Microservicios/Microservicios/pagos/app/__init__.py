from flask import Flask
from app.extensions import db, ma
from app.routes.pago_routes import pago_bp
from app.routes.metodo_pago_routes import metodo_pago_bp
from app.routes.informacion_metodo_pago_routes import informacion_metodo_pago_bp
from app.routes.orden_pago_routes import orden_pago_bp  
from os import path
import os
from app.config import Config
from flask_cors import CORS

# Crear carpeta para comprobantes si no existe
os.makedirs(Config.DIRECTORIO_COMPROBANTES, exist_ok=True)

def create_app():
    app = Flask(__name__)

    app.config.from_object('app.config.Config')
    CORS(app, resources={r"/*": {"origins": ["http://localhost:5173"]}},
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers="*")

    db.init_app(app)
    ma.init_app(app)

    # Registrar blueprints
    app.register_blueprint(pago_bp, url_prefix="/pagos")
    app.register_blueprint(metodo_pago_bp, url_prefix="/metodos_pago")
    app.register_blueprint(informacion_metodo_pago_bp, url_prefix="/informacion_metodos_pago")
    app.register_blueprint(orden_pago_bp, url_prefix="/orden_pago")  # ✅ Añadido

    # Servir comprobantes
    from flask import send_from_directory

    @app.route('/archivos/comprobantes/<int:id_pago>/<filename>')
    def serve_comprobante(id_pago, filename):
        carpeta = os.path.join(Config.DIRECTORIO_COMPROBANTES, str(id_pago))
        return send_from_directory(carpeta, filename)

    return app
