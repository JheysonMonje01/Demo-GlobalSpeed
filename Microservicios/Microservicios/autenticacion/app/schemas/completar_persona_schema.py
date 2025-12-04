from marshmallow import Schema, fields, validate, validates, ValidationError

class CompletarPersonaSchema(Schema):
    id_usuario = fields.Int(required=True)
    cedula_ruc = fields.Str(required=True, validate=validate.Length(min=10, max=13))
    nombre = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    apellido = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    telefono = fields.Str(required=True, validate=validate.Length(min=7, max=15))
    correo = fields.Email(required=True)
    direccion_domiciliaria = fields.Str(allow_none=True)
    foto = fields.Raw(allow_none=True)
    id_rol = fields.Int(required=True)

    @validates('cedula_ruc')
    def validate_cedula_ruc(self, value):
        if not value.isdigit():
            raise ValidationError("La cédula/RUC debe contener solo números.")
        if len(value) == 13 and not value.endswith("001"):
            raise ValidationError("El RUC debe terminar en '001'.")
