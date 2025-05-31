from app import create_app, db
from flask.cli import FlaskGroup

app = create_app()
cli = FlaskGroup(app)

@cli.command("create_db")
def create_db():
    db.create_all()
    print("Base de datos creada.")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
