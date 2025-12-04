from flask import Blueprint, request, send_file, jsonify
from app.services.orden_instalacion_service import (
    crear_orden_instalacion,
    asignar_tecnico_a_orden, 
    finalizar_orden,
    cambiar_tecnico_orden
)
from app.models.orden_instalacion import OrdenInstalacion
from app.schemas.orden_instalacion_schema import OrdenInstalacionSchema
from app.extensions import db
from sqlalchemy import and_
from sqlalchemy import func

from werkzeug.utils import secure_filename
import os

ordenes_bp = Blueprint("ordenes_bp", __name__, url_prefix="/ordenes_instalacion")

schema = OrdenInstalacionSchema()
schemas = OrdenInstalacionSchema(many=True)


# Crear orden de instalación
@ordenes_bp.route("/", methods=["POST"])
def crear_orden():
    data = request.get_json()
    return crear_orden_instalacion(data)


# Asignar técnico a una orden manualmente
@ordenes_bp.route("/asignar-tecnico/<int:id_orden>", methods=["PUT"])
def asignar_tecnico(id_orden):
    data = request.get_json()
    id_tecnico = data.get("id_tecnico")

    if not id_tecnico:
        return {"error": "El campo 'id_tecnico' es obligatorio"}, 400

    return asignar_tecnico_a_orden(id_orden, id_tecnico)


# Obtener todas las órdenes
@ordenes_bp.route("/", methods=["GET"])
def listar_ordenes():
    ordenes = OrdenInstalacion.query.order_by(OrdenInstalacion.fecha_creacion.desc()).all()
    return schemas.dump(ordenes), 200


# Obtener una orden por ID
@ordenes_bp.route("/<int:id_orden>", methods=["GET"])
def obtener_orden(id_orden):
    orden = OrdenInstalacion.query.get(id_orden)
    if not orden:
        return {"error": "Orden no encontrada"}, 404
    return schema.dump(orden), 200

#finalizar la orden de instalacion
@ordenes_bp.route("/finalizar/<int:id_orden>", methods=["PUT"])
def finalizar_orden_instalacion(id_orden):
    return finalizar_orden(id_orden)

#cambiar de tecnico a la orden
@ordenes_bp.route("/cambiar-tecnico/<int:id_orden>", methods=["PUT"])
def cambiar_tecnico(id_orden):
    data = request.get_json()
    nuevo_id_tecnico = data.get("id_tecnico")

    if not nuevo_id_tecnico:
        return {"error": "El campo 'id_tecnico' es obligatorio."}, 400

    return cambiar_tecnico_orden(id_orden, nuevo_id_tecnico)

