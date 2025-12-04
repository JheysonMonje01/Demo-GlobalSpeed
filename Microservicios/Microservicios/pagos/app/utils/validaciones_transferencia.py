def validar_datos_transferencia(data):
    errores = {}

    # Validar nombre del titular
    nombre = data.get("nombre_beneficiario", "").strip()
    if not nombre:
        errores["nombre_beneficiario"] = "El nombre del beneficiario es obligatorio."
    elif len(nombre) < 3:
        errores["nombre_beneficiario"] = "El nombre debe tener al menos 3 caracteres."

    # Validar entidad financiera
    banco = data.get("entidad_financiera", "").strip()
    if not banco:
        errores["entidad_financiera"] = "El nombre del banco o entidad financiera es obligatorio."
    elif len(banco) < 3:
        errores["entidad_financiera"] = "El nombre del banco debe tener al menos 3 caracteres."

    # Validar número de cuenta
    cuenta = data.get("numero_cuenta", "").strip()
    if not cuenta:
        errores["numero_cuenta"] = "El número de cuenta es obligatorio."
    elif not cuenta.isdigit():
        errores["numero_cuenta"] = "El número de cuenta debe contener solo dígitos."
    elif len(cuenta) < 6:
        errores["numero_cuenta"] = "El número de cuenta es demasiado corto."

    # Validar tipo de cuenta
    tipo = data.get("tipo_cuenta", "").strip().lower()
    if tipo not in ["ahorros", "corriente"]:
        errores["tipo_cuenta"] = "El tipo de cuenta debe ser 'ahorros' o 'corriente'."

    # Validar ID de método de pago
    id_metodo = data.get("id_metodo_pago")
    if id_metodo is None:
        errores["id_metodo_pago"] = "El ID del método de pago es obligatorio."
    elif not isinstance(id_metodo, int) or id_metodo <= 0:
        errores["id_metodo_pago"] = "El ID del método de pago debe ser un entero positivo."

    return errores


