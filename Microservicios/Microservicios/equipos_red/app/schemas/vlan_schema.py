from app.models.vlan_model import VLAN
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

class VLANSchema(SQLAlchemySchema):
    class Meta:
        model = VLAN
        load_instance = True

    id_vlan = auto_field()
    numero_vlan = auto_field()
    nombre = auto_field()
    interface_destino = auto_field()
    fecha_creacion = auto_field()
    fecha_modificacion = auto_field()
    id_mikrotik = auto_field()  # ➕ agregado