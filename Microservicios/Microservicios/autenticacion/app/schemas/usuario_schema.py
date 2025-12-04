from marshmallow import Schema, fields, validates, ValidationError
import re

class UsuarioRegistroSchema(Schema):
    correo = fields.Email(required=True)
    contrasena = fields.Str(required=True)
    telefono = fields.Str(required=True)
    id_rol = fields.Int(required=True)

    @validates("contrasena")
    def validate_password(self, value):
        if len(value) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres")
        if not re.search(r"[A-Z]", value):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula")
        if not re.search(r"[a-z]", value):
            raise ValidationError("La contraseña debe contener al menos una letra minúscula")
        if not re.search(r"\d", value):
            raise ValidationError("La contraseña debe contener al menos un número")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValidationError("La contraseña debe contener al menos un carácter especial")

class UsuarioLoginSchema(Schema):
    correo = fields.Email(required=True)
    contrasena = fields.Str(required=True)
