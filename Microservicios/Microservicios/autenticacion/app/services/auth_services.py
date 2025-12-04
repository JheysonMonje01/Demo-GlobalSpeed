from flask import jsonify, request
from app import db
import requests
from app.models.usuario_model import Usuario
from app.schemas.usuario_schema import UsuarioRegistroSchema, UsuarioLoginSchema
from app.utils.password_manager import hash_password, verificar_password
from app.utils.jwt_manager import crear_token, crear_refresh_token
from marshmallow import ValidationError
from datetime import datetime
import re

registro_schema = UsuarioRegistroSchema()
login_schema = UsuarioLoginSchema()

def register_user(data):
    try:
        datos_validados = registro_schema.load(data)
    except ValidationError as err:
        return jsonify({"errores": err.messages}), 400

    correo = datos_validados['correo']
    telefono = datos_validados['telefono']
    contrasena = datos_validados['contrasena']
    id_rol = datos_validados['id_rol']

    if Usuario.query.filter_by(correo=correo).first():
        return jsonify({"error": "El correo ya está registrado"}), 400

    if Usuario.query.filter_by(telefono=telefono).first():
        return jsonify({"error": "El teléfono ya está registrado"}), 400

    if (
        len(contrasena) < 8 or
        not re.search(r'[A-Z]', contrasena) or
        not re.search(r'[a-z]', contrasena) or
        not re.search(r'[0-9]', contrasena) or
        not re.search(r'[!@#$%^&*(),.?":{}|<>]', contrasena)
    ):
        return jsonify({
            "error": "La contraseña debe tener al menos 8 caracteres, incluyendo mayúsculas, minúsculas, números y caracteres especiales."
        }), 400

    hashed_password = hash_password(contrasena)

    nuevo_usuario = Usuario(
        correo=correo,
        contrasena=hashed_password,
        telefono=telefono,
        id_rol=id_rol,
        estado=True
    )

    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({"mensaje": "Usuario registrado exitosamente"}), 201







"""FUNCION PARA EL MÉTODO GET DE LOS USUARIOS CON FILTRADO"""

from sqlalchemy import asc

def buscar_usuarios():
    id_usuario = request.args.get("id_usuario")
    correo = request.args.get("correo")
    telefono = request.args.get("telefono")
    estado = request.args.get("estado")
    id_rol = request.args.get("id_rol")

    query = Usuario.query

    if id_usuario:
        query = query.filter(Usuario.id_usuario == id_usuario)
    if correo:
        query = query.filter(Usuario.correo.ilike(f"%{correo}%"))
    if telefono:
        query = query.filter(Usuario.telefono.ilike(f"%{telefono}%"))
    if estado is not None:
        if estado.lower() == 'true':
            query = query.filter(Usuario.estado.is_(True))
        elif estado.lower() == 'false':
            query = query.filter(Usuario.estado.is_(False))
    if id_rol:
        query = query.filter(Usuario.id_rol == id_rol)

    query = query.order_by(asc(Usuario.id_usuario))

    usuarios = query.all()
    resultados = [
        {
            "id_usuario": u.id_usuario,
            "correo": u.correo,
            "telefono": u.telefono,
            "estado": u.estado,
            "id_rol": u.id_rol
        }
        for u in usuarios
    ]

    return jsonify(resultados), 200





"""FUNCION PARA ACTUALIZAR USUARIO"""

from app.models.usuario_model import Usuario
from app.models.rol_model import Rol

def actualizar_usuario(id_usuario, data):
    usuario = Usuario.query.get(id_usuario)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    correo = data.get("correo")
    telefono = data.get("telefono")
    estado = data.get("estado")
    id_rol = data.get("id_rol")

    # Validar correo si se envía
    if correo:
        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            return jsonify({"error": "Formato de correo inválido"}), 400

        existente = Usuario.query.filter(
            Usuario.correo == correo, Usuario.id_usuario != id_usuario
        ).first()
        if existente:
            return jsonify({"error": "El correo ya está en uso por otro usuario"}), 400
        usuario.correo = correo
    elif correo == "":
        return jsonify({"error": "El campo 'correo' no puede estar vacío"}), 400

    # Validar teléfono si se envía
    if telefono:
        existente = Usuario.query.filter(
            Usuario.telefono == telefono, Usuario.id_usuario != id_usuario
        ).first()
        if existente:
            return jsonify({"error": "El teléfono ya está en uso por otro usuario"}), 400
        usuario.telefono = telefono
    elif telefono == "":
        return jsonify({"error": "El campo 'telefono' no puede estar vacío"}), 400

    # Validar estado (True o False)
    if estado is not None:
        if isinstance(estado, bool):
            usuario.estado = estado
        elif isinstance(estado, str) and estado.lower() in ['true', 'false']:
            usuario.estado = estado.lower() == 'true'
        else:
            return jsonify({"error": "Valor inválido para 'estado'"}), 400

    # Validar existencia del rol si se proporciona
    if id_rol:
        rol_existente = Rol.query.get(id_rol)
        if not rol_existente:
            return jsonify({"error": f"El rol con ID {id_rol} no existe"}), 400
        usuario.id_rol = id_rol

    usuario.fecha_modificacion = datetime.utcnow()
    db.session.commit()

    return jsonify({"mensaje": "Usuario actualizado exitosamente"}), 200


