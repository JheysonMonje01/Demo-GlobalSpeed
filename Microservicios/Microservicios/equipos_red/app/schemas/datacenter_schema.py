from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.datacenter import DataCenter
from app.extensions import db

class DataCenterSchema(SQLAlchemySchema):
    class Meta:
        model = DataCenter
        load_instance = True
        sqla_session = db.session  # ✅ Requerido para `SQLAlchemySchema`

    id_datacenter = auto_field(dump_only=True)
    nombre = auto_field(required=True)
    ubicacion = auto_field(required=True)
    latitud = auto_field()
    longitud = auto_field()
    fecha_creacion = auto_field(dump_only=True)
    fecha_modificacion = auto_field(dump_only=True)
