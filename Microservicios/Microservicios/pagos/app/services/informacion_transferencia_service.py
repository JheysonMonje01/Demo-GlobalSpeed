from app.models.informacion_metodo_pago_model import InformacionMetodoPago
from app.extensions import db
from app.utils.validaciones_transferencia import validar_datos_transferencia
from sqlalchemy.exc import SQLAlchemyError



def crear_informacion_transferencia(data):
    """
    Crea un nuevo registro de información para método de pago por transferencia bancaria.

    Args:
        data (dict): Datos enviados desde el frontend para crear la información bancaria.

    Returns:
        tuple: (objeto creado o mensaje de error, código HTTP)
    """
    errores = validar_datos_transferencia(data)
    if errores:
        return {"error": errores}, 400

    numero_cuenta = data.get("numero_cuenta", "").strip()
    # Validar si ya existe número de cuenta (ignorando mayúsculas)
    cuenta_existente = InformacionMetodoPago.query.filter(
        func.lower(InformacionMetodoPago.numero_cuenta) == numero_cuenta.lower()
    ).first()
    if cuenta_existente:
        return {"error": f"Ya existe un registro con el número de cuenta '{numero_cuenta}'."}, 409

    try:
        nueva_info = InformacionMetodoPago(
            nombre_beneficiario=data.get("nombre_beneficiario", "").strip(),
            entidad_financiera=data.get("entidad_financiera", "").strip(),
            numero_cuenta=numero_cuenta,
            tipo_cuenta=data.get("tipo_cuenta", "").strip().lower(),
            instrucciones=data.get("instrucciones", "").strip(),
            id_metodo_pago=data.get("id_metodo_pago"),
            estado=data.get("estado", True)
        )

        db.session.add(nueva_info)
        db.session.commit()
        return nueva_info, 201

    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "Error al guardar en la base de datos."}, 500

    except Exception as e:
        db.session.rollback()
        return {"error": f"Error inesperado: {str(e)}"}, 500




def actualizar_informacion_transferencia(id_info, data):
    """
    Actualiza un registro existente de información de método de pago por transferencia.

    Args:
        id_info (int): ID del registro a actualizar.
        data (dict): Datos nuevos enviados desde el frontend.

    Returns:
        tuple: (objeto actualizado o mensaje de error, código HTTP)
    """
    info = InformacionMetodoPago.query.get(id_info)
    if not info:
        return {"error": "Registro no encontrado."}, 404

    errores = validar_datos_transferencia(data)
    if errores:
        return {"error": errores}, 400

    nuevo_numero_cuenta = data.get("numero_cuenta", "").strip()

    # Verificar si ese número de cuenta ya existe en otro registro
    duplicado = InformacionMetodoPago.query.filter(
        func.lower(InformacionMetodoPago.numero_cuenta) == nuevo_numero_cuenta.lower(),
        InformacionMetodoPago.id_info != id_info
    ).first()

    if duplicado:
        return {"error": f"El número de cuenta '{nuevo_numero_cuenta}' ya está registrado en otro registro."}, 409

    try:
        info.nombre_beneficiario = data.get("nombre_beneficiario", "").strip()
        info.entidad_financiera = data.get("entidad_financiera", "").strip()
        info.numero_cuenta = nuevo_numero_cuenta
        info.tipo_cuenta = data.get("tipo_cuenta", "").strip().lower()
        info.instrucciones = data.get("instrucciones", "").strip()
        info.id_metodo_pago = data.get("id_metodo_pago", info.id_metodo_pago)
        info.estado = data.get("estado", info.estado)

        db.session.commit()
        return info, 200

    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "Error al actualizar en la base de datos."}, 500

    except Exception as e:
        db.session.rollback()
        return {"error": f"Error inesperado: {str(e)}"}, 500




"""***************************************************************"""

from app.models.informacion_metodo_pago_model import InformacionMetodoPago
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func


def obtener_informacion_transferencia_por_id(id_info):
    info = InformacionMetodoPago.query.get(id_info)
    if not info:
        return {"error": "Registro no encontrado."}, 404
    return info, 200


def obtener_informaciones_transferencia_filtradas(filtros):
    try:
        query = InformacionMetodoPago.query

        banco = filtros.get("banco")
        nombre = filtros.get("nombre_beneficiario")
        tipo_cuenta = filtros.get("tipo_cuenta")
        estado = filtros.get("estado")

        if banco:
            if len(banco) > 100:
                return {"error": "Filtro 'banco' demasiado largo."}, 400
            query = query.filter(InformacionMetodoPago.entidad_financiera.ilike(f"%{banco.strip()}%"))

        if nombre:
            if len(nombre) > 100:
                return {"error": "Filtro 'nombre_beneficiario' demasiado largo."}, 400
            query = query.filter(InformacionMetodoPago.nombre_beneficiario.ilike(f"%{nombre.strip()}%"))

        if tipo_cuenta:
            tipo_normalizado = tipo_cuenta.strip().lower()
            if tipo_normalizado not in ["ahorros", "corriente"]:
                return {"error": "El tipo de cuenta debe ser 'ahorros' o 'corriente'."}, 400
            query = query.filter(func.lower(InformacionMetodoPago.tipo_cuenta) == tipo_normalizado)

        if estado is not None:
            if estado.lower() not in ["true", "false"]:
                return {"error": "El valor de 'estado' debe ser true o false."}, 400
            query = query.filter(InformacionMetodoPago.estado == (estado.lower() == "true"))

        resultados = query.order_by(InformacionMetodoPago.fecha_creacion.desc()).all()
        return resultados, 200

    except SQLAlchemyError:
        return {"error": "Error al consultar la base de datos."}, 500

    except Exception as e:
        return {"error": f"Error inesperado: {str(e)}"}, 500


def eliminar_informacion_transferencia(id_info):
    info = InformacionMetodoPago.query.get(id_info)
    if not info:
        return {"error": "Registro no encontrado."}, 404

    try:
        db.session.delete(info)
        db.session.commit()
        return {"mensaje": "Información eliminada correctamente."}, 200

    except SQLAlchemyError:
        db.session.rollback()
        return {"error": "Error al eliminar en la base de datos."}, 500

    except Exception as e:
        db.session.rollback()
        return {"error": f"Error inesperado: {str(e)}"}, 500



