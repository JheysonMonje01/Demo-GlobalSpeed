from app.extensions import ma
from app.models.orden_instalacion import OrdenInstalacion

class OrdenInstalacionSchema(ma.SQLAlchemySchema):
    class Meta:
        model = OrdenInstalacion
        load_instance = True

    id_orden = ma.auto_field()
    id_contrato = ma.auto_field()
    ubicacion_instalacion = ma.auto_field()
    id_tecnico = ma.auto_field()
    estado = ma.auto_field()
    documento_pdf = ma.auto_field()
    fecha_asignacion = ma.auto_field()
    fecha_instalacion = ma.auto_field()
    fecha_creacion = ma.auto_field()
    fecha_modificacion = ma.auto_field()
