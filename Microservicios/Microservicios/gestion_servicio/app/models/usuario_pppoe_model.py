from app.extensions import db
from datetime import datetime

class UsuarioPPPoE(db.Model):
    __tablename__ = 'usuario_pppoe'

    id_usuario_pppoe = db.Column(db.Integer, primary_key=True)
    id_contrato = db.Column(db.Integer, nullable=False)  # valor obtenido por HTTP externo
    usuario_pppoe = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.String(255), nullable=False)  # idealmente encriptada
    nombre_cliente = db.Column(db.String(100))
    ip_remota = db.Column(db.String(15))  # Puede ser NULL
    estado = db.Column(db.Boolean, default=True)  # TRUE = activo
    mikrotik_nombre = db.Column(db.String(100))  # Identificador lógico del router

    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, onupdate=datetime.utcnow)


