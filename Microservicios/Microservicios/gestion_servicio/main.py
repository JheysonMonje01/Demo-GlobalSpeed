from app import create_app  # pero asegurándote que app es un módulo (tiene __init__.py)
from app.config import Config
from app.extensions import db

app = create_app()

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5007, debug=True)


