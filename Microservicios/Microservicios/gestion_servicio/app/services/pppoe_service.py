from app.models.usuario_pppoe_model import UsuarioPPPoE
from app.models.ips_asignadas_pppoe_model import IPAsignadaPPPoE
from app.schemas.gestion_servicio_schema import GestionServicioSchema
from app.extensions import db
from app.utils.api_clients import (
    obtener_contrato,
    obtener_plan,
    obtener_pool_por_nombre,
    crear_perfil_en_mikrotik
)
from app.utils.ip_utils import generar_ip_libre
from datetime import datetime
from app.utils.pools_utils import obtener_datos_pool_por_nombre, obtener_ip_libre_en_pool, obtener_datos_red_por_contrato, obtener_vlan_por_id, actualizar_estado_onu, obtener_onu_por_contrato
from app.utils.clientes_persona import obtener_datos_cliente
from app.utils.api_instalaciones import obtener_orden_por_contrato
from app.services.gestion_service import registrar_evento_gestion

from unidecode import unidecode
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
def generar_comando_ont_huawei(id_contrato, vlan):
    resultado = obtener_datos_red_por_contrato(id_contrato)
    logging.info(f"[DEBUG] Datos red: {resultado}")
    if resultado["status"] != "success":
        return "No se pudo obtener los datos de red para construir el comando."

    datos = resultado["datos"]
    frame = datos["frame"]
    slot = datos["slot_numero"]
    port = datos["numero_puerto"]
    serial = datos["serial"]
    ont_id = datos["ont_id"]
    id_cliente = datos.get("id_cliente")  # Este campo debe estar presente en los datos de red
    logging.info(f"[DEBUG] Cliente ID: {id_cliente}")
    

     # Obtener datos del cliente (nombre + apellido)
    if id_cliente:
        cliente_info = obtener_datos_cliente(id_cliente)  # Este devuelve el dict con la clave 'persona'
        persona = cliente_info
        logging.info(f"[DEBUG] Persona: {persona}")
        if "nombre" in persona and "apellido" in persona:
            primer_nombre = unidecode(persona["nombre"].split()[0])
            primer_apellido = unidecode(persona["apellido"].split()[0])
            desc = f"{id_contrato}_{primer_nombre}{primer_apellido}"


    service_port = id_contrato

    comando = [
    f"interface gpon {frame}/{slot}",
    f"ont add {port} {ont_id} sn-auth {serial} omci ont-lineprofile-id 2 ont-srvprofile-id 10 desc \"{desc}\"",
    f"service-port {service_port} vlan {vlan} gpon {frame}/{slot}/{port} ont {ont_id} gemport 1 multi-service user-vlan {vlan} tag-transform translate inbound traffic-table index 7 outbound traffic-table index 7"
    ]
    return {
    "status": "success",
    "comando_olt_huawei": comando
}, 201


