from app.extensions import db
from datetime import datetime

class MetodoPago(db.Model):
    __tablename__ = 'metodo_pago'

    id_metodo_pago = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.String(255))
    requiere_verificacion = db.Column(db.Boolean, default=False)
    estado = db.Column(db.Boolean, default=True)
    orden_visualizacion = db.Column(db.Integer, default=0)

    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, onupdate=datetime.utcnow)
