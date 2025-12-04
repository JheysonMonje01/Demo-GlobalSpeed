from app.extensions import ma
from marshmallow import fields

class ONUAsignarSchema(ma.Schema):
    id_contrato = fields.Int(required=True)
    id_caja = fields.Int(required=True)
    id_puerto_pon_olt = fields.Int(required=True)
    numero_puerto_nap = fields.Int(required=True)
    ont_id = fields.Int(required=True)
    estado = fields.Str(required=True)

onu_asignar_schema = ONUAsignarSchema()
