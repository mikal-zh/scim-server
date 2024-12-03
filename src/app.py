from flask import Flask
from services.database import db
from services.auth import auth_router
import app_config
from flask_session import Session
from services.scim import scim_router
from services.menu import menu_router

def create_app():
    app = Flask(__name__)
    app.config.from_object(app_config)
    Session(app)
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:g@localhost:3306/scim"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

app = create_app()
app.register_blueprint(auth_router)
app.register_blueprint(scim_router)
app.register_blueprint(menu_router)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
