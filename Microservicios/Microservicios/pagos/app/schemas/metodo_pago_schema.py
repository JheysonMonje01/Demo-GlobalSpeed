from app.models.metodo_pago_model import MetodoPago
from app.schemas.informacion_metodo_pago_schema import InformacionMetodoPagoSchema
from app.extensions import ma

class MetodoPagoSchema(ma.SQLAlchemySchema):
    class Meta:
        model = MetodoPago
        load_instance = True

    id_metodo_pago = ma.auto_field()
    nombre = ma.auto_field(required=True)
    descripcion = ma.auto_field()
    requiere_verificacion = ma.auto_field()
    estado = ma.auto_field()
    orden_visualizacion = ma.auto_field()
    fecha_creacion = ma.auto_field(dump_only=True)
    fecha_modificacion = ma.auto_field(dump_only=True)

    # Relacionado (para mostrar junto a info bancaria si aplica)
    informacion_adicional = ma.Nested(InformacionMetodoPagoSchema, many=True, dump_only=True)
