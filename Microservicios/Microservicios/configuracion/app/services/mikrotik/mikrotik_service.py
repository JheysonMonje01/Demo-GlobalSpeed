import paramiko
import socket
from   flask import request, jsonify 
from app.models.mikrotik_model import MikrotikAPIConfig
from app.extensions import db
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from app.schemas.mikrotik_schema import MikrotikConfigSchema
import os
import socket
import paramiko
from marshmallow.exceptions import ValidationError
from app.utils.ssh_manager import ejecutar_comando_ssh


"""EN PRODUCCION CAMBIAR PARA NO EXPONER LOS ERRORES INTERNOS"""

def test_conexion_mikrotik_ssh(data):
    try:
        host = data.get("host")
        puerto = data.get("puerto", 22)
        usuario = data.get("usuario")
        clave_privada = data.get("clave_privada")

        # Validación de campos requeridos
        if not all([host, usuario, clave_privada]):
            return {"status": "error", "message": "Host, usuario y ruta de clave privada son obligatorios."}, 400

        # Validar que la ruta sea segura y esté dentro de /app/.ssh/
        ruta_base = "/app/.ssh/"
        if not clave_privada.startswith(ruta_base):
            return {
                "status": "error",
                "message": f"Ruta no permitida. Solo se aceptan claves dentro de {ruta_base}"
            }, 403

        # Verificar que el archivo exista
        if not os.path.isfile(clave_privada):
            return {
                "status": "error",
                "message": f"Archivo de clave no encontrado: {clave_privada}"
            }, 404

        # Verificar conexión al host y puerto SSH
        try:
            socket.create_connection((host, puerto), timeout=5)
        except socket.error:
            return {
                "status": "error",
                "message": "No se puede establecer conexión TCP con el host/puerto especificado."
            }, 400

        # Crear cliente SSH con clave privada
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            pkey = paramiko.RSAKey.from_private_key_file(clave_privada)
            client.connect(hostname=host, port=puerto, username=usuario, pkey=pkey, timeout=5)

            stdin, stdout, stderr = client.exec_command("/system/resource/print")
            salida = stdout.read().decode().strip()
            client.close()

            return {
                "status": "success",
                "message": "Conexión SSH exitosa con MikroTik.",
                "output": salida
            }, 200

        except paramiko.AuthenticationException:
            return {"status": "error", "message": "Autenticación fallida. Verifica usuario o clave privada."}, 401
        except Exception as e:
            return {"status": "error", "message": f"Error SSH inesperado: {str(e)}"}, 500

    except Exception as e:
        return {"status": "error", "message": f"Error general en la validación SSH: {str(e)}"}, 500



"""FUNCIONES PARA CREAR UNA NUEVA CONFIGURACION DE MIKROTIK"""

def crear_configuracion_mikrotik(data):
    try:
        schema = MikrotikConfigSchema()
        nueva_config = schema.load(data)

        # Verificar duplicado por host y puerto
        existente = MikrotikAPIConfig.query.filter_by(
            host=nueva_config.host, puerto=nueva_config.puerto).first()
        if existente:
            raise ValueError("Ya existe una configuración con ese host y puerto.")

        # Validar conexión SSH antes de guardar
        clave_privada = data.get("clave_privada")
        if not clave_privada:
            raise ValueError("La ruta de la clave privada es requerida para validar la conexión.")

        ruta_base = "/app/.ssh/"
        if not clave_privada.startswith(ruta_base):
            raise ValueError(f"Ruta no permitida. Solo se aceptan claves dentro de {ruta_base}")

        if not os.path.isfile(clave_privada):
            raise ValueError(f"Archivo de clave privada no encontrado: {clave_privada}")

        # Verificar conexión al puerto SSH
        try:
            socket.create_connection((nueva_config.host, nueva_config.puerto or 22), timeout=5)
        except socket.error:
            raise ValueError("No se puede establecer conexión TCP con el host/puerto.")

        # Autenticación vía clave privada
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            pkey = paramiko.RSAKey.from_private_key_file(clave_privada)
            client.connect(
                hostname=nueva_config.host,
                port=nueva_config.puerto or 22,
                username=nueva_config.usuario,
                pkey=pkey,
                timeout=5
            )
            client.close()
        except paramiko.AuthenticationException:
            raise ValueError("Autenticación fallida con SSH. Verifica el usuario o la clave.")
        except Exception as e:
            raise ValueError(f"Error al validar la conexión SSH: {str(e)}")

        # Si pasó todo, guardar en la BD
        nueva_config.fecha_modificacion = datetime.utcnow()
        db.session.add(nueva_config)
        db.session.commit()

        return {
            "status": "success",
            "message": "Configuración MikroTik registrada correctamente.",
            "data": schema.dump(nueva_config)
        }, 201

    except ValueError as ve:
        return {"status": "error", "message": str(ve)}, 400
    except IntegrityError:
        db.session.rollback()
        return {"status": "error", "message": "Error de integridad: configuración duplicada."}, 409
    except Exception as e:
        db.session.rollback()
        return {"status": "error", "message": f"Error inesperado: {str(e)}"}, 500

