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

@menu_router.route('/commande', methods=["GET"])
def commande():
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    query = "SELECT * FROM Menu;"# where username = \"user1\";"
    cursor.execute(query)

    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    # total = rows[2] + rows[4]
    # print (total)

    cursor.close()
    conn.close()

    return render_template("commande.html", columns=columns, rows=rows)#, total = total)

@menu_router.route("/menu", methods=["POST"])
def create_menu():
    username = "user"
    Entree = request.json.get("Entree")
    Plat = request.json.get("Plat")
    Dessert = request.json.get("Dessert")
    Total = request.json.get("Total")

    try:
        menu = Menu(
            Entree = Entree,
            Plat = Plat,
            Dessert = Dessert,
            username = username,
            Total = Total,
        )
        db.session.add(menu)
        db.session.commit()
        serialized_menu = menu.serialize()
        return make_response(jsonify(serialized_menu), 201)
    
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