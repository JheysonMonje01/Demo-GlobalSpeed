# config.py

import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-por-defecto")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Ruta absoluta correcta dentro del contenedor Docker
    DIRECTORIO_COMPROBANTES = os.path.join(BASE_DIR, "archivos", "comprobantes")

   # URLs para otros servicios
    CONTRATO_SERVICE_URL = os.getenv("CONTRATO_SERVICE_URL")
    PLANES_SERVICE_URL = os.getenv("PLANES_SERVICE_URL")
    