"""**************************************************************************************************************"""


"""FUNCIONES PARA ACTUALIZAR LA CONFIGURACION DE MIKROTIK"""
def actualizar_configuracion_mikrotik(id_mikrotik, data):
    try:
        # 🔍 1. Buscar configuración existente
        config = MikrotikAPIConfig.query.get(id_mikrotik)
        if not config:
            return {"status": "error", "message": "Configuración no encontrada."}, 404

        # ⚠️ 2. Verificar conflictos con otro host+puerto
        nuevo_host = data.get("host", config.host)
        nuevo_puerto = data.get("puerto", config.puerto)

        conflicto = MikrotikAPIConfig.query.filter(
            MikrotikAPIConfig.host == nuevo_host,
            MikrotikAPIConfig.puerto == nuevo_puerto,
            MikrotikAPIConfig.id_mikrotik != id_mikrotik
        ).first()

        if conflicto:
            return {
                "status": "error",
                "message": "Ya existe otra configuración con ese host y puerto."
            }, 409

        # ✅ 3. Validar con el esquema (evitamos sobreescribir campos no permitidos)
        schema = MikrotikConfigSchema(partial=True)
        schema.load(data, partial=True)  # validación (ignorar resultado)

        campos_permitidos = ['nombre', 'host', 'puerto', 'usuario', 'estado']
        for campo in campos_permitidos:
            if campo in data:
                valor = data[campo]

                # Validaciones específicas
                if campo == 'puerto' and (not isinstance(valor, int) or valor < 1 or valor > 65535):
                    return {"status": "error", "message": "Puerto inválido."}, 400
                if campo == 'estado' and not isinstance(valor, bool):
                    return {"status": "error", "message": "El campo 'estado' debe ser booleano."}, 400

                setattr(config, campo, valor)

        # 🕓 4. Actualizar y guardar
        config.fecha_modificacion = datetime.utcnow()
        db.session.commit()

        return {
            "status": "success",
            "message": "Configuración actualizada correctamente.",
            "data": schema.dump(config)
        }, 200

    except ValidationError as ve:
        return {"status": "error", "message": ve.messages}, 400

    except Exception as e:
        db.session.rollback()
        return {"status": "error", "message": f"Error al actualizar: {str(e)}"}, 500


"""***************************************************************************************************************"""
"""FUNCION PARA BUSCAR Y RETORNAR UNA CONFIGURACION DE MIKROTIK POR ID"""

