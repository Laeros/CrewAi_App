from app import create_app, db
from flask.cli import FlaskGroup

app = create_app()
cli = FlaskGroup(create_app=create_app)

# Comando personalizado para crear la base de datos
@cli.command("create_db")
def create_db():
    with app.app_context():
        db.create_all()
        print("✅ Base de datos creada correctamente.")

# Ejecutar CLI si se llama directamente el script
if __name__ == '__main__':
    cli()
