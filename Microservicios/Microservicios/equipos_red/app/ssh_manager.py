import paramiko

def ejecutar_comando_ssh(host, usuario, contrasena, comando, puerto=22):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=host, port=puerto, username=usuario, password=contrasena, timeout=5)
    stdin, stdout, stderr = client.exec_command(comando)
    salida = stdout.read().decode()
    client.close()
    return salida

def obtener_onus_autofind(config):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=config.host,
        port=config.puerto,
        username=config.usuario,
        password=config.contrasena,
        timeout=5
    )
    stdin, stdout, stderr = client.exec_command("display ont autofind all")
    salida = stdout.read().decode()
    client.close()
    return salida