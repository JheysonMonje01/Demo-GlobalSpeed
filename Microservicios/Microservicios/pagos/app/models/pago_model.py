from app.extensions import db
from datetime import datetime

class Pago(db.Model):
    __tablename__ = 'pago'

    id_pago = db.Column(db.Integer, primary_key=True)

    id_contrato = db.Column(db.Integer, nullable=False)
    id_metodo_pago = db.Column(db.Integer, db.ForeignKey('metodo_pago.id_metodo_pago', ondelete="RESTRICT"), nullable=False)

    monto = db.Column(db.Numeric(10, 2), nullable=False)
    mes_correspondiente = db.Column(db.Date, nullable=False)

    comprobante = db.Column(db.String(255))  # Ruta del archivo o base64
    observacion = db.Column(db.String(255))

    estado = db.Column(db.Boolean, default=False)
    
    # 🔁 Eliminamos la ForeignKey y mantenemos el campo como Integer
    verificado_por = db.Column(db.Integer, nullable=True)

    fecha_verificacion = db.Column(db.DateTime)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, onupdate=datetime.utcnow)

    metodo_pago = db.relationship("MetodoPago", backref="pagos", lazy=True)
