from paramiko import SSHClient, AutoAddPolicy
import os

def ejecutar_comando_ont_completo(data, olt_config):
    try:
        for campo in ["ip", "usuario", "contrasena"]:
            if not olt_config.get(campo):
                return False, f"Falta el campo obligatorio: {campo}"

        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(
            hostname=olt_config["ip"],
            username=olt_config["usuario"],
            password=olt_config["contrasena"],
            timeout=10
        )

        frame = data["frame"]
        slot = data["slot"]
        puerto = data["port"]
        serial = data["serial"]
        descripcion = data["descripcion"]
        ont_id = data["ont_id"]
        vlan = data["vlan"]
        service_port_id = data["service_port_id"]  # generalmente el id_contrato

        # 1️⃣ Comando ont add
        comando_ont_add = (
            f"interface gpon {frame}/{slot}\n"
            f"ont add {puerto} sn-auth {serial} "
            f"ont-lineprofile-id 10 ont-srvprofile-id 10 desc \"{descripcion}\""
        )

        # 2️⃣ Comando service-port
        comando_service_port = (
            f"service-port {service_port_id} vlan {vlan} gpon {frame}/{slot}/{puerto} "
            f"ont {ont_id} gemport 1 multi-service user-vlan {vlan} tag-transform translate"
        )

        # Ejecutar ambos comandos
        for cmd in [comando_ont_add, comando_service_port]:
            stdin, stdout, stderr = ssh.exec_command(cmd)
            salida = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            if error:
                ssh.close()
                return False, f"❌ Error ejecutando comando: {error}"

        ssh.close()
        return True, "✅ Comandos ONT ejecutados correctamente"

    except Exception as e:
        return False, f"❌ Error SSH: {str(e)}"