def obtener_configuraciones_mikrotik():
    try:
        query = MikrotikAPIConfig.query
        filtros = request.args

        # ⚠️ Lista blanca de filtros válidos
        filtros_permitidos = {
            'id_mikrotik', 'nombre', 'host', 'usuario', 'puerto', 'estado',
            'fecha_creacion_inicio', 'fecha_creacion_fin',
            'fecha_modificacion_inicio', 'fecha_modificacion_fin'
        }

        # 🔐 Rechazar filtros no permitidos
        for param in filtros:
            if param not in filtros_permitidos:
                return jsonify({
                    "status": "error",
                    "message": f"Parámetro no permitido: '{param}'"
                }), 400

        # Filtros comunes
        if 'id_mikrotik' in filtros:
            try:
                query = query.filter_by(id_mikrotik=int(filtros['id_mikrotik']))
            except ValueError:
                return jsonify({"status": "error", "message": "El id_mikrotik debe ser un número entero."}), 400

        if 'nombre' in filtros:
            query = query.filter(MikrotikAPIConfig.nombre.ilike(f"%{filtros['nombre']}%"))

        if 'host' in filtros:
            query = query.filter(MikrotikAPIConfig.host.ilike(f"%{filtros['host']}%"))

        if 'usuario' in filtros:
            query = query.filter(MikrotikAPIConfig.usuario.ilike(f"%{filtros['usuario']}%"))

        if 'puerto' in filtros:
            try:
                query = query.filter(MikrotikAPIConfig.puerto == int(filtros['puerto']))
            except ValueError:
                return jsonify({"status": "error", "message": "El puerto debe ser un número entero."}), 400

        if 'estado' in filtros:
            estado_val = filtros['estado'].lower()
            if estado_val in ['true', '1']:
                query = query.filter(MikrotikAPIConfig.estado.is_(True))
            elif estado_val in ['false', '0']:
                query = query.filter(MikrotikAPIConfig.estado.is_(False))
            else:
                return jsonify({"status": "error", "message": "El campo estado debe ser true o false."}), 400

        # Filtros por fecha de creación
        fecha_creacion_inicio = filtros.get('fecha_creacion_inicio')
        fecha_creacion_fin = filtros.get('fecha_creacion_fin')

        if fecha_creacion_inicio:
            try:
                inicio = datetime.fromisoformat(fecha_creacion_inicio)
                query = query.filter(MikrotikAPIConfig.fecha_creacion >= inicio)
            except ValueError:
                return jsonify({"status": "error", "message": "Formato inválido en fecha_creacion_inicio (usar ISO 8601)"}), 400

        if fecha_creacion_fin:
            try:
                fin = datetime.fromisoformat(fecha_creacion_fin)
                query = query.filter(MikrotikAPIConfig.fecha_creacion <= fin)
            except ValueError:
                return jsonify({"status": "error", "message": "Formato inválido en fecha_creacion_fin (usar ISO 8601)"}), 400

        # Filtros por fecha de modificación
        fecha_mod_inicio = filtros.get('fecha_modificacion_inicio')
        fecha_mod_fin = filtros.get('fecha_modificacion_fin')

        if fecha_mod_inicio:
            try:
                inicio = datetime.fromisoformat(fecha_mod_inicio)
                query = query.filter(MikrotikAPIConfig.fecha_modificacion >= inicio)
            except ValueError:
                return jsonify({"status": "error", "message": "Formato inválido en fecha_modificacion_inicio (usar ISO 8601)"}), 400

        if fecha_mod_fin:
            try:
                fin = datetime.fromisoformat(fecha_mod_fin)
                query = query.filter(MikrotikAPIConfig.fecha_modificacion <= fin)
            except ValueError:
                return jsonify({"status": "error", "message": "Formato inválido en fecha_modificacion_fin (usar ISO 8601)"}), 400

        # Ordenar por defecto de forma ascendente por ID
        resultados = query.order_by(MikrotikAPIConfig.id_mikrotik.asc()).all()
        schema = MikrotikConfigSchema(many=True)
        return jsonify(schema.dump(resultados)), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al obtener configuraciones: {str(e)}"
        }), 500


def obtener_configuracion_por_id(id_mikrotik):
    from app.models.mikrotik_model import MikrotikAPIConfig
    from app.schemas.mikrotik_schema import MikrotikConfigSchema

    try:
        config = MikrotikAPIConfig.query.get(id_mikrotik)
        if not config:
            return jsonify({"status": "error", "message": "Configuración no encontrada"}), 404

        schema = MikrotikConfigSchema()
        return jsonify(schema.dump(config)), 200

    except Exception as e:
        return jsonify({"status": "error", "message": f"Error interno: {str(e)}"}), 500


"""***************************************************************************************************************"""

"""FUNCION PARA ELIMINAR UNA CONFIGURACION DE MIKROTIK POR ID DE FORMA LOGICA"""

