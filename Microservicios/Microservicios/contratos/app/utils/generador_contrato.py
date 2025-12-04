import os
import uuid
import subprocess
from docxtpl import DocxTemplate
from datetime import datetime
import pytz  # ✅ Añadido para fecha local de Ecuador

import locale

from flask import current_app

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Ej: /app/utils
TEMPLATES_DIR = os.path.join(BASE_DIR, '..', 'templates')  # /app/templates
STATIC_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'static', 'contratos'))  # /app/static/contratos

def generar_contrato_pdf(cliente, empresa, plan, contrato, ruta_pdf_final, onu):

    # Diccionario manual de meses en español
    MESES_ES = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    try:
        plantilla_path = os.path.join(TEMPLATES_DIR, 'Plantilla_Contratos.docx')
        if not os.path.exists(plantilla_path):
            raise FileNotFoundError("No se encontró la plantilla 'Plantilla_Contratos.docx'")

        doc = DocxTemplate(plantilla_path)

        # ✅ Obtener fecha actual con hora local de Ecuador
        tz_ecuador = pytz.timezone("America/Guayaquil")
        fecha_actual = datetime.now(tz_ecuador)

        # Formatear manualmente
        dia = fecha_actual.day
        mes = MESES_ES[fecha_actual.month]
        anio = fecha_actual.year
        fecha_actual_ecuador = f"{dia} de {mes} de {anio}"

        # ✅ Obtener correos y teléfonos concatenados por coma
        correos = ', '.join(c["correo"] for c in empresa.get("correos", []))
        telefonos = ', '.join(t["telefono"] for t in empresa.get("telefonos", []))

        contexto = {
            "nombre_cliente": f"{cliente.get('apellido', '')} {cliente.get('nombre', '')}".upper(),
            "cedula_cliente": cliente.get("cedula_ruc") or cliente.get("identificacion", ""),
            "correo_cliente": cliente.get("correo", ""),
            "direccion_cliente": contrato.ubicacion,
            "telefono_cliente": cliente.get("telefono", ""),
            "provincia_cliente": cliente.get("provincia", ""),
            "canton_cliente": cliente.get("canton", ""),
            "parroquia_cliente": cliente.get("parroquia", ""),
            "nombre_empresa": empresa.get("nombre", ""),
            "direccion_empresa": empresa.get("direccion", ""),
            "telefono_empresa": telefonos,
            "ruc_empresa": empresa.get("ruc", ""),
            "correo_empresa": correos,
            "web_empresa": empresa.get("web", ""),
            "nombre_plan": plan.get("nombre_plan", plan.get("nombre", "")),
            "precio_plan": f"${float(plan.get('precio', 0)):.2f}",
            "vel_b": f"{int(plan.get('velocidad_bajada', 0))}",
            "vel_s": f"{int(plan.get('velocidad_subida', 0))}",
            "representante": empresa.get("representante_legal", empresa.get("representante", "")),
            "ciudad": "Riobamba",
            "fecha_actual": fecha_actual_ecuador,
            "modelo_ont": (onu.get("modelo_onu") or "").upper(),
            "serial_ont": (onu.get("serial") or "").upper(),
        }

        doc.render(contexto)

        nombre_base = f"contrato_{uuid.uuid4().hex}"
        docx_temp_path = os.path.join(STATIC_DIR, f"{nombre_base}.docx")
        doc.save(docx_temp_path)

        current_app.logger.info(f"Docx guardado correctamente en: {docx_temp_path}")

        subprocess.run([
            "libreoffice", "--headless", "--convert-to", "pdf", "--outdir", STATIC_DIR, docx_temp_path
        ], check=True)

        current_app.logger.info(f"PDF generado correctamente.")
        pdf_generado = os.path.join(STATIC_DIR, f"{nombre_base}.pdf")
        os.rename(pdf_generado, ruta_pdf_final)
        os.remove(docx_temp_path)

    except Exception as e:
        raise RuntimeError(f"Error al generar el contrato PDF: {str(e)}")
