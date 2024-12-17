import uuid
from services.database import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

# Define a many-to-many relationship
links = db.Table(
    "link",
    db.Column(
        "group_id", db.String(128), db.ForeignKey("groups.id"), primary_key=True
    ),
    db.Column(
        "user_id", db.String(128), db.ForeignKey("users.id"), primary_key=True
    ),
)

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String(128), primary_key=True, default=uuid.uuid4)
    active = db.Column(db.Boolean)
    userName = db.Column(db.String(128), nullable=False, unique=True)
    name_givenName = db.Column(db.String(64))
    name_middleName = db.Column(db.String(64))
    name_familyName = db.Column(db.String(64))
    groups = db.relationship(
        "Group",
        secondary=links,
        lazy="subquery",
        backref=db.backref("users", lazy=True),
    )
    displayName = db.Column(db.String(64))
    locale = db.Column(db.String(64))
    externalId = db.Column(db.String(64))
    menu = relationship('Menu', backref='user')

    def __init__(
        self,
        active,
        userName,
        givenName,
        middleName,
        familyName,
        displayName,
        locale,
        externalId,
    ):
        self.active = active
        self.userName = userName
        self.name_givenName = givenName
        self.name_middleName = middleName
        self.name_familyName = familyName
        self.displayName = displayName
        self.locale = locale
        self.externalId = externalId

    def __repr__(self):
        return "<id {}>".format(self.id)

    def serialize(self):
        groups = []
        for group in self.groups:
            groups.append({"display": group.displayName, "value": group.id})

        return {
            "schemas": [
                "urn:ietf:params:scim:schemas:core:2.0:User",
            ],
            "id": self.id,
            "userName": self.userName,
            "name": {
                "givenName": self.name_givenName,
                "middleName": self.name_middleName,
                "familyName": self.name_familyName,
            },
            "displayName": self.displayName,
            "locale": self.locale,
            "externalId": self.externalId,
            "active": self.active,
            "groups": groups,
            "meta": {
                "resourceType": "User",
                "created": "2010-01-23T04:56:22Z",
                "lastModified": "2011-05-13T04:42:34Z",
            },
        }

class Group(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.String(128), primary_key=True, default=uuid.uuid4)
    displayName = db.Column(db.String(64))

    def serialize(self):
        users = []
        for user in self.users:
            users.append({"display": user.userName, "value": user.id})

        return {
            "schemas": [
                "urn:ietf:params:scim:schemas:core:2.0:Group",
            ],
            "id": self.id,
            "meta": {
                "resourceType": "Group",
                "created": "2010-01-23T04:56:22Z",
                "lastModified": "2011-05-13T04:42:34Z",
            },
            "displayName": self.displayName,
            "members": users,
        }

class Menu(db.Model):
    __tablename__ = "Menu"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(128), ForeignKey('users.id'), nullable=False)
    Entree = db.Column(db.Integer)
    Plat = db.Column(db.Integer)
    Dessert = db.Column(db.Integer)
    Total = db.Column(db.Integer)

    def __init__(
        self,
        user_id,
        Entree,
        Plat,
        Dessert,
        Total,
    ):
        self.user_id = user_id
        self.Entree = Entree
        self.Plat = Plat
        self.Dessert = Dessert
        self.Total = Total

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "Entree": self.Entree,
            "Plat": self.Plat,
            "Dessert": self.Dessert,
            "Total": self.Total
        }
