from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow_sqlalchemy.fields import Nested
from app.schemas.persona_schema import PersonaSchema
from app.models.cliente_model import Cliente

class ClienteSchema(SQLAlchemySchema):
    class Meta:
        model = Cliente
        load_instance = True
        include_fk = True

    id_cliente = auto_field()
    id_persona = auto_field()
    persona = Nested(PersonaSchema)  # Relación con datos anidados

cliente_schema = ClienteSchema()
clientes_schema = ClienteSchema(many=True)
