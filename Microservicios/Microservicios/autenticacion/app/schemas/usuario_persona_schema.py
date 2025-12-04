"""
from marshmallow import Schema, fields, validate

class UsuarioPersonaRegistroSchema(Schema):
    correo = fields.Email(required=True)
    contrasena = fields.String(required=True)
    telefono = fields.String(required=True, validate=validate.Length(min=7))
    id_rol = fields.Integer(required=True)

    nombre = fields.String(required=True)
    apellido = fields.String(required=True)
"""



from marshmallow import Schema, fields, validate, validates, ValidationError

class UsuarioPersonaRegistroSchema(Schema):
    correo = fields.Email(required=True)
    contrasena = fields.String(required=True)
    telefono = fields.String(required=True, validate=validate.Length(min=7))
    id_rol = fields.Integer(required=True)

    cedula_ruc = fields.Str(required=True, validate=validate.Length(min=10, max=13))
    nombre = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    apellido = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    direccion_domiciliaria = fields.Str(required=False, allow_none=True)
    foto = fields.Raw(required=False, allow_none=True)

    @validates('cedula_ruc')
    def validate_cedula_ruc(self, value):
        if not value.isdigit():
            raise ValidationError("La cédula/RUC debe contener solo números.")



