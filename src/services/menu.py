from flask import Blueprint, render_template, Flask
from flask import jsonify, make_response, request, redirect, url_for
from services.database import db
from models.models import Menu
import mysql.connector
from services.authentification import auth
from models.models import User

menu_router = Blueprint('menu', __name__,)

config = {
    'user': 'admin_secure',
    'password': 'g',
    'host': '0.0.0.0',
    'database': 'scim'
}

# @menu_router.route("/home")
# def home():
#     return render_template("home.html")

@menu_router.route('/commande', methods=["GET"])
def commande():
    user = auth.get_user()
    username = user["name"]
    if not user:
        return redirect(url_for("auth.login"))

    conn = mysql.connector.connect(**config)
    cursor = conn.cursor()

    query = "SELECT * FROM Menu where username = %s;"# where username = \"user1\";"
    cursor.execute(query, (username,))

    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    entree = 0
    plat = 0
    dessert = 0
    total_all = 0
    for total_nb in rows:
        entree = entree + total_nb[2]
        plat = plat + total_nb[3]
        dessert = dessert + total_nb[4]
        total_all = total_all + total_nb[5]

    # print(entree, plat, dessert, total_all)
    return render_template("commande.html", columns=columns, rows=rows, user=user, entree=entree, plat=plat, dessert=dessert, total_all=total_all)

@menu_router.route("/menu", methods=["POST"])
def create_menu():
    user = auth.get_user()
    if not user:
        return redirect(url_for("auth.login"))
    username = user["name"] #scim User.query.filter_by(userName=user["email"]).first().name_givenName
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