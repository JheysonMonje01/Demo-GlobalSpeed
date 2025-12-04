from app.models.plan_model import PlanInternet
from app.extensions import db
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from flask import current_app
import requests
import ipaddress
from app.utils.api_vlans import get_vlan_por_id
from app.utils.api_contratos import verificar_contratos_activos
from sqlalchemy.exc import SQLAlchemyError
from app.schemas.plan_schema import PlanSchema
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def crear_plan(data):
    try:
        # 🔍 Validaciones de campos requeridos
        campos_obligatorios = ["nombre_plan", "velocidad_subida", "velocidad_bajada", "ip_local", "precio", "id_vlan"]
        for campo in campos_obligatorios:
            if campo not in data or data[campo] in [None, ""]:
                return False, f"El campo '{campo}' es obligatorio."

        # ✔️ Validaciones de formato y rangos
        if not isinstance(data["velocidad_subida"], int) or data["velocidad_subida"] <= 0:
            return False, "La velocidad de subida debe ser un número entero mayor a 0."

        if not isinstance(data["velocidad_bajada"], int) or data["velocidad_bajada"] <= 0:
            return False, "La velocidad de bajada debe ser un número entero mayor a 0."

        if not isinstance(data["precio"], (int, float)) or data["precio"] < 0 or data["precio"] > 1000:
            return False, "El precio debe estar entre 0 y 1000."

        try:
            ipaddress.ip_address(data["ip_local"])
            if data.get("dns"):
                ipaddress.ip_address(data["dns"])
        except ValueError:
            return False, "La dirección IP local o DNS no es válida."

        # 📡 Validación de VLAN
        id_vlan = data["id_vlan"]
        exito_vlan, resultado_vlan = get_vlan_por_id(id_vlan)
        if not exito_vlan:
            return False, f"Validación de VLAN fallida: {resultado_vlan}"

        # 🔒 Validación de unicidad
        if PlanInternet.query.filter_by(nombre_plan=data["nombre_plan"]).first():
            return False, "Ya existe un plan con ese nombre."

        #if PlanInternet.query.filter_by(id_vlan=id_vlan).first():
         #   return False, "Ya existe un plan asociado a esta VLAN."

        # 🌐 Obtener IP remota desde pool
        id_pool_remoto = data.get("id_pool_remoto")
        if not id_pool_remoto:
            return False, "El campo 'id_pool_remoto' es obligatorio."

        try:
            url_pool = f"http://equipos_red:5004/pools/{id_pool_remoto}"
            response = requests.get(url_pool, timeout=5)
            if response.status_code != 200:
                return False, f"No se pudo obtener el pool remoto con ID {id_pool_remoto}"
            datos_pool = response.json()
            ip_remota = datos_pool.get("nombre")
            if not ip_remota:
                return False, "El pool remoto no tiene definido un nombre válido."
        except Exception as e:
            return False, f"Error al consultar el pool remoto: {str(e)}"

        # ⚙️ Valores opcionales con default
        rafaga_subida = data.get("rafaga_subida")
        rafaga_bajada = data.get("rafaga_bajada")
        max_subida = data.get("max_subida")
        max_bajada = data.get("max_bajada")
        tiempo_rafaga_subida = data.get("tiempo_rafaga_subida")
        tiempo_rafaga_bajada = data.get("tiempo_rafaga_bajada")
        # Generar address_list automáticamente
        # 🔄 Convertir velocidad_bajada en Mbps
        velocidad_mbps = int(data["velocidad_bajada"])

        # 🏷️ Generar el address_list como "PLAN10MB"
        nombre_address_list = f"PLAN{velocidad_mbps}MB"


        # 🚀 Crear en MikroTik
        payload_mikrotik = {
            "nombre_plan": data["nombre_plan"],
            "velocidad_subida": data["velocidad_subida"],
            "velocidad_bajada": data["velocidad_bajada"],
            "rafaga_subida": rafaga_subida,
            "rafaga_bajada": rafaga_bajada,
            "max_subida": max_subida,
            "max_bajada": max_bajada,
            "tiempo_rafaga_subida": tiempo_rafaga_subida,
            "tiempo_rafaga_bajada": tiempo_rafaga_bajada,
            "ip_local": data["ip_local"],
            "ip_remota": ip_remota,
            "dns": data.get("dns"),
            "address_list": nombre_address_list
        }

        url_mikrotik = current_app.config.get("CONFIGURACION_SERVICE_URL", "http://configuracion:5002") + "/mikrotik/crear-plan"
        try:
            res = requests.post(url_mikrotik, json=payload_mikrotik, timeout=10)
            if res.status_code not in [200, 201]:
                return False, f"Error desde MikroTik: {res.json().get('message', 'Error desconocido')}"
        except Exception as e:
            return False, f"No se pudo conectar al microservicio de configuración: {str(e)}"

        # 💾 Guardar en BD
        nuevo_plan = PlanInternet(
            nombre_plan=data["nombre_plan"],
            velocidad_subida=data["velocidad_subida"],
            velocidad_bajada=data["velocidad_bajada"],
            rafaga_subida=rafaga_subida,
            rafaga_bajada=rafaga_bajada,
            max_subida=max_subida,
            max_bajada=max_bajada,
            tiempo_rafaga_subida=tiempo_rafaga_subida,
            tiempo_rafaga_bajada=tiempo_rafaga_bajada,
            ip_local=data["ip_local"],
            ip_remota=ip_remota,
            dns=data.get("dns"),
            precio=data["precio"],
            id_vlan=id_vlan,
            address_list=nombre_address_list,
            fecha_creacion=datetime.utcnow(),
            fecha_modificacion=datetime.utcnow()
        )

        db.session.add(nuevo_plan)
        db.session.commit()
        return True, nuevo_plan

    except SQLAlchemyError as db_err:
        db.session.rollback()
        return False, f"Error al guardar en la base de datos: {str(db_err)}"

    except Exception as e:
        db.session.rollback()
        return False, f"Error inesperado: {str(e)}"

 
 
 
 
