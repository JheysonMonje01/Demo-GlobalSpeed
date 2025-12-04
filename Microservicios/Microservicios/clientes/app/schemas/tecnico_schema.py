from marshmallow import Schema, fields, validate

class TecnicoSchema(Schema):
    id_tecnico = fields.Int(dump_only=True)
    id_persona = fields.Int(required=True)
    estado = fields.Str(
        required=False,
        validate=validate.OneOf(["activo", "ocupado", "inactivo"]),
        missing="activo"
    )
    fecha_creacion = fields.DateTime(dump_only=True)
    fecha_modificacion = fields.DateTime(dump_only=True)

tecnico_schema = TecnicoSchema()
tecnicos_schema = TecnicoSchema(many=True)
