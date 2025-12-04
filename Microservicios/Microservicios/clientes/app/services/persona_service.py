from flask import jsonify, request
from app import db
from app.models.persona_model import Persona
from app.schemas.persona_schema import persona_schema, personas_schema
from datetime import datetime

def crear_persona(data):
    errors = persona_schema.validate(data)
    if errors:
        return jsonify(errors), 400

    persona = Persona(**data)
    db.session.add(persona)
    db.session.commit()
    return persona_schema.jsonify(persona), 201





def listar_personas_con_filtros():
    query = Persona.query
    filtros = request.args

    if 'id_persona' in filtros:
        try:
            id_persona = int(filtros['id_persona'])
            query = query.filter_by(id_persona=id_persona)
        except ValueError:
            return jsonify({"error": "El id_persona debe ser un número entero válido."}), 400

    if 'nombre' in filtros:
        query = query.filter(Persona.nombre.ilike(f"%{filtros['nombre']}%"))
    if 'apellido' in filtros:
        query = query.filter(Persona.apellido.ilike(f"%{filtros['apellido']}%"))
    if 'cedula_ruc' in filtros:
        query = query.filter(Persona.cedula_ruc.ilike(f"%{filtros['cedula_ruc']}%"))
    if 'correo' in filtros:
        query = query.filter_by(correo=filtros['correo'])
    if 'telefono' in filtros:
        query = query.filter_by(telefono=filtros['telefono'])

    # Filtro por tipo de rol
    rol = filtros.get('rol')  # cliente | tecnico | administrador
    if rol:
        rol = rol.lower()
        if rol == 'cliente':
            query = query.join(Persona.cliente)
        elif rol == 'tecnico':
            query = query.join(Persona.tecnico)
        elif rol == 'administrador':
            query = query.join(Persona.administrador)
        else:
            return jsonify({"error": "Valor de rol inválido. Debe ser cliente, tecnico o administrador."}), 400

    personas = query.all()
    return jsonify(personas_schema.dump(personas)), 200




def obtener_persona(id_persona):
    persona = Persona.query.get(id_persona)
    if not persona:
        return jsonify({"error": "Persona no encontrada"}), 404
    return persona_schema.jsonify(persona), 200

def actualizar_persona(id_persona, data):
    persona = Persona.query.get(id_persona)
    if not persona:
        return jsonify({"error": "Persona no encontrada"}), 404

    for field, value in data.items():
        if hasattr(persona, field):
            setattr(persona, field, value)

    persona.fecha_modificacion = datetime.utcnow()
    db.session.commit()
    return persona_schema.jsonify(persona), 200

def eliminar_persona(id_persona):
    persona = Persona.query.get(id_persona)
    if not persona:
        return jsonify({"error": "Persona no encontrada"}), 404

    db.session.delete(persona)
    db.session.commit()
    return jsonify({"mensaje": "Persona eliminada"}), 200


"""**************************************************************************"""


from app.db import db
from app.models.persona_model import Persona
from app.models.cliente_model import Cliente
from app.models.tecnico_model import Tecnico
from app.models.administrador_model import Administrador

def crear_persona_desde_autenticacion(data):
    campos_obligatorios = ['cedula_ruc', 'nombre', 'apellido', 'telefono', 'correo', 'id_usuario', 'id_rol']
    for campo in campos_obligatorios:
        if campo not in data or data[campo] in [None, ""]:
            raise ValueError(f"El campo {campo} es obligatorio.")

    nueva_persona = Persona(
        cedula_ruc=data['cedula_ruc'],
        nombre=data['nombre'],
        apellido=data['apellido'],
        telefono=data['telefono'],
        correo=data['correo'],
        direccion_domiciliaria=data.get('direccion_domiciliaria'),
        foto=data.get('foto'),
        id_usuario=data['id_usuario']
    )
    db.session.add(nueva_persona)
    db.session.commit()

    id_persona = nueva_persona.id_persona
    id_rol = data['id_rol']

    if id_rol == 3:
        db.session.add(Cliente(id_persona=id_persona))
    elif id_rol == 2:
        db.session.add(Tecnico(id_persona=id_persona))
    elif id_rol == 1:
        db.session.add(Administrador(id_persona=id_persona))

    db.session.commit()
    return {"mensaje": "Persona registrada correctamente", "id_persona": id_persona}




"""**************************************************************************"""




"""FUNCION PARA EL MICROSERCVICIO DE GESTION_SERVICIO"""

def obtener_persona_por_id_cliente(id_cliente):
    """
    Devuelve los datos completos de la persona asociada a un cliente.
    """
    from app.models.cliente_model import Cliente

    cliente = Cliente.query.get(id_cliente)
    if not cliente:
        return jsonify({"status": "error", "message": "Cliente no encontrado"}), 404

    persona = Persona.query.get(cliente.id_persona)
    if not persona:
        return jsonify({"status": "error", "message": "Persona no encontrada para el cliente"}), 404

    return jsonify({
        "status": "success",
        "cliente": {
            "id_cliente": cliente.id_cliente,
            "id_persona": cliente.id_persona,
            "persona": persona_schema.dump(persona)
        }
    }), 200