# services/mikrotik_service.py
def eliminar_logicamente_mikrotik(id_mikrotik):
    try:
        config = MikrotikAPIConfig.query.get(id_mikrotik)
        if not config:
            return {"status": "error", "message": "Configuración no encontrada."}, 404

        if not config.estado:
            return {"status": "error", "message": "La configuración ya está desactivada."}, 400

        config.estado = False
        config.fecha_modificacion = datetime.utcnow()
        db.session.commit()

        return {
            "status": "success",
            "message": "Configuración desactivada correctamente.",
            "data": MikrotikConfigSchema().dump(config)
        }, 200

    except Exception as e:
        db.session.rollback()
        return {"status": "error", "message": f"Error al desactivar: {str(e)}"}, 500


"""****************************************************************************************************************"""

"""FUNCION PARA ELIMINAR UNA CONFIGURACION DE MIKROTIK POR ID DE FORMA FISICA"""

# services/mikrotik_service.py
def eliminar_fisicamente_mikrotik(id_mikrotik):
    try:
        config = MikrotikAPIConfig.query.get(id_mikrotik)
        if not config:
            return {"status": "error", "message": "Configuración no encontrada."}, 404

        db.session.delete(config)
        db.session.commit()

        return {
            "status": "success",
            "message": "Configuración eliminada permanentemente."
        }, 200

    except Exception as e:
        db.session.rollback()
        return {"status": "error", "message": f"Error al eliminar: {str(e)}"}, 500



"""****************************************************************************************************************"""

"""FUNCION PARA CREAR UNA VLAN EN UN MIKROTIK A TRAVES DE SSH"""

from paramiko import SSHClient, RSAKey, AutoAddPolicy

def crear_vlan_en_mikrotik(numero_vlan, nombre, interface):
    try:
        mikrotik = MikrotikAPIConfig.query.filter_by(estado=True).first()
        if not mikrotik:
            return False, "No hay MikroTik activo configurado"

        try:
            numero_vlan = int(numero_vlan)
            if not (1 <= numero_vlan <= 4095):
                return False, "El número de VLAN debe estar entre 1 y 4095"
        except ValueError:
            return False, "El número de VLAN debe ser un entero válido"

        if not interface or not isinstance(interface, str):
            return False, "Nombre de interfaz inválido"

        ruta_clave = "/app/.ssh/id_rsa"
        if not os.path.exists(ruta_clave):
            return False, "Clave privada no encontrada en /app/.ssh/id_rsa"

        clave = RSAKey.from_private_key_file(ruta_clave)
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(
            hostname=mikrotik.host,
            port=mikrotik.puerto or 22,
            username=mikrotik.usuario,
            pkey=clave,
            timeout=10
        )

        # ✅ Validar que la interfaz exista correctamente
        stdin, stdout, stderr = ssh.exec_command(f'/interface print where name="{interface}"')
        interfaces = stdout.read().decode().strip()
        if not interfaces:
            ssh.close()
            return False, f"La interfaz '{interface}' no existe en el MikroTik"

        # ✅ Comando de creación
        comando = f"/interface vlan add name={nombre} vlan-id={numero_vlan} interface={interface}"
        stdin, stdout, stderr = ssh.exec_command(comando)

        salida = stdout.read().decode().strip()
        error = stderr.read().decode().strip()
        ssh.close()

        if error:
            return False, f"Error MikroTik: {error}"

        return True, salida or f"VLAN {numero_vlan} creada exitosamente"

    except Exception as e:
        return False, f"Error al crear VLAN en MikroTik: {str(e)}"

"""****************************************************************************************************************"""

"""FUNCION PARA modificar"""


def actualizar_configuracion(id_mikrotik, data):
    try:
        config = MikrotikAPIConfig.query.get(id_mikrotik)
        if not config:
            return jsonify({"status": "error", "message": "Configuración no encontrada"}), 404

        # Campos que pueden ser actualizados
        campos_permitidos = ['nombre', 'host', 'usuario', 'contrasena', 'estado']
        cambios = False

        for campo in campos_permitidos:
            if campo in data:
                nuevo_valor = data[campo]
                # Si el valor es distinto al actual, actualizar
                if getattr(config, campo) != nuevo_valor:
                    setattr(config, campo, nuevo_valor)
                    cambios = True

        if not cambios:
            return jsonify({
                "status": "warning",
                "message": "No se realizaron cambios."
            }), 400

        config.fecha_modificacion = datetime.utcnow()
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Configuración actualizada correctamente."
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Error al actualizar: {str(e)}"}), 500


"""****************************************************************************************************************"""

