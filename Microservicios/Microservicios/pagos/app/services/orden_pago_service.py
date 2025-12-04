from datetime import datetime
from decimal import Decimal
from calendar import monthrange
from app.models.orden_pago_model import OrdenPago
from app.extensions import db
from app.schemas.orden_pago_schema import OrdenPagoSchema
from app.utils.api_planes_utils import obtener_datos_plan
from sqlalchemy.exc import SQLAlchemyError
orden_pago_schema = OrdenPagoSchema(many=True)

def calcular_fecha_vencimiento(fecha_inicio):
    año = fecha_inicio.year
    mes = fecha_inicio.month + 1 if fecha_inicio.month < 12 else 1
    año += 1 if mes == 1 else 0

    dia = fecha_inicio.day
    ultimo_dia_mes_siguiente = monthrange(año, mes)[1]
    dia_vencimiento = dia if dia <= ultimo_dia_mes_siguiente else ultimo_dia_mes_siguiente

    return datetime(año, mes, dia_vencimiento)


def crear_orden_inicial(id_contrato, id_plan, fecha_inicio_str):
    try:
        fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d")

        # Obtener plan
        resultado = obtener_datos_plan(id_plan)
        if resultado["status"] != "success":
            return False, resultado.get("message", "Error al obtener el plan"), None

        plan = resultado["plan"]
        monto = Decimal(plan.get("precio"))
        if not monto:
            return False, "Precio del plan inválido o no definido", None

        vencimiento = calcular_fecha_vencimiento(fecha_inicio)

        orden = OrdenPago(
            id_contrato=id_contrato,
            mes_correspondiente=fecha_inicio.date().replace(day=1),
            monto=monto,
            estado="pendiente",
            fecha_vencimiento=vencimiento
        )

        db.session.add(orden)
        db.session.commit()

        return True, "Orden inicial creada correctamente", [orden.id_orden_pago]

    except Exception as e:
        db.session.rollback()
        return False, f"Error inesperado: {str(e)}", None


"""******************************************************************************************************"""

"""FUNCION PARA CREAR LA ORDEN DE PAGO DE FORMA MANUAL"""
from app.utils.contrato_utils import obtener_datos_contrato
from app.models.orden_pago_model import OrdenPago
from app.extensions import db
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError


def crear_orden_manual(data):
    try:
        id_contrato = data.get("id_contrato")
        fecha_str = data.get("mes_correspondiente")

        if not id_contrato or not fecha_str:
            return {"error": "Faltan campos obligatorios: id_contrato o mes_correspondiente."}, 400

        # Validar que el contrato exista
        resultado_contrato = obtener_datos_contrato(id_contrato)
        if not resultado_contrato or not resultado_contrato.get("id_contrato"):
            return {"error": "Contrato no encontrado o error al consultarlo."}, 404

        contrato = resultado_contrato
        id_plan = contrato.get("id_plan")
        if not id_plan:
            return {"error": "El contrato no contiene un plan asociado válido."}, 400

        # Validar que el plan exista
        resultado_plan = obtener_datos_plan(id_plan)
        if resultado_plan.get("status") != "success":
            return {"error": "Error al obtener datos del plan."}, 400

        precio = Decimal(resultado_plan["plan"].get("precio", 0))
        if precio <= 0:
            return {"error": "Precio inválido en el plan."}, 400

        # Parsear fecha y ajustar al día 1 del mes
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
            mes_correspondiente = fecha.date().replace(day=1)
        except ValueError:
            return {"error": "Formato de fecha inválido. Usa YYYY-MM-DD."}, 400

        # Validar que no exista una orden del mismo mes para ese contrato
        existe = OrdenPago.query.filter_by(
            id_contrato=id_contrato,
            mes_correspondiente=mes_correspondiente
        ).first()
        if existe:
            return {"error": "Ya existe una orden de pago para ese contrato y mes."}, 400

        # Fecha de vencimiento: mismo día del mes siguiente, o último día si no existe
        try:
            siguiente_mes = (fecha.replace(day=28) + timedelta(days=4)).replace(day=fecha.day)
        except ValueError:
            # Si no existe ese día, usar último día del mes siguiente
            siguiente_mes = (fecha.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        nueva_orden = OrdenPago(
            id_contrato=id_contrato,
            mes_correspondiente=mes_correspondiente,
            monto=precio,
            estado="pendiente",
            fecha_generacion=datetime.utcnow(),
            fecha_vencimiento=siguiente_mes
        )

        db.session.add(nueva_orden)
        db.session.commit()

        return {"message": "Orden de pago creada correctamente.", "id_orden_pago": nueva_orden.id_orden_pago}, 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": f"Error en la base de datos: {str(e)}"}, 500
    except Exception as e:
        db.session.rollback()
        return {"error": f"Error inesperado: {str(e)}"}, 500





"""******************************************************************************************************"""

"""Que revise las órdenes pendientes y actualice su estado a vencido si corresponde."""


from app.models.orden_pago_model import OrdenPago
from app.extensions import db
from datetime import datetime

def verificar_vencimientos_ordenes():
    try:
        hoy = datetime.now()

        ordenes_a_vencer = OrdenPago.query.filter(
            OrdenPago.estado == 'pendiente',
            OrdenPago.fecha_vencimiento < hoy
        ).all()

        total_actualizadas = 0

        for orden in ordenes_a_vencer:
            orden.estado = 'vencido'
            total_actualizadas += 1

        db.session.commit()

        return {
            "status": "success",
            "message": f"✅ {total_actualizadas} órdenes marcadas como vencidas",
            "total_vencidas": total_actualizadas
        }

    except Exception as e:
        db.session.rollback()
        return {
            "status": "error",
            "message": f"❌ Error al verificar vencimientos: {str(e)}"
        }


"""**************************************************************************************************************"""


def actualizar_orden_pago(id_orden_pago, data):
    try:
        orden = OrdenPago.query.get(id_orden_pago)
        if not orden:
            return {"error": "La orden de pago no existe."}, 404

        if orden.estado not in ["pendiente", "vencido"]:
            return {"error": "Solo se pueden modificar órdenes en estado pendiente o vencido."}, 400

        if orden.id_pago is not None:
            return {"error": "La orden ya tiene un pago registrado y no puede modificarse."}, 400

        # Validar y actualizar monto
        if "monto" in data:
            try:
                monto = float(data["monto"])
                if monto <= 0:
                    return {"error": "El monto debe ser un valor positivo."}, 400
                orden.monto = monto
            except ValueError:
                return {"error": "El monto debe ser un número válido."}, 400

        # Validar y actualizar fecha de vencimiento
        if "fecha_vencimiento" in data:
            try:
                nueva_fecha = datetime.strptime(data["fecha_vencimiento"], "%Y-%m-%d")
                orden.fecha_vencimiento = nueva_fecha
            except ValueError:
                return {"error": "Fecha de vencimiento inválida. Formato esperado: YYYY-MM-DD."}, 400

        # Actualizar observación si viene
        if "observacion" in data:
            orden.observacion = data["observacion"].strip()

        db.session.commit()
        return {"message": "Orden de pago actualizada correctamente."}, 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return {"error": f"Error al actualizar orden: {str(e)}"}, 500
    except Exception as e:
        db.session.rollback()
        return {"error": f"Error inesperado: {str(e)}"}, 500


"""***************************************************************************************************************"""


def obtener_ordenes_por_contrato(id_contrato, estado=None):
    try:
        query = OrdenPago.query.filter_by(id_contrato=id_contrato)

        if estado:
            query = query.filter_by(estado=estado)

        ordenes = query.order_by(OrdenPago.mes_correspondiente.desc()).all()

        resultados = []
        for orden in ordenes:
            resultados.append({
                "id_orden_pago": orden.id_orden_pago,
                "mes_correspondiente": orden.mes_correspondiente.strftime("%Y-%m-%d"),
                "fecha_generacion": orden.fecha_generacion.strftime("%Y-%m-%d"),
                "fecha_vencimiento": orden.fecha_vencimiento.strftime("%Y-%m-%d"),
                "estado": orden.estado,
                "monto": float(orden.monto),
                "fecha_pago": orden.fecha_pago.strftime("%Y-%m-%d") if orden.fecha_pago else None,
                "id_pago": orden.id_pago
            })

        return resultados, 200

    except Exception as e:
        return {"error": f"Error al obtener órdenes: {str(e)}"}, 500


"""***************************************************************************************************************"""


def obtener_ordenes_por_estado(estado):
    try:
        estados_validos = ["pendiente", "vencido", "cancelado"]
        if estado not in estados_validos:
            return {"error": f"Estado inválido. Debe ser uno de: {', '.join(estados_validos)}"}, 400

        from app.models.orden_pago_model import OrdenPago

        ordenes = OrdenPago.query.filter_by(estado=estado).order_by(OrdenPago.mes_correspondiente.desc()).all()

        resultados = []
        for orden in ordenes:
            resultados.append({
                "id_orden_pago": orden.id_orden_pago,
                "id_contrato": orden.id_contrato,
                "mes_correspondiente": orden.mes_correspondiente.strftime("%Y-%m-%d"),
                "fecha_generacion": orden.fecha_generacion.strftime("%Y-%m-%d"),
                "fecha_vencimiento": orden.fecha_vencimiento.strftime("%Y-%m-%d"),
                "estado": orden.estado,
                "monto": float(orden.monto),
                "fecha_pago": orden.fecha_pago.strftime("%Y-%m-%d") if orden.fecha_pago else None,
                "id_pago": orden.id_pago
            })

        return resultados, 200

    except Exception as e:
        return {"error": f"Error al obtener órdenes por estado: {str(e)}"}, 500


def obtener_todas_las_ordenes():
    try:
        ordenes = OrdenPago.query.order_by(OrdenPago.fecha_generacion.desc()).all()
        data = orden_pago_schema.dump(ordenes)
        return {"status": "success", "ordenes": data}, 200
    except Exception as e:
        return {"status": "error", "message": f"Error al obtener órdenes de pago: {str(e)}"}, 500

from app.models.orden_pago_model import OrdenPago
from app.schemas.orden_pago_schema import OrdenPagoSchema
from app.utils.api_clientes import get_cliente_por_id
from app.utils.api_contratos import get_contrato_por_id
from app.utils.api_planes_utils import obtener_datos_plan

def obtener_ordenes_con_detalle():
    try:
        ordenes = OrdenPago.query.all()
        resultado = []

        for orden in ordenes:
            contrato_res = get_contrato_por_id(orden.id_contrato)
            if contrato_res.get("status") != "success":
                continue

            contrato = contrato_res["contrato"]
            id_cliente = contrato["id_cliente"]
            id_plan = contrato["id_plan"]

            cliente_res = get_cliente_por_id(id_cliente)
            nombre_cliente = ""
            if cliente_res.get("status") == "success":
                persona = cliente_res["cliente"].get("persona", {})
                nombre_cliente = f"{persona.get('nombre', '').split()[0]} {persona.get('apellido', '').split()[0]}"

            plan_res = obtener_datos_plan(id_plan)
            nombre_plan = ""
            if plan_res.get("status") == "success":
                nombre_plan = plan_res["plan"].get("nombre_plan", "")

            resultado.append({
                "id_orden_pago": orden.id_orden_pago,
                "estado": orden.estado,
                "fecha_generacion": orden.fecha_generacion,
                "fecha_vencimiento": orden.fecha_vencimiento,
                "fecha_pago": orden.fecha_pago,
                "mes_correspondiente": orden.mes_correspondiente,
                "monto": orden.monto,
                "nombre_cliente": nombre_cliente,
                "nombre_plan": nombre_plan,
            })

        return resultado, 200

    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

from flask import  jsonify, request


#por contrato 
def obtener_ordenes_por_contrato_estados_con_detalle(id_contrato):
    try:
        # Obtener estados como lista desde query param
        estados_param = request.args.get("estado", "")
        estados_filtrar = [estado.strip().lower() for estado in estados_param.split(",") if estado.strip()]

        ordenes = OrdenPago.query.filter_by(id_contrato=id_contrato).all()
        resultado = []

        for orden in ordenes:
            if estados_filtrar and orden.estado.lower() not in estados_filtrar:
                continue

            contrato_res = get_contrato_por_id(orden.id_contrato)
            if contrato_res.get("status") != "success":
                continue

            contrato = contrato_res["contrato"]
            id_cliente = contrato["id_cliente"]
            id_plan = contrato["id_plan"]

            # Obtener nombre cliente
            cliente_res = get_cliente_por_id(id_cliente)
            nombre_cliente = ""
            if cliente_res.get("status") == "success":
                persona = cliente_res["cliente"].get("persona", {})
                nombre_cliente = f"{persona.get('nombre', '').split()[0]} {persona.get('apellido', '').split()[0]}"

            # Obtener nombre plan
            plan_res = obtener_datos_plan(id_plan)
            nombre_plan = ""
            if plan_res.get("status") == "success":
                nombre_plan = plan_res["plan"].get("nombre_plan", "")

            resultado.append({
                "id_orden_pago": orden.id_orden_pago,
                "estado": orden.estado,
                "monto": orden.monto,
                "nombre_cliente": nombre_cliente,
                "nombre_plan": nombre_plan
            })

        return jsonify(resultado), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
