from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields, validate
from app.models.caja_nap import CajaNAP

class CajaNAPSchema(SQLAlchemySchema):
    class Meta:
        model = CajaNAP
        load_instance = True
        include_fk = True

    id_caja = auto_field(dump_only=True)
    nombre_caja_nap = auto_field(required=True, validate=validate.Length(min=2, max=100))
    ubicacion = auto_field(required=True, validate=validate.Length(min=2))
    latitud = auto_field(required=True)
    longitud = auto_field(required=True)
    observacion = auto_field()
    capacidad_puertos_cliente = auto_field(required=True, validate=validate.Range(min=1))
    puertos_ocupados = auto_field(dump_only=True)
    estado = auto_field(required=False)
    radio_cobertura = auto_field(required=True, validate=validate.Range(min=10))
    id_puerto_pon_olt = auto_field(required=True)

    fecha_creacion = auto_field(dump_only=True)
    fecha_modificacion = auto_field(dump_only=True)