"""*****************************************************************************"""
 
 
def obtener_pool_por_id(pool_id):
    try:
        url = f"http://equipos_red:5004/pools/{pool_id}"
        res = requests.get(url, timeout=5)

        if res.status_code != 200:
            return False, f"No se encontró el pool con ID {pool_id}"

        return True, res.json()

    except Exception as e:
        return False, f"Error al conectar con el microservicio de equipos_red: {str(e)}"

 
"""*****************************************************************************"""

def obtener_plan_por_id(id_plan):
    try:
        plan = PlanInternet.query.get(id_plan)
        if not plan:
            return False, f"No se encontró ningún plan con ID {id_plan}"
        return True, plan
    except SQLAlchemyError as e:
        return False, f"Error al acceder a la base de datos: {str(e)}"



"""LISTAR TODOS LOS PLANES DE INTERNET"""


def listar_todos_los_planes():
    try:
        planes = PlanInternet.query.all()
        from app.schemas.plan_schema import PlanSchema
        schema = PlanSchema(many=True)
        return True, schema.dump(planes)
    except SQLAlchemyError as e:
        return False, f"Error al listar planes: {str(e)}"


"""FUNCION PAARA BUSCAR PLANES DE INTERNET CON FILTROS"""



plan_schema = PlanSchema()
plan_schema_many = PlanSchema(many=True)

def buscar_planes(filtros):
    try:
        query = PlanInternet.query

        # Validar si hay al menos un filtro reconocido
        filtros_aplicados = 0

        if 'id_plan' in filtros:
            try:
                id_plan = int(filtros['id_plan'])
                query = query.filter(PlanInternet.id_plan == id_plan)
                filtros_aplicados += 1
            except ValueError:
                return False, "El valor de 'id_plan' debe ser un número entero."

        if 'nombre_plan' in filtros:
            query = query.filter(PlanInternet.nombre_plan.ilike(f"%{filtros['nombre_plan']}%"))
            filtros_aplicados += 1

        if 'velocidad_subida' in filtros:
            try:
                subida = int(filtros['velocidad_subida'])
                query = query.filter(PlanInternet.velocidad_subida == subida)
                filtros_aplicados += 1
            except ValueError:
                return False, "El valor de 'velocidad_subida' debe ser un número entero."

        if 'velocidad_bajada' in filtros:
            try:
                bajada = int(filtros['velocidad_bajada'])
                query = query.filter(PlanInternet.velocidad_bajada == bajada)
                filtros_aplicados += 1
            except ValueError:
                return False, "El valor de 'velocidad_bajada' debe ser un número entero."

        if 'precio' in filtros:
            try:
                precio = float(filtros['precio'])
                query = query.filter(PlanInternet.precio == precio)
                filtros_aplicados += 1
            except ValueError:
                return False, "El valor de 'precio' debe ser un número válido."

        if 'id_vlan' in filtros:
            try:
                id_vlan = int(filtros['id_vlan'])
                query = query.filter(PlanInternet.id_vlan == id_vlan)
                filtros_aplicados += 1
            except ValueError:
                return False, "El valor de 'id_vlan' debe ser un número entero."

        if filtros_aplicados == 0:
            return False, "No se proporcionaron filtros válidos."

        resultados = query.all()

        return True, resultados

    except SQLAlchemyError as e:
        return False, f"Error al buscar planes: {str(e)}"
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"