"""FUNCION PARA CREAR UN PLAN EN UN MIKROTIK A TRAVES DE SSH"""

import os
import logging

def crear_plan_en_mikrotik(data):
    try:
        mikrotik = MikrotikAPIConfig.query.filter_by(estado=True).first()
        if not mikrotik:
            logging.error("No hay MikroTik activo configurado.")
            return False, "No hay MikroTik activo configurado"

        nombre_plan = data.get("nombre_plan")
        subida = data.get("velocidad_subida")
        bajada = data.get("velocidad_bajada")
        ip_local = data.get("ip_local")
        ip_remota = data.get("ip_remota")
        dns = data.get("dns")
        address_list = data.get("address_list")  # 👈 Nuevo

        if not all([nombre_plan, subida, bajada]):
            return False, "Faltan campos requeridos: nombre_plan, velocidad_subida, velocidad_bajada"

        # Opcionales
        max_subida = data.get("max_subida")
        max_bajada = data.get("max_bajada")
        rafaga_subida = data.get("rafaga_subida")
        rafaga_bajada = data.get("rafaga_bajada")
        tiempo_rafaga_subida = data.get("tiempo_rafaga_subida")
        tiempo_rafaga_bajada = data.get("tiempo_rafaga_bajada")

        # Construir rate-limit completo
        rate_limit = f"{subida}M/{bajada}M"

        if all([max_subida, max_bajada, rafaga_subida, rafaga_bajada, tiempo_rafaga_subida, tiempo_rafaga_bajada]):
            rate_limit += f" {max_subida}M/{max_bajada}M {rafaga_subida}M/{rafaga_bajada}M {tiempo_rafaga_subida}/{tiempo_rafaga_bajada}"


        ruta_clave = "/app/.ssh/id_rsa"
        if not os.path.exists(ruta_clave):
            return False, "Clave privada no encontrada en /app/.ssh/id_rsa"

        clave = RSAKey.from_private_key_file(ruta_clave)

        cliente = SSHClient()
        cliente.set_missing_host_key_policy(AutoAddPolicy())
        cliente.connect(
            hostname=mikrotik.host,
            port=mikrotik.puerto or 22,
            username=mikrotik.usuario,
            pkey=clave,
            timeout=10
        )

        logging.info(f"✅ Conectado a MikroTik {mikrotik.host}")

        # Verificar existencia exacta
        stdin_check, stdout_check, _ = cliente.exec_command('/ppp profile print without-paging')
        perfiles = stdout_check.read().decode().strip().splitlines()
        if any(f'name="{nombre_plan}"' in linea for linea in perfiles):
            cliente.close()
            return False, f"Ya existe un perfil PPP con el nombre: {nombre_plan}"

        # Comando sin comillas en valores IP
        comando = f'/ppp profile add name="{nombre_plan}" rate-limit="{rate_limit}"'
        if ip_local:
            comando += f' local-address={ip_local}'
        if ip_remota:
            comando += f' remote-address={ip_remota}'
        if dns:
            comando += f' dns-server={dns}'
        if address_list:
            comando += f' address-list={address_list}'  # ✅ Aquí se añade


        logging.debug(f"🛰️ Enviando comando: {comando}")
        stdin, stdout, stderr = cliente.exec_command(comando)
        salida = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        # Verificación posterior
        stdin_verif, stdout_verif, _ = cliente.exec_command(f'/ppp profile print where name="{nombre_plan}"')
        verificacion = stdout_verif.read().decode().strip()
        cliente.close()

        logging.debug(f"📤 STDOUT: {salida}")
        logging.debug(f"📛 STDERR: {error}")

        if error:
            return False, f"Error MikroTik: {error}"
        if not verificacion:
            return False, f"No se pudo verificar la creación del perfil '{nombre_plan}' en MikroTik"

        return True, f"Perfil '{nombre_plan}' creado correctamente en MikroTik"

    except Exception as e:
        logging.exception("Excepción al crear el plan en MikroTik")
        return False, f"Error al crear el plan en MikroTik: {str(e)}"


"""****************************************************************************************************************"""
"""FUNCION PARA CREAR UN IP POOL EN UN MIKROTIK A TRAVES DE SSH"""

