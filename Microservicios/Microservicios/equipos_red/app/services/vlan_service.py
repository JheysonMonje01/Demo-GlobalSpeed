from app.models.vlan_model import VLAN
from app.extensions import db
from app.utils.api_config import post_configuracion
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import logging
from app.utils.api_config import verificar_mikrotik_existe


def crear_vlan(numero_vlan, nombre, interface, id_mikrotik):

    # Validar que el MikroTik exista
    # ✅ Validar que el MikroTik exista en el microservicio
    existe, resultado = verificar_mikrotik_existe(id_mikrotik)
    if not existe:
        return False, f"ID MikroTik inválido: {resultado}"



    if not numero_vlan or not interface or not id_mikrotik:
        return False, "Número de VLAN, interfaz e ID MikroTik son requeridos"
    

    # Validación de unicidad previa
    existente = VLAN.query.filter_by(numero_vlan=numero_vlan).first()
    if existente:
        return False, f"La VLAN con número {numero_vlan} ya existe"

    # Construir payload para MikroTik
    payload = {
        "numero_vlan": numero_vlan,
        "nombre": nombre,
        "interface": interface
    }

    try:
        # 1. Intentar configurar en MikroTik
        exito, resultado = post_configuracion("/mikrotik/crear-vlan", payload)
        logging.info(f"[MikroTik] Resultado creación VLAN: {exito}, {resultado}")

        if not exito:
            return False, f"Error al configurar MikroTik: {resultado}"

        # 2. Guardar en base de datos si MikroTik fue exitoso
        nueva_vlan = VLAN(
            numero_vlan=numero_vlan,
            nombre=nombre,
            interface_destino=interface,
            id_mikrotik=id_mikrotik,
            fecha_creacion=datetime.utcnow(),
            fecha_modificacion=datetime.utcnow()
        )

        db.session.add(nueva_vlan)
        db.session.commit()
        return True, nueva_vlan

    except SQLAlchemyError as e:
        db.session.rollback()
        logging.exception("Error en base de datos al guardar VLAN")
        return False, f"Error al guardar en la base de datos: {str(e)}"

    except Exception as e:
        db.session.rollback()
        logging.exception("Excepción inesperada al crear VLAN")
        return False, f"Error inesperado: {str(e)}"


def obtener_vlans_filtradas(filtros):
    try:
        query = VLAN.query
        filtros_validos = {'id_vlan', 'numero_vlan', 'nombre', 'interface_destino'}

        for key in filtros:
            if key not in filtros_validos:
                return False, f"Parámetro no permitido: '{key}'"

        if 'id_vlan' in filtros:
            try:
                query = query.filter_by(id_vlan=int(filtros['id_vlan']))
            except ValueError:
                return False, "id_vlan debe ser numérico"

        if 'numero_vlan' in filtros:
            try:
                query = query.filter_by(numero_vlan=int(filtros['numero_vlan']))
            except ValueError:
                return False, "numero_vlan debe ser numérico"

        if 'nombre' in filtros:
            query = query.filter(VLAN.nombre.ilike(f"%{filtros['nombre']}%"))

        if 'interface_destino' in filtros:
            query = query.filter(VLAN.interface_destino.ilike(f"%{filtros['interface_destino']}%"))

        if not filtros:
            return False, "Debe especificar al menos un filtro válido para buscar VLANs"

        vlans = query.order_by(VLAN.numero_vlan.asc()).all()
        return True, vlans

    except Exception as e:
        logging.exception("Error al filtrar VLANs")
        return False, f"Error al obtener VLANs: {str(e)}"


def obtener_vlan_por_id(id_vlan):
    try:
        vlan = VLAN.query.get(id_vlan)
        if not vlan:
            return False, f"No se encontró ninguna VLAN con id {id_vlan}"
        return True, vlan
    except SQLAlchemyError as e:
        logging.exception("Error al buscar VLAN por ID")
        return False, f"Error al buscar VLAN: {str(e)}"

def listar_todas_las_vlans():
    try:
        vlans = VLAN.query.order_by(VLAN.numero_vlan.asc()).all()
        return True, vlans
    except SQLAlchemyError as e:
        return False, f"Error al obtener VLANs: {str(e)}"
