from flask import Flask, jsonify, abort, make_response, request
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from database import db
from models import User, Group
import re

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
            if request.headers["Authorization"].split("Bearer ")[1] != "123456789":
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
        return func(*args, **kwargs)
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

@app.after_request
def after_request(response):
    """Add the appropriate SCIM headers to all responses."""
    response.headers['Content-Type'] = 'application/scim+json'
    return response

@app.route("/scim/v2/Schemas")
def get_schemas():
    """Get SCIM Schemas"""
    schemas = [
        {
            "id": "urn:ietf:params:scim:schemas:core:2.0:User",
            "name": "User",
            "description": "Core schema for representing users.",
            "attributes": [
                {
                    "name": "userName",
                    "type": "string",
                    "multiValued": False,
                    "description": "Unique identifier for the user, typically used for authentication.",
                    "required": True,
                    "caseExact": False,
                    "mutability": "readWrite",
                    "returned": "always",
                    "uniqueness": "server"
                },
                {
                    "name": "id",
                    "type": "string",
                    "multiValued": False,
                    "description": "Unique identifier for the user resource.",
                    "required": True,
                    "caseExact": False,
                    "mutability": "readOnly",
                    "returned": "always",
                    "uniqueness": "server"
                },
                {
                    "name": "active",
                    "type": "boolean",
                    "multiValued": False,
                    "description": "A Boolean value indicating the user's active state.",
                    "required": False,
                    "mutability": "readWrite",
                    "returned": "default",
                    "uniqueness": "none"
                },
                {
                    "name": "emails",
                    "type": "complex",
                    "multiValued": True,
                    "description": "Email addresses for the user.",
                    "required": True,
                    "subAttributes": [
                        {
                            "name": "value",
                            "type": "string",
                            "multiValued": False,
                            "description": "Email address value.",
                            "required": True,
                            "caseExact": False,
                            "mutability": "readWrite",
                            "returned": "default",
                            "uniqueness": "none"
                        },
                        {
                            "name": "type",
                            "type": "string",
                            "multiValued": False,
                            "description": "Type of email (e.g., work, home).",
                            "required": True,
                            "caseExact": False,
                            "mutability": "readWrite",
                            "returned": "default",
                            "uniqueness": "none",
                            "canonicalValues": ["work"]
                        },
                        {
                            "name": "primary",
                            "type": "boolean",
                            "multiValued": False,
                            "description": "Indicates whether this email is the primary email.",
                            "required": True,
                            "mutability": "readWrite",
                            "returned": "default",
                            "uniqueness": "none"
                        }
                    ],
                    "mutability": "readWrite",
                    "returned": "default",
                    "uniqueness": "none"
                },
                {
                    "name": "name",
                    "type": "complex",
                    "multiValued": False,
                    "description": "Name for the user.",
                    "required": False,
                    "subAttributes": [
                        {
                            "name": "formatted",
                            "type": "string",
                            "multiValued": False,
                            "description": "name value.",
                            "required": False,
                            "caseExact": False,
                            "mutability": "readWrite",
                            "returned": "default",
                            "uniqueness": "none"
                        },
                        {
                            "name": "familyName",
                            "type": "string",
                            "multiValued": False,
                            "description": ".",
                            "required": False,
                            "caseExact": False,
                            "mutability": "readWrite",
                            "returned": "default",
                            "uniqueness": "none"
                        },
                        {
                            "name": "givenName",
                            "type": "string",
                            "multiValued": False,
                            "description": ".",
                            "required": False,
                            "caseExact": False,
                            "mutability": "readWrite",
                            "returned": "default",
                            "uniqueness": "none"
                        }
                    ],
                    "mutability": "readWrite",
                    "returned": "default",
                    "uniqueness": "none"
                },
                {
                    "name": "meta",
                    "type": "complex",
                    "multiValued": False,
                    "description": "Metadata about the resource.",
                    "required": False,
                    "subAttributes": [
                        {
                            "name": "created",
                            "type": "dateTime",
                            "multiValued": False,
                            "description": "The date the resource was created.",
                            "required": False,
                            "mutability": "readOnly",
                            "returned": "default",
                            "uniqueness": "none"
                        },
                        {
                            "name": "lastModified",
                            "type": "dateTime",
                            "multiValued": False,
                            "description": "The date the resource was last modified.",
                            "required": False,
                            "mutability": "readOnly",
                            "returned": "default",
                            "uniqueness": "none"
                        },
                        {
                            "name": "resourceType",
                            "type": "string",
                            "multiValued": False,
                            "description": "The type of SCIM resource.",
                            "required": False,
                            "mutability": "readOnly",
                            "returned": "default",
                            "uniqueness": "none"
                        }
                    ],
                    "mutability": "readOnly",
                    "returned": "default",
                    "uniqueness": "none"
                }
            ],
            "meta": {
                "resourceType": "Schema",
                "location": "/scim/v2/Schemas/urn:ietf:params:scim:schemas:core:2.0:User"
            }
        }
    ]

    return make_response(
        jsonify({
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": len(schemas),
            "Resources": schemas
        }),
        200
    )

