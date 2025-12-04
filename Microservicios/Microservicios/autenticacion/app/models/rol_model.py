from app import db

class Rol(db.Model):
    __tablename__ = 'roles'

    id_rol = db.Column(db.Integer, primary_key=True)
    nombre_rol = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(255))
    estado = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    fecha_modificacion = db.Column(db.DateTime, onupdate=db.func.current_timestamp())

    # Aquí está la relación
    usuarios = db.relationship('Usuario', back_populates='rol', cascade="all, delete", lazy=True)
