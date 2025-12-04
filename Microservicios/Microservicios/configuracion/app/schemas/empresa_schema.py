import base64
from marshmallow import fields
from app.models.empresa_model import Empresa, EmpresaTelefono, EmpresaCorreo
from app.extensions import ma
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from marshmallow import fields, post_load, post_dump
# 🔹 Schema de EmpresaTelefono
class EmpresaTelefonoSchema(ma.SQLAlchemySchema):
    class Meta:
        model = EmpresaTelefono
        load_instance = True

    id_telefono = ma.auto_field()
    telefono = ma.auto_field()
    tipo = ma.auto_field()
    fecha_creacion = ma.auto_field()
    fecha_modificacion = ma.auto_field()
    id_empresa = ma.auto_field(dump_only=True)  # ✅ solo salida

# 🔹 Schema de EmpresaCorreo
class EmpresaCorreoSchema(ma.SQLAlchemySchema):
    class Meta:
        model = EmpresaCorreo
        load_instance = True

    id_correo = ma.auto_field()
    correo = ma.auto_field()
    tipo = ma.auto_field()
    fecha_creacion = ma.auto_field()
    fecha_modificacion = ma.auto_field()
    id_empresa = ma.auto_field(dump_only=True)  # ✅ solo salida

# 🔹 Schema principal de Empresa
class EmpresaSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Empresa
        load_instance = True

    id_empresa = ma.auto_field()
    nombre = ma.auto_field()
    representante = ma.auto_field()
    ruc = ma.auto_field()
    direccion = ma.auto_field()

    # ✅ logo como base64 solo en dump
    logo = fields.Raw(allow_none=True)  # Raw para aceptar bytes o base64

    fecha_creacion = ma.auto_field()
    fecha_modificacion = ma.auto_field()

    telefonos = ma.Nested(EmpresaTelefonoSchema, many=True)
    correos = ma.Nested(EmpresaCorreoSchema, many=True)

    @post_load
    def decode_logo(self, data, **kwargs):
        """Convierte logo en base64 a binario (para guardar en la DB)."""
        if isinstance(data.get("logo"), str):
            try:
                data["logo"] = base64.b64decode(data["logo"])
            except Exception:
                data["logo"] = None  # Si no se puede decodificar, lo ignora
        return data

    @post_dump
    def encode_logo(self, data, **kwargs):
        """Convierte binario de logo a base64 (para enviar al frontend)."""
        if isinstance(data.get("logo"), (bytes, bytearray)):
            try:
                data["logo"] = base64.b64encode(data["logo"]).decode("utf-8")
            except Exception:
                data["logo"] = None
        return data
    fecha_creacion = auto_field(dump_only=True)
    fecha_modificacion = auto_field(dump_only=True)
