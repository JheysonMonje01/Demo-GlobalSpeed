from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.configuracion_model import Configuracion
from app.extensions import db

class ConfiguracionSchema(SQLAlchemySchema):
    class Meta:
        model = Configuracion
        load_instance = True
        sqla_session = db.session  # ✅ ¡Requerido!

    id_configuracion = auto_field(dump_only=True)
    clave = auto_field(required=True)
    valor = auto_field(required=True)
    descripcion = auto_field()
    id_usuario = auto_field(required=True)
    estado = auto_field()
    fecha_creacion = auto_field(dump_only=True)
    fecha_modificacion = auto_field(dump_only=True)