def crear_pool_en_mikrotik(data):
    try:
        nombre = data["nombre"]
        inicio = data["rango_inicio"]
        fin = data["rango_fin"]

        # Obtener MikroTik activo
        mikrotik = MikrotikAPIConfig.query.filter_by(estado=True).first()
        if not mikrotik:
            return False, "No hay MikroTik activo configurado"

        ruta_clave = "/app/.ssh/id_rsa"
        if not os.path.isfile(ruta_clave):
            return False, "Clave privada no encontrada en /app/.ssh/id_rsa"

        # Verificar si ya existe un pool con ese nombre
        comando_verificacion = "/ip pool print without-paging"
        exito, salida = ejecutar_comando_ssh(
            host=mikrotik.host,
            usuario=mikrotik.usuario,
            clave_path=ruta_clave,
            puerto=mikrotik.puerto or 22,
            comando=comando_verificacion
        )

        if not exito:
            return False, f"Error al verificar pools existentes: {salida}"

        if any(f'name="{nombre}"' in linea for linea in salida.splitlines()):
            return False, f"Ya existe un pool en MikroTik con el nombre '{nombre}'"

        # Crear nuevo pool
        comando_creacion = f"/ip pool add name={nombre} ranges={inicio}-{fin}"
        exito, salida = ejecutar_comando_ssh(
            host=mikrotik.host,
            usuario=mikrotik.usuario,
            clave_path=ruta_clave,
            puerto=mikrotik.puerto or 22,
            comando=comando_creacion
        )

        if not exito:
            return False, f"Error desde MikroTik: {salida}"

        return True, f"Pool IP '{nombre}' creado en MikroTik correctamente"

    except Exception as e:
        logging.exception("Error al crear pool en MikroTik")
        return False, f"Error al crear pool en MikroTik: {str(e)}"


"""FUNCION PARA ACTUALIZAR UN PLAN EN MIKROTIK"""

def actualizar_plan_en_mikrotik(data):
    try:
        mikrotik = MikrotikAPIConfig.query.filter_by(estado=True).first()
        if not mikrotik:
            return False, "No hay MikroTik activo configurado"

        nombre_plan = data.get("nombre_plan")
        if not nombre_plan:
            return False, "El nombre del plan es obligatorio para actualizar"

        # 🛡️ Cargar clave privada
        ruta_clave = "/app/.ssh/id_rsa"
        if not os.path.exists(ruta_clave):
            return False, "Clave privada no encontrada en /app/.ssh/id_rsa"

        clave = RSAKey.from_private_key_file(ruta_clave)

        cliente = SSHClient()
        cliente.set_missing_host_key_policy(AutoAddPolicy())
        cliente.connect(
            hostname=mikrotik.host,
            port=mikrotik.puerto or 22,
            username=mikrotik.usuario,
            pkey=clave,
            timeout=10
        )

        # 🔎 Verificar si el perfil existe
        stdin_check, stdout_check, _ = cliente.exec_command('/ppp profile print without-paging')
        perfiles = stdout_check.read().decode().strip().splitlines()
        if not any(f'name="{nombre_plan}"' in linea for linea in perfiles):
            cliente.close()
            return False, f"No se encontró el perfil PPP con el nombre: {nombre_plan}"

        # 🔧 Construir nuevo rate-limit
        subida = data.get("velocidad_subida")
        bajada = data.get("velocidad_bajada")
        rafaga_subida = data.get("rafaga_subida", 0)
        rafaga_bajada = data.get("rafaga_bajada", 0)
        max_subida = data.get("max_subida", 0)
        max_bajada = data.get("max_bajada", 0)
        tiempo_rafaga_subida = data.get("tiempo_rafaga_subida", 5)
        tiempo_rafaga_bajada = data.get("tiempo_rafaga_bajada", 5)
        ip_local = data.get("ip_local")
        ip_remota = data.get("ip_remota")
        dns = data.get("dns")
        address_list = data.get("address_list")  # 👈 Nuevo

        rate_limit = (
            f"{bajada}M/{subida}M "
            f"{max_bajada}M/{max_subida}M "
            f"{rafaga_bajada}M/{rafaga_subida}M "
            f"{tiempo_rafaga_bajada}/{tiempo_rafaga_subida}"
        )

        # 🛠️ Comando de actualización (por nombre)
        comando = f'/ppp profile set [find name="{nombre_plan}"] rate-limit="{rate_limit}"'
        if ip_local:
            comando += f' local-address={ip_local}'
        if ip_remota:
            comando += f' remote-address={ip_remota}'
        if dns:
            comando += f' dns-server={dns}'
        if address_list:
            comando += f' address-list={address_list}'  # ✅ Aquí se añade

        stdin, stdout, stderr = cliente.exec_command(comando)
        salida = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        cliente.close()

        if error:
            return False, f"Error al actualizar en MikroTik: {error}"

        return True, f"Plan '{nombre_plan}' actualizado correctamente en MikroTik."

    except Exception as e:
        logging.exception("Error al actualizar plan en MikroTik")
        return False, f"Error inesperado al actualizar plan en MikroTik: {str(e)}"



