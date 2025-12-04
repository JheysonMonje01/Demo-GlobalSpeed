from app.extensions import db

class VLAN(db.Model):
    __tablename__ = 'vlan'

    id_vlan = db.Column(db.Integer, primary_key=True)
    numero_vlan = db.Column(db.Integer, unique=True, nullable=False)
    nombre = db.Column(db.String(50))
    interface_destino = db.Column(db.String(50))
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    fecha_modificacion = db.Column(db.DateTime, onupdate=db.func.current_timestamp())
    id_mikrotik = db.Column(db.Integer, nullable=False)  # ➕ nuevo campo
