from app.extensions import db
from datetime import datetime

class IPAsignadaPPPoE(db.Model):
    __tablename__ = 'ips_asignadas_pppoe'

    id_ip_asignada = db.Column(db.Integer, primary_key=True)
    id_usuario_pppoe = db.Column(db.Integer, db.ForeignKey('usuario_pppoe.id_usuario_pppoe', ondelete='CASCADE'), unique=True, nullable=False)
    ip = db.Column(db.String(15), unique=True, nullable=False)
    id_pool = db.Column(db.Integer, nullable=False)
    nombre_pool = db.Column(db.String(50))
    asignada = db.Column(db.Boolean, default=True)
    fecha_asignacion = db.Column(db.DateTime, default=datetime.utcnow)

    # Relación opcional si deseas acceder desde el usuario_pppoe
    usuario_pppoe = db.relationship("UsuarioPPPoE", backref=db.backref("ip_asignada", uselist=False, cascade="all, delete"))


