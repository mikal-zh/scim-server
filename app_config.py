import os

AUTHORITY = os.getenv("AUTHORITY")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

REDIRECT_PATH = "/getAToken"
SCOPE = ["User.Read", "email", "profile", "openid"]
SESSION_TYPE = "filesystem"