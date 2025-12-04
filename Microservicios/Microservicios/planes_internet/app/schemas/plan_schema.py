from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import validates, ValidationError, fields
from app.models.plan_model import PlanInternet

class PlanSchema(SQLAlchemySchema):
    class Meta:
        model = PlanInternet
        load_instance = True

    id_plan = auto_field()
    nombre_plan = auto_field(required=True)
    velocidad_subida = auto_field(required=True)
    velocidad_bajada = auto_field(required=True)
    rafaga_subida = auto_field()
    rafaga_bajada = auto_field()
    max_subida = auto_field()
    max_bajada = auto_field()
    tiempo_rafaga_subida = auto_field()
    tiempo_rafaga_bajada = auto_field()
    ip_local = auto_field(required=True)
    ip_remota = auto_field(required=True)
    dns = auto_field()
    precio = auto_field(required=True)  # ✅ Añadido este campo
    id_vlan = auto_field(required=True)
    address_list = auto_field()

    fecha_creacion = auto_field()
    fecha_modificacion = auto_field()

    @validates("velocidad_subida")
    def validate_velocidad_subida(self, value):
        if value < 1 or value > 1000000:
            raise ValidationError("La velocidad de subida debe estar entre 1 y 1,000,000 Kbps")

    @validates("ip_local")
    def validate_ip_local(self, value):
        import ipaddress
        try:
            ipaddress.ip_address(value)
        except ValueError:
            raise ValidationError("IP local inválida")

