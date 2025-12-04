from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field, fields
from app.models.ip_pool_model import IpPool
from marshmallow import validates, ValidationError
import ipaddress

class IpPoolSchema(SQLAlchemySchema):
    class Meta:
        model = IpPool
        load_instance = True
        include_fk = True  # NECESARIO para cargar campos como id_mikrotik

    id_pool = auto_field(dump_only=True)
    nombre = auto_field(required=True)
    rango_inicio = auto_field(required=True)
    rango_fin = auto_field(required=True)
    mascara_subred = auto_field()
    gateway = auto_field()
    dns_servidor = auto_field()
    descripcion = auto_field()
    estado = auto_field()
    id_mikrotik = auto_field(required=True)
    fecha_creacion = auto_field(dump_only=True)
    fecha_modificacion = auto_field(dump_only=True)

    @validates("rango_inicio")
    def validar_ip_inicio(self, value):
        try:
            ipaddress.IPv4Address(value)
        except ValueError:
            raise ValidationError("La IP de inicio no es válida")

    @validates("rango_fin")
    def validar_ip_fin(self, value):
        try:
            ipaddress.IPv4Address(value)
        except ValueError:
            raise ValidationError("La IP final no es válida")

    @validates("mascara_subred")
    def validar_mascara(self, value):
        if value:
            try:
                ipaddress.IPv4Network(f"0.0.0.0/{value}")
            except ValueError:
                raise ValidationError("Máscara de subred inválida")

    @validates("gateway")
    def validar_gateway(self, value):
        if value:
            try:
                ipaddress.IPv4Address(value)
            except ValueError:
                raise ValidationError("Gateway inválido")

    @validates("dns_servidor")
    def validar_dns(self, value):
        if value:
            try:
                ipaddress.IPv4Address(value)
            except ValueError:
                raise ValidationError("DNS inválido")
