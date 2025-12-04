from app.models.configuracion_model import Configuracion
from app.extensions import db
from sqlalchemy.exc import IntegrityError
import requests

def validar_usuario(id_usuario):
    url = f"http://autenticacion:5000/auth/usuarios/filtrado?id_usuario={id_usuario}"
    
    try:
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            user_data = response.json()

            if isinstance(user_data, list) and len(user_data) > 0:
                usuario = user_data[0]
                if isinstance(usuario, dict) and usuario.get("id_usuario") == id_usuario:
                    return {"exists": True}
                else:
                    return {
                        "exists": False,
                        "error": "Usuario no coincide con el id proporcionado."
                    }
            else:
                return {
                    "exists": False,
                    "error": "Respuesta vacía o inválida del microservicio de autenticación."
                }

        elif response.status_code == 404:
            return {
                "exists": False,
                "error": "El usuario no existe en el microservicio de autenticación."
            }

        else:
            return {
                "exists": False,
                "error": f"Error inesperado al validar usuario: Código {response.status_code}."
            }

    except requests.ConnectionError:
        return {
            "exists": False,
            "error": "No se pudo conectar con el microservicio de autenticación (contenedor posiblemente caído)."
        }
    except requests.Timeout:
        return {
            "exists": False,
            "error": "Tiempo de espera agotado al contactar al microservicio de autenticación."
        }
    except requests.RequestException as e:
        return {
            "exists": False,
            "error": f"Error general al contactar autenticación: {str(e)}"
        }
    except Exception as e:
        return {
            "exists": False,
            "error": f"Error inesperado durante la validación del usuario: {str(e)}"
        }

def crear_configuracion(data):
    try:
        validacion_usuario = validar_usuario(data.id_usuario)

        if not validacion_usuario.get("exists"):
            error_msg = validacion_usuario.get("error", "Usuario no válido o no encontrado.")
            raise ValueError(f"No se puede registrar configuración: {error_msg}")

        if Configuracion.query.filter_by(clave=data.clave).first():
            raise ValueError("Ya existe una configuración registrada con esa clave.")

        nueva_config = data
        db.session.add(nueva_config)
        db.session.commit()

        return {
            "status": "success",
            "message": "Configuración registrada correctamente.",
            "data": nueva_config
        }

    except ValueError as ve:
        return {
            "status": "error",
            "message": str(ve)
        }

    except IntegrityError:
        db.session.rollback()
        return {
            "status": "error",
            "message": "Violación de integridad: clave duplicada u otra restricción."
        }

    except Exception as e:
        db.session.rollback()
        return {
            "status": "error",
            "message": f"Error interno al registrar configuración: {str(e)}"
        }


"""****************************************************************************"""
"""FUNCONES PARA ACTUALIZAR UNA CONFIGURACIÓN"""
def actualizar_configuracion(id_configuracion, data):
    try:
        configuracion = Configuracion.query.get(id_configuracion)

        if not configuracion:
            return {
                "status": "error",
                "message": f"No se encontró ninguna configuración con ID {id_configuracion}."
            }

        validacion_usuario = validar_usuario(data.id_usuario)

        if not validacion_usuario.get("exists"):
            error_msg = validacion_usuario.get("error", "Usuario no válido o no encontrado.")
            raise ValueError(f"No se puede actualizar configuración: {error_msg}")

        # Verifica si ya existe otra configuración con la misma clave
        if Configuracion.query.filter(
            Configuracion.clave == data.clave,
            Configuracion.id_configuracion != id_configuracion
        ).first():
            raise ValueError("Ya existe otra configuración registrada con esa clave.")

        # Actualizar campos
        configuracion.clave = data.clave
        configuracion.valor = data.valor
        configuracion.descripcion = data.descripcion
        configuracion.id_usuario = data.id_usuario
        configuracion.estado = data.estado

        db.session.commit()

        return {
            "status": "success",
            "message": "Configuración actualizada correctamente.",
            "data": configuracion
        }

    except ValueError as ve:
        return {
            "status": "error",
            "message": str(ve)
        }

    except IntegrityError:
        db.session.rollback()
        return {
            "status": "error",
            "message": "Violación de integridad: clave duplicada u otra restricción."
        }

    except Exception as e:
        db.session.rollback()
        return {
            "status": "error",
            "message": f"Error interno al actualizar configuración: {str(e)}"
        }
        
"""****************************************************************************"""

"""FUNCIONES PARA OBTENER CONFIGURACIONES FILTRADAS"""

from flask import abort
from app.models.configuracion_model import Configuracion

def str_to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        val = value.lower()
        if val in ['true', '1']:
            return True
        elif val in ['false', '0']:
            return False
    return None

def obtener_configuraciones_filtradas(filtros):
    try:
        query = Configuracion.query

        filtros_permitidos = {'clave', 'valor', 'descripcion', 'estado', 'id_usuario'}
        filtros_recibidos = set(filtros.keys())

        filtros_invalidos = filtros_recibidos - filtros_permitidos
        if filtros_invalidos:
            raise ValueError(f"Los siguientes filtros no son válidos: {', '.join(filtros_invalidos)}")

        if clave := filtros.get('clave'):
            query = query.filter(Configuracion.clave.ilike(f"%{clave}%"))

        if valor := filtros.get('valor'):
            query = query.filter(Configuracion.valor.ilike(f"%{valor}%"))

        if descripcion := filtros.get('descripcion'):
            query = query.filter(Configuracion.descripcion.ilike(f"%{descripcion}%"))

        if 'estado' in filtros:
            estado_valor = str_to_bool(filtros['estado'])
            if estado_valor is None:
                raise ValueError("El filtro 'estado' debe ser true, false, 1 o 0.")
            query = query.filter(Configuracion.estado == estado_valor)

        if 'id_usuario' in filtros:
            try:
                id_usuario = int(filtros['id_usuario'])
                query = query.filter(Configuracion.id_usuario == id_usuario)
            except ValueError:
                raise ValueError("El filtro 'id_usuario' debe ser un número entero válido.")

        return query.order_by(Configuracion.id_configuracion.desc()).all()

    except ValueError as ve:
        abort(400, description=str(ve))
    except Exception:
        abort(500, description="Error inesperado al obtener configuraciones. Contacte con el administrador.")




"""*******************************************************************************************************************************"""