"""###############################################################################"""
from app.utils.password_manager import hash_password, verificar_password

def cambiar_contrasena(id_usuario, data):
    usuario = Usuario.query.get(id_usuario)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    actual = data.get("contrasena_actual")
    nueva = data.get("nueva_contrasena")
    confirmar = data.get("confirmar_contrasena")

    if not all([actual, nueva, confirmar]):
        return jsonify({"error": "Se requieren todos los campos"}), 400

    if not verificar_password(actual, usuario.contrasena):
        return jsonify({"error": "La contraseña actual es incorrecta"}), 401

    if nueva != confirmar:
        return jsonify({"error": "La nueva contraseña y su confirmación no coinciden"}), 400

    # Validar seguridad de contraseña
    if (
        len(nueva) < 8 or
        not re.search(r"[A-Z]", nueva) or
        not re.search(r"[a-z]", nueva) or
        not re.search(r"\d", nueva) or
        not re.search(r"[!@#$%^&*(),.?\":{}|<>]", nueva)
    ):
        return jsonify({"error": "La contraseña debe tener al menos 8 caracteres, incluyendo mayúsculas, minúsculas, números y caracteres especiales."}), 400

    usuario.contrasena = hash_password(nueva)
    usuario.fecha_modificacion = datetime.utcnow()
    db.session.commit()

    return jsonify({"mensaje": "Contraseña actualizada correctamente"}), 200
















"""####################################################################################3"""

def eliminar_usuario(id_usuario):
    usuario = Usuario.query.get(id_usuario)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if not usuario.estado:
        return jsonify({"error": "El usuario ya está inactivo"}), 400

    usuario.estado = False
    usuario.fecha_modificacion = datetime.utcnow()
    db.session.commit()

    return jsonify({"mensaje": "Usuario desactivado correctamente"}), 200

"""####################################################################################3"""

def eliminar_usuario_total(id_usuario):
    usuario = Usuario.query.get(id_usuario)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    db.session.delete(usuario)
    db.session.commit()

    return jsonify({"mensaje": "Usuario eliminado permanentemente"}), 200





"""#####################################################################################3"""









"""FUNCION DEL LOGIN CON REDIS"""


def login_user(data):
    try:
        datos_validados = login_schema.load(data)
    except ValidationError as err:
        return jsonify({"errores": err.messages}), 400

    correo = datos_validados['correo']
    contrasena = datos_validados['contrasena']

    usuario = Usuario.query.filter_by(correo=correo).first()

    if not usuario:
        return jsonify({"error": "El usuario no está registrado"}), 404

    if not verificar_password(contrasena, usuario.contrasena):
        return jsonify({"error": "Credenciales incorrectas"}), 401

    if not usuario.estado:
        return jsonify({"error": "El usuario está inactivo"}), 403

    token = crear_token({
        "id": usuario.id_usuario,
        "correo": usuario.correo,
        "rol": usuario.id_rol
    })

    refresh = crear_refresh_token({
        "id": usuario.id_usuario,
        "correo": usuario.correo,
        "rol": usuario.id_rol
    })

    return jsonify({
        "mensaje": "Inicio de sesión exitoso",
        "token": token,
        "refresh_token": refresh
    }), 200
    
    

"""FUNCIONES PARA EL REFRESH TOKEN Y PARA EL LOGOUT""" 
from flask_jwt_extended import decode_token
import json
from app.utils.jwt_manager import crear_token, crear_refresh_token, es_refresh_token_valido, eliminar_refresh_token