def crear_usuario_pppoe(data):
    try:
        id_contrato = data.get("id_contrato")
        usuario = data.get("usuario_pppoe")
        contrasena = data.get("contrasena")

        if not id_contrato or not usuario or not contrasena:
            return {"status": "error", "message": "Faltan campos obligatorios"}, 400

        # ✅ Validar que el contrato no tenga ya un usuario PPPoE asignado
        if UsuarioPPPoE.query.filter_by(id_contrato=id_contrato).first():
            return {
                "status": "error",
                "message": "Ya existe un usuario PPPoE para este contrato"
            }, 400

        contrato = obtener_contrato(id_contrato)
        if not contrato:
            return {"status": "error", "message": "Contrato no encontrado"}, 404

        plan = obtener_plan(contrato["id_plan"])
        if not plan:
            return {"status": "error", "message": "Plan no encontrado"}, 404

        pool = obtener_pool_por_nombre(plan["ip_remota"])
        if not pool:
            return {"status": "error", "message": "Pool no encontrado"}, 404
        
        id_cliente = contrato.get("id_cliente")

        cliente_resp = requests.get(f"http://clientes:5001/api/por-cliente/{id_cliente}")
        if not cliente_resp.ok:
            return {"status": "error", "message": "No se pudo obtener cliente"}, 400
        
        cliente_json = cliente_resp.json()
        persona = cliente_json.get("cliente", {}).get("persona", {})
        nombre_cliente = persona.get("nombre", "cliente")
        apellido_cliente = persona.get("apellido", "generico")

        # Obtener una IP libre del rango del pool
        ip_asignada = generar_ip_libre(pool["rango_inicio"], pool["rango_fin"], pool["id_pool"])
        if not ip_asignada:
            return {"status": "error", "message": "No hay IPs libres disponibles o duplicada"}, 400

        # ✅ Obtener VLAN desde el microservicio equipos_red
        vlan_data = obtener_vlan_por_id(plan.get("id_vlan"))
        numero_vlan = vlan_data.get("numero_vlan") if vlan_data else None
        if not numero_vlan:
            return {"status": "error", "message": "No se pudo obtener la VLAN del plan"}, 400
        
        # Obtener la VLAN a partir del id_vlan del plan
        # Obtener la VLAN a partir del id_vlan del plan
        vlan = None
        if "id_vlan" in plan:
            vlan_resp = obtener_vlan_por_id(plan["id_vlan"])
            if vlan_resp and "numero_vlan" in vlan_resp:
                vlan = vlan_resp["numero_vlan"]
            else:
                return {"status": "error", "message": "No se pudo obtener la VLAN del plan"}, 400

        # 🔧 Simulación del comando Huawei (sin ejecución real aún)
        comando_olt = generar_comando_ont_huawei(id_contrato, vlan) if vlan else "VLAN no disponible"

        
        # Crear el registro de usuario PPPoE
        nuevo_usuario = UsuarioPPPoE(
            id_contrato=id_contrato,
            usuario_pppoe=usuario,
            contrasena=contrasena,
            nombre_cliente=f"{nombre_cliente} {apellido_cliente}",
            ip_remota=ip_asignada,
            mikrotik_nombre="MikroTik Principal",
            fecha_creacion=datetime.utcnow()
        )
        db.session.add(nuevo_usuario)
        db.session.flush()

        # Registrar la IP como asignada
        ip_registro = IPAsignadaPPPoE(
            id_usuario_pppoe=nuevo_usuario.id_usuario_pppoe,
            ip=ip_asignada,
            id_pool=pool["id_pool"],
            nombre_pool=pool["nombre"],
            asignada=True,
            fecha_asignacion=datetime.utcnow()
        )
        db.session.add(ip_registro)

        # Crear el perfil en MikroTik
        ok, respuesta = crear_perfil_en_mikrotik({
            "usuario_pppoe": usuario,
            "contrasena_pppoe": contrasena,
            "perfil": plan["nombre_plan"],
            "remote_address": ip_asignada
        })

        if not ok:
            db.session.rollback()
            return {
                "status": "error",
                "message": "Error al crear perfil en MikroTik",
                "detalle": respuesta
            }, 500
        
        # ✅ ACTUALIZAR ESTADO DE LA ONU
        onu = obtener_onu_por_contrato(id_contrato)
        if onu and "id_onu" in onu:
            id_onu = onu["id_onu"]
            orden = obtener_orden_por_contrato(id_contrato)
            if orden and orden.get("estado") == "finalizado":
                estado = "activo"
            else:
                estado = "preactivacion"
            actualizar_estado_onu(id_onu, estado)
        id_usuario = data.get("id_usuario")
        logging.info(f"[DEBUG] id usuario: {id_usuario}")
        # Registrar evento en la gestión del servicio
        ok_gestion, mensaje_gestion = registrar_evento_gestion(
            id_usuario_pppoe=nuevo_usuario.id_usuario_pppoe,
            id_contrato=id_contrato,
            estado_servicio=1,  # activo
            motivo="Activación inicial del servicio PPPoE",
            id_usuario_admin=data.get("id_usuario")
        )
        if not ok_gestion:
            logging.error(f"❌ Error al registrar evento de gestión: {mensaje_gestion}")
            db.session.rollback()
            return {
                "status": "error",
                "message": "No se pudo registrar en gestión del servicio",
                "detalle": mensaje_gestion
            }, 500
        logging.info("✅ Evento de gestión registrado exitosamente para activación del PPPoE.")
        db.session.commit()
        return {
            "status": "success",
            "message": "Usuario PPPoE creado correctamente",
            "usuario_pppoe": usuario,
            "ip_remota": ip_asignada,
            "perfil": plan["nombre_plan"],
            "comando_olt_huawei": comando_olt  # ✅ Devolvemos el comando generado
        }, 201

    except Exception as e:
        db.session.rollback()
        return {"status": "error", "message": str(e)}, 500






