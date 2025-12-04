import os
import uuid
import subprocess
from docxtpl import DocxTemplate
from datetime import datetime
import pytz  # ✅ Añadido para fecha local de Ecuador
import shutil

import locale

from flask import current_app

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Ej: /app/utils
TEMPLATES_DIR = os.path.join(BASE_DIR, '..', 'templates')  # /app/templates
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'archivos', 'ordenes'))  # /app/static/ordenes

def formatear_fecha(fecha):
    if isinstance(fecha, datetime):
        return fecha.strftime("%d/%m/%Y")
    try:
        return datetime.fromisoformat(str(fecha)).strftime("%d/%m/%Y")
    except Exception:
        return str(fecha)

def generar_ordenes_pdf(cliente, tecnico, plan, contrato, ruta_pdf_final, onu, orden, caja_nap):

    # Diccionario manual de meses en español
    MESES_ES = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    try:
        plantilla_path = os.path.join(TEMPLATES_DIR, 'plantilla_orden_instalacion.docx')
        if not os.path.exists(plantilla_path):
            raise FileNotFoundError("No se encontró la plantilla 'plantilla_orden_instalacion.docx'")

        doc = DocxTemplate(plantilla_path)

        # ✅ Obtener fecha actual con hora local de Ecuador
        tz_ecuador = pytz.timezone("America/Guayaquil")
        fecha_actual = datetime.now(tz_ecuador)

        # Formatear manualmente
        dia = fecha_actual.day
        mes = MESES_ES[fecha_actual.month]
        anio = fecha_actual.year
        fecha_actual_ecuador = f"{dia} de {mes} de {anio}"


        contexto = {
            "cliente_nombre": f"{cliente.get('nombre', '')}".upper(),
            "cliente_apellido": f"{cliente.get('apellido', '')}".upper(),
            "cliente_cedula": cliente.get("cedula_ruc") or cliente.get("identificacion", ""),
            "cliente_correo": cliente.get("correo", ""),
            "ubicacion_instalacion": contrato.get("ubicacion", ""),
            "cliente_telefono": cliente.get("telefono", ""),
            "tecnico_nombre": f"{tecnico.get('nombre', '')}".upper(),
            "tecnico_apellido": f"{tecnico.get('apellido', '')}".upper(),
            "tecnico_correo": tecnico.get("correo", ""),
            "tecnico_telefono": tecnico.get("telefono", ""),
            "fecha_asignacion": formatear_fecha(orden.fecha_asignacion),
            "nombre_plan": plan.get("nombre_plan", plan.get("nombre", "")),
            "precio": f"${float(plan.get('precio', 0)):.2f}",
            "velocidad": f"{int(plan.get('velocidad_bajada', 0))}",
            "fecha_actual": fecha_actual_ecuador,
            "modelo": (onu.get("modelo_onu") or "").upper(),
            "serial": (onu.get("serial") or "").upper(),
            "fecha_contrato": formatear_fecha(contrato.get("fecha_creacion")),
            "id_orden": orden.id_orden,
            "caja_nombre": (caja_nap.get("nombre_caja_nap") or ""),
            "caja_ubicacion": (caja_nap.get("ubicacion") or ""),
            "numero_puerto":(onu.get("numero_puerto_nap") or "")
        }

        doc.render(contexto)

        nombre_base = f"orden_instalacion_{uuid.uuid4().hex}"
        docx_temp_path = os.path.join(STATIC_DIR, f"{nombre_base}.docx")
        doc.save(docx_temp_path)

        current_app.logger.info(f"Docx guardado correctamente en: {docx_temp_path}")

        subprocess.run([
            "libreoffice", "--headless", "--convert-to", "pdf", "--outdir", STATIC_DIR, docx_temp_path
        ], check=True)

        pdf_generado = os.path.join(STATIC_DIR, f"{nombre_base}.pdf")

        current_app.logger.info(f"PDF generado correctamente.")
        shutil.copyfile(pdf_generado, ruta_pdf_final)
        os.remove(pdf_generado)
        os.remove(docx_temp_path)

    except Exception as e:
        raise RuntimeError(f"Error al generar la orden PDF: {str(e)}")
