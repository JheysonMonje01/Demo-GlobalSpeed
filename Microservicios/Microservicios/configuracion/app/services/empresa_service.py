from app.models.empresa_model import Empresa, EmpresaTelefono, EmpresaCorreo
from app.extensions import db
from sqlalchemy.exc import IntegrityError

"""FUNCION PARA CREAR UNA NUEVA EMPRESA"""
def crear_empresa(form, files):
    try:
        nombre = form.get('nombre')
        representante = form.get('representante')
        ruc = form.get('ruc')
        direccion = form.get('direccion')
        logo_file = files.get('logo')

        logo_bytes = logo_file.read() if logo_file else None

        from app.models.empresa_model import Empresa, EmpresaTelefono, EmpresaCorreo
        import json

        telefonos = json.loads(form.get('telefonos', '[]'))
        correos = json.loads(form.get('correos', '[]'))

        empresa = Empresa(
            nombre=nombre,
            representante=representante,
            ruc=ruc,
            direccion=direccion,
            logo=logo_bytes
        )

        for tel in telefonos:
            empresa.telefonos.append(EmpresaTelefono(**tel))

        for corr in correos:
            empresa.correos.append(EmpresaCorreo(**corr))

        # Validar duplicado RUC
        if Empresa.query.filter_by(ruc=ruc).first():
            raise ValueError("Ya existe una empresa registrada con ese RUC.")

        db.session.add(empresa)
        db.session.commit()

        return {
            "status": "success",
            "message": "Empresa creada correctamente.",
            "data": empresa
        }

    except ValueError as ve:
        return {
            "status": "error",
            "message": str(ve)
        }

    except IntegrityError:
        db.session.rollback()
        return {
            "status": "error",
            "message": "Violación de integridad: campos únicos o inválidos."
        }

    except Exception as e:
        db.session.rollback()
        return {
            "status": "error",
            "message": f"Error interno al crear empresa: {str(e)}"
        }


"""FUNCION PARA AGREGAR UN TELÉFONO"""
def agregar_telefono(id_empresa, data):
    empresa = Empresa.query.get(id_empresa)
    if not empresa:
        return {"status": "error", "message": "Empresa no encontrada."}

    nuevo_tel = EmpresaTelefono(
        telefono=data['telefono'],
        tipo=data.get('tipo'),
        empresa=empresa
    )
    db.session.add(nuevo_tel)
    db.session.commit()

    return {"status": "success", "message": "Teléfono añadido.", "data": nuevo_tel}


"""FUNCION PARA AGREGAR UN CORREO"""
def agregar_correo(id_empresa, data):
    empresa = Empresa.query.get(id_empresa)
    if not empresa:
        return {"status": "error", "message": "Empresa no encontrada."}

    nuevo_cor = EmpresaCorreo(
        correo=data['correo'],
        tipo=data.get('tipo'),
        empresa=empresa
    )
    db.session.add(nuevo_cor)
    db.session.commit()

    return {"status": "success", "message": "Correo añadido.", "data": nuevo_cor}





"""****************************************************************************"""

"""FUNCIONES PARA ACTUALIZAR LA INFORMACIÓN DE UNA EMPRESA"""

def actualizar_empresa(id_empresa, form, files):
    try:
        empresa = Empresa.query.get(id_empresa)
        if not empresa:
            return {
                "status": "error",
                "message": f"No se encontró ninguna empresa con ID {id_empresa}."
            }

        # Verificación de RUC duplicado
        ruc_nuevo = form.get("ruc")
        if ruc_nuevo and Empresa.query.filter(Empresa.ruc == ruc_nuevo, Empresa.id_empresa != id_empresa).first():
            return {
                "status": "error",
                "message": "Ya existe otra empresa registrada con ese RUC."
            }

        empresa.nombre = form.get("nombre", empresa.nombre)
        empresa.representante = form.get("representante", empresa.representante)
        empresa.ruc = ruc_nuevo or empresa.ruc
        empresa.direccion = form.get("direccion", empresa.direccion)

        # 🔥 ESTA ES LA CLAVE:
        # ✅ Convertir base64 a binario para guardar en BYTEA
        logo_file = files.get('logo')
        if logo_file:
            empresa.logo = logo_file.read()

        db.session.commit()

        return {
            "status": "success",
            "message": "Empresa actualizada correctamente.",
            "data": empresa
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
            "message": f"Error interno al actualizar empresa: {str(e)}"
        }



