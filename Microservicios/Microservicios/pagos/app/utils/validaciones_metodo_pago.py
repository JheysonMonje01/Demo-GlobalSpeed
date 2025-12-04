from app.models.metodo_pago_model import MetodoPago
from sqlalchemy import func

def validar_nombre_unico(nombre, id_excluir=None):
    query = MetodoPago.query.filter(func.lower(MetodoPago.nombre) == nombre.lower())
    if id_excluir:
        query = query.filter(MetodoPago.id_metodo_pago != id_excluir)
    return not query.first()

def validar_orden_visualizacion_unico(orden, id_excluir=None):
    query = MetodoPago.query.filter(
        MetodoPago.orden_visualizacion == orden,
        MetodoPago.estado == True
    )
    if id_excluir:
        query = query.filter(MetodoPago.id_metodo_pago != id_excluir)
    return not query.first()

def parse_bool(value):
    return str(value).lower() in ['true', '1', 'yes']