def refresh_token(data):
    refresh_token = data.get("refresh_token")
    if not refresh_token:
        return jsonify({"error": "Se requiere el refresh_token"}), 400

    if not es_refresh_token_valido(refresh_token):
        return jsonify({"error": "Refresh token inválido o expirado"}), 401

    try:
        identity = json.loads(decode_token(refresh_token)["sub"])
    except Exception:
        return jsonify({"error": "Refresh token inválido"}), 401

    nuevo_token = crear_token(identity)
    return jsonify({
        "mensaje": "Token renovado exitosamente",
        "token": nuevo_token
    }), 200

def logout(data):
    refresh_token = data.get("refresh_token")
    if not refresh_token:
        return jsonify({"error": "Se requiere el refresh_token"}), 400

    eliminar_refresh_token(refresh_token)
    return jsonify({"mensaje": "Sesión cerrada correctamente"}), 200


    
    

"""FUNCIONES PARA LA RECUPERACION DE CONTRASEÑA"""

from app.utils.email_sender import enviar_correo_recuperacion
from datetime import timedelta

def solicitar_recuperacion(data):
    correo = data.get("correo")
    if not correo:
        return jsonify({"error": "El correo es obligatorio"}), 400

    usuario = Usuario.query.filter_by(correo=correo).first()
    if not usuario:
        return jsonify({"mensaje": "Si el correo está registrado, se enviará un email"}), 200

    # Crear token JWT válido por 15 minutos
    token = crear_token(
        {"id": usuario.id_usuario, "correo": usuario.correo},
        expiracion=15  # ← solo el número de minutos
    )


    status = enviar_correo_recuperacion(correo, token)

    if status == 202:
        return jsonify({"mensaje": "Correo enviado con instrucciones"}), 200
    else:
        return jsonify({"error": "Error al enviar el correo"}), 500





"""RESTABLECER CONTRASEÑA"""
from flask_jwt_extended import decode_token
from app.models.usuario_model import Usuario
from app.utils.password_manager import hash_password
from app import db
from datetime import datetime
import json
import re

def restablecer_contrasena(data):
    token = data.get("token")
    nueva = data.get("nueva_contrasena")
    confirmar = data.get("confirmar_contrasena")

    if not token or not nueva or not confirmar:
        return jsonify({"error": "Todos los campos son obligatorios"}), 400

    if nueva != confirmar:
        return jsonify({"error": "Las contraseñas no coinciden"}), 400

    # Validación de seguridad
    if (
        len(nueva) < 8 or
        not re.search(r"[A-Z]", nueva) or
        not re.search(r"[a-z]", nueva) or
        not re.search(r"[0-9]", nueva) or
        not re.search(r"[!@#$%^&*(),.?\":{}|<>]", nueva)
    ):
        return jsonify({
            "error": "La contraseña debe tener al menos 8 caracteres, incluyendo mayúsculas, minúsculas, números y caracteres especiales."
        }), 400

    try:
        decoded = decode_token(token)
        payload = decoded.get("sub") or decoded.get("identity")

        if isinstance(payload, str):
            payload = json.loads(payload)

        id_usuario = payload.get("id")
        if not id_usuario:
            return jsonify({"error": "Token inválido: sin ID de usuario"}), 400

        usuario = Usuario.query.get(id_usuario)
        if not usuario:
            return jsonify({"error": "Usuario no encontrado"}), 404

        if hash_password(nueva) == usuario.contrasena:
            return jsonify({"error": "La nueva contraseña no puede ser igual a la anterior"}), 400

        # Actualiza la contraseña
        usuario.contrasena = hash_password(nueva)
        usuario.actualizado_en = datetime.utcnow()
        db.session.commit()

        return jsonify({"mensaje": "Contraseña restablecida con éxito"}), 200

    except Exception as e:
        return jsonify({"error": "Token inválido o expirado", "detalle": str(e)}), 401