"""FUNCION PARA ACTUALIZAR UNA EMPRESA CON JSON"""
def actualizar_empresa_json(id_empresa, data):
    try:
        empresa = Empresa.query.get(id_empresa)
        if not empresa:
            return {
                "status": "error",
                "message": f"No se encontró ninguna empresa con ID {id_empresa}."
            }

        ruc_nuevo = data.get("ruc")
        if ruc_nuevo and Empresa.query.filter(Empresa.ruc == ruc_nuevo, Empresa.id_empresa != id_empresa).first():
            return {
                "status": "error",
                "message": "Ya existe otra empresa registrada con ese RUC."
            }

        empresa.nombre = data.get("nombre", empresa.nombre)
        empresa.representante = data.get("representante", empresa.representante)
        empresa.ruc = ruc_nuevo or empresa.ruc
        empresa.direccion = data.get("direccion", empresa.direccion)

        # ✅ Actualizar teléfonos si se envían
        if "telefonos" in data:
            empresa.telefonos.clear()
            for tel in data["telefonos"]:
                empresa.telefonos.append(EmpresaTelefono(**tel))

        # ✅ Actualizar correos si se envían
        if "correos" in data:
            empresa.correos.clear()
            for corr in data["correos"]:
                empresa.correos.append(EmpresaCorreo(**corr))

        db.session.commit()

        return {
            "status": "success",
            "message": "Empresa actualizada correctamente.",
            "data": empresa
        }

    except Exception as e:
        db.session.rollback()
        return {
            "status": "error",
            "message": f"Error interno al actualizar empresa: {str(e)}"
        }














        
"""****************************************************************************"""

"""FUNCIONES PARA BUSCAR LOS DATOS DE UNA EMPRESA"""

from app.models.empresa_model import Empresa, EmpresaCorreo
from flask import abort



def obtener_empresas_filtradas(filtros):
    try:
        query = Empresa.query

        filtros_permitidos = {'id_empresa', 'ruc', 'nombre', 'representante', 'correo', 'direccion'}
        filtros_recibidos = set(filtros.keys())

        filtros_invalidos = filtros_recibidos - filtros_permitidos
        if filtros_invalidos:
            raise ValueError(f"Los siguientes filtros no son válidos: {', '.join(filtros_invalidos)}")

        if id_empresa := filtros.get('id_empresa'):
            if not id_empresa.isdigit():
                raise ValueError("El filtro 'id_empresa' debe ser un número entero.")
            query = query.filter(Empresa.id_empresa == int(id_empresa))

        if ruc := filtros.get('ruc'):
            query = query.filter(Empresa.ruc.ilike(f"%{ruc}%"))

        if nombre := filtros.get('nombre'):
            query = query.filter(Empresa.nombre.ilike(f"%{nombre}%"))

        if representante := filtros.get('representante'):
            query = query.filter(Empresa.representante.ilike(f"%{representante}%"))

        if correo := filtros.get('correo'):
            query = query.filter(Empresa.correo.ilike(f"%{correo}%"))

        if direccion := filtros.get('direccion'):
            query = query.filter(Empresa.direccion.ilike(f"%{direccion}%"))

        return query.all()

    except ValueError as ve:
        abort(400, description=str(ve))

    except Exception as e:
        abort(500, description="Error inesperado al obtener empresas. Contacte con el administrador.")


"""****************************************************************************"""
