from flask import Flask, jsonify, make_response, request, redirect, render_template, session, url_for
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from database import db
from models import User, Group
import re
from sqlalchemy import func
from auth import auth_router
import app_config
import identity.web
import requests
from flask_session import Session
from scim import scim_router

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

auth = identity.web.Auth(
    session=session,
    authority=app.config["AUTHORITY"],
    client_id=app.config["CLIENT_ID"],
    client_credential=app.config["CLIENT_SECRET"],
)

@app.route("/login")
def login():
    return render_template("template/login.html", **auth.log_in(
        scopes=app_config.SCOPE, # Have user consent to scopes during log-in
        redirect_uri=url_for("auth_response", _external=True)
    ))

@app.route(app_config.REDIRECT_PATH)
def auth_response():
    result = auth.complete_log_in(request.args)
    if "error" in result:
        return render_template("template/auth_error.html", result=result)
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    return redirect(auth.log_out(url_for("index", _external=True)))
@app.route("/")
def index():
    user = auth.get_user()
    if not user:
        return redirect(url_for("login"))
    return render_template("template/index.html", user=user)

@app.route("/call_downstream_api")
def call_downstream_api():
    token = auth.get_token_for_user(app_config.SCOPE)
    if "error" in token:
        return redirect(url_for("login"))
    # Use access token to call downstream api
    api_result = requests.get(
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        timeout=30,
    ).json()
    return render_template('template/display.html', result=api_result)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")