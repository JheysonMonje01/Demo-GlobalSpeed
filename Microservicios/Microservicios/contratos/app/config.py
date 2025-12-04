import os
from dotenv import load_dotenv

# Cargar variables de entorno del archivo .env
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CONFIGURACION_SERVICE_URL = os.getenv("CONFIGURACION_SERVICE_URL")
