import traceback
from decimal import Decimal
from datetime import datetime
from app.models.pago_model import Pago
from app.models.metodo_pago_model import MetodoPago
from app.extensions import db
from sqlalchemy.exc import SQLAlchemyError
from app.utils.contrato_utils import obtener_datos_contrato  # ✅ Importación correcta



def crear_pago(data):
    try:
        print("📥 Datos recibidos para crear pago:", data)

        id_contrato = data.get("id_contrato")
        id_orden_pago = data.get("id_orden_pago")
        id_metodo_pago = data.get("id_metodo_pago")
        monto = data.get("monto")
        observacion = data.get("observacion", "").strip()

        errores = {}

        # Validar campos obligatorios
        if not id_contrato:
            errores["id_contrato"] = "El contrato es obligatorio."
        if not id_metodo_pago:
            errores["id_metodo_pago"] = "El método de pago es obligatorio."
        if not id_orden_pago:
            errores["id_orden_pago"] = "La orden de pago es obligatoria."

        # Validar existencia del contrato (microservicio)
        if id_contrato:
            contrato_info = obtener_datos_contrato(id_contrato)
            if contrato_info.get("status") == "error":
                errores["id_contrato"] = f"No se encontró un contrato con ID {id_contrato}."

        # Validar método de pago
        if id_metodo_pago:
            metodo = MetodoPago.query.get(id_metodo_pago)
            if not metodo:
                errores["id_metodo_pago"] = "Método de pago no válido."

        # Validar monto
        try:
            monto_decimal = Decimal(monto)
            if monto_decimal <= 0:
                errores["monto"] = "El monto debe ser un valor positivo."
        except:
            errores["monto"] = "Monto inválido. Debe ser numérico."

        # Validar orden de pago
        from app.models.orden_pago_model import OrdenPago
        orden = OrdenPago.query.get(id_orden_pago)

        if not orden:
            errores["id_orden_pago"] = "La orden de pago no existe."
        else:
            if orden.estado == "cancelado":
                errores["id_orden_pago"] = "La orden ha sido cancelada. No puede ser pagada."
            elif orden.id_contrato != id_contrato:
                errores["id_orden_pago"] = "La orden no pertenece al contrato especificado."
            elif orden.id_pago is not None:
                errores["id_orden_pago"] = "La orden ya tiene un pago asignado."

        # Si hay errores, retornarlos
        if errores:
            return {"errores": errores, "mensaje": "❌ Error de validación."}, 400

        # Crear pago
        nuevo_pago = Pago(
            id_contrato=id_contrato,
            id_metodo_pago=id_metodo_pago,
            monto=monto_decimal,
            mes_correspondiente=orden.mes_correspondiente,
            observacion=observacion,
            estado=False,
            fecha_creacion=datetime.utcnow()
        )

        db.session.add(nuevo_pago)
        db.session.flush()  # obtener id_pago para actualizar orden

        orden.id_pago = nuevo_pago.id_pago
        orden.estado = "cancelado"
        orden.fecha_pago = datetime.utcnow()

        db.session.commit()
        print("✅ Pago creado correctamente con ID:", nuevo_pago.id_pago)
        return nuevo_pago, 201

    except SQLAlchemyError as e:
        db.session.rollback()
        print("❌ Error SQLAlchemy:", str(e))
        return {"error": "Error al registrar el pago en base de datos."}, 500
    except Exception as e:
        db.session.rollback()
        print("❌ Error inesperado:", str(e))
        return {"error": f"Error inesperado: {str(e)}"}, 500




def actualizar_pago(id_pago, data):
    try:
        print(f"🔄 Actualizando pago con ID: {id_pago} con data: {data}")
        pago = Pago.query.get(id_pago)
        if not pago:
            print("❌ Pago no encontrado")
            return {"error": "Pago no encontrado."}, 404

        errores = {}
        cambios = False

        # Validar y actualizar monto
        if "monto" in data:
            try:
                monto_decimal = Decimal(data["monto"])
                if monto_decimal <= 0:
                    errores["monto"] = "El monto debe ser positivo."
                else:
                    if monto_decimal != pago.monto:
                        pago.monto = monto_decimal
                        cambios = True
            except Exception as e:
                print("⚠️ Error en monto:", e)
                errores["monto"] = "Monto inválido. Debe ser numérico."

        # No se permite modificar mes_correspondiente directamente
        if "mes_correspondiente" in data:
            errores["mes_correspondiente"] = (
                "No se puede modificar el mes de pago directamente. Este valor depende de la orden de pago asociada."
            )

        # Actualizar observación
        if "observacion" in data:
            nueva_observacion = data["observacion"].strip()
            if nueva_observacion != pago.observacion:
                pago.observacion = nueva_observacion
                cambios = True

        # Validación final
        if errores:
            print("❌ Errores de validación:", errores)
            return {"errores": errores, "mensaje": "Error de validación."}, 400

        if not cambios:
            return {"mensaje": "No se realizaron cambios."}, 400

        pago.fecha_modificacion = datetime.utcnow()
        db.session.commit()
        print("✅ Pago actualizado correctamente.")
        return pago, 200

    except SQLAlchemyError as e:
        db.session.rollback()
        print("❌ SQLAlchemy Error al actualizar el pago:", str(e))
        traceback.print_exc()
        return {"error": "Error al actualizar el pago."}, 500

    except Exception as e:
        db.session.rollback()
        print("❌ Error inesperado al actualizar el pago:", str(e))
        traceback.print_exc()
        return {"error": f"Error inesperado: {str(e)}"}, 500




"""****************************************************************"""

from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

