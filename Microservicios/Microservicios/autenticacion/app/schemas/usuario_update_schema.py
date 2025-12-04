from marshmallow import Schema, fields, validate

class UsuarioUpdateSchema(Schema):
    correo = fields.Email(required=False)
    telefono = fields.String(validate=validate.Length(min=7), required=False)
    contrasena = fields.String(required=False)
    id_rol = fields.Int(required=False)
    estado = fields.Boolean(required=False)

    # Datos de persona (sincronización)
    nombre = fields.Str(required=False)
    apellido = fields.Str(required=False)
    direccion_domiciliaria = fields.Str(allow_none=True)
    foto = fields.Str(allow_none=True)
