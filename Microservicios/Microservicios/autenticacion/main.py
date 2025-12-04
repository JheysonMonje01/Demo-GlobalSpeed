from app import create_app
from dotenv import load_dotenv
import os

# Detectar entorno: default 'development'
env = os.getenv('FLASK_ENV', 'development')

# Cargar el .env correcto según entorno
if env == 'production':
    load_dotenv('.env.production')
else:
    load_dotenv('.env')

app = create_app()

if __name__ == "__main__":
    # En producción, debug=False
    debug_mode = env != 'production'
    app.run(host="0.0.0.0", port=5000, debug=debug_mode)
