'''from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.extensions import db

class ONU(db.Model):
    __tablename__ = 'onu'

    id_onu = db.Column(db.Integer, primary_key=True)
    serial_number = db.Column(db.String(100), nullable=False, unique=True)
    ont_id = db.Column(db.String(50), nullable=True)
    modelo_onu = db.Column(db.String(100), nullable=False)
    numero_puerto_nap = db.Column(db.Integer, nullable=True)

    id_caja = db.Column(db.Integer, db.ForeignKey('caja_nap.id_caja'), nullable=True)
    id_puerto_pon_olt = db.Column(db.Integer, db.ForeignKey('puertos_pon_olt.id_puerto_pon_olt'), nullable=False)
    id_contrato = db.Column(db.Integer) #db.ForeignKey('contrato.id_contrato'), nullable=False)

    estado = db.Column(db.String(20), default='pendiente')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    puerto_pon = relationship("PuertoPONOLT", backref="onus")
    #contrato = relationship("Contrato", backref="onus")
    # relación con caja ya está definida como backref desde la clase CajaNAP'''

from app.extensions import db
from datetime import datetime

class ONU(db.Model):
    __tablename__ = 'onu'

    id_onu = db.Column(db.Integer, primary_key=True)
    
    serial = db.Column(db.String(100), nullable=False, unique=True)
    modelo_onu = db.Column(db.String(100), nullable=True)

    id_caja = db.Column(db.Integer, db.ForeignKey('caja_nap.id_caja'), nullable=True)
    id_contrato = db.Column(db.Integer, nullable=True)
    id_puerto_pon_olt = db.Column(db.Integer, db.ForeignKey('puertos_pon_olt.id_puerto_pon_olt'), nullable=True)
    
    numero_puerto_nap = db.Column(db.Integer, nullable=True)
    ont_id = db.Column(db.Integer, nullable=True)
    
    estado = db.Column(db.String(30), nullable=False, default='libre')
    
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones (usamos back_populates para evitar conflicto de nombres)
    #caja = db.relationship("CajaNAP", back_populates="onus", lazy=True)
    #puerto_pon = db.relationship("PuertoPONOLT", back_populates="onus", lazy=True)


