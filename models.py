# from sqlalchemy.dialects.mysql import UUID
import uuid
from database import db

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
    userName = db.Column(db.String(128))
    givenName = db.Column(db.String(64))
    middleName = db.Column(db.String(64))
    familyName = db.Column(db.String(64))
    groups = db.relationship(
        "Group",
        secondary=links,
        lazy="subquery",
        backref=db.backref("users", lazy=True),
    )
    emails_primary = db.Column(db.Boolean)
    emails_value = db.Column(db.String(64))
    emails_type = db.Column(db.String(64))
    displayName = db.Column(db.String(64))
    locale = db.Column(db.String(64))
    externalId = db.Column(db.String(64))
    password = db.Column(db.String(64))

    def __init__(
        self,
        active,
        userName,
        givenName,
        middleName,
        familyName,
        emails_primary,
        emails_value,
        emails_type,
        displayName,
        locale,
        externalId,
        password,
    ):
        self.active = active
        self.userName = userName
        self.givenName = givenName
        self.middleName = middleName
        self.familyName = familyName
        self.emails_primary = emails_primary
        self.emails_value = emails_value
        self.emails_type = emails_type
        self.displayName = displayName
        self.locale = locale
        self.externalId = externalId
        self.password = password

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
                "givenName": self.givenName,
                "middleName": self.middleName,
                "familyName": self.familyName,
            },
            "emails": [
                {
                    "primary": self.emails_primary,
                    "value": self.emails_value,
                    "type": self.emails_type,
                }
            ],
            "displayName": self.displayName,
            "locale": self.locale,
            "externalId": self.externalId,
            "active": self.active,
            "groups": groups,
            "meta": {"resourceType": "User"},
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
            },
            "displayName": self.displayName,
            "members": users,
        }
