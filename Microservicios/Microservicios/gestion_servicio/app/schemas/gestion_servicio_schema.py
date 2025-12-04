from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.gestion_servicio_model import GestionServicio

class GestionServicioSchema(SQLAlchemySchema):
    class Meta:
        model = GestionServicio
        load_instance = True

    id_gestion = auto_field(dump_only=True)
    id_usuario_pppoe = auto_field(dump_only=True)
    id_contrato = auto_field(required=True)
    estado_servicio = auto_field(required=True)
    motivo = auto_field()
    usuario_admin_correo = auto_field()
    fecha_evento = auto_field(dump_only=True)
    fecha_creacion = auto_field(dump_only=True)