"""****************************************************************************"""

"""FUNCION PARA ACTUALIZAR UN PLAN"""

def actualizar_plan(id_plan, data):
    try:
        plan = PlanInternet.query.get(id_plan)
        if not plan:
            return False, f"No se encontró ningún plan con ID {id_plan}"

        requiere_actualizacion_mikrotik = False

        if "id_vlan" in data and data["id_vlan"] != plan.id_vlan:
            return False, "No se permite cambiar la VLAN de un plan existente."

        if "nombre_plan" in data and data["nombre_plan"] != plan.nombre_plan:
            return False, "No se permite cambiar el nombre del plan."

        if "velocidad_subida" in data:
            if not isinstance(data["velocidad_subida"], int) or data["velocidad_subida"] <= 0:
                return False, "La velocidad de subida debe ser un entero positivo."
            plan.velocidad_subida = data["velocidad_subida"]
            requiere_actualizacion_mikrotik = True
        
        if "velocidad_bajada" in data:
            if not isinstance(data["velocidad_bajada"], int) or data["velocidad_bajada"] <= 0:
                return False, "La velocidad de bajada debe ser un entero positivo."
            plan.velocidad_bajada = data["velocidad_bajada"]

            # 🔄 Convertir a Mbps y actualizar address_list
            velocidad_mbps = int(data["velocidad_bajada"])
            plan.address_list = f"PLAN{velocidad_mbps}MB"
            requiere_actualizacion_mikrotik = True

        if "precio" in data:
            try:
                precio_bruto = data["precio"]
                precio_decimal = Decimal(str(precio_bruto)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                if precio_decimal < 0 or precio_decimal > 1000:
                    return False, "El precio debe estar entre 0.00 y 1000.00"
                plan.precio = precio_decimal
            except (InvalidOperation, ValueError):
                return False, "El valor proporcionado para 'precio' no es válido. Use un número como 20.00 o 0.99"

        for campo in ["ip_local", "dns"]:
            if campo in data:
                try:
                    ipaddress.ip_address(data[campo])
                    setattr(plan, campo, data[campo])
                    requiere_actualizacion_mikrotik = True
                except ValueError:
                    return False, f"El valor para {campo} no es una IP válida."

        for campo in ["rafaga_subida", "rafaga_bajada", "max_subida", "max_bajada", "tiempo_rafaga_subida", "tiempo_rafaga_bajada"]:
            if campo in data:
                valor = data[campo]
                if not isinstance(valor, int) or valor < 0:
                    return False, f"El campo '{campo}' debe ser un número entero positivo."
                setattr(plan, campo, valor)
                requiere_actualizacion_mikrotik = True

        if "id_pool_remoto" in data:
            try:
                id_pool = data["id_pool_remoto"]
                url_pool = f"http://equipos_red:5004/pools/{id_pool}"
                response = requests.get(url_pool, timeout=5)
                if response.status_code != 200:
                    return False, f"No se encontró el pool remoto con ID {id_pool}"
                datos_pool = response.json()
                nombre_pool = datos_pool.get("nombre")
                if not nombre_pool:
                    return False, "El pool remoto no tiene un nombre definido."
                plan.ip_remota = nombre_pool
                requiere_actualizacion_mikrotik = True
            except Exception as e:
                return False, f"Error al obtener el pool remoto: {str(e)}"

        plan.fecha_modificacion = datetime.utcnow()

        if requiere_actualizacion_mikrotik:
            payload_actualizacion = {
                "nombre_plan": plan.nombre_plan,
                "velocidad_subida": plan.velocidad_subida,
                "velocidad_bajada": plan.velocidad_bajada,
                "rafaga_subida": plan.rafaga_subida,
                "rafaga_bajada": plan.rafaga_bajada,
                "max_subida": plan.max_subida,
                "max_bajada": plan.max_bajada,
                "tiempo_rafaga_subida": plan.tiempo_rafaga_subida,
                "tiempo_rafaga_bajada": plan.tiempo_rafaga_bajada,
                "ip_local": plan.ip_local,
                "ip_remota": plan.ip_remota,
                "dns": plan.dns,
                "address_list": plan.address_list
            }

            url_mikrotik = current_app.config.get("CONFIGURACION_SERVICE_URL", "http://configuracion:5002") + "/mikrotik/actualizar-plan"
            try:
                res = requests.put(url_mikrotik, json=payload_actualizacion, timeout=10)
                if res.status_code not in [200, 201]:
                    try:
                        return False, f"Error al actualizar en MikroTik: {res.json().get('message', 'Error desconocido')}"
                    except:
                        return False, f"Error al actualizar en MikroTik: respuesta inválida (status {res.status_code})"
            except Exception as e:
                return False, f"No se pudo conectar al microservicio de configuración: {str(e)}"


        db.session.commit()
        return True, plan

    except SQLAlchemyError as db_err:
        db.session.rollback()
        return False, f"Error al actualizar en la base de datos: {str(db_err)}"
    except Exception as e:
        db.session.rollback()
        return False, f"Error inesperado: {str(e)}"




"""****************************************************************************"""


"""FUNCION PARA ELIMINAR UN PLAN"""
def eliminar_plan(id_plan):
    try:
        plan = PlanInternet.query.get(id_plan)
        if not plan:
            return False, "Plan no encontrado"

        # Verificar si hay contratos asociados al plan
        en_uso, resultado = verificar_contratos_activos(id_plan)
        if isinstance(resultado, str):
            return False, resultado
        if en_uso:
            return False, "No se puede eliminar el plan porque está asociado a contratos activos."

        # Payload para eliminar y posible rollback
        payload = {
            "nombre_plan": plan.nombre_plan
        }

        # Payload completo para rollback
        payload_rollback = {
            "nombre_plan": plan.nombre_plan,
            "velocidad_subida": plan.velocidad_subida,
            "velocidad_bajada": plan.velocidad_bajada,
            "rafaga_subida": plan.rafaga_subida,
            "rafaga_bajada": plan.rafaga_bajada,
            "max_subida": plan.max_subida,
            "max_bajada": plan.max_bajada,
            "tiempo_rafaga_subida": plan.tiempo_rafaga_subida,
            "tiempo_rafaga_bajada": plan.tiempo_rafaga_bajada,
            "ip_local": plan.ip_local,
            "ip_remota": plan.ip_remota,
            "dns": plan.dns
        }

        try:
            url_config = current_app.config.get("CONFIGURACION_SERVICE_URL", "http://configuracion:5002") + "/mikrotik/eliminar-plan"
            res = requests.delete(url_config, json=payload, timeout=10)

            if res.status_code != 200:
                return False, f"Error al eliminar el plan en MikroTik: {res.json().get('message')}"

        except Exception as e:
            return False, f"No se pudo conectar al microservicio de configuración (MikroTik): {str(e)}"

        # Si MikroTik eliminó correctamente, proceder a eliminar en base de datos
        try:
            db.session.delete(plan)
            db.session.commit()
            return True, "Plan eliminado correctamente"

        except Exception as e:
            # Intentar restaurar en MikroTik
            try:
                rollback_url = current_app.config.get("CONFIGURACION_SERVICE_URL", "http://configuracion:5002") + "/mikrotik/restaurar-plan"
                requests.post(rollback_url, json=payload_rollback, timeout=10)
            except:
                pass  # Si falla rollback en MikroTik, igual mostramos el error principal

            db.session.rollback()
            return False, f"Error al eliminar en base de datos. Se intentó revertir en MikroTik: {str(e)}"

    except SQLAlchemyError as err:
        db.session.rollback()
        return False, f"Error de base de datos: {str(err)}"
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"
