from app import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id_usuario = db.Column(db.Integer, primary_key=True)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(15), unique=True)
    id_rol = db.Column(db.Integer, db.ForeignKey('roles.id_rol'), nullable=False)
    estado = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=db.func.current_timestamp())
    fecha_modificacion = db.Column(db.DateTime, onupdate=db.func.current_timestamp())

    # Relación inversa
    rol = db.relationship('Rol', back_populates='usuarios')
