from marshmallow import Schema, fields

class LoginSchema(Schema):
    correo = fields.Email(required=True)
    contraseña = fields.String(required=True)
