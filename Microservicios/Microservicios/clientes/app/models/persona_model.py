from app.db import db
from datetime import datetime

class Persona(db.Model):
    __tablename__ = 'persona'

    id_persona = db.Column(db.Integer, primary_key=True)
    cedula_ruc = db.Column(db.String(13), unique=True, nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    apellido = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(15), nullable=False)
    correo = db.Column(db.String(100), nullable=False)
    direccion_domiciliaria = db.Column(db.String(50))
    foto = db.Column(db.LargeBinary)
    id_usuario = db.Column(db.Integer, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime)

    cliente = db.relationship('Cliente', backref='persona', uselist=False)
    tecnico = db.relationship('Tecnico', backref='persona', uselist=False)
    administrador = db.relationship('Administrador', backref='persona', uselist=False)