"""***************************************************************************"""
"""FUNCION PARA CREAR USUARIOS DINAMICAMENTE EN MIKROTIK PARA PPPoE"""


import random
import string
from unidecode import unidecode
from app.extensions import db
from app.models.usuario_pppoe_model import UsuarioPPPoE
from app.models.ips_asignadas_pppoe_model import IPAsignadaPPPoE
from app.utils.api_clients import crear_perfil_en_mikrotik
from app.utils.contratos_utils import obtener_datos_contrato
from app.utils.planes_utils import obtener_datos_plan

from datetime import datetime
import requests



def generar_contrasena_segura(longitud=12):
    caracteres = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choices(caracteres, k=longitud))

def generar_nombre_usuario_pppoe(nombre, apellido, id_contrato):
    base = unidecode(f"{nombre}{apellido}{id_contrato}").lower()
    usuario = base.replace(" ", "")[:28] + "!"  # máximo 32 caracteres
    return usuario

def crear_usuario_pppoe_automatico(data):
    try:
        id_contrato = data.get("id_contrato")
        if not id_contrato:
            return {"status": "error", "message": "El campo 'id_contrato' es obligatorio"}, 400

        # Verificar que no exista ya un usuario para este contrato
        if UsuarioPPPoE.query.filter_by(id_contrato=id_contrato).first():
            return {
                "status": "error",
                "message": "Ya existe un usuario PPPoE para este contrato"
            }, 400

        contrato_resp = obtener_datos_contrato(id_contrato)
        if contrato_resp.get("status") != "success":
            return {"status": "error", "message": "Contrato no encontrado", "detalle": contrato_resp}, 404

        contrato = contrato_resp.get("contrato")
        id_plan = contrato.get("id_plan")
        id_cliente = contrato.get("id_cliente")

        if not id_plan or not id_cliente:
            return {"status": "error", "message": "Contrato incompleto"}, 400

        cliente_resp = requests.get(f"http://clientes:5001/api/por-cliente/{id_cliente}")
        if not cliente_resp.ok:
            return {"status": "error", "message": "No se pudo obtener cliente"}, 400

        cliente_json = cliente_resp.json()
        persona = cliente_json.get("cliente", {}).get("persona", {})
        nombre_cliente = persona.get("nombre", "cliente")
        apellido_cliente = persona.get("apellido", "generico")

        plan_resp = obtener_datos_plan(id_plan)
        if plan_resp.get("status") != "success":
            return {"status": "error", "message": "Plan no encontrado", "detalle": plan_resp}, 404
        plan = plan_resp.get("plan")

        pool_resp = obtener_datos_pool_por_nombre(plan.get("ip_remota"))
        if pool_resp.get("status") != "success":
            return {"status": "error", "message": "Pool no encontrado", "detalle": pool_resp}, 404
        pool = pool_resp.get("pool")

        ip_libre = obtener_ip_libre_en_pool(pool.get("rango_inicio"), pool.get("rango_fin"))
        if not ip_libre:
            return {"status": "error", "message": "No hay IPs libres disponibles"}, 400

        usuario_pppoe = generar_nombre_usuario_pppoe(nombre_cliente, apellido_cliente, id_contrato)
        contrasena_pppoe = generar_contrasena_segura()

        # Obtener la VLAN a partir del id_vlan del plan
        vlan = None
        if "id_vlan" in plan:
            vlan_resp = obtener_vlan_por_id(plan["id_vlan"])
            if vlan_resp and "numero_vlan" in vlan_resp:
                vlan = vlan_resp["numero_vlan"]
            else:
                return {"status": "error", "message": "No se pudo obtener la VLAN del plan"}, 400

        # 🔧 Simulación del comando Huawei (sin ejecución real aún)
        comando_olt = generar_comando_ont_huawei(id_contrato, vlan) if vlan else "VLAN no disponible"


        if UsuarioPPPoE.query.filter_by(usuario_pppoe=usuario_pppoe).first():
            return {"status": "error", "message": "El usuario PPPoE generado ya existe"}, 400

        nuevo_usuario = UsuarioPPPoE(
            id_contrato=id_contrato,
            usuario_pppoe=usuario_pppoe,
            contrasena=contrasena_pppoe,
            nombre_cliente=f"{nombre_cliente} {apellido_cliente}",
            ip_remota=ip_libre,
            mikrotik_nombre="MikroTik Principal",
            fecha_creacion=datetime.utcnow()
        )
        db.session.add(nuevo_usuario)
        db.session.flush()

        ip_asignada = IPAsignadaPPPoE(
            id_usuario_pppoe=nuevo_usuario.id_usuario_pppoe,
            ip=ip_libre,
            id_pool=pool.get("id_pool"),
            nombre_pool=pool.get("nombre"),
            asignada=True,
            fecha_asignacion=datetime.utcnow()
        )
        db.session.add(ip_asignada)

        payload_mikrotik = {
            "usuario_pppoe": usuario_pppoe,
            "contrasena_pppoe": contrasena_pppoe,
            "perfil": plan.get("nombre_plan"),
            "remote_address": ip_libre
        }

        ok, resultado = crear_perfil_en_mikrotik(payload_mikrotik)
        if not ok:
            db.session.rollback()
            return {"status": "error", "message": "Error al crear perfil en MikroTik", "detalle": resultado}, 500

        
         # ✅ ACTUALIZAR ESTADO DE LA ONU
        onu = obtener_onu_por_contrato(id_contrato)
        if onu and "id_onu" in onu:
            id_onu = onu["id_onu"]
            orden = obtener_orden_por_contrato(id_contrato)
            if orden and orden.get("estado") == "finalizado":
                estado = "activo"
            else:
                estado = "preactivacion"
            actualizar_estado_onu(id_onu, estado)

        # Registrar evento en la gestión del servicio
        ok_gestion, mensaje_gestion = registrar_evento_gestion(
            id_usuario_pppoe=nuevo_usuario.id_usuario_pppoe,
            id_contrato=id_contrato,
            estado_servicio=1,  # activo
            motivo="Activación inicial del servicio PPPoE",
            id_usuario_admin=data.get("id_usuario")
        )
        if not ok_gestion:
            db.session.rollback()
            return {
                "status": "error",
                "message": "No se pudo registrar en gestión del servicio",
                "detalle": mensaje_gestion
            }, 500

        db.session.commit()
        return {
            "status": "success",
            "message": "Usuario PPPoE creado automáticamente",
            "usuario_pppoe": usuario_pppoe,
            "contrasena_pppoe": contrasena_pppoe,
            "ip_remota": ip_libre,
            "perfil": plan.get("nombre_plan"),
            "comando_huawei": comando_olt
        }, 201

    except Exception as e:
        db.session.rollback()
        return {"status": "error", "message": f"Error interno: {str(e)}"}, 500







