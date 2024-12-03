from flask import Blueprint, render_template, Flask
from flask import jsonify, make_response, request
from services.database import db
from models.models import Menu
import mysql.connector

menu_router = Blueprint('menu', __name__,)

config = {
    'user': 'admin_secure',
    'password': 'g',
    'host': '0.0.0.0',
    'database': 'scim'
}

@menu_router.route('/hello', methods=["GET"])
def hello():
    return jsonify('Hello World!')

@menu_router.route('/commande', methods=["GET"])
def commande():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    # Requête pour récupérer les données
    query = "SELECT * FROM Menu;"
    cursor.execute(query)

    # Récupération des colonnes et des lignes
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    # Fermeture de la connexion
    cursor.close()
    conn.close()

    return render_template("commande.html", columns=columns, rows=rows)

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