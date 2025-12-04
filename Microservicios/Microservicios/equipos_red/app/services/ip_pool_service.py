from app.models.ip_pool_model import IpPool
from app.extensions import db
from app.utils.api_config import post_configuracion
from sqlalchemy.exc import SQLAlchemyError
from ipaddress import ip_address
import logging
import re

def crear_ip_pool(data):
    try:
        nombre = data.nombre.strip()
        rango_inicio = data.rango_inicio
        rango_fin = data.rango_fin
        id_mikrotik = data.id_mikrotik
        print("[DEBUG] ID MikroTik recibido:", data.id_mikrotik)
        print("[DEBUG] Validando MikroTik existente...")


        if not all([nombre, rango_inicio, rango_fin, id_mikrotik]):
            return False, "Faltan campos obligatorios: nombre, rango_inicio, rango_fin, id_mikrotik"

        # Validar nombre compatible con MikroTik
        if not re.match(r"^[a-zA-Z0-9_-]+$", nombre):
            return False, "El nombre del pool no debe contener espacios ni caracteres especiales. Solo letras, números, guiones y guión bajo."

        # Validar duplicado por nombre en DB
        if IpPool.query.filter_by(nombre=nombre).first():
            return False, f"Ya existe un pool con el nombre '{nombre}'"
        
        # Validar existencia del MikroTik
        if not verificar_mikrotik_existe(id_mikrotik):
            return False, f"No se encontró el MikroTik con ID {id_mikrotik}"

        # Validar solapamiento con pools existentes en DB
        nuevo_inicio = ip_address(rango_inicio)
        nuevo_fin = ip_address(rango_fin)

        for pool in IpPool.query.all():
            existente_inicio = ip_address(pool.rango_inicio)
            existente_fin = ip_address(pool.rango_fin)
            if (nuevo_inicio <= existente_fin and nuevo_fin >= existente_inicio):
                return False, f"El rango {rango_inicio} - {rango_fin} se solapa con el pool existente '{pool.nombre}'"

        # Crear en DB
        nuevo_pool = IpPool(
            nombre=nombre,
            rango_inicio=rango_inicio,
            rango_fin=rango_fin,
            mascara_subred=data.mascara_subred,
            gateway=data.gateway,
            dns_servidor=data.dns_servidor,
            descripcion=data.descripcion,
            estado=True,
            id_mikrotik=id_mikrotik
        )

        db.session.add(nuevo_pool)
        db.session.commit()

        # Crear en MikroTik
        payload = {
            "nombre": nombre,
            "rango_inicio": rango_inicio,
            "rango_fin": rango_fin
        }

        exito, mensaje = post_configuracion("/mikrotik/pools", payload)
        if not exito:
            db.session.rollback()
            logging.warning(f"[MikroTik] Falló creación, rollback DB: {mensaje}")
            return False, f"Error al crear en MikroTik: {mensaje}"
        
        return True, "Pool IP creado correctamente en DB y MikroTik"

    except SQLAlchemyError:
        db.session.rollback()
        logging.exception("Error en la base de datos al crear IP Pool")
        return False, "Error en la base de datos al crear IP Pool"
    except Exception as e:
        db.session.rollback()
        logging.exception("Excepción inesperada al crear IP Pool")
        return False, f"Error inesperado: {str(e)}"


"""FUNCION PARA RETORNAR INFORMACION DE UN POOL IP"""

def obtener_pool_por_id(id_pool):
    try:
        if not isinstance(id_pool, int) or id_pool <= 0:
            return False, "El ID del pool debe ser un entero positivo"

        pool = IpPool.query.get(id_pool)
        if not pool:
            return False, f"No se encontró un pool con ID {id_pool}"

        return True, pool

    except SQLAlchemyError:
        logging.exception("Error de base de datos al obtener el IP Pool por ID")
        return False, "Error en base de datos"

    except Exception as e:
        logging.exception("Excepción inesperada en obtener_pool_por_id")
        return False, f"Error inesperado: {str(e)}"


from app.utils.api_config import get_configuracion

def verificar_mikrotik_existe(id_mikrotik):
    exito, data = get_configuracion(f"/mikrotik/configuraciones/{id_mikrotik}")

    print("[DEBUG] Respuesta desde configuracion:", data)

    if not exito or not isinstance(data, dict):
        return False

    try:
        if int(data.get("id_mikrotik", -1)) != int(id_mikrotik):
            return False
    except ValueError:
        return False

    if data.get("estado") is not True:
        return False

    return True


def obtener_ip_pools():
    try:
        pools = IpPool.query.order_by(IpPool.id_pool.asc()).all()
        return True, pools
    except SQLAlchemyError as e:
        return False, f"Error al consultar pools: {str(e)}"


"""FUNCION PARA LISTAR TODOS LOS POOLS PARA EL MICROSERVICIO DE GESTION SERVICIO"""

def listar_todos_los_pools():
    try:
        pools = IpPool.query.all()
        return True, pools
    except SQLAlchemyError:
        logging.exception("Error al listar pools de IP")
        return False, "Error de base de datos al listar pools"
    except Exception as e:
        logging.exception("Excepción inesperada al listar pools")
        return False, f"Error inesperado: {str(e)}"


"""FUNCION PARA OBTENER EL POOL POR NOMBRE PARA EL MICROSERVICIO DE GESTION SERVICIO"""

def obtener_pool_por_nombre(nombre_pool):
    try:
        if not nombre_pool:
            return False, "El nombre del pool es obligatorio"

        pool = IpPool.query.filter_by(nombre=nombre_pool).first()
        if not pool:
            return False, f"No se encontró un pool con nombre '{nombre_pool}'"

        return True, pool

    except SQLAlchemyError:
        logging.exception("Error de base de datos al obtener IP Pool por nombre")
        return False, "Error en base de datos"

    except Exception as e:
        logging.exception("Excepción inesperada en obtener_pool_por_nombre")
        return False, f"Error inesperado: {str(e)}"
