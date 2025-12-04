import paramiko

def ejecutar_comando_ssh(host, usuario, clave_path, puerto, comando):
    try:
        key = paramiko.RSAKey.from_private_key_file(clave_path)

        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        cliente.connect(hostname=host, username=usuario, pkey=key, port=puerto)

        stdin, stdout, stderr = cliente.exec_command(comando)
        salida = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        cliente.close()

        if error:
            return False, error
        return True, salida

    except Exception as e:
        return False, str(e)
