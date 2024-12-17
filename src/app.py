from flask import Flask
from services.database import db
from services.authentification import auth_router
from flask_session import Session
from services.scim import scim_router
from services.menu import menu_router
from app_config import PORT
import app_config

def create_app():
    app = Flask(__name__)
    app.config.from_object(app_config)
    Session(app)
    db.init_app(app)
    return app

app = create_app()
app.register_blueprint(auth_router)
app.register_blueprint(scim_router)
app.register_blueprint(menu_router)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=PORT)
