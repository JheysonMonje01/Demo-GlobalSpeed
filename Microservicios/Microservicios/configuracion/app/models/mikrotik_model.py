from app.extensions import db
from datetime import datetime

class MikrotikAPIConfig(db.Model):
    __tablename__ = 'mikrotik_api_config'

    id_mikrotik = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    host = db.Column(db.String(100), nullable=False)
    puerto = db.Column(db.Integer, default=8728)
    usuario = db.Column(db.String(100), nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)  # Se puede cifrar
    estado = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, onupdate=datetime.utcnow)