#ver documento o descargar
@ordenes_bp.route('/documento/<int:id_orden>', methods=['GET'])
def obtener_pdf_orden(id_orden):
    orden = OrdenInstalacion.query.get(id_orden)
    if not orden or not orden.documento_pdf:
        return {"error": "Orden no encontrada o sin documento asociado"}, 404

    try:
        return send_file(
            orden.documento_pdf,
            as_attachment=True,
            download_name=f"orden_instalacion_{id_orden}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        return {"error": f"Error al descargar el PDF: {str(e)}"}, 500

#ver documento de la orden    
@ordenes_bp.route('/ver-documento/<int:id_orden>', methods=['GET'])
def ver_pdf_orden(id_orden):
    orden = OrdenInstalacion.query.get(id_orden)
    if not orden or not orden.documento_pdf:
        return {"error": "Orden no encontrada o sin documento asociado"}, 404

    try:
        ruta_absoluta = os.path.abspath(orden.documento_pdf)

        if not os.path.isfile(ruta_absoluta):
            return {"error": f"Archivo no encontrado: {ruta_absoluta}"}, 404

        return send_file(
            ruta_absoluta,
            as_attachment=False,
            download_name=f"orden_instalacion_{id_orden}.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        return {"error": f"Error al visualizar el PDF: {str(e)}"}, 500


#actualizar el documento
@ordenes_bp.route('/documento/<int:id_orden>', methods=['PUT'])
def subir_documento_pdf(id_orden):
    orden = OrdenInstalacion.query.get(id_orden)
    if not orden:
        return {"error": "Orden de instalación no encontrada."}, 404

    if 'documento' not in request.files:
        return {"error": "No se ha enviado ningún archivo."}, 400

    archivo = request.files['documento']
    if archivo.filename == '':
        return {"error": "El archivo está vacío."}, 400

    if not archivo.filename.lower().endswith('.pdf'):
        return {"error": "Solo se permiten archivos PDF."}, 400

    try:
        nombre_archivo = secure_filename(f"orden_instalacion_{id_orden}.pdf")
        ruta_directorio = os.path.join('archivos', 'ordenes')
        os.makedirs(ruta_directorio, exist_ok=True)

        ruta_archivo = os.path.join(ruta_directorio, nombre_archivo)
        archivo.save(ruta_archivo)

        # Actualizar la ruta en la base de datos
        orden.documento_pdf = ruta_archivo
        db.session.commit()

        return {"mensaje": "Documento PDF cargado exitosamente."}, 200
    except Exception as e:
        return {"error": f"No se pudo guardar el archivo: {str(e)}"}, 500


#ver ordenes por id contrato
@ordenes_bp.route('/por-contrato/<int:id_contrato>', methods=['GET'])
def obtener_orden_por_contrato(id_contrato):
    orden = OrdenInstalacion.query.filter_by(id_contrato=id_contrato).first()
    if not orden:
        return {"error": "No se encontró una orden para este contrato"}, 404

    return OrdenInstalacionSchema().dump(orden), 200

#ver ordenes por id
@ordenes_bp.route('/<int:id_orden>', methods=['GET'])
def obtener_orden_por_id(id_orden):
    orden = OrdenInstalacion.query.get(id_orden)
    if not orden:
        return {"error": "Orden no encontrada"}, 404

    return OrdenInstalacionSchema().dump(orden), 200

#ver por filtros
@ordenes_bp.route('/filtros', methods=['GET'])
def obtener_ordenes_filtradas():
    estado = request.args.get('estado')
    id_tecnico = request.args.get('id_tecnico')
    fecha_asignacion_inicio = request.args.get('fecha_asignacion_inicio')
    fecha_asignacion_fin = request.args.get('fecha_asignacion_fin')
    fecha_finalizacion_inicio = request.args.get('fecha_finalizacion_inicio')
    fecha_finalizacion_fin = request.args.get('fecha_finalizacion_fin')

    query = OrdenInstalacion.query

    if estado:
        query = query.filter_by(estado=estado)
    if id_tecnico:
        query = query.filter_by(id_tecnico=id_tecnico)
    if fecha_asignacion_inicio and fecha_asignacion_fin:
        query = query.filter(
            and_(
                OrdenInstalacion.fecha_asignacion >= fecha_asignacion_inicio,
                OrdenInstalacion.fecha_asignacion <= fecha_asignacion_fin
            )
        )
    if fecha_finalizacion_inicio and fecha_finalizacion_fin:
        query = query.filter(
            and_(
                OrdenInstalacion.fecha_finalizacion >= fecha_finalizacion_inicio,
                OrdenInstalacion.fecha_finalizacion <= fecha_finalizacion_fin
            )
        )

    ordenes = query.order_by(OrdenInstalacion.fecha_creacion.desc()).all()
    return OrdenInstalacionSchema(many=True).dump(ordenes), 200

#cambiar el estado de la orden
@ordenes_bp.route("/estado/<int:id_orden>", methods=["PUT"])
def actualizar_estado_orden(id_orden):
    data = request.get_json()
    nuevo_estado = data.get("estado")

    if not nuevo_estado:
        return {"error": "El campo 'estado' es obligatorio."}, 400

    orden = OrdenInstalacion.query.get(id_orden)
    if not orden:
        return {"error": f"No se encontró la orden con ID {id_orden}"}, 404

    orden.estado = nuevo_estado

    # Si el estado es "finalizado", guarda también la fecha_instalacion
    if nuevo_estado == "finalizado":
        from datetime import datetime
        orden.fecha_instalacion = datetime.utcnow()

    db.session.commit()

    return {"mensaje": "Estado de la orden actualizado correctamente."}, 200

#eliminar la orden
@ordenes_bp.route("/<int:id_orden>", methods=["DELETE"])
def eliminar_orden(id_orden):
    orden = OrdenInstalacion.query.get(id_orden)
    if not orden:
        return {"error": f"No se encontró la orden con ID {id_orden}"}, 404

    db.session.delete(orden)
    db.session.commit()

    return {"mensaje": "Orden eliminada correctamente."}, 200

#contar las ordenes por cada estado
@ordenes_bp.route("/estadisticas/por-estado", methods=["GET"])
def contar_ordenes_por_estado():
    resultados = (
        db.session.query(OrdenInstalacion.estado, func.count().label("cantidad"))
        .group_by(OrdenInstalacion.estado)
        .all()
    )

    datos = [{"estado": estado, "cantidad": cantidad} for estado, cantidad in resultados]
    return jsonify(datos), 200

#contar las ordenes por tecnico
@ordenes_bp.route("/estadisticas/por-tecnico", methods=["GET"])
def contar_ordenes_por_tecnico():
    resultados = (
        db.session.query(OrdenInstalacion.id_tecnico, func.count().label("cantidad"))
        .filter(OrdenInstalacion.id_tecnico.isnot(None))
        .group_by(OrdenInstalacion.id_tecnico)
        .all()
    )

    datos = [{"id_tecnico": id_tecnico, "cantidad": cantidad} for id_tecnico, cantidad in resultados]
    return jsonify(datos), 200

#contar por mes las ordenes 
@ordenes_bp.route("/estadisticas/por-mes", methods=["GET"])
def contar_ordenes_por_mes():
    from datetime import datetime

    año_actual = datetime.utcnow().year

    resultados = (
        db.session.query(
            func.extract("month", OrdenInstalacion.fecha_creacion).label("mes"),
            func.count().label("cantidad")
        )
        .filter(func.extract("year", OrdenInstalacion.fecha_creacion) == año_actual)
        .group_by(func.extract("month", OrdenInstalacion.fecha_creacion))
        .order_by("mes")
        .all()
    )

    datos = [{"mes": int(mes), "cantidad": cantidad} for mes, cantidad in resultados]
    return jsonify(datos), 200

# Obtener todas las órdenes asignadas a un técnico específico
@ordenes_bp.route("/por-tecnico/<int:id_tecnico>", methods=["GET"])
def obtener_ordenes_por_tecnico(id_tecnico):
    ordenes = OrdenInstalacion.query.filter_by(id_tecnico=id_tecnico).order_by(OrdenInstalacion.fecha_creacion.desc()).all()

    if not ordenes:
        return jsonify({"mensaje": f"No se encontraron órdenes para el técnico con ID {id_tecnico}"}), 404

    return OrdenInstalacionSchema(many=True).dump(ordenes), 200