""" *** PARA CREAR EL USUARIO Y MANDAR ESOS CAMPOS A LA TABLA PERSONA ***"""
"""******************************************************************************************"""
"""
from flask import jsonify
from app import db
from app.models.usuario_model import Usuario
from app.schemas.usuario_persona_schema import UsuarioPersonaRegistroSchema
from app.utils.password_manager import hash_password
from marshmallow import ValidationError
import re
import requests

registro_completo_schema = UsuarioPersonaRegistroSchema()

def register_user_con_persona(data):
    try:
        datos_validados = registro_completo_schema.load(data)
    except ValidationError as err:
        return jsonify({"errores": err.messages}), 400

    correo = datos_validados["correo"]
    telefono = datos_validados["telefono"]
    contrasena = datos_validados["contrasena"]
    id_rol = datos_validados["id_rol"]
    nombre = datos_validados["nombre"]
    apellido = datos_validados["apellido"]

    if Usuario.query.filter_by(correo=correo).first():
        return jsonify({"error": "El correo ya está registrado"}), 400
    if Usuario.query.filter_by(telefono=telefono).first():
        return jsonify({"error": "El teléfono ya está registrado"}), 400

    # Validación de contraseña segura
    if (
        len(contrasena) < 8 or
        not re.search(r'[A-Z]', contrasena) or
        not re.search(r'[a-z]', contrasena) or
        not re.search(r'[0-9]', contrasena) or
        not re.search(r'[!@#$%^&*(),.?":{}|<>]', contrasena)
    ):
        return jsonify({
            "error": "La contraseña debe tener al menos 8 caracteres, incluyendo mayúsculas, minúsculas, números y caracteres especiales."
        }), 400

    hashed_password = hash_password(contrasena)

    # Crear usuario
    nuevo_usuario = Usuario(
        correo=correo,
        contrasena=hashed_password,
        telefono=telefono,
        id_rol=id_rol,
        estado=True
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    # Preparar payload para microservicio de clientes
    payload = {
        #"cedula_ruc": "",
        "nombre": nombre,
        "apellido": apellido,
        "telefono": telefono,
        "correo": correo,
        #"direccion_domiciliaria": None,
        "id_usuario": nuevo_usuario.id_usuario,
        "id_rol": id_rol
    }

    try:
        response = requests.post("http://clientes:5001/api/personas/externo", json=payload, timeout=5)

        if response.status_code != 201:
            return jsonify({
                "mensaje": "Usuario creado, pero falló la creación de persona.",
                "detalle": response.text
            }), 201

    except requests.RequestException as e:
        return jsonify({
            "mensaje": "Usuario creado, pero error al conectar con el microservicio de clientes.",
            "error": str(e)
        }), 201

    return jsonify({"mensaje": "Usuario y persona registrados correctamente"}), 201

"""

"""******************************************************************************************"""



"""
from flask import jsonify
from app import db
from app.models.usuario_model import Usuario
from app.schemas.usuario_persona_schema import UsuarioPersonaRegistroSchema
from app.utils.password_manager import hash_password
from marshmallow import ValidationError
import re
import requests

registro_completo_schema = UsuarioPersonaRegistroSchema()

def register_user_con_persona(data):
    try:
        datos_validados = registro_completo_schema.load(data)
    except ValidationError as err:
        return jsonify({"errores": err.messages}), 400

    correo = datos_validados["correo"]
    telefono = datos_validados["telefono"]
    contrasena = datos_validados["contrasena"]
    id_rol = datos_validados["id_rol"]
    nombre = datos_validados["nombre"]
    apellido = datos_validados["apellido"]
    cedula_ruc = datos_validados["cedula_ruc"]
    direccion_domiciliaria = datos_validados.get("direccion_domiciliaria")
    foto = datos_validados.get("foto")

    if Usuario.query.filter_by(correo=correo).first():
        return jsonify({"error": "El correo ya está registrado"}), 400
    if Usuario.query.filter_by(telefono=telefono).first():
        return jsonify({"error": "El teléfono ya está registrado"}), 400

    if (
        len(contrasena) < 8 or
        not re.search(r'[A-Z]', contrasena) or
        not re.search(r'[a-z]', contrasena) or
        not re.search(r'[0-9]', contrasena) or
        not re.search(r'[!@#$%^&*(),.?":{}|<>]', contrasena)
    ):
        return jsonify({
            "error": "La contraseña debe tener al menos 8 caracteres, incluyendo mayúsculas, minúsculas, números y caracteres especiales."
        }), 400

    hashed_password = hash_password(contrasena)

    nuevo_usuario = Usuario(
        correo=correo,
        contrasena=hashed_password,
        telefono=telefono,
        id_rol=id_rol,
        estado=True
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    # Payload para microservicio de clientes
    payload = {
        "cedula_ruc": cedula_ruc,
        "nombre": nombre,
        "apellido": apellido,
        "telefono": telefono,
        "correo": correo,
        "direccion_domiciliaria": direccion_domiciliaria,
        "foto": foto,
        "id_usuario": nuevo_usuario.id_usuario,
        "id_rol": id_rol
    }

    try:
        response = requests.post("http://clientes:5001/api/personas/externo", json=payload, timeout=5)

        if response.status_code != 201:
            return jsonify({
                "mensaje": "Usuario creado, pero falló la creación de persona.",
                "detalle": response.text
            }), 201

    except requests.RequestException as e:
        return jsonify({
            "mensaje": "Usuario creado, pero error al conectar con el microservicio de clientes.",
            "error": str(e)
        }), 201

    return jsonify({"mensaje": "Usuario y persona registrados correctamente"}), 201

    """
    
