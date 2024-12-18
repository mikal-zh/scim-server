from flask import Blueprint, render_template, session
from flask import jsonify, make_response, request, redirect, url_for
from services.database import db
from models.models import Menu
from models.models import User
from sqlalchemy import func
import services.identity as idt

menu_router = Blueprint('menu', __name__,)

@menu_router.route('/commande', methods=["GET"])
def commande():
    user = idt.get_user_info()
    if not user:
        return redirect(url_for("auth.login"))
    username = user.get("preferred_username") or user.get("username") or user.get("email")
    user = User.query.filter(func.lower(User.userName) == username).first()

    results:list[Menu] = Menu.query.filter(Menu.user_id == user.id).all()
    
    entree = 0
    plat = 0
    dessert = 0
    total_all = 0
    for menu in results:
        entree = entree + menu.Entree
        plat = plat + menu.Plat
        dessert = dessert + menu.Dessert
        total_all = total_all + menu.Total

    columns = ["id", "Entree", "Plat", "Dessert", "Total"]
    rows = [[menu.id, menu.Entree, menu.Plat, menu.Dessert, menu.Total] for menu in results]

    # print(entree, plat, dessert, total_all)
    return render_template("commande.html", columns=columns, rows=rows, user=user, entree=entree, plat=plat, dessert=dessert, total_all=total_all)

@menu_router.route("/menu", methods=["POST"])
def create_menu():
    user = idt.get_user_info()
    if not user:
        return redirect(url_for("auth.login"))
    
    username = user.get("preferred_username") or user.get("username") or user.get("email")
    user = User.query.filter(func.lower(User.userName) == username).first()

    Entree = request.json.get("Entree")
    Plat = request.json.get("Plat")
    Dessert = request.json.get("Dessert")
    Total = request.json.get("Total")

    menu = Menu(
        user_id = user.id,
        Entree = Entree,
        Plat = Plat,
        Dessert = Dessert,
        Total = Total,
    )
    db.session.add(menu)
    db.session.commit()
    serialized_menu = menu.serialize()
    return make_response(jsonify(serialized_menu), 201)