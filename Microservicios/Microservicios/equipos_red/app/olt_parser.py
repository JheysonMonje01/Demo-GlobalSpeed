import re
from datetime import datetime

def parsear_salida_autofind(salida):
    """
    Parsea la salida del comando `display ont autofind all` y devuelve una lista de ONUs detectadas.
    
    Formato esperado por línea (ejemplo):
    F/S/P     SN            Control flag  Run state  Config state  Match state  Protect side  Match Distance
    0/0/1     HWTC12345678  active        online     unconfig      match        none          10m
    """
    onus = []
    lineas = salida.splitlines()

    for linea in lineas:
        if re.match(r"^\d+/\d+/\d+\s+\w{4}\w{8}", linea.strip()):
            partes = linea.split()

            try:
                fsp = partes[0]  # 0/0/1
                serial = partes[1]  # HWTC12345678
                ont_id = obtener_id_simulado(fsp)  # Simula un ID interno
                estado = partes[3]  # Ej: "online"
                
                onu = {
                    "f_s_p": fsp,
                    "ont_sn": serial,
                    "ont_id": ont_id,
                    "estado": estado,
                    "fecha_detectada": datetime.now().isoformat()
                }
                onus.append(onu)

            except Exception as e:
                print(f"[ERROR] Fallo al parsear línea: {linea} -> {e}")

    return onus
