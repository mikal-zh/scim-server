from flask import Blueprint

auth_router = Blueprint('auth', __name__, template_folder='templates')

# @auth_router.route()