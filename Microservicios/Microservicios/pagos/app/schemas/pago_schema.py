import os
from flask import url_for
from app.models.pago_model import Pago
from app.extensions import ma
from marshmallow import fields

class PagoSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Pago
        load_instance = True

    id_pago = ma.auto_field()
    id_contrato = ma.auto_field(required=True)
    id_metodo_pago = ma.auto_field(required=True)
    monto = ma.auto_field(required=True)
    mes_correspondiente = ma.auto_field(required=True)

    comprobante = ma.auto_field()  # ruta relativa (ej. comprobantes/2/nombre.png)
    comprobante_url = fields.Method("get_comprobante_url")  # ruta completa accesible por el frontend

    observacion = ma.auto_field()
    estado = ma.auto_field()
    verificado_por = ma.auto_field()
    fecha_verificacion = ma.auto_field()
    fecha_creacion = ma.auto_field(dump_only=True)
    fecha_modificacion = ma.auto_field(dump_only=True)

    def get_comprobante_url(self, obj):
        if obj.comprobante:
            id_pago = obj.id_pago
            filename = os.path.basename(obj.comprobante)
            return url_for('serve_comprobante', id_pago=id_pago, filename=filename, _external=True)
        return None
