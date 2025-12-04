from flask import request, jsonify
from app.models.mikrotik_model import MikrotikAPIConfig
from app.extensions import db
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from app.schemas.mikrotik_schema import MikrotikConfigSchema
import os
from marshmallow.exceptions import ValidationError
from app.utils.ssh_manager import ejecutar_comando_ssh
from paramiko import SSHClient, RSAKey, AutoAddPolicy

def crear_perfil_pppoe_en_mikrotik(data):
    try:
        campos_obligatorios = ["usuario_pppoe", "contrasena_pppoe", "perfil"]
        for campo in campos_obligatorios:
            if campo not in data or not data[campo]:
                return False, {
                    "status": "error",
                    "message": f"El campo '{campo}' es obligatorio."
                }

        mikrotik = MikrotikAPIConfig.query.filter_by(estado=True).first()
        if not mikrotik:
            return False, {
                "status": "error",
                "message": "No hay configuración activa de MikroTik"
            }

        ruta_clave = "/app/.ssh/id_rsa"
        if not os.path.exists(ruta_clave):
            return False, {
                "status": "error",
                "message": "Clave SSH no encontrada en /app/.ssh/id_rsa"
            }

        clave = RSAKey.from_private_key_file(ruta_clave)
        cliente = SSHClient()
        cliente.set_missing_host_key_policy(AutoAddPolicy())
        cliente.connect(
            hostname=mikrotik.host,
            port=int(mikrotik.puerto or 22),
            username=mikrotik.usuario,
            pkey=clave,
            timeout=10
        )

        # Comando base
        comando = (
            f'/ppp secret add '
            f'name="{data["usuario_pppoe"]}" '
            f'password="{data["contrasena_pppoe"]}" '
            f'service=pppoe '
            f'profile="{data["perfil"]}"'
        )

        # Agregar remote-address si se proporciona
        if "remote_address" in data and data["remote_address"]:
            comando += f' remote-address="{data["remote_address"]}"'

        # Ejecutar comando
        cliente.exec_command(comando)
        cliente.close()

        return True, {"status": "success", "message": "Perfil PPPoE creado exitosamente"}

    except Exception as e:
        return False, {
            "status": "error",
            "message": f"Error al crear perfil PPPoE: {str(e)}"
        }


"""***************************************************************************"""

"""FUNCION PARA ACTUALIZAR UN PERFIL PPPoE EN MIKROTIK"""


def actualizar_perfil_pppoe_en_mikrotik(data):
    try:
        campos_obligatorios = ["usuario_pppoe", "contrasena_pppoe", "perfil", "remote_address"]
        for campo in campos_obligatorios:
            if campo not in data or not str(data[campo]).strip():
                return False, {
                    "status": "error",
                    "message": f"El campo '{campo}' es obligatorio."
                }

        usuario_pppoe = data["usuario_pppoe"].strip()
        nueva_contrasena = data["contrasena_pppoe"].strip()
        nuevo_perfil = data["perfil"].strip()
        remote_address = data["remote_address"].strip()

        mikrotik = MikrotikAPIConfig.query.filter_by(estado=True).first()
        if not mikrotik:
            return False, {
                "status": "error",
                "message": "No hay configuración activa de MikroTik"
            }

        ruta_clave = "/app/.ssh/id_rsa"
        if not os.path.exists(ruta_clave):
            return False, {
                "status": "error",
                "message": "Clave SSH no encontrada en /app/.ssh/id_rsa"
            }

        clave = RSAKey.from_private_key_file(ruta_clave)
        cliente = SSHClient()
        cliente.set_missing_host_key_policy(AutoAddPolicy())
        cliente.connect(
            hostname=mikrotik.host,
            port=int(mikrotik.puerto or 22),
            username=mikrotik.usuario,
            pkey=clave,
            timeout=10
        )

        # Buscar el usuario PPPoE actual
        comando_busqueda = f'/ppp secret print where name="{usuario_pppoe}"'
        stdin, stdout, stderr = cliente.exec_command(comando_busqueda)
        resultado = stdout.read().decode()

        if not resultado.strip():
            cliente.close()
            return False, {
                "status": "error",
                "message": f"No se encontró el perfil PPPoE con el nombre '{usuario_pppoe}'"
            }

        # Eliminar usuario antiguo y recrearlo
        cliente.exec_command(f'/ppp secret remove [find name="{usuario_pppoe}"]')
        comando_nuevo = (
            f'/ppp secret add '
            f'name="{usuario_pppoe}" '
            f'password="{nueva_contrasena}" '
            f'service=pppoe '
            f'profile="{nuevo_perfil}" '
            f'remote-address="{remote_address}"'
        )
        cliente.exec_command(comando_nuevo)
        cliente.close()

        return True, {
            "status": "success",
            "message": "Perfil PPPoE actualizado exitosamente en MikroTik"
        }

    except Exception as e:
        return False, {
            "status": "error",
            "message": f"Error al actualizar perfil PPPoE: {str(e)}"
        }
        
        
