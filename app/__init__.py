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

    # ✅ Habilitar CORS para todos los orígenes (⚠️ sólo en desarrollo o pruebas)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Registrar rutas
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
