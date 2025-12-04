from app.extensions import db
from datetime import datetime


class TarjetaOLT(db.Model):
    __tablename__ = 'tarjeta_olt'

    id_tarjeta_olt = db.Column(db.Integer, primary_key=True)
    id_olt = db.Column(db.Integer, db.ForeignKey('olt.id_olt'), nullable=False)
    slot_numero = db.Column(db.Integer, nullable=False)  # NUEVO
    nombre = db.Column(db.String(100), nullable=False)
    capacidad_puertos_pon = db.Column(db.Integer, nullable=False)  # NUEVO
    estado = db.Column(db.Boolean, default=True)  # NUEVO
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

