from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app.models.contrato_model import Contrato

class ContratoSchema(SQLAlchemySchema):
    class Meta:
        model = Contrato
        load_instance = True
        include_fk = True

    id_contrato = auto_field()
    id_cliente = auto_field()
    id_plan = auto_field()
    id_empresa = auto_field()
    ubicacion = auto_field()
    latitud = auto_field()      # ✅ NUEVO
    longitud = auto_field()     # ✅ NUEVO
    url_archivo = auto_field()
    fecha_fin_contrato = auto_field()
    fecha_creacion = auto_field()
    fecha_modificacion = auto_field()


contrato_schema = ContratoSchema()
contratos_schema = ContratoSchema(many=True)