# app.py (archivo principal)
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

# Inicializar extensiones
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuración de la base de datos
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuración CORS - ESTO ES LO QUE TE FALTA
    CORS(app, 
         origins=[
             'https://crew-ai-app-w8ef.vercel.app',
             'http://localhost:3000',
             'http://localhost:5173'
         ],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=True)
    
    # Inicializar extensiones con la app
    db.init_app(app)
    
    # Registrar blueprints
    from app.routes import api_bp
    app.register_blueprint(api_bp)
    
    # Manejo de errores globales
    @app.errorhandler(500)
    def handle_500_error(e):
        return {'error': 'Internal Server Error', 'message': str(e)}, 500
    
    @app.errorhandler(404)
    def handle_404_error(e):
        return {'error': 'Not Found', 'message': str(e)}, 404
    
    return app

# Para Railway/producción
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
