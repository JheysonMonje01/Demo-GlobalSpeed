from app.extensions import db
from sqlalchemy.sql import func

class DataCenter(db.Model):
    __tablename__ = 'datacenter'

    id_datacenter = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ubicacion = db.Column(db.String(255), nullable=False)
    latitud = db.Column(db.Float)
    longitud = db.Column(db.Float)
    fecha_creacion = db.Column(db.DateTime(timezone=True), server_default=func.now())
    fecha_modificacion = db.Column(db.DateTime(timezone=True), onupdate=func.now())
