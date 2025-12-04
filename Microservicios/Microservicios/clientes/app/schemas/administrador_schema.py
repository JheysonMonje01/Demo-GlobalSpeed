from marshmallow import Schema, fields
from app.models.administrador_model import Administrador

class AdministradorSchema(Schema):
    id_administrador = fields.Int(dump_only=True)
    id_persona = fields.Int(required=True)
    # Agrega otros campos si los tienes

# Instancias necesarias
administrador_schema = AdministradorSchema()
administradores_schema = AdministradorSchema(many=True)
