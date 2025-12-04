from flask import Flask
from app.extensions import db
from app.routes.pppoe_routes import pppoe_bp
from app.routes.gestion_routes import gestion_bp
from app.config import Config
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)

    from app.routes.pppoe_routes import pppoe_bp 
    app.register_blueprint(pppoe_bp, url_prefix='/pppoe')
    app.register_blueprint(gestion_bp, url_prefix='/gestion')
    
    
    
    return app
