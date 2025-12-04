# app/models/puerto_pon_olt.py
from app.extensions import db
from datetime import datetime
from app.models.tarjeta_olt import TarjetaOLT
from app.models.onu import ONU

class PuertoPONOLT(db.Model):
    __tablename__ = 'puertos_pon_olt'

    id_puerto_pon_olt = db.Column(db.Integer, primary_key=True)
    id_tarjeta_olt = db.Column(db.Integer, db.ForeignKey('tarjeta_olt.id_tarjeta_olt'), nullable=False)
    numero_puerto = db.Column(db.Integer, nullable=False)
    estado_puerto = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tarjeta = db.relationship("TarjetaOLT", backref="puertos_pon", lazy=True)
    #onus = db.relationship("ONU", back_populates="puerto_pon", cascade="all, delete-orphan", lazy=True)