import os
from app.models.mikrotik_model import MikrotikAPIConfig
from app.utils.ssh_manager import ejecutar_comando_ssh

def obtener_interfaces_mikrotik(id_mikrotik):
    config = MikrotikAPIConfig.query.get(id_mikrotik)
    if not config:
        return False, "Configuración MikroTik no encontrada"

    host = config.host
    puerto = config.puerto or 22
    usuario = config.usuario
    clave_path = "/app/.ssh/id_rsa"  # ⚠️ Asegúrate de que este archivo exista dentro del contenedor

    if not os.path.isfile(clave_path):
        return False, f"Clave privada no encontrada en {clave_path}"

    comando = "/interface/print terse"

    exito, salida = ejecutar_comando_ssh(
        host,
        usuario,
        clave_path,
        puerto,
        comando
    )

    if not exito:
        return False, f"Error al conectar por SSH: {salida}"

    interfaces = []
    for linea in salida.splitlines():
        if "name=" in linea:
            partes = linea.split("name=")
            if len(partes) > 1:
                nombre = partes[1].split()[0]
                interfaces.append(nombre)

    return True, interfaces