def serialize_user(user):
    return {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:User"],
            "id": user.id,
            "userName": user.userName,
            "displayName" : user.displayName,
            "active": user.active,
            "emails": [{
                "value": user.emails_value,
                "type": user.emails_type,
                "primary": user.emails_primary
            }],
            "name": {
                "givenName": user.name_givenName,
                "familyName": user.name_familyName,
                "middleName": user.name_middleName
            },
            "locale": user.locale,
        }

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
        serialize_user(user) for user in users
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
        200
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
    emails = request.json.get("emails", [])
    externalId = request.json.get("externalId")
    groups = request.json.get("groups", [])
    locale = request.json.get("locale")
    givenName = request.json.get("name", {}).get("givenName")
    middleName = request.json.get("name", {}).get("middleName")
    familyName = request.json.get("name", {}).get("familyName")
    password = request.json.get("password")
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

            serialized_user = serialize_user(user)
            return make_response(jsonify(serialized_user), 201)
        except Exception as e:
            return str(e)

def format_attr(input_str):
    input_str = input_str.replace('.', '_')
    return re.sub(r'\[.*?\]', '', input_str)

@app.route("/scim/v2/Users/<string:user_id>", methods=["PATCH"])
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
        print(request.json)
        for operation in request.json["Operations"]:
            # make the operation
            op = operation.get("op")
            path = operation.get("path")
            value = operation.get("value")

            if not op:
                return make_response(
                    jsonify(
                        {
                            "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                            "detail": "Operation must include 'op' and 'path'.",
                            "status": 400,
                        }
                    ),
                    400,
                )
            
            if op == "replace" and not path:
                # Replace the entire user object
                if not isinstance(value, dict):
                    return make_response(
                        jsonify(
                            {
                                "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                                "detail": "Value must be a dictionary when replacing the entire user.",
                                "status": 400,
                            }
                        ),
                        400,
                    )

                # Update each attribute in the user object
                for attr, attr_value in value.items():
                    attr = format_attr(attr)
                    # remove point in attribute name and add a maj to next letter
                    if hasattr(user, attr):
                        setattr(user, attr, attr_value)
                    else:
                        return make_response(
                            jsonify(
                                {
                                    "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                                    "detail": f"Attribute '{attr}' not found on user.",
                                    "status": 400,
                                }
                            ),
                            400,
                        )
            elif path:
                # Normalize path for attribute matching
                attribute = path.split(":")[-1]  # Get the attribute name after any namespace prefixes
                attribute = format_attr(attribute)

                if op == "add":
                    current_value = getattr(user, attribute, None)
                    if current_value is None:
                        setattr(user, attribute, value)
                    elif isinstance(current_value, list):
                        current_value.append(value)
                    else:
                        return make_response(
                            jsonify(
                                {
                                    "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                                    "detail": f"Cannot add value to non-list attribute: {attribute}",
                                    "status": 400,
                                }
                            ),
                            400,
                        )
                elif op == "replace":
                    setattr(user, attribute, value)
                elif op == "remove":
                    if hasattr(user, attribute):
                        setattr(user, attribute, None)
                else:
                    return make_response(
                        jsonify(
                            {
                                "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                                "detail": f"Unsupported operation: {op}",
                                "status": 400,
                            }
                        ),
                        400,
                    )

        db.session.commit()

        print("before/after", User.query.get(user_id).serialize(), user.serialize())

        return make_response(jsonify(user.serialize()), 200)

# @app.route("/scim/v2/Users/<string:user_id>", methods=["PATCH"])
# @auth_required
# def deactivate_user(user_id):
#     """Deactivate SCIM User"""
#     is_user_active = request.json["Operations"][0]
#     print("deactivate ",is_user_active, user_id)
#     user = User.query.get(user_id)
#     user.active = False

#     db.session.commit()
#     return make_response("", 204)

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
