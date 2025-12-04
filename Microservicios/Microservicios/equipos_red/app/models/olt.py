# models/olt.py
from app.extensions import db
from datetime import datetime
from app.models.tarjeta_olt import TarjetaOLT

class OLT(db.Model):
    __tablename__ = 'olt'

    id_olt = db.Column(db.Integer, primary_key=True)
    id_datacenter = db.Column(db.Integer, db.ForeignKey('datacenter.id_datacenter'), nullable=False)
    marca = db.Column(db.String(100), nullable=False)
    modelo = db.Column(db.String(100), nullable=False)
    capacidad = db.Column(db.Integer, nullable=False)
    slots_ocupados = db.Column(db.Integer, default=0)
    ip_gestion = db.Column(db.String(100), nullable=False)
    usuario_gestion = db.Column(db.String(100), nullable=False)  # NUEVO
    contrasena_gestion = db.Column(db.String(100), nullable=False)  # NUEVO
    estado = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    datacenter = db.relationship("DataCenter", backref="olts", lazy=True)
    tarjetas_olt = db.relationship("TarjetaOLT", backref="olt", cascade="all, delete-orphan", lazy=True)

    def actualizar_slots_ocupados(self):
        self.slots_ocupados = len([
        tarjeta for tarjeta in self.tarjetas_olt 
        if tarjeta.estado is True
    ])
