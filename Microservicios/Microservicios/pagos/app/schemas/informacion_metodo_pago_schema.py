from app.models.informacion_metodo_pago_model import InformacionMetodoPago
from app.extensions import ma

class InformacionMetodoPagoSchema(ma.SQLAlchemySchema):
    class Meta:
        model = InformacionMetodoPago
        load_instance = True

    id_info = ma.auto_field()
    id_metodo_pago = ma.auto_field(required=True)

    nombre_beneficiario = ma.auto_field()
    numero_cuenta = ma.auto_field()
    tipo_cuenta = ma.auto_field()
    entidad_financiera = ma.auto_field()
    instrucciones = ma.auto_field()

    estado = ma.auto_field()
    fecha_creacion = ma.auto_field(dump_only=True)
    fecha_modificacion = ma.auto_field(dump_only=True)