"""FUNCION PARA ELIMINAR UN PLAN EN MIKROTIK"""

def eliminar_plan_en_mikrotik(data):
    try:
        nombre_plan = data.get("nombre_plan")
        if not nombre_plan:
            return False, "Campo 'nombre_plan' es obligatorio."

        # Obtener la configuración activa de MikroTik
        mikrotik = MikrotikAPIConfig.query.filter_by(estado=True).first()
        if not mikrotik:
            return False, "No hay MikroTik activo disponible."

        ruta_clave = "/app/.ssh/id_rsa"
        if not os.path.exists(ruta_clave):
            return False, "Clave SSH no encontrada en /app/.ssh/id_rsa"

        clave = RSAKey.from_private_key_file(ruta_clave)

        cliente = SSHClient()
        cliente.set_missing_host_key_policy(AutoAddPolicy())
        cliente.connect(
            hostname=mikrotik.host,
            port=mikrotik.puerto or 22,
            username=mikrotik.usuario,
            pkey=clave,
            timeout=10
        )

        # Verificar si el plan existe
        stdin_check, stdout_check, _ = cliente.exec_command('/ppp profile print without-paging')
        perfiles = stdout_check.read().decode().strip().splitlines()

        if not any(f'name="{nombre_plan}"' in linea for linea in perfiles):
            cliente.close()
            return False, f"No existe el perfil PPP '{nombre_plan}' en MikroTik."

        # Ejecutar comando para eliminar el plan
        stdin, stdout, stderr = cliente.exec_command(f'/ppp profile remove [find name="{nombre_plan}"]')
        error = stderr.read().decode().strip()

        # Verificar eliminación más robustamente
        stdin_ver, stdout_ver, _ = cliente.exec_command('/ppp profile print without-paging')
        perfiles_restantes = stdout_ver.read().decode().strip().splitlines()
        cliente.close()

        if error:
            return False, f"Error al eliminar plan en MikroTik: {error}"

        if any(f'name="{nombre_plan}"' in linea for linea in perfiles_restantes):
            return False, f"No se pudo eliminar el perfil '{nombre_plan}', aún existe."

        return True, f"Perfil '{nombre_plan}' eliminado correctamente de MikroTik."

    except Exception as e:
        return False, f"Error al conectar con MikroTik: {str(e)}"












"""FUNCION PARA RESTAURAR UN PLAN EN MIKROTIK"""


def restaurar_plan_en_mikrotik(data):
    try:
        nombre_plan = data.get("nombre_plan")
        if not nombre_plan:
            return False, "Campo 'nombre_plan' es obligatorio para restaurar"

        # Puedes añadir aquí valores por defecto si los necesitas para la restauración de emergencia
        # o puedes enviar todos los campos necesarios desde planes_internet si deseas una restauración exacta

        # Por ahora intentaremos una restauración mínima:
        data_completa = {
            "nombre_plan": nombre_plan,
            "velocidad_subida": 1000,
            "velocidad_bajada": 1000,
            "rafaga_subida": 2000,
            "rafaga_bajada": 2000,
            "max_subida": 3000,
            "max_bajada": 3000,
            "tiempo_rafaga_subida": 5,
            "tiempo_rafaga_bajada": 5,
            "ip_local": "",
            "ip_remota": "",
            "dns": ""
        }

        return crear_plan_en_mikrotik(data_completa)

    except Exception as e:
        return False, f"Error al intentar restaurar plan en MikroTik: {str(e)}"




