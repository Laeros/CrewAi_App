from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os

load_dotenv()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate = Migrate(app, db)

    # ✅ Habilitar CORS tanto para desarrollo local como para Vercel
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:5173",  # Para desarrollo local
                "https://crew-ai-app-w8ef.vercel.app"  # Tu frontend en Vercel
            ]
        }
    })

    # Registrar rutas
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
