from flask import Flask
from flask_cors import CORS
from app.extensions import db, ma  # ✅ usa las instancias correctas

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config.from_object('app.config.Config')

    db.init_app(app)  # ✅ registra app con SQLAlchemy
    ma.init_app(app)

    from app.routes.datacenter_routes import datacenter_bp
    from app.routes.olt_routes import olt_bp
    from app.routes.tarjeta_olt_routes import tarjeta_olt_bp
    from app.routes.puerto_pon_olt_routes import puerto_bp
    from app.routes.caja_nap_routes import caja_nap_bp
    #from app.routes.onu_routes import onu_bp
    #from app.routes.simulador_mapper import onu_sim_bp
    from app.routes.vlan_routes import vlan_bp
    from app.routes.ip_pool_routes import ip_pool_bp
    from app.routes.onu_routes import onu_bp

    app.register_blueprint(datacenter_bp)
    app.register_blueprint(olt_bp)
    app.register_blueprint(tarjeta_olt_bp)
    app.register_blueprint(puerto_bp)
    app.register_blueprint(caja_nap_bp)
    app.register_blueprint(onu_bp)
    #app.register_blueprint(onu_sim_bp)
    app.register_blueprint(vlan_bp, url_prefix='/api')
    app.register_blueprint(ip_pool_bp, url_prefix='/pools')

    return app
