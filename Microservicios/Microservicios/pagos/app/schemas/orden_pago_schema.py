from marshmallow import fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from app.models.orden_pago_model import OrdenPago

class OrdenPagoSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = OrdenPago
        load_instance = True
        include_fk = True
        exclude = ("pago",)

    id_orden_pago = fields.Int(dump_only=True)
    id_contrato = fields.Int(required=True)
    mes_correspondiente = fields.Date(required=True)
    monto = fields.Decimal(as_string=True, required=True)
    estado = fields.Str(validate=validate.OneOf(["pendiente", "cancelado", "vencido"]))
    fecha_generacion = fields.DateTime(dump_only=True)
    fecha_vencimiento = fields.DateTime(required=True)
    fecha_pago = fields.DateTime(allow_none=True)
    id_pago = fields.Int(allow_none=True)

