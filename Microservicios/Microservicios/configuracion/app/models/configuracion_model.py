from app.extensions import db

class Configuracion(db.Model):
    __tablename__ = 'configuracion'

    id_configuracion = db.Column(db.Integer, primary_key=True)
    clave = db.Column(db.String(100), unique=True, nullable=False)
    valor = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    id_usuario = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.now())
    fecha_modificacion = db.Column(db.DateTime, onupdate=db.func.now())

