from flask import Flask, jsonify, abort, make_response, request
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from database import db
from models import User, Group

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:g@localhost:3306/scim"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app

app = create_app()

def auth_required(func):
    """Flask decorator to require the presence of a valid Authorization header."""
    @wraps(func)
    def check_auth(*args, **kwargs):
        try:
            if request.headers["Authorization"].split("Bearer ")[1] == "123456789":
                return func(*args, **kwargs)
            else:
                return make_response(jsonify({
                    "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                    "status": "403",
                    "detail": "Unauthorized"
                }), 403, {"Content-Type": "application/scim+json"})
        except KeyError:
            return make_response(jsonify({
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                "status": "403",
                "detail": "Unauthorized"
            }), 403, {"Content-Type": "application/scim+json"})
    return check_auth

@app.before_request
def before_request():
    """Ensure requests have the correct Content-Type."""
    if request.method in ['POST', 'PUT', 'PATCH']:
        if 'application/scim+json' not in request.headers.get('Content-Type', ''):
            return make_response(jsonify({
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                "detail": "Content-Type must be application/scim+json"
            }), 415, {"Content-Type": "application/scim+json"})

# @app.after_request
# def after_request(response):
#     """Add the appropriate SCIM headers to all responses."""
#     response.headers['Content-Type'] = 'application/scim+json'
#     return response

@app.route("/scim/v2/Users", methods=["GET"])
@auth_required
def get_users():
    """Get SCIM Users"""
    start_index = int(request.args.get('startIndex', 1))
    count = int(request.args.get('count', 10))

    if "filter" in request.args:
        # Extraire le filtre et chercher par userName
        single_filter = request.args["filter"].split(" ")
        filter_value = single_filter[2].strip('"')

        # Requête pour obtenir le nombre total d’utilisateurs correspondant au filtre
        total_results = User.query.filter_by(userName=filter_value).count()

        # Récupérer uniquement le premier utilisateur correspondant pour ce filtre
        user = User.query.filter_by(userName=filter_value).first()
        users = [user] if user else []
    else:
        # Sans filtre, appliquer la pagination sur tous les utilisateurs
        pagination = User.query.paginate(start_index, count, False)
        users = pagination.items
        total_results = pagination.total

    # Sérialisation des utilisateurs selon le format SCIM2
    serialized_users = [
        {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
            "id": user.id,
            "userName": user.userName,
            # Ajoute ici d'autres champs requis par le standard SCIM2, comme les emails, le nom, etc.
        }
        for user in users
    ]

    # Construire et retourner la réponse SCIM avec les bonnes valeurs pour les champs requis
    return make_response(
        jsonify({
           "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
           "totalResults": total_results,
           "startIndex": start_index,
           "itemsPerPage": len(users),
           "Resources": serialized_users
        }),
        200,
        {"Content-Type": "application/scim+json"}
    )


@app.route("/scim/v2/Users/<string:user_id>", methods=["GET"])
@auth_required
def get_user(user_id):
    """Get SCIM User"""
    user = User.query.get(user_id)
    if not user:
        return make_response(
            jsonify({
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                "detail": "User not found",
                "status": 404
            }),
            404
        )
    return jsonify(user.serialize())

@app.route("/scim/v2/Users", methods=["POST"])
@auth_required
def create_user():
    """Create SCIM User"""
    active = request.json.get("active")
    displayName = request.json.get("displayName")
    emails = request.json.get("emails")
    externalId = request.json.get("externalId")
    groups = request.json.get("groups")
    locale = request.json.get("locale")
    givenName = request.json["name"].get("givenName")
    middleName = request.json["name"].get("middleName")
    familyName = request.json["name"].get("familyName")
    password = request.json.get("password")
    schemas = request.json.get("schemas")
    userName = request.json.get("userName")

    existing_user = User.query.filter_by(userName=userName).first()

    if existing_user:
        return make_response(
            jsonify(
                {
                    "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                    "detail": "User already exists in the database.",
                    "status": 409,
                }
            ),
            409,
        )
    else:
        try:
            user = User(
                active=active,
                displayName=displayName,
                emails_primary=emails[0]["primary"],
                emails_value=emails[0]["value"],
                emails_type=emails[0]["type"],
                externalId=externalId,
                locale=locale,
                givenName=givenName,
                middleName=middleName,
                familyName=familyName,
                password=password,
                userName=userName,
            )
            db.session.add(user)

            if groups:
                for group in groups:
                    existing_group = Group.query.get(group["value"])

                    if existing_group:
                        existing_group.users.append(user)
                    else:
                        new_group = Group(displayName=group["displayName"])
                        db.session.add(new_group)
                        new_group.users.append(user)

            db.session.commit()
            print(user.serialize())
            return make_response(jsonify(user.serialize()), 201)
        except Exception as e:
            return str(e)