"""******************************************************************************************"""

from flask import jsonify
from app import db
from app.models.usuario_model import Usuario
from app.schemas.usuario_persona_schema import UsuarioPersonaRegistroSchema
from app.utils.password_manager import hash_password
from marshmallow import ValidationError
import re
import requests

registro_completo_schema = UsuarioPersonaRegistroSchema()


def register_user_con_persona(data):
    try:
        datos_validados = registro_completo_schema.load(data)
    except ValidationError as err:
        return jsonify({"errores": err.messages}), 400

    correo = datos_validados["correo"]
    telefono = datos_validados["telefono"]
    contrasena = datos_validados["contrasena"]
    id_rol = datos_validados["id_rol"]
    nombre = datos_validados["nombre"]
    apellido = datos_validados["apellido"]
    cedula_ruc = datos_validados["cedula_ruc"]
    direccion_domiciliaria = datos_validados.get("direccion_domiciliaria")
    foto = datos_validados.get("foto")

    if Usuario.query.filter_by(correo=correo).first():
        return jsonify({"error": "Este correo ya está registrado en el sistema."}), 400
    if Usuario.query.filter_by(telefono=telefono).first():
        return jsonify({"error": "Este número de teléfono ya está registrado."}), 400

    if (
        len(contrasena) < 8 or
        not re.search(r'[A-Z]', contrasena) or
        not re.search(r'[a-z]', contrasena) or
        not re.search(r'[0-9]', contrasena) or
        not re.search(r'[!@#$%^&*(),.?":{}|<>]', contrasena)
    ):
        return jsonify({
            "error": "La contraseña debe tener al menos 8 caracteres, incluyendo mayúsculas, minúsculas, números y caracteres especiales."
        }), 400

    hashed_password = hash_password(contrasena)

    nuevo_usuario = Usuario(
        correo=correo,
        contrasena=hashed_password,
        telefono=telefono,
        id_rol=id_rol,
        estado=True
    )
    db.session.add(nuevo_usuario)
    db.session.commit()

    payload = {
        "cedula_ruc": cedula_ruc,
        "nombre": nombre,
        "apellido": apellido,
        "telefono": telefono,
        "correo": correo,
        "direccion_domiciliaria": direccion_domiciliaria,
        "foto": foto,
        "id_usuario": nuevo_usuario.id_usuario,
        "id_rol": id_rol
    }

    try:
        response = requests.post("http://clientes:5001/api/personas/externo", json=payload, timeout=5)

        if response.status_code != 201:
            return jsonify({
                "mensaje": "El usuario fue creado exitosamente, pero no se pudo registrar su perfil personal.",
                "accion": "Puede intentar completarlo más tarde desde el panel de administración.",
                "detalle_error": response.text
            }), 201

    except requests.RequestException:
        return jsonify({
            "mensaje": "El usuario fue creado exitosamente, pero ocurrió un problema al comunicarse con el servicio de perfiles.",
            "accion": "Verifique la conexión del microservicio de clientes e intente completar el perfil posteriormente."
        }), 201

    return jsonify({"mensaje": "Usuario y perfil registrados correctamente."}), 201



"""******************************************************************************************"""
from app.schemas.completar_persona_schema import CompletarPersonaSchema
from flask import jsonify
import requests
from marshmallow import ValidationError

completar_persona_schema = CompletarPersonaSchema()

def completar_persona(data):
    try:
        datos_validados = completar_persona_schema.load(data)
    except ValidationError as err:
        return jsonify({
            "mensaje": "Error de validación en los datos enviados.",
            "errores": err.messages
        }), 400

    try:
        response = requests.post("http://clientes:5001/api/personas/externo", json=datos_validados, timeout=5)

        if response.status_code == 201:
            return jsonify({
                "mensaje": "Perfil de usuario completado exitosamente."
            }), 201

        else:
            return jsonify({
                "mensaje": "No se pudo completar el perfil del usuario.",
                "accion": "Revise los datos o intente nuevamente más tarde.",
                "detalle_error": response.text
            }), response.status_code

    except requests.RequestException:
        return jsonify({
            "mensaje": "No fue posible conectar con el servicio de perfiles.",
            "accion": "Verifique que el microservicio de clientes esté activo e intente de nuevo."
        }), 503

