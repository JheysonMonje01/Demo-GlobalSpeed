from app.extensions import db
from datetime import datetime

class InformacionMetodoPago(db.Model):
    __tablename__ = 'informacion_metodo_pago'

    id_info = db.Column(db.Integer, primary_key=True)
    
    id_metodo_pago = db.Column(db.Integer, db.ForeignKey('metodo_pago.id_metodo_pago', ondelete="CASCADE"), nullable=False)

    nombre_beneficiario = db.Column(db.String(100))
    numero_cuenta = db.Column(db.String(30))
    tipo_cuenta = db.Column(db.String(30))  # Ej: 'Ahorros', 'Corriente'
    entidad_financiera = db.Column(db.String(100))
    instrucciones = db.Column(db.Text)  # Texto adicional para mostrar al cliente (opcional)

    estado = db.Column(db.Boolean, default=True)

    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relación opcional con MetodoPago si deseas acceder desde el modelo
    metodo_pago = db.relationship('MetodoPago', backref='informacion_adicional', lazy=True)