"""**************************************************************************"""

from app.models.ips_asignadas_pppoe_model import IPAsignadaPPPoE
from app.utils.api_clients import obtener_contrato, obtener_plan, actualizar_perfil_en_mikrotik
from app.utils.pools_utils import obtener_datos_pool_por_nombre, obtener_ip_libre_en_pool
from app.extensions import db
from datetime import datetime


def actualizar_usuario_pppoe(id_usuario, data):
    try:
        # Validar existencia del usuario PPPoE
        usuario_obj = UsuarioPPPoE.query.get(id_usuario)
        if not usuario_obj:
            return {"status": "error", "message": "Usuario PPPoE no encontrado"}, 404

        # Validar campos obligatorios
        campos_obligatorios = ["nueva_contrasena_pppoe", "nuevo_perfil"]
        for campo in campos_obligatorios:
            if campo not in data or not data[campo].strip():
                return {"status": "error", "message": f"El campo '{campo}' es obligatorio"}, 400

        nueva_contrasena = data["nueva_contrasena_pppoe"].strip()
        nuevo_perfil = data["nuevo_perfil"].strip()
        nuevo_remote_address = data.get("nuevo_remote_address")

        usuario_pppoe = usuario_obj.usuario_pppoe

        # Obtener datos del contrato y plan
        contrato_res = obtener_contrato(usuario_obj.id_contrato)
        if not contrato_res or "id_plan" not in contrato_res:
            return {"status": "error", "message": "Contrato inválido o no encontrado"}, 404

        id_plan = contrato_res["id_plan"]
        plan_res = obtener_plan(id_plan)
        if not plan_res or "nombre_plan" not in plan_res:
            return {"status": "error", "message": "Plan inválido o no encontrado"}, 404

        nombre_pool = plan_res.get("ip_remota")
        pool_res = obtener_datos_pool_por_nombre(nombre_pool)
        if pool_res["status"] != "success":
            return {"status": "error", "message": "No se pudo obtener datos del pool"}, 400

        pool = pool_res["pool"]
        nueva_ip = obtener_ip_libre_en_pool(pool["rango_inicio"], pool["rango_fin"])
        if not nueva_ip:
            return {"status": "error", "message": "No hay IP disponible en el pool"}, 400

        # Preparar datos para MikroTik
        payload = {
            "usuario_pppoe": usuario_pppoe,
            "contrasena_pppoe": nueva_contrasena,
            "perfil": nuevo_perfil,
            "remote_address": nueva_ip
        }

        # Actualizar en MikroTik
        ok, respuesta = actualizar_perfil_en_mikrotik(payload)
        if not ok:
            return {
                "status": "error",
                "message": "Error al actualizar perfil en MikroTik",
                "detalle": respuesta
            }, 500

        # Actualizar en base de datos
        usuario_obj.contrasena = nueva_contrasena
        usuario_obj.ip_remota = nueva_ip

        # Registrar IP asignada (insertar o actualizar)
        registro_existente = IPAsignadaPPPoE.query.filter_by(id_usuario_pppoe=usuario_obj.id_usuario_pppoe).first()

        if registro_existente:
            registro_existente.ip = nueva_ip
            registro_existente.id_pool = pool["id_pool"]
            registro_existente.nombre_pool = nombre_pool
            registro_existente.asignada = True
            registro_existente.fecha_asignacion = datetime.utcnow()
        else:
            nuevo = IPAsignadaPPPoE(
                id_usuario_pppoe=usuario_obj.id_usuario_pppoe,
                ip=nueva_ip,
                id_pool=pool["id_pool"],
                nombre_pool=nombre_pool,
                asignada=True,
                fecha_asignacion=datetime.utcnow()
            )
            db.session.add(nuevo)

        db.session.commit()

        return {"status": "success", "message": "Perfil PPPoE actualizado correctamente"}, 200

    except Exception as e:
        db.session.rollback()
        return {"status": "error", "message": f"Error interno: {str(e)}"}, 500



"""**************************************************************************"""

"""FUNCION PARA OBTENER USUARIOS PPPoE CON FILTROS"""
from app.models.usuario_pppoe_model import UsuarioPPPoE
from app.extensions import db

def obtener_usuarios_pppoe(filtros):
    try:
        filtros_permitidos = {
            "id_usuario_pppoe": "entero",
            "id_contrato": "entero",
            "usuario_pppoe": "texto",
            "ip_remota": "texto",
            "nombre_cliente": "texto",
            "mikrotik_nombre": "texto",
            "estado":"texto"
        }

        query = UsuarioPPPoE.query

        for clave, valor in filtros.items():
            if clave not in filtros_permitidos:
                return {
                    "status": "error",
                    "message": "Parámetro de búsqueda no válido"
                }, 400

            tipo = filtros_permitidos[clave]
            columna = getattr(UsuarioPPPoE, clave)

            if tipo == "entero":
                try:
                    valor_entero = int(valor)
                    query = query.filter(columna == valor_entero)
                except ValueError:
                    return {"status": "error", "message": f"El valor de '{clave}' debe ser un número entero"}, 400
            elif tipo == "texto":
                query = query.filter(columna.ilike(f"%{valor}%"))

        usuarios = query.order_by(UsuarioPPPoE.fecha_creacion.desc()).all()

        resultado = []
        for u in usuarios:
            resultado.append({
                "id_usuario_pppoe": u.id_usuario_pppoe,
                "id_contrato": u.id_contrato,
                "usuario_pppoe": u.usuario_pppoe,
                "nombre_cliente": u.nombre_cliente,
                "ip_remota": u.ip_remota,
                "mikrotik_nombre": u.mikrotik_nombre,
                "estado": u.estado,
                "fecha_creacion": u.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S") if u.fecha_creacion else None
            })

        return {"status": "success", "usuarios_pppoe": resultado}, 200

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error al obtener usuarios PPPoE: {str(e)}"
        }, 500


"""***************************************************************************"""

import os
from dotenv import load_dotenv
from app.utils.api_config import CONFIG_SERVICE_URL


load_dotenv()
from app.utils.api_config import delete_usuario_pppoe_en_mikrotik

def eliminar_usuario_pppoe(id_usuario_pppoe):
    try:
        usuario = UsuarioPPPoE.query.get(id_usuario_pppoe)
        if not usuario:
            return {"status": "error", "message": "Usuario PPPoE no encontrado"}, 404

        # Primero intentamos eliminar en MikroTik usando función utilitaria
        payload = {"usuario_pppoe": usuario.usuario_pppoe}
        ok, respuesta = delete_usuario_pppoe_en_mikrotik(payload)

        if not ok or respuesta.get("status") != "success":
            return {
                "status": "error",
                "message": f"No se pudo eliminar el perfil en MikroTik: {respuesta.get('message', '')}"
            }, 400

        # Si fue exitoso en MikroTik, eliminamos localmente
        db.session.delete(usuario)
        db.session.commit()

        return {"status": "success", "message": "Usuario PPPoE eliminado correctamente"}, 200

    except Exception as e:
        db.session.rollback()
        return {
            "status": "error",
            "message": f"Error al eliminar usuario PPPoE: {str(e)}"
        }, 500


from app.models.usuario_pppoe_model import UsuarioPPPoE
from app.utils.contratos_utils import obtener_datos_contrato
from app.utils.planes_utils import obtener_datos_plan

def obtener_detalle_pppoe():
    try:
        usuarios = UsuarioPPPoE.query.all()
        lista = []

        for usuario in usuarios:
            id_contrato = usuario.id_contrato
            contrato_resp = obtener_datos_contrato(id_contrato)

            if contrato_resp["status"] != "success":
                continue
            contrato = contrato_resp["contrato"]
            id_plan = contrato.get("id_plan")

            plan_resp = obtener_datos_plan(id_plan)
            nombre_plan = plan_resp["plan"].get("nombre_plan") if plan_resp["status"] == "success" else "Desconocido"

            lista.append({
                "id_usuario_pppoe": usuario.id_usuario_pppoe,
                "usuario_pppoe": usuario.usuario_pppoe,
                "nombre_cliente": usuario.nombre_cliente,
                "nombre_plan": nombre_plan,
                "ip_remota": usuario.ip_remota,
                "estado": usuario.estado
            })

        return {"status": "success", "data": lista}, 200

    except Exception as e:
        return {"status": "error", "message": str(e)}, 500
    

#obtener usuario pppoe con id
from app.models.usuario_pppoe_model import UsuarioPPPoE
from app.extensions import db
from app.schemas.usuario_pppoe_schema import UsuarioPPPoESchema

def obtener_pppoe_por_id(id_usuario_pppoe):
    usuario = db.session.query(UsuarioPPPoE).filter_by(id_usuario_pppoe=id_usuario_pppoe).first()
    if usuario:
        schema = UsuarioPPPoESchema()  # ✅ instancia del schema
        return schema.dump(usuario)
    return None