"""******************************************************************************************"""
"""FUNCION PARA ACTUALIZAR USUARIO Y SINCRONIZAR CON PERSONA"""

from app.schemas.usuario_update_schema import UsuarioUpdateSchema
from app.utils.password_manager import hash_password
from app.models.usuario_model import Usuario

usuario_update_schema = UsuarioUpdateSchema()

def actualizar_usuario(id_usuario, data):
    usuario = Usuario.query.get(id_usuario)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    try:
        datos_validados = usuario_update_schema.load(data)
    except ValidationError as err:
        return jsonify({"errores": err.messages}), 400

    cambios = []

    if "correo" in datos_validados and datos_validados["correo"] != usuario.correo:
        usuario.correo = datos_validados["correo"]
        cambios.append("correo")

    if "telefono" in datos_validados and datos_validados["telefono"] != usuario.telefono:
        usuario.telefono = datos_validados["telefono"]
        cambios.append("telefono")

    if "id_rol" in datos_validados and datos_validados["id_rol"] != usuario.id_rol:
        usuario.id_rol = datos_validados["id_rol"]
        cambios.append("id_rol")

    if "estado" in datos_validados and datos_validados["estado"] != usuario.estado:
        usuario.estado = datos_validados["estado"]
        cambios.append("estado")

    if "contrasena" in datos_validados:
        nueva_contrasena = datos_validados["contrasena"]
        if len(nueva_contrasena) >= 8:
            usuario.contrasena = hash_password(nueva_contrasena)
            cambios.append("contrasena")

    db.session.commit()

    # Llamar a microservicio de clientes para sincronizar los datos de persona
    sync_payload = {
        "id_usuario": id_usuario,
        "correo": usuario.correo,
        "telefono": usuario.telefono
    }

    for campo in ["nombre", "apellido", "direccion_domiciliaria", "foto"]:
        if campo in datos_validados:
            sync_payload[campo] = datos_validados[campo]

    try:
        requests.put("http://clientes:5001/api/personas/sincronizar-completo", json=sync_payload, timeout=5)
    except requests.RequestException:
        pass  # Registrar en logs si deseas, pero no bloquea la actualización

    return jsonify({"mensaje": "Usuario actualizado correctamente", "campos_actualizados": cambios}), 200


"""*******************************************************************************************"""

"""  FUNCION PARA ELIMINAR USUARIO LOGICO (CAMBIAR ESTADO A FALSE) Y SINCRONIZAR CON PERSONA  """
def eliminar_usuario_logico(id_usuario):
    usuario = Usuario.query.get(id_usuario)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    if usuario.estado is False:
        return jsonify({"mensaje": "El usuario ya se encuentra desactivado."}), 200

    usuario.estado = False
    db.session.commit()

    return jsonify({"mensaje": "Usuario desactivado correctamente."}), 200


def eliminar_usuario_fisico(id_usuario):
    usuario = Usuario.query.get(id_usuario)

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    db.session.delete(usuario)
    db.session.commit()

    # Notificar al microservicio de clientes para eliminar persona
    try:
        response = requests.delete(f"http://clientes:5001/api/personas/por-usuario/{id_usuario}", timeout=5)

        if response.status_code not in (200, 204):
            return jsonify({
                "mensaje": "Usuario eliminado, pero no se pudo eliminar su perfil en el microservicio de clientes.",
                "detalle": response.text
            }), 200

    except requests.RequestException:
        return jsonify({
            "mensaje": "Usuario eliminado, pero no se pudo contactar al microservicio de clientes.",
        }), 200

    return jsonify({"mensaje": "Usuario y perfil asociados eliminados permanentemente."}), 200


"""********************************************************************************************"""



from app.models.usuario_model import Usuario

def obtener_usuario_por_id(id_usuario):
    try:
        usuario = Usuario.query.get(id_usuario)
        if not usuario:
            return {"status": "error", "message": "Usuario no encontrado"}, 404

        return {
            "status": "success",
            "usuario": {
                "id_usuario": usuario.id_usuario,
                "correo": usuario.correo,
                "telefono": usuario.telefono,
                "id_rol": usuario.id_rol,
                "estado": usuario.estado,
                "fecha_creacion": usuario.fecha_creacion.strftime("%Y-%m-%d %H:%M:%S") if usuario.fecha_creacion else None
            }
        }, 200
    except Exception as e:
        return {"status": "error", "message": f"Error interno: {str(e)}"}, 500


