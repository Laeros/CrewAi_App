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

    # ✅ Leer orígenes permitidos desde la variable de entorno
    cors_origins = os.getenv("CORS_ALLOWED_ORIGINS", "*")
    CORS(app, resources={r"/api/*": {"origins": cors_origins.split(",")}})

    # Registrar rutas
    from .routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    return app
