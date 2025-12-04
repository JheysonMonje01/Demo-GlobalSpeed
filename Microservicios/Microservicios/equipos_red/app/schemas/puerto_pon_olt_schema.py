# app/schemas/puerto_pon_olt_schema.py
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.puerto_pon_olt import PuertoPONOLT
from app.extensions import db


class PuertoPONOLT_Schema(SQLAlchemySchema):
    class Meta:
        model = PuertoPONOLT
        load_instance = True
        sqla_session = db.session

    id_puerto_pon_olt = auto_field(dump_only=True)
    id_tarjeta_olt = auto_field(required=True)
    numero_puerto = auto_field()
    estado_puerto = auto_field()
    fecha_creacion = auto_field(dump_only=True)
    fecha_modificacion = auto_field(dump_only=True)
