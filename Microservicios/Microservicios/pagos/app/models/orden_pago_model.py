from app.extensions import db
from datetime import datetime

class OrdenPago(db.Model):
    __tablename__ = 'orden_pago'

    id_orden_pago = db.Column(db.Integer, primary_key=True)
    id_contrato = db.Column(db.Integer, nullable=False)  # Relación lógica externa
    mes_correspondiente = db.Column(db.Date, nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='pendiente')
    fecha_generacion = db.Column(db.DateTime, default=datetime.now)
    fecha_vencimiento = db.Column(db.DateTime, nullable=False)
    fecha_pago = db.Column(db.DateTime)

    id_pago = db.Column(db.Integer, db.ForeignKey('pago.id_pago', ondelete='SET NULL'))
    pago = db.relationship('Pago', backref=db.backref('orden_pago', uselist=False), lazy=True)

