from app.utils.empresa_client import obtener_datos_empresa

def obtener_nombre_empresa():
    data = obtener_datos_empresa()
    if data:
        return f"Nuestra empresa se llama {data.get('nombre', 'Nombre no disponible')}."
    return "No se pudo obtener el nombre de la empresa."

def obtener_direccion_empresa():
    data = obtener_datos_empresa()
    if data:
        return f"Nos encontramos ubicados en {data.get('direccion', 'Dirección no disponible')}."
    return "No se pudo obtener la dirección."

def obtener_correos_empresa():
    data = obtener_datos_empresa()
    if data and "correos" in data and data["correos"]:
        correos = [c["correo"] for c in data["correos"]]
        lista = ", ".join(correos)
        return f"Puedes escribirnos a los siguientes correos: {lista}."
    return "No se encontraron correos registrados."

def obtener_telefonos_empresa():
    data = obtener_datos_empresa()
    if data and "telefonos" in data and data["telefonos"]:
        telefonos = [t["telefono"] for t in data["telefonos"]]
        lista = ", ".join(telefonos)
        return f"Puedes comunicarte con nosotros al: {lista}."
    return "No se encontraron teléfonos registrados."

def obtener_representante_empresa():
    data = obtener_datos_empresa()
    if data and data.get("representante"):
        return f"El representante legal de la empresa es el Ing. {data['representante']}."
    return "No se pudo obtener el representante de la empresa."

def obtener_contactos_empresa():
    data = obtener_datos_empresa()
    if not data:
        return "No se pudo obtener los datos de contacto de la empresa."

    mensajes = []

    # Teléfonos
    telefonos = data.get("telefonos", [])
    if telefonos:
        numeros = ", ".join([t["telefono"] for t in telefonos])
        mensajes.append(f"Teléfonos: {numeros}")
    else:
        mensajes.append("No hay teléfonos registrados.")

    # Correos
    correos = data.get("correos", [])
    if correos:
        emails = ", ".join([c["correo"] for c in correos])
        mensajes.append(f"Correos electrónicos: {emails}")
    else:
        mensajes.append("No hay correos electrónicos registrados.")

    return " | ".join(mensajes)

def obtener_horario_atencion():
    return (
        "Nuestro horario de atención es de lunes a viernes de 9:30 a 17:30, "
        "y los sábados de 09:00 a 14:00. Estaremos encantados de ayudarte dentro de ese horario. 😊"
    )
