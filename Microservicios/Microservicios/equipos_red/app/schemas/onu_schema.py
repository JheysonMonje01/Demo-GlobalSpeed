'''from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields, validate
from app.models.onu import ONU

class ONUSchema(SQLAlchemySchema):
    class Meta:
        model = ONU
        load_instance = True
        include_fk = True

    id_onu = auto_field(dump_only=True)
    serial_number = auto_field(required=True, validate=validate.Length(min=4, max=100))
    ont_id = auto_field()
    modelo_onu = auto_field(required=True)
    numero_puerto_nap = auto_field(required=True, validate=validate.Range(min=1))

    id_caja = auto_field(required=True)
    id_puerto_pon_olt = auto_field(required=True)
    id_contrato = auto_field(required=True)

    estado = auto_field(required=False)
    fecha_creacion = auto_field(dump_only=True)
    fecha_modificacion = auto_field(dump_only=True)'''

from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import validates, ValidationError
from app.models.onu import ONU
from app.extensions import db

class ONUSchema(SQLAlchemySchema):
    class Meta:
        model = ONU
        load_instance = True
        sqla_session = db.session

    id_onu = auto_field(dump_only=True)
    serial = auto_field(required=True)
    modelo_onu = auto_field()
    id_caja = auto_field(allow_none=True)
    id_contrato = auto_field(allow_none=True)
    id_puerto_pon_olt = auto_field(allow_none=True)
    numero_puerto_nap = auto_field(allow_none=True)
    ont_id = auto_field(allow_none=True)
    estado = auto_field()
    fecha_creacion = auto_field(dump_only=True)
    fecha_modificacion = auto_field(dump_only=True)

    @validates('serial')
    def validate_serial(self, value):
        if not value or len(value.strip()) < 4:
            raise ValidationError("El número de serie debe tener al menos 4 caracteres.")
