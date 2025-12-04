from app.extensions import db
from datetime import datetime

class PlanInternet(db.Model):
    __tablename__ = 'planes'

    id_plan = db.Column(db.Integer, primary_key=True)
    nombre_plan = db.Column(db.String(50), nullable=False, unique=True)
    velocidad_subida = db.Column(db.Integer, nullable=False)  # en Kbps
    velocidad_bajada = db.Column(db.Integer, nullable=False)
    rafaga_subida = db.Column(db.Integer, nullable=True)
    rafaga_bajada = db.Column(db.Integer, nullable=True)
    max_subida = db.Column(db.Integer, nullable=True)
    max_bajada = db.Column(db.Integer, nullable=True)
    tiempo_rafaga_subida = db.Column(db.Integer, nullable=True)
    tiempo_rafaga_bajada = db.Column(db.Integer, nullable=True)

    ip_local = db.Column(db.String(50), nullable=False)
    ip_remota = db.Column(db.String(50), nullable=False)
    dns = db.Column(db.String(50), nullable=True)

    precio = db.Column(db.Numeric(10, 2), nullable=False)  # 💰 Campo obligatorio

    id_vlan = db.Column(db.Integer, nullable=False)  # Foreign Key (asociación lógica)
    address_list = db.Column(db.String(100))



    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, onupdate=datetime.utcnow)
