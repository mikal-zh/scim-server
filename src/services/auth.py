from flask import Blueprint
from flask import Flask, jsonify, make_response, request, redirect, render_template, session, url_for
from functools import wraps
from services.database import db
from sqlalchemy import func
import app_config
import identity.web
import requests
from app_config import AUTHORITY, CLIENT_ID, CLIENT_SECRET

auth_router = Blueprint('auth', __name__, template_folder="../template/")

print("env var", AUTHORITY, CLIENT_ID)

auth = identity.web.Auth(
    session=session,
    authority= AUTHORITY,
    client_id=  CLIENT_ID,
    client_credential=  CLIENT_SECRET,
)

@auth_router.route("/login")
def login():
    return render_template("login.html", **auth.log_in(
        scopes=app_config.SCOPE, # Have user consent to scopes during log-in
        redirect_uri= "https://securesnack.ariovis.fr/auth/redirect", #url_for(".auth_response", _external=True)
    ))

@auth_router.route(app_config.REDIRECT_PATH)
def auth_response():
    result = auth.complete_log_in(request.args)
    if "error" in result:
        return render_template("auth_error.html", result=result)
    return redirect(url_for(".index"))

@auth_router.route("/logout")
def logout():
    return redirect(auth.log_out(url_for(".index", _external=True)))

@auth_router.route("/index.html")
def index():
    user = auth.get_user()
    if not user:
        return redirect(url_for("auth.login"))
    print(user)
    return render_template("index.html", user=user)

@auth_router.route("/call_downstream_api")
def call_downstream_api():
    token = auth.get_token_for_user(app_config.SCOPE)
    if "error" in token:
        return redirect(url_for(".login"))
    # Use access token to call downstream api
    api_result = requests.get(
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        timeout=30,
    ).json()
    return render_template('display.html', result=api_result)