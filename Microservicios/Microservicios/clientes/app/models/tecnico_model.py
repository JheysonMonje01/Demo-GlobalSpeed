from app.db import db
from datetime import datetime

class Tecnico(db.Model):
    __tablename__ = 'tecnico'

    id_tecnico = db.Column(db.Integer, primary_key=True)
    id_persona = db.Column(db.Integer, db.ForeignKey('persona.id_persona', ondelete='CASCADE'), unique=True, nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='activo')
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
