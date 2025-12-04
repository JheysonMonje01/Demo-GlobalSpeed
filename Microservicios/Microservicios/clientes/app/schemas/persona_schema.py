from marshmallow import Schema, fields, validate, validates, ValidationError
import base64

class PersonaSchema(Schema):
    id_persona = fields.Int(dump_only=True)
    cedula_ruc = fields.Str(required=True, validate=validate.Length(min=10, max=13))
    nombre = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    apellido = fields.Str(required=True, validate=validate.Length(min=2, max=50))
    telefono = fields.Str(required=True, validate=validate.Length(min=7, max=15))
    correo = fields.Email(required=True)
    direccion_domiciliaria = fields.Str(allow_none=True)
    foto = fields.Method("get_foto_base64")
    id_usuario = fields.Int(required=True)
    fecha_creacion = fields.DateTime(dump_only=True)
    fecha_modificacion = fields.DateTime(dump_only=True)

    @validates('cedula_ruc')
    def validate_cedula_ruc(self, value):
        if not value.isdigit():
            raise ValidationError("La cédula/RUC debe contener solo números.")
        if len(value) == 13 and not value.endswith("001"):
            raise ValidationError("El RUC debe terminar en '001'.")
    
    def get_foto_base64(self, obj):
        if obj.foto:
            try:
                return base64.b64encode(obj.foto).decode('utf-8')
            except Exception:
                return None
        return None

persona_schema = PersonaSchema()
personas_schema = PersonaSchema(many=True)
