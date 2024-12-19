from flask import Blueprint
from flask import Flask, jsonify, make_response, request, session
from functools import wraps
from services.database import db
from models.models import User, Group, Menu
import re
from sqlalchemy import func
from app_config import SCIM_SECRET

scim_router = Blueprint('scim', __name__, template_folder='templates')

def auth_required(func):
    """Flask decorator to require the presence of a valid Authorization header."""
    @wraps(func)
    def check_auth(*args, **kwargs):
        try:
            if request.headers["Authorization"].split("Bearer ")[1] != SCIM_SECRET:
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

@scim_router.before_request
def before_request():
    """Ensure requests have the correct Content-Type."""
    if request.method in ['POST', 'PUT', 'PATCH']:
        if 'application/scim+json' not in request.headers.get('Content-Type', ''):
            return make_response(jsonify({
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                "detail": "Content-Type must be application/scim+json"
            }), 415, {"Content-Type": "application/scim+json"})

@scim_router.after_request
def after_request(response):
    """Add the appropriate SCIM headers to all responses."""
    response.headers['Content-Type'] = 'application/scim+json'
    return response

@scim_router.route("/scim/v2/Schemas")
def get_schemas():
    """Get SCIM Schemas"""
    schemas = [
        {
            "id": "urn:ietf:params:scim:schemas:core:2.0:User",
            "name": "User",
            "description": "Core User schema",
            "attributes": [
                {"name": "id", "type": "string", "multiValued": False, "required": True, "mutability": "readOnly"},
                {"name": "userName", "type": "string", "multiValued": False, "required": True, "mutability": "readWrite"},
                {"name": "name", "type": "complex", "multiValued": False, "required": False, "mutability": "readWrite", "subAttributes": [
                    {"name": "givenName", "type": "string", "multiValued": False, "mutability": "readWrite"},
                    {"name": "middleName", "type": "string", "multiValued": False, "mutability": "readWrite"},
                    {"name": "familyName", "type": "string", "multiValued": False, "mutability": "readWrite"}
                ]},
                {"name": "displayName", "type": "string", "multiValued": False, "mutability": "readWrite"},
                {"name": "locale", "type": "string", "multiValued": False, "mutability": "readWrite"},
                {"name": "externalId", "type": "string", "multiValued": False, "mutability": "readWrite"},
                {"name": "active", "type": "boolean", "multiValued": False, "mutability": "readWrite"},
                {"name": "groups", "type": "complex", "multiValued": True, "mutability": "readOnly", "subAttributes": [
                    {"name": "display", "type": "string", "multiValued": False, "mutability": "readOnly"},
                    {"name": "value", "type": "string", "multiValued": False, "mutability": "readOnly"}
                ]},
                {"name": "meta", "type": "complex", "multiValued": False, "mutability": "readOnly", "subAttributes": [
                    {"name": "resourceType", "type": "string", "multiValued": False, "mutability": "readOnly"},
                    {"name": "created", "type": "string", "multiValued": False, "mutability": "readOnly"},
                    {"name": "lastModified", "type": "string", "multiValued": False, "mutability": "readOnly"}
                ]}
            ]
        },
        {
            "id": "urn:ietf:params:scim:schemas:core:2.0:Group",
            "name": "Group",
            "description": "Core Group schema",
            "attributes": [
                {"name": "id", "type": "string", "multiValued": False, "required": True, "mutability": "readOnly"},
                {"name": "displayName", "type": "string", "multiValued": False, "required": True, "mutability": "readWrite"},
                {"name": "members", "type": "complex", "multiValued": True, "mutability": "readWrite", "subAttributes": [
                    {"name": "value", "type": "string", "multiValued": False, "mutability": "readWrite"},
                    {"name": "display", "type": "string", "multiValued": False, "mutability": "readWrite"}
                ]},
                {"name": "meta", "type": "complex", "multiValued": False, "mutability": "readOnly", "subAttributes": [
                    {"name": "resourceType", "type": "string", "multiValued": False, "mutability": "readOnly"},
                    {"name": "created", "type": "string", "multiValued": False, "mutability": "readOnly"},
                    {"name": "lastModified", "type": "string", "multiValued": False, "mutability": "readOnly"}
                ]}
            ]
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

@scim_router.route("/scim/v2/Users", methods=["GET"])
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

    serialized_users = [u.serialize() for u in users]

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

@scim_router.route("/scim/v2/Users/<string:user_id>", methods=["GET"])
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

@scim_router.route("/scim/v2/Users", methods=["POST"])
@auth_required
def create_user():
    """Create SCIM User"""
    active = request.json.get("active") or True
    if isinstance(active, str):
        active = active.lower() == "true"
    displayName = request.json.get("displayName")
    externalId = request.json.get("externalId")
    groups = request.json.get("groups", [])
    locale = request.json.get("locale")
    givenName = request.json.get("name", {}).get("givenName")
    middleName = request.json.get("name", {}).get("middleName")
    familyName = request.json.get("name", {}).get("familyName")
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
                externalId=externalId,
                locale=locale,
                givenName=givenName,
                middleName=middleName,
                familyName=familyName,
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

            serialized_user = user.serialize()            
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
    return re.sub(r'\[.*?\]', '', input_str)

@scim_router.route("/scim/v2/Users/<string:user_id>", methods=["PATCH"])
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
            op = operation.get("op").lower()
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
                            attr = format_attr(attr)
                            # remove point in attribute name and add a maj to next letter
                            if hasattr(user, attr):
                                if isinstance(getattr(user, attr), bool):
                                    attr_value = attr_value.lower() == "true" if isinstance(attr_value, str) else bool(attr_value)
                                setattr(user, attr, attr_value)
                            else:
                                raise AttributeError
                elif path:
                    # Normalize path for attribute matching
                    attribute = path.split(":")[-1]  # Get the attribute name after any namespace prefixes
                    attribute = format_attr(attribute)

                    if op == "replace" or op == "add":
                        if hasattr(user, attribute):
                            if isinstance(getattr(user, attribute), bool):
                                value = value.lower() == "true" if isinstance(value, str) else bool(value)
                            setattr(user, attribute, value)
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
        return make_response(jsonify(user.serialize()), 200)

@scim_router.route("/scim/v2/Users/<string:user_id>", methods=["DELETE"])
@auth_required
def delete_user(user_id):
    """Delete SCIM User"""
    user = User.query.get(user_id)
    db.session.delete(user)
    db.session.commit()
    
    return make_response("", 204)

@scim_router.route("/scim/v2/Groups", methods=["GET"])
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
        serialized_group = group.serialize()
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

@scim_router.route("/scim/v2/Groups/<string:group_id>", methods=["GET"])
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

    serialized_group = group.serialize()
    for attr in excluded_attributes:
        attr = attr.strip()  # Clean up whitespace
        if attr in serialized_group:
            del serialized_group[attr]

    return jsonify(serialized_group), 200

@scim_router.route("/scim/v2/Groups", methods=["POST"])
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

        return make_response(jsonify(group.serialize()), 201)
    except Exception as e:
        return make_response(
            jsonify({
                "schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"],
                "detail": str(e),
                "status": 500
            }),
            500
        )

@scim_router.route("/scim/v2/Groups/<group_id>", methods=["PATCH"])
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
        return make_response(jsonify(group.serialize()), 200)
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

@scim_router.route("/scim/v2/Groups/<string:group_id>", methods=["DELETE"])
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
