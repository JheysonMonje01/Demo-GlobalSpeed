from app.extensions import db

class IpPool(db.Model):
    __tablename__ = 'ip_pools'

    id_pool = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    rango_inicio = db.Column(db.String(15), nullable=False)
    rango_fin = db.Column(db.String(15), nullable=False)
    mascara_subred = db.Column(db.String(15))  # Opcional
    gateway = db.Column(db.String(15))         # Opcional
    dns_servidor = db.Column(db.String(50))    # Opcional
    descripcion = db.Column(db.Text)
    estado = db.Column(db.Boolean, default=True)

    #id_vlan = db.Column(db.Integer, db.ForeignKey('vlan.id_vlan', ondelete='RESTRICT'), nullable=False)
    id_mikrotik = db.Column(db.Integer, nullable=False)  # NO ForeignKey

    fecha_creacion = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    fecha_modificacion = db.Column(db.DateTime, onupdate=db.func.current_timestamp())

    # Relación (opcional si se desea navegar desde pool a VLAN)
    #vlan = db.relationship("VLAN", backref=db.backref("pools", lazy=True))

