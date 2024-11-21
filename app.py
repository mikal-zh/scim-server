from flask import Flask, jsonify, abort, make_response, request
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from database import db
from models import User, Group
import re
from sqlalchemy import func

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
    user = {
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
            "meta": {
                "resourceType": "User",
                "created": "2010-01-23T04:56:22Z",
                "lastModified": "2011-05-13T04:42:34Z",
            },
            "locale": user.locale,
        }
    return user

@app.route("/scim/v2/Users", methods=["GET"])
@auth_required
def get_users():
    """Get SCIM Users"""
    start_index = int(request.args.get('startIndex', 1))
    count = int(request.args.get('count', 10))

    if "filter" in request.args:
        filter_parts = request.args["filter"].split(" ")
        if len(filter_parts) == 3 and filter_parts[0] == "userName" and filter_parts[1] == "eq":
            filter_value = filter_parts[2].strip('"').lower()
            users = User.query.filter(func.lower(User.userName) == filter_value).all()
            total_results = len(users)
        else:
            users = []
            total_results = 0
    else:
        pagination = User.query.paginate(start_index, count, False)
        users = pagination.items
        total_results = pagination.total

    serialized_users = [serialize_user(e) for e in users]

    return make_response(
        jsonify({
            "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
            "totalResults": total_results,
            "startIndex": start_index,
            "itemsPerPage": count,
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
    
    return jsonify(serialize_user(user))

@app.route("/scim/v2/Users", methods=["POST"])
@auth_required
def create_user():
    """Create SCIM User"""
    active = request.json.get("active") or True
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
                emails_primary=emails[0]["primary"] if len(emails)>0 else None,
                emails_value=emails[0]["value"] if len(emails)>0 else None,
                emails_type=emails[0]["type"] if len(emails)>0 else None,
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
            
            return make_response(
                jsonify(
                    {
                        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                        "detail": "Creation of user failed" + str(e),
                        "status": 500,
                    }
                ),
                500,
            )

def format_attr(input_str):
    input_str = input_str.replace('.', '_')
    multival_param = re.search(r'\[\w+\s+(?:eq|ne|co|sw|ew|gt|lt|ge|le)\s+["\']([^"\']+)["\']\]', input_str)
    return (re.sub(r'\[.*?\]', '', input_str), multival_param.group(1) if multival_param else None)

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

            try:
                if not path:
                    # Replace the entire user object
                    if not isinstance(value, dict):
                        raise AttributeError
                    if op == "replace" or op == "add":
                        # Update each attribute in the user object
                        for attr, attr_value in value.items():
                            attr, multival_param = format_attr(attr)
                            # remove point in attribute name and add a maj to next letter
                            if hasattr(user, attr):
                                setattr(user, attr, attr_value)
                                if multival_param and "email" in attribute:
                                    user.emails_type = multival_param
                            else:
                                raise AttributeError
                elif path:
                    # Normalize path for attribute matching
                    attribute = path.split(":")[-1]  # Get the attribute name after any namespace prefixes
                    attribute,multival_param = format_attr(attribute)

                    if op == "replace" or op == "add":
                        if hasattr(user, attribute):
                            setattr(user, attribute, value)
                            if multival_param and "email" in attribute:
                                user.emails_type = multival_param
                        else:
                            raise AttributeError
                    elif op == "remove":
                        if hasattr(user, attribute):
                            setattr(user, attribute, None)
                        else:
                            raise AttributeError
                    else:
                        raise NotImplementedError
            except AttributeError:
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
            except NotImplementedError:
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
        return make_response(jsonify(serialize_user(user)), 200)

@app.route("/scim/v2/Users/<string:user_id>", methods=["DELETE"])
@auth_required
def delete_user(user_id):
    """Delete SCIM User"""
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return make_response("", 204)

def serialize_group(group):
    return {
        "schemas": ["urn:ietf:params:scim:schemas:core:2.0:Group"],
        "id": group.id,
        "displayName": group.displayName,
        "members": [
            {"value": member.id, "display": member.displayName}
            for member in group.users
        ],
        "meta": {
            "resourceType": "Group",
        },
    }

@app.route("/scim/v2/Groups", methods=["GET"])
@auth_required
def get_groups():
    """Get SCIM Groups with filtering and excluded attributes support"""
    # Parse query parameters
    filter_param = request.args.get("filter")
    excluded_attributes = request.args.get("excludedAttributes", "")
    excluded_attributes = excluded_attributes.split(",") if excluded_attributes else []

    # Start the base query
    query = Group.query

    # Handle filtering
    if filter_param:
        try:
            # Example: filter=displayName eq "GroupName"
            filter_parts = filter_param.split(" ", 2)
            if len(filter_parts) != 3 or filter_parts[1] != "eq":
                raise ValueError("Unsupported filter format.")

            filter_field = filter_parts[0]
            filter_value = filter_parts[2].strip('"')

            if filter_field == "displayName":
                query = query.filter(Group.displayName == filter_value)
            else:
                raise ValueError("Unsupported filter field.")
        except ValueError:
            return make_response(
                jsonify({
                    "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                    "detail": "Unsupported filter.",
                    "status": 400
                }),
                400
            )

    # Execute the query
    groups = query.all()

    # Serialize groups
    serialized_groups = []
    for group in groups:
        serialized_group = serialize_group(group)

        # Exclude specified attributes
        for attr in excluded_attributes:
            attr = attr.strip()
            if attr in serialized_group:
                del serialized_group[attr]

        serialized_groups.append(serialized_group)

    # Build the SCIM response
    response = {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
        "totalResults": len(groups),
        "startIndex": 1,  # SCIM default startIndex
        "itemsPerPage": len(groups),
        "Resources": serialized_groups
    }

    return jsonify(response), 200

@app.route("/scim/v2/Groups/<string:group_id>", methods=["GET"])
@auth_required
def get_group(group_id):
    """Get SCIM Group by ID, with support for excluding attributes"""
    group = Group.query.get(group_id)
    if not group:
        return make_response(
            jsonify({
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                "detail": "Group not found",
                "status": 404
            }),
            404
        )

    excluded_attributes = request.args.get('excludedAttributes', '')
    excluded_attributes = excluded_attributes.split(',') if excluded_attributes else []

    serialized_group = serialize_group(group)

    for attr in excluded_attributes:
        attr = attr.strip()  # Clean up whitespace
        if attr in serialized_group:
            del serialized_group[attr]

    return jsonify(serialized_group), 200

@app.route("/scim/v2/Groups", methods=["POST"])
@auth_required
def create_group():
    """Create SCIM Group"""
    displayName = request.json.get("displayName")
    schemas = request.json.get("schemas", [])

    # Validate input
    if not displayName or "urn:ietf:params:scim:schemas:core:2.0:Group" not in schemas:
        return make_response(
            jsonify({
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                "detail": "Invalid request: 'displayName' is required and schemas must include 'urn:ietf:params:scim:schemas:core:2.0:Group'.",
                "status": 400
            }),
            400
        )

    # Check for duplicate displayName
    existing_group = Group.query.filter_by(displayName=displayName).first()
    if existing_group:
        return make_response(
            jsonify({
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                "detail": f"Group with displayName '{displayName}' already exists.",
                "status": 409
            }),
            409
        )

    try:
        # Create the new group
        group = Group(displayName=displayName)
        db.session.add(group)
        db.session.commit()

        return make_response(jsonify(serialize_group(group)), 201)
    except Exception as e:
        return make_response(
            jsonify({
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                "detail": str(e),
                "status": 500
            }),
            500
        )

@app.route("/scim/v2/Groups/<group_id>", methods=["PATCH"])
@auth_required
def update_group(group_id):
    """Update SCIM Group"""
    group = Group.query.get(group_id)

    if not group:
        return make_response(
            jsonify({
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                "detail": "Group not found",
                "status": 404,
            }),
            404,
        )

    try:
        for operation in request.json["Operations"]:
            op = operation.get("op")
            path = operation.get("path")
            value = operation.get("value")

            if not op:
                return make_response(
                    jsonify({
                        "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                        "detail": "Operation must include 'op'.",
                        "status": 400,
                    }),
                    400,
                )

            if op == "replace" and not path:
                for field,val in value.items():
                    if field == "displayName":
                        group.displayName = val
                    if field == "members":
                        group.users = val

            if op == "replace" and path == "displayName":
                group.displayName = value

            elif op in ["add", "replace"] and path == "members":
                for member in value:
                    user = User.query.get(member["value"])
                    if user:
                        group.users.append(user)

            elif op == "remove" and "members" in path:
                match = re.search(r'members\[(value|display)\s+eq\s+"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}|[a-f0-9-]{12,64})"\]', path)
                if match:
                    field = match.group(1)
                    filter = match.group(2)
                    match field:
                        case "value":
                            group.users = [user for user in group.users if user.id != filter]
                        case "display":
                            group.users = [user for user in group.users if user.displayName != filter]
                else:
                    print("no match")

            elif op == "replace" and path == "externalId":
                group.externalId = value

        db.session.commit()
        return make_response(jsonify(serialize_group(group)), 200)
    except Exception as e:
        db.session.rollback()
        return make_response(
            jsonify({
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                "detail": str(e),
                "status": 500,
            }),
            500,
        )

@app.route("/scim/v2/Groups/<string:group_id>", methods=["DELETE"])
@auth_required
def delete_group(group_id):
    group = Group.query.get(group_id)
    if not group:
        return make_response(
            jsonify({
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                "detail": "Group not found",
                "status": 404
            }),
            404
        )
    db.session.delete(group)
    db.session.commit()
    return "", 204

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")