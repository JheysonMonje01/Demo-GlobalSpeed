from flask import Flask
from app.config import Config
from flask_cors import CORS
from app.routes.chatbot_routes import chatbot_bp
from app.routes.dialogflow_bridge import dialogflow_bridge_bp



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    app.register_blueprint(chatbot_bp)
    app.register_blueprint(dialogflow_bridge_bp)

    return app
