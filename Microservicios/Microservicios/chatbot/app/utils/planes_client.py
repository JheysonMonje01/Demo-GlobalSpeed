import os
import requests

PLANES_SERVICE_URL = os.getenv("PLANES_SERVICE_URL", "http://planes_internet:5005")

def obtener_planes_disponibles():
    try:
        res = requests.get(f"{PLANES_SERVICE_URL}/planes/")
        if res.status_code == 200:
            response_json = res.json()
            return response_json.get("data", [])  # 👈 importante
        return []
    except Exception as e:
        print(f"❌ Error al obtener planes: {e}")
        return []

def generar_contexto_planes():
    planes = obtener_planes_disponibles()
    if not planes:
        return "Actualmente no hay planes registrados."

    contexto = "Estos son los planes de internet disponibles:\n"
    for plan in planes:
        nombre = plan.get("nombre_plan", "Plan sin nombre")
        precio = plan.get("precio", "No disponible")
        velocidad = plan.get("velocidad_subida", "Velocidad no definida")
        contexto += f"- {nombre}: {velocidad}, precio ${precio} al mes.\n"
    return contexto