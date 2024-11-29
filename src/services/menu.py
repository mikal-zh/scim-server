from flask import Blueprint
from flask import Flask, jsonify, make_response, request, session
from functools import wraps
from services.database import db
from models.models import User, Group, Menu
import re
from sqlalchemy import func
# from services.auth import auth_router

menu_router = Blueprint('menu', __name__,)

@menu_router.route('/hello')
def hello():
    return 'Hello World!'

@menu_router.route("/menu", methods=["POST"])
def create_menu():
    username = "user"
    nb_entree = request.json.get("nb_entree")
    nb_plat = request.json.get("nb_plat")
    nb_dessert = request.json.get("nb_dessert")

    try:
        menu = Menu(
            nb_entree = nb_entree,
            nb_plat = nb_plat,
            nb_dessert = nb_dessert,
            username = username,
        )
        db.session.add(menu)
        db.session.commit()
        # serialized_menu = menu.serialize()            
    
    except Exception as e:
        return make_response(
            jsonify(
                {
                    "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                    "detail": "Creation of user failed" + str(e),
                    "status": 400,
                }
            ),
            400,
        )

# @menu_router.route('/menu', method="GET")
# def menu_page():
#     user = auth.get_user()
#     if not user:
#         # redirect to login
#     else:
#         # show menu page