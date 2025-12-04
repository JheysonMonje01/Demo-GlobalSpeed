from app.extensions import db
from datetime import datetime

class Contrato(db.Model):
    __tablename__ = 'contrato'

    id_contrato = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, nullable=False)
    id_plan = db.Column(db.Integer, nullable=False)
    id_empresa = db.Column(db.Integer, nullable=False)
    ubicacion = db.Column(db.String(100), nullable=False)
    latitud = db.Column(db.Float, nullable=True)      # ✅ NUEVO
    longitud = db.Column(db.Float, nullable=True)     # ✅ NUEVO
    url_archivo = db.Column(db.Text)
    fecha_fin_contrato = db.Column(db.Date)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, onupdate=datetime.utcnow)
