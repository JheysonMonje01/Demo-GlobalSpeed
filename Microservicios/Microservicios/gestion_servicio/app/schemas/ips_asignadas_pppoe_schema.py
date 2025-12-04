from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.ips_asignadas_pppoe_model import IPAsignadaPPPoE

class IPAsignadaPPPoESchema(SQLAlchemySchema):
    class Meta:
        model = IPAsignadaPPPoE
        load_instance = True

    id_ip_asignada = auto_field(dump_only=True)
    id_usuario_pppoe = auto_field(required=True)
    ip = auto_field(required=True)
    id_pool = auto_field(required=True)
    nombre_pool = auto_field()
    asignada = auto_field()
    fecha_asignacion = auto_field(dump_only=True)
 