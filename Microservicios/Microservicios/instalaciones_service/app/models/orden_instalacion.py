from app.extensions import db
from datetime import datetime

class OrdenInstalacion(db.Model):
    __tablename__ = "ordenes_instalacion"

    id_orden = db.Column(db.Integer, primary_key=True)
    id_contrato = db.Column(db.Integer, nullable=False)
    ubicacion_instalacion = db.Column(db.Text, nullable=False)
    id_tecnico = db.Column(db.Integer, nullable=True)
    estado = db.Column(db.String(30), nullable=False, default="pendiente_asignacion")
    documento_pdf = db.Column(db.Text)
    fecha_asignacion = db.Column(db.DateTime)
    fecha_instalacion = db.Column(db.DateTime)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
