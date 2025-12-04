from flask import jsonify
from app.db import db
from app.models.persona_model import Persona
from datetime import datetime
import base64


def sincronizar_datos_usuario(id_usuario, nuevo_correo=None, nuevo_telefono=None):
    """
    Sincroniza correo y/o teléfono del usuario con su registro en la tabla persona.

    Args:
        id_usuario (int): ID del usuario cuyo registro fue actualizado.
        nuevo_correo (str): Correo actualizado (opcional).
        nuevo_telefono (str): Teléfono actualizado (opcional).
    """
    persona = Persona.query.filter_by(id_usuario=id_usuario).first()

    if not persona:
        return jsonify({"error": "No existe una persona asociada a este usuario"}), 404

    actualizado = False

    if nuevo_correo and persona.correo != nuevo_correo:
        persona.correo = nuevo_correo
        actualizado = True

    if nuevo_telefono and persona.telefono != nuevo_telefono:
        persona.telefono = nuevo_telefono
        actualizado = True

    if actualizado:
        persona.fecha_modificacion = datetime.utcnow()
        db.session.commit()

    return jsonify({"mensaje": "Datos sincronizados correctamente"}), 200



"""***********************************************************************************"""

"""SINCRONIZACION DE DATOS DE USUARIO PARA LA ACTUALIZACION DE CORREO Y TELEFONO EN LA TABLA PERSONA"""

from datetime import datetime

def sincronizar_persona_completa(data):
    
    id_usuario = data.get('id_usuario')
    persona = Persona.query.filter_by(id_usuario=id_usuario).first()

    if not id_usuario:
        return jsonify({"error": "El campo 'id_usuario' es obligatorio."}), 400

    

    if not persona:
        return jsonify({"error": "No se encontró una persona asociada a este usuario."}), 404

    campos_actualizados = []

    if "correo" in data and data["correo"] != persona.correo:
        persona.correo = data["correo"]
        campos_actualizados.append("correo")

    if "telefono" in data and data["telefono"] != persona.telefono:
        persona.telefono = data["telefono"]
        campos_actualizados.append("telefono")

    if "nombre" in data and data["nombre"] != persona.nombre:
        persona.nombre = data["nombre"]
        campos_actualizados.append("nombre")

    if "apellido" in data and data["apellido"] != persona.apellido:
        persona.apellido = data["apellido"]
        campos_actualizados.append("apellido")

    if "direccion_domiciliaria" in data and data["direccion_domiciliaria"] != persona.direccion_domiciliaria:
        persona.direccion_domiciliaria = data["direccion_domiciliaria"]
        campos_actualizados.append("direccion_domiciliaria")

    # Manejo especial para imagen

    # ✅ Manejo de imagen correctamente
    if "foto" in data and data["foto"]:
        try:
            base64_data = data["foto"].split(",")[1] if "," in data["foto"] else data["foto"]
            nueva_foto = base64.b64decode(base64_data)

            if persona.foto != nueva_foto:
                persona.foto = nueva_foto
                campos_actualizados.append("foto")  # ✅ AÑADIR AQUÍ
                print("✅ Foto actualizada (bytes):", len(nueva_foto))
            else:
                print("ℹ️ Misma foto enviada, no se actualiza")
        except Exception as e:
            print("❌ Error al decodificar imagen:", str(e))





    if not campos_actualizados:
        return jsonify({"mensaje": "No se realizaron cambios. Los datos ya están actualizados."}), 200

    persona.fecha_modificacion = datetime.utcnow()
    db.session.commit()

    return jsonify({
        "mensaje": "Datos de persona actualizados correctamente.",
        "campos_actualizados": campos_actualizados
    }), 200




"""************************************************************************************"""