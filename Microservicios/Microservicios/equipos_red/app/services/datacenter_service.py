from app.models.datacenter import DataCenter
from app.extensions import db
from sqlalchemy.exc import IntegrityError
from flask import abort

def crear_datacenter(data):
    try:
        # Verificar si ya existe un DataCenter con el mismo nombre y ubicación
        existente = DataCenter.query.filter_by(nombre=data.nombre, ubicacion=data.ubicacion).first()
        if existente:
            raise ValueError("Ya existe un DataCenter con ese nombre y ubicación.")

        db.session.add(data)
        db.session.commit()

        return {
            "status": "success",
            "message": "DataCenter creado correctamente.",
            "data": data
        }

    except ValueError as ve:
        return {"status": "error", "message": str(ve)}

    except IntegrityError:
        db.session.rollback()
        return {
            "status": "error",
            "message": "Violación de integridad: campos únicos o foráneos duplicados o inválidos."
        }

    except Exception as e:
        db.session.rollback()
        return {
            "status": "error",
            "message": f"Error interno al crear DataCenter: {str(e)}"
        }


def actualizar_datacenter(id_datacenter, data):
    try:
        datacenter = DataCenter.query.get(id_datacenter)

        if not datacenter:
            return {
                "status": "error",
                "message": f"No se encontró DataCenter con ID {id_datacenter}"
            }

        # Validación de duplicados
        duplicado = DataCenter.query.filter(
            DataCenter.nombre == data.nombre,
            DataCenter.ubicacion == data.ubicacion,
            DataCenter.id_datacenter != id_datacenter
        ).first()

        if duplicado:
            return {
                "status": "error",
                "message": "Ya existe otro DataCenter con ese nombre y ubicación."
            }

        # Actualización de campos
        datacenter.nombre = data.nombre
        datacenter.ubicacion = data.ubicacion
        datacenter.latitud = data.latitud
        datacenter.longitud = data.longitud

        db.session.commit()

        return {
            "status": "success",
            "message": "DataCenter actualizado correctamente.",
            "data": datacenter
        }

    except IntegrityError:
        db.session.rollback()
        return {
            "status": "error",
            "message": "Violación de integridad: datos duplicados o inválidos."
        }

    except Exception as e:
        db.session.rollback()
        return {
            "status": "error",
            "message": f"Error interno al actualizar DataCenter: {str(e)}"
        }


def obtener_datacenters_filtrados(filtros):
    try:
        query = DataCenter.query
        filtros_permitidos = {'nombre', 'ubicacion'}

        for key, value in filtros.items():
            if key not in filtros_permitidos:
                raise ValueError(f"Filtro no válido: {key}")

            if key == 'nombre':
                query = query.filter(DataCenter.nombre.ilike(f"%{value}%"))
            elif key == 'ubicacion':
                query = query.filter(DataCenter.ubicacion.ilike(f"%{value}%"))

        return query.all()

    except ValueError as ve:
        abort(400, description=str(ve))

    except Exception as e:
        abort(500, description="Error al obtener los DataCenters.")


def obtener_datacenter(id_datacenter):
    datacenter = DataCenter.query.get(id_datacenter)
    if not datacenter:
        abort(404, description=f"DataCenter con ID {id_datacenter} no encontrado.")
    return datacenter


def eliminar_datacenter(id_datacenter):
    try:
        datacenter = DataCenter.query.get(id_datacenter)

        if not datacenter:
            return {
                "status": "error",
                "message": f"No se encontró DataCenter con ID {id_datacenter}"
            }

        db.session.delete(datacenter)
        db.session.commit()

        return {
            "status": "success",
            "message": "DataCenter eliminado correctamente."
        }

    except Exception as e:
        db.session.rollback()
        return {
            "status": "error",
            "message": f"Error al eliminar DataCenter: {str(e)}"
        }
