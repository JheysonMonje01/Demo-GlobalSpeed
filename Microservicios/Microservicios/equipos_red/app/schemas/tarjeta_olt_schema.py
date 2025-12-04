from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.tarjeta_olt import TarjetaOLT
from app.extensions import db

class TarjetaOLTSchema(SQLAlchemySchema):
    class Meta:
        model = TarjetaOLT
        load_instance = True
        sqla_session = db.session

    id_tarjeta_olt = auto_field(dump_only=True)
    id_olt = auto_field(required=True)
    slot_numero = auto_field(required=True)  # NUEVO
    nombre = auto_field(required=True)
    capacidad_puertos_pon = auto_field(required=True)  # REEMPLAZA a "capacidad"
    estado = auto_field()  # NUEVO
    fecha_creacion = auto_field(dump_only=True)
    fecha_modificacion = auto_field(dump_only=True)
