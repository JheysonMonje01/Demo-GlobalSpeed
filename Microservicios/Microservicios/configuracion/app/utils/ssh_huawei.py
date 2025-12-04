import paramiko

def probar_conexion_olt_con_credenciales(host, username, password, puerto=22):
    try:
        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        cliente.connect(
            hostname=host,
            port=puerto,
            username=username,
            password=password,
            timeout=10
        )

        # Si se conectó correctamente
        cliente.close()
        return {
            "status": "success",
            "message": f"✅ Conexión exitosa con la OLT en {host}."
        }

    except paramiko.AuthenticationException:
        return {
            "status": "error",
            "message": "❌ Autenticación fallida. Verifica usuario y contraseña."
        }

    except paramiko.SSHException as e:
        return {
            "status": "error",
            "message": f"❌ Error SSH: {str(e)}"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"❌ Error de conexión: {str(e)}"
        }