# GET por ID
def obtener_pago_por_id(id_pago):
    try:
        pago = Pago.query.get(id_pago)
        if not pago:
            return {"error": "Pago no encontrado."}, 404
        return pago, 200
    except Exception as e:
        return {"error": f"Error al obtener el pago: {str(e)}"}, 500

# DELETE
def eliminar_pago(id_pago):
    try:
        pago = Pago.query.get(id_pago)
        if not pago:
            return {"error": "Pago no encontrado."}, 404

        db.session.delete(pago)
        db.session.commit()
        return {"mensaje": "Pago eliminado correctamente."}, 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": "Error de base de datos al eliminar el pago."}, 500
    except Exception as e:
        db.session.rollback()
        return {"error": f"Error inesperado: {str(e)}"}, 500

# GET con filtros validados
def listar_pagos_con_filtros(params):
    filtros_validos = {"id_contrato", "id_metodo_pago", "estado", "desde", "hasta", "mes"}
    filtros_invalidos = [k for k in params if k not in filtros_validos]

    if filtros_invalidos:
        return {"error": f"Filtros no permitidos: {', '.join(filtros_invalidos)}"}, 400

    query = Pago.query

    if "id_contrato" in params:
        query = query.filter(Pago.id_contrato == params["id_contrato"])

    if "id_metodo_pago" in params:
        query = query.filter(Pago.id_metodo_pago == params["id_metodo_pago"])

    if "estado" in params:
        estado = params["estado"].lower()
        if estado not in ["true", "false"]:
            return {"error": "El campo 'estado' debe ser 'true' o 'false'."}, 400
        query = query.filter(Pago.estado == (estado == "true"))

    if "desde" in params:
        try:
            fecha = datetime.strptime(params["desde"], "%Y-%m-%d")
            query = query.filter(Pago.fecha_creacion >= fecha)
        except:
            return {"error": "El campo 'desde' debe tener formato YYYY-MM-DD."}, 400

    if "hasta" in params:
        try:
            fecha = datetime.strptime(params["hasta"], "%Y-%m-%d")
            query = query.filter(Pago.fecha_creacion <= fecha)
        except:
            return {"error": "El campo 'hasta' debe tener formato YYYY-MM-DD."}, 400

    if "mes" in params:
        try:
            mes = datetime.strptime(params["mes"], "%Y-%m")
            query = query.filter(
                Pago.mes_correspondiente.year == mes.year,
                Pago.mes_correspondiente.month == mes.month
            )
        except:
            return {"error": "El campo 'mes' debe tener formato YYYY-MM."}, 400

    try:
        pagos = query.order_by(Pago.fecha_creacion.desc()).all()
        return pagos, 200
    except Exception as e:
        return {"error": f"Error al obtener los pagos: {str(e)}"}, 500


from app.models.pago_model import Pago
from app.models.metodo_pago_model import MetodoPago
from app.extensions import db
from app.utils.api_clientes import get_cliente_por_id
from app.utils.api_contratos import get_contrato_por_id
from app.utils.api_planes_utils import obtener_datos_plan


def obtener_pagos_por_contrato(id_contrato):
    contrato = get_contrato_por_id(id_contrato)
    if not contrato:
        raise Exception("Contrato no encontrado")

    id_cliente = contrato.get("id_cliente")
    id_plan = contrato.get("id_plan")

    cliente = get_cliente_por_id(id_cliente)
    plan = obtener_datos_plan(id_plan)

    pagos = Pago.query.filter_by(id_contrato=id_contrato).order_by(Pago.fecha_creacion.desc()).all()

    resultado = []
    for pago in pagos:
        metodo = MetodoPago.query.get(pago.id_metodo_pago)

        resultado.append({
            "id_pago": pago.id_pago,
            "cliente": f"{cliente.get('nombre', '').split()[0]} {cliente.get('apellido', '').split()[0]}",
            "plan": plan.get("nombre_plan", "Desconocido"),
            "monto": float(pago.monto),
            "observacion": pago.observacion or "",
            "fecha_pago": pago.fecha_creacion.strftime("%Y-%m-%d"),
            "metodo_pago": metodo.nombre if metodo else "Desconocido",
        })

    return resultado


def obtener_pagos_con_detalle():
    try:
        pagos = Pago.query.all()
        resultado = []

        for pago in pagos:
            contrato_res = get_contrato_por_id(pago.id_contrato)
            if contrato_res.get("status") != "success":
                continue

            contrato = contrato_res["contrato"]
            id_cliente = contrato["id_cliente"]
            id_plan = contrato["id_plan"]

            # Cliente
            cliente_res = get_cliente_por_id(id_cliente)
            nombre_cliente = ""
            if cliente_res.get("status") == "success":
                persona = cliente_res["cliente"].get("persona", {})
                nombre_cliente = f"{persona.get('nombre', '').split()[0]} {persona.get('apellido', '').split()[0]}"

            # Plan
            plan_res = obtener_datos_plan(id_plan)
            nombre_plan = ""
            if plan_res.get("status") == "success":
                nombre_plan = plan_res["plan"].get("nombre_plan", "")

            # Método de pago
            metodo = MetodoPago.query.get(pago.id_metodo_pago)
            nombre_metodo = metodo.nombre if metodo else "Desconocido"

            resultado.append({
                "id_pago": pago.id_pago,
                "cliente": nombre_cliente,
                "plan": nombre_plan,
                "monto": float(pago.monto),
                "observacion": pago.observacion or "",
                "fecha_pago": pago.fecha_creacion.strftime("%Y-%m-%d"),
                "metodo_pago": nombre_metodo,
                
            })

        return resultado

    except Exception as e:
        raise Exception(f"Error al obtener pagos con detalle: {str(e)}")