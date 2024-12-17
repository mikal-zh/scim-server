from flask import Blueprint
from flask import request, redirect, render_template, session, url_for
import app_config
import identity.web
from app_config import AUTHORITY, CLIENT_ID, CLIENT_SECRET

auth_router = Blueprint('auth', __name__, template_folder="../template/")

auth = identity.web.Auth(
    session=session,
    authority= AUTHORITY,
    client_id=  CLIENT_ID,
    client_credential=  CLIENT_SECRET,
)

@auth_router.route("/")
@auth_router.route("/login")
def login():
    return render_template("login.html", **auth.log_in(
        redirect_uri= url_for(".auth_response", _external=True)
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

@auth_router.route("/index")
def index():
    user = auth.get_user()
    if not user:
        return redirect(url_for("auth.login"))
    return render_template("index.html", user=user)
