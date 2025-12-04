from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.usuario_pppoe_model import UsuarioPPPoE

class UsuarioPPPoESchema(SQLAlchemySchema):
    class Meta:
        model = UsuarioPPPoE
        load_instance = True  # Crea instancias del modelo al deserializar

    id_usuario_pppoe = auto_field(dump_only=True)
    id_contrato = auto_field(required=True)
    usuario_pppoe = auto_field(required=True)
    contrasena = auto_field(required=True)
    nombre_cliente = auto_field()
    ip_remota = auto_field()
    estado = auto_field()
    mikrotik_nombre = auto_field()
    fecha_creacion = auto_field(dump_only=True)
    fecha_modificacion = auto_field(dump_only=True)
