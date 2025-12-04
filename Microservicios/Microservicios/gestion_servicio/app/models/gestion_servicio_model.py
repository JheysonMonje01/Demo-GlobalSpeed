from app.extensions import db
from datetime import datetime

class GestionServicio(db.Model):
    __tablename__ = 'gestion_servicio'

    id_gestion = db.Column(db.Integer, primary_key=True)
    id_usuario_pppoe = db.Column(db.Integer, nullable=False)
    id_contrato = db.Column(db.Integer, nullable=False)  # relación lógica externa
    estado_servicio = db.Column(db.Integer, nullable=False)  # 1=activo, 2=suspendido, 3=cortado
    motivo = db.Column(db.Text)
    usuario_admin_correo = db.Column(db.String(100))  # obtenido desde el JWT

    fecha_evento = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)

  

