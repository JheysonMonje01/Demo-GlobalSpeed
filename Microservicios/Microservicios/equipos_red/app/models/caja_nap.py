from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.extensions import db
from app.models.onu import ONU

class CajaNAP(db.Model):
    __tablename__ = 'caja_nap'

    id_caja = db.Column(db.Integer, primary_key=True)
    nombre_caja_nap = db.Column(db.String(100), nullable=False)
    ubicacion = db.Column(db.String(255), nullable=False)
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    observacion = db.Column(db.Text, nullable=True)
    
    capacidad_puertos_cliente = db.Column(db.Integer, nullable=False)
    puertos_ocupados = db.Column(db.Integer, default=0)
    
    estado = db.Column(db.Boolean, default=True)
    radio_cobertura = db.Column(db.Float, nullable=True)

    id_puerto_pon_olt = db.Column(
        db.Integer, 
        db.ForeignKey('puertos_pon_olt.id_puerto_pon_olt', ondelete='CASCADE'), 
        nullable=False
    )

    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    puerto_pon = relationship("PuertoPONOLT", backref="cajas_nap", lazy=True)
    #onus = relationship("ONU", back_populates="caja", cascade="all, delete-orphan", lazy=True)

    def actualizar_puertos_ocupados(self):
        self.puertos_ocupados = len([onu for onu in self.onus if onu.estado])
