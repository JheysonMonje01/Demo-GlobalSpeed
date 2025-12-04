from app.models.metodo_pago_model import MetodoPago
from app.models.pago_model import Pago
from app.extensions import db
from app.utils.validaciones_metodo_pago import (
    validar_nombre_unico,
    validar_orden_visualizacion_unico,
    parse_bool
)

def crear_metodo_pago(data):
    nombre = data.get('nombre', '').strip()
    orden = data.get('orden_visualizacion')

    if not nombre:
        return {"error": "El nombre del método de pago es obligatorio."}, 400
    if len(nombre) > 50:
        return {"error": "El nombre no debe superar los 50 caracteres."}, 400
    if not validar_nombre_unico(nombre):
        return {"error": f"Ya existe un método de pago con el nombre '{nombre}'."}, 409

    if orden is not None:
        if not isinstance(orden, int) or orden < 1:
            return {"error": "El campo 'orden_visualizacion' debe ser un entero mayor o igual a 1."}, 400
        if not validar_orden_visualizacion_unico(orden):
            return {"error": f"Ya hay otro método de pago con orden_visualizacion = {orden}."}, 409

    try:
        nuevo_metodo = MetodoPago(
            nombre=nombre,
            descripcion=data.get("descripcion", ""),
            requiere_verificacion=data.get("requiere_verificacion", False),
            estado=data.get("estado", True),
            orden_visualizacion=orden if orden is not None else None
        )
        db.session.add(nuevo_metodo)
        db.session.commit()
        return nuevo_metodo, 201
    except Exception as e:
        db.session.rollback()
        return {"error": f"Error al crear el método de pago: {str(e)}"}, 500



def actualizar_metodo_pago(id_metodo, data):
    metodo = MetodoPago.query.get(id_metodo)
    if not metodo:
        return {"error": "Método de pago no encontrado."}, 404

    nombre = data.get('nombre', '').strip()
    orden = data.get('orden_visualizacion')

    if not nombre:
        return {"error": "El nombre del método de pago es obligatorio."}, 400
    if len(nombre) > 50:
        return {"error": "El nombre no debe superar los 50 caracteres."}, 400
    if not validar_nombre_unico(nombre, id_excluir=id_metodo):
        return {"error": f"Ya existe otro método de pago con el nombre '{nombre}'."}, 409

    if orden is not None:
        if not isinstance(orden, int) or orden < 1:
            return {"error": "El campo 'orden_visualizacion' debe ser un entero mayor o igual a 1."}, 400
        if not validar_orden_visualizacion_unico(orden, id_excluir=id_metodo):
            return {"error": f"Ya hay otro método de pago con orden_visualizacion = {orden}."}, 409

    try:
        metodo.nombre = nombre
        metodo.descripcion = data.get("descripcion", metodo.descripcion)
        metodo.requiere_verificacion = data.get("requiere_verificacion", metodo.requiere_verificacion)
        metodo.estado = data.get("estado", metodo.estado)
        metodo.orden_visualizacion = orden if orden is not None else metodo.orden_visualizacion

        db.session.commit()
        return metodo, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Error al actualizar el método de pago: {str(e)}"}, 500



def obtener_metodo_pago_por_id(id_metodo):
    metodo = MetodoPago.query.get(id_metodo)
    if not metodo:
        return {"error": "Método de pago no encontrado."}, 404
    return metodo, 200



def obtener_metodos_pago_filtrados(filtros):
    try:
        query = MetodoPago.query

        nombre = filtros.get("nombre")
        estado = filtros.get("estado")
        requiere_verificacion = filtros.get("requiere_verificacion")
        orden = filtros.get("orden_visualizacion")

        if nombre:
            if len(nombre.strip()) > 50:
                return {"error": "El filtro 'nombre' es demasiado largo."}, 400
            query = query.filter(MetodoPago.nombre.ilike(f"%{nombre.strip()}%"))

        if estado is not None:
            if estado.lower() not in ["true", "false"]:
                return {"error": "El valor de 'estado' debe ser true o false."}, 400
            query = query.filter(MetodoPago.estado == (estado.lower() == "true"))

        if requiere_verificacion is not None:
            if requiere_verificacion.lower() not in ["true", "false"]:
                return {"error": "El valor de 'requiere_verificacion' debe ser true o false."}, 400
            query = query.filter(MetodoPago.requiere_verificacion == (requiere_verificacion.lower() == "true"))

        if orden:
            if not orden.isdigit() or int(orden) < 1:
                return {"error": "El campo 'orden_visualizacion' debe ser un número entero positivo."}, 400
            query = query.filter(MetodoPago.orden_visualizacion == int(orden))

        metodos = query.order_by(MetodoPago.orden_visualizacion.asc()).all()
        return metodos, 200
    except Exception as e:
        return {"error": f"Error al filtrar métodos de pago: {str(e)}"}, 500


"""FUNCIONES PARA ELIMINAR MÉTODOS DE PAGO"""

def eliminar_metodo_pago(id_metodo_pago):
    metodo = MetodoPago.query.get(id_metodo_pago)
    if not metodo:
        return {"error": "Método de pago no encontrado."}, 404

    pagos_relacionados = Pago.query.filter_by(id_metodo_pago=id_metodo_pago).count()
    if pagos_relacionados > 0:
        return {
            "error": "No se puede eliminar este método de pago porque está asociado a registros de pagos existentes."
        }, 409

    try:
        db.session.delete(metodo)
        db.session.commit()
        return {"mensaje": "Método de pago eliminado correctamente."}, 200

        # Alternativa borrado lógico:
        # metodo.estado = False
        # db.session.commit()
        # return {"mensaje": "Método de pago desactivado correctamente."}, 200
    except Exception as e:
        db.session.rollback()
        return {"error": f"Error al eliminar el método de pago: {str(e)}"}, 500
