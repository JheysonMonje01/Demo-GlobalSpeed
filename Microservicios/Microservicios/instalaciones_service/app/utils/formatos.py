def formatear_telefono_a_internacional(telefono_local):
    if not telefono_local:
        return None
    telefono = telefono_local.strip().replace(" ", "").replace("-", "")
    if telefono.startswith("0") and len(telefono) == 10:
        return f"+593{telefono[1:]}"
    return telefono if telefono.startswith("+") else None