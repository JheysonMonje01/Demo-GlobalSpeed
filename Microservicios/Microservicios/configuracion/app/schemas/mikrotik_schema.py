from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import validates, ValidationError, fields
from app.models.mikrotik_model import MikrotikAPIConfig
from app.extensions import db

class MikrotikConfigSchema(SQLAlchemySchema):
    class Meta:
        model = MikrotikAPIConfig
        load_instance = True
        sqla_session = db.session

    id_mikrotik = auto_field(dump_only=True)
    nombre = auto_field(required=True)
    host = auto_field(required=True)
    puerto = auto_field()
    usuario = auto_field(required=True)
    contrasena = auto_field(required=True, load_only=True)
    estado = auto_field()
    fecha_creacion = auto_field(dump_only=True)
    fecha_modificacion = auto_field(dump_only=True)

    # Campo exclusivo para verificación SSH (no va a la BD)
    clave_privada = fields.String(load_only=True)

    @validates('nombre')
    def validar_nombre(self, value):
        if not value.strip():
            raise ValidationError("El nombre no puede estar vacío.")
        if len(value) > 50:
            raise ValidationError("El nombre no debe exceder 50 caracteres.")

    @validates('host')
    def validar_host(self, value):
        if not value.strip():
            raise ValidationError("El host no puede estar vacío.")
        if len(value) > 100:
            raise ValidationError("El host no debe exceder 100 caracteres.")

    @validates('puerto')
    def validar_puerto(self, value):
        if value is not None and (value < 1 or value > 65535):
            raise ValidationError("El puerto debe estar entre 1 y 65535.")

    @validates('usuario')
    def validar_usuario(self, value):
        if not value.strip():
            raise ValidationError("El usuario no puede estar vacío.")
        if len(value) > 100:
            raise ValidationError("El usuario no debe exceder 100 caracteres.")

    @validates('contrasena')
    def validar_contrasena(self, value):
        if not value.strip():
            raise ValidationError("La contraseña no puede estar vacía.")
        if len(value) < 4:
            raise ValidationError("La contraseña debe tener al menos 4 caracteres.")




