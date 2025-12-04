from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.olt import OLT
from app.extensions import db

class OLTSchema(SQLAlchemySchema):
    class Meta:
        model = OLT
        load_instance = True
        sqla_session = db.session

    id_olt = auto_field(dump_only=True)
    id_datacenter = auto_field(required=True)
    marca = auto_field(required=True)
    modelo = auto_field(required=True)
    capacidad = auto_field(required=True)
    slots_ocupados = auto_field()
    ip_gestion = auto_field(required=True)
    usuario_gestion = auto_field(required=True)       # ← Añadido
    contrasena_gestion = auto_field(required=True, load_only=True)# ← Añadido
    estado = auto_field()
    fecha_creacion = auto_field(dump_only=True)
    fecha_modificacion = auto_field(dump_only=True)