@app.route("/scim/v2/Users/<string:user_id>", methods=["PUT"])
@auth_required
def update_user(user_id):
    """Update SCIM User"""
    user = User.query.get(user_id)

    if not user:
        return make_response(
            jsonify(
                {
                    "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                    "detail": "User not found",
                    "status": 404,
                }
            ),
            404,
        )
    else:
        groups = request.json.get("groups")
        user.active = request.json.get("active")
        user.displayName = request.json.get("displayName")
        user.emails = request.json.get("emails")
        user.externalId = request.json.get("externalId")
        user.locale = request.json.get("locale")
        user.name = request.json.get("name")
        user.familyName = request.json["name"].get("familyName")
        user.middleName = request.json["name"].get("middleName")
        user.givenName = request.json["name"].get("givenName")
        user.password = request.json.get("password")
        user.schemas = request.json.get("schemas")
        user.userName = request.json.get("userName")

        db.session.commit()
        return make_response(jsonify(user.serialize()), 200)

@app.route("/scim/v2/Users/<string:user_id>", methods=["PATCH"])
@auth_required
def deactivate_user(user_id):
    """Deactivate SCIM User"""
    is_user_active = request.json["Operations"][0]["value"]["active"]
    user = User.query.get(user_id)
    user.active = is_user_active

    db.session.commit()
    return make_response("", 204)

@app.route("/scim/v2/Users/<string:user_id>", methods=["DELETE"])
@auth_required
def delete_user(user_id):
    """Delete SCIM User"""
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    return make_response("", 204)

@app.route("/scim/v2/Groups", methods=["GET"])
@auth_required
def get_groups():
    """Get SCIM Groups"""
    groups = Group.query.all()
    return jsonify([e.serialize() for e in groups])

@app.route("/scim/v2/Groups/<string:group_id>", methods=["GET"])
@auth_required
def get_group(group_id):
    """Get SCIM Group"""
    group = Group.query.get(group_id)
    if not group:
        abort(404)
    return jsonify(group.serialize())

@app.route("/scim/v2/Groups", methods=["POST"])
@auth_required
def create_group():
    """Create SCIM Group"""
    displayName = request.json["displayName"]
    members = request.json["members"]

    try:
        group = Group(
            displayName=displayName,
        )
        db.session.add(group)
        db.session.commit()
        return make_response(jsonify(group.serialize()), 201)
    except Exception as e:
        return str(e)

@app.route("/scim/v2/Groups/<string:group_id>", methods=["PATCH", "PUT"])
@auth_required
def update_group(group_id):
    """Update SCIM Group"""
    if "members" in request.json:
        members = request.json["members"]
    else:
        members = request.json["Operations"][0]["value"]

        if request.json["Operations"][0]["op"] == "replace":
            return make_response("", 204)

    group = Group.query.get(group_id)
    db.session.add(group)

    for member in members:
        existing_user = User.query.get(member["value"])

        if existing_user:
            group.users.append(existing_user)

    db.session.commit()
    return make_response(jsonify(group.serialize()), 200)

@app.route("/scim/v2/Groups/<string:group_id>", methods=["DELETE"])
@auth_required
def delete_group(group_id):
    """Delete SCIM Group"""
    group = Group.query.get(group_id)
    db.session.delete(group)
    db.session.commit()
    return make_response("", 204)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