"""***************************************************************************"""

"""FUNCION PARA ELIMINAR UN USUARIO PPPoE EN MIKROTIK"""

def eliminar_usuario_pppoe_en_mikrotik(data):
    try:
        usuario_pppoe = data.get("usuario_pppoe", "").strip()
        if not usuario_pppoe:
            return False, {
                "status": "error",
                "message": "El campo 'usuario_pppoe' es obligatorio."
            }

        mikrotik = MikrotikAPIConfig.query.filter_by(estado=True).first()
        if not mikrotik:
            return False, {
                "status": "error",
                "message": "No hay configuración activa de MikroTik"
            }

        ruta_clave = "/app/.ssh/id_rsa"
        if not os.path.exists(ruta_clave):
            return False, {
                "status": "error",
                "message": "Clave SSH no encontrada en /app/.ssh/id_rsa"
            }

        clave = RSAKey.from_private_key_file(ruta_clave)
        cliente = SSHClient()
        cliente.set_missing_host_key_policy(AutoAddPolicy())
        cliente.connect(
            hostname=mikrotik.host,
            port=int(mikrotik.puerto or 22),
            username=mikrotik.usuario,
            pkey=clave,
            timeout=10
        )

        # Verificar si el usuario PPPoE existe
        comando_busqueda = f'/ppp secret print where name="{usuario_pppoe}"'
        stdin, stdout, stderr = cliente.exec_command(comando_busqueda)
        resultado = stdout.read().decode()

        if not resultado.strip():
            cliente.close()
            return False, {
                "status": "error",
                "message": f"No se encontró el usuario PPPoE '{usuario_pppoe}' en MikroTik"
            }

        # Eliminar usuario
        comando_eliminar = f'/ppp secret remove [find name="{usuario_pppoe}"]'
        cliente.exec_command(comando_eliminar)
        cliente.close()

        return True, {
            "status": "success",
            "message": f"Usuario PPPoE '{usuario_pppoe}' eliminado correctamente de MikroTik"
        }

    except Exception as e:
        # ✅ Este return garantiza que siempre se devuelva un dict como segundo valor
        return False, {
            "status": "error",
            "message": f"Error inesperado al eliminar usuario PPPoE: {str(e)}"
        }

def desactivar_usuario_pppoe_en_mikrotik(data):
    try:
        usuario_pppoe = data.get("usuario_pppoe", "").strip()
        if not usuario_pppoe:
            return False, {"status": "error", "message": "Falta 'usuario_pppoe'"}

        mikrotik = MikrotikAPIConfig.query.filter_by(estado=True).first()
        if not mikrotik:
            return False, {"status": "error", "message": "Sin configuración activa"}

        ruta_clave = "/app/.ssh/id_rsa"
        clave = RSAKey.from_private_key_file(ruta_clave)
        cliente = SSHClient()
        cliente.set_missing_host_key_policy(AutoAddPolicy())
        cliente.connect(
            hostname=mikrotik.host,
            port=int(mikrotik.puerto or 22),
            username=mikrotik.usuario,
            pkey=clave,
            timeout=10
        )

        # 🔴 Deshabilitar usuario PPPoE
        cliente.exec_command(f'/ppp secret disable [find name="{usuario_pppoe}"]')

        # 🧯 Eliminar sesión activa si está conectado
        cliente.exec_command(f'/ppp active remove [find name="{usuario_pppoe}"]')

        cliente.close()
        return True, {
            "status": "success",
            "message": f"Usuario PPPoE '{usuario_pppoe}' desactivado correctamente"
        }

    except Exception as e:
        return False, {"status": "error", "message": str(e)}

def activar_usuario_pppoe_en_mikrotik(data):
    try:
        usuario_pppoe = data.get("usuario_pppoe", "").strip()
        if not usuario_pppoe:
            return False, {"status": "error", "message": "Falta 'usuario_pppoe'"}

        mikrotik = MikrotikAPIConfig.query.filter_by(estado=True).first()
        if not mikrotik:
            return False, {"status": "error", "message": "Sin configuración activa"}

        ruta_clave = "/app/.ssh/id_rsa"
        clave = RSAKey.from_private_key_file(ruta_clave)
        cliente = SSHClient()
        cliente.set_missing_host_key_policy(AutoAddPolicy())
        cliente.connect(
            hostname=mikrotik.host,
            port=int(mikrotik.puerto or 22),
            username=mikrotik.usuario,
            pkey=clave,
            timeout=10
        )

        # ✅ Habilitar usuario PPPoE
        cliente.exec_command(f'/ppp secret enable [find name="{usuario_pppoe}"]')

        cliente.close()
        return True, {
            "status": "success",
            "message": f"Usuario PPPoE '{usuario_pppoe}' activado correctamente"
        }

    except Exception as e:
        return False, {"status": "error", "message": str(e)}

import re
import logging
#monitoreo de trafico
def obtener_trafico_usuario_pppoe(data): 
    try:
        usuario_raw = data.get("usuario_pppoe", "").strip()
        logging.info(f"🔍 Usuario recibido: {usuario_raw}")

        if not usuario_raw:
            return False, {"status": "error", "message": "Falta 'usuario_pppoe'"}

        usuario_mikrotik = usuario_raw if usuario_raw.startswith("pppoe-") else f"pppoe-{usuario_raw}"
        logging.info(f"👤 Usuario ajustado para MikroTik: {usuario_mikrotik}")

        mikrotik = MikrotikAPIConfig.query.filter_by(estado=True).first()
        if not mikrotik:
            logging.warning("⚠️ No hay configuración activa de MikroTik")
            return False, {"status": "error", "message": "Sin configuración activa"}

        ruta_clave = "/app/.ssh/id_rsa"
        clave = RSAKey.from_private_key_file(ruta_clave)

        cliente = SSHClient()
        cliente.set_missing_host_key_policy(AutoAddPolicy())
        cliente.connect(
            hostname=mikrotik.host,
            port=int(mikrotik.puerto or 22),
            username=mikrotik.usuario,
            pkey=clave,
            timeout=10
        )
        logging.info(f"✅ Conexión SSH exitosa con MikroTik: {mikrotik.host}")

        comando = '/queue simple print stats without-paging'
        stdin, stdout, stderr = cliente.exec_command(comando)
        salida = stdout.read().decode("utf-8")
        cliente.close()

        logging.info("📥 Salida del comando MikroTik:")
        logging.info(salida)

        # Reunir todas las líneas en bloques individuales por cada entrada
        lineas = salida.strip().splitlines()
        bloques = []
        bloque_actual = ""

        for linea in lineas:
            if linea.startswith(" "):  # Línea continuación del bloque anterior
                bloque_actual += " " + linea.strip()
            else:
                if bloque_actual:
                    bloques.append(bloque_actual.strip())
                bloque_actual = linea.strip()
        if bloque_actual:
            bloques.append(bloque_actual.strip())

        logging.info(f"🧩 Se encontraron {len(bloques)} bloques")

        for bloque in bloques:
            if re.search(r'name="<?' + re.escape(usuario_mikrotik) + r'>?"', bloque):
                logging.info(f"🎯 Bloque encontrado para {usuario_mikrotik}: {bloque}")

                # Limpiar el bloque: reemplazar múltiples espacios y saltos de línea
                bloque = re.sub(r'\s+', ' ', bloque.strip())

                def extraer(campo):
                    match = re.search(rf'{campo}=([\d]+/[^\s]+)', bloque)
                    return match.group(1) if match else "0/0"

                def extraer_simple(campo):
                    match = re.search(rf'{campo}=([^\s]+)', bloque)
                    return match.group(1) if match else "0bps"

                return True, {
                    "status": "success",
                    "usuario_pppoe": usuario_mikrotik,
                    "rate": extraer_simple("rate"),
                    "packet_rate": extraer("packet-rate"),
                    "total_rate": extraer_simple("total-rate"),
                    "bytes": extraer("bytes"),
                    "total_bytes": extraer("total-bytes"),
                    "packets": extraer("packets"),
                    "total_packets": extraer("total-packets"),
                    "queued_bytes": extraer("queued-bytes"),
                    "queued_packets": extraer("queued-packets"),
                    "dropped": extraer("dropped"),
                }

        logging.warning(f"🚫 No se encontró tráfico para '{usuario_mikrotik}'")
        return False, {
            "status": "not_found",
            "message": f"No se encontró tráfico para '{usuario_mikrotik}'"
        }

    except Exception as e:
        logging.exception("❌ Error inesperado durante el monitoreo de tráfico")
        return False, {"status": "error", "message": str(e)}