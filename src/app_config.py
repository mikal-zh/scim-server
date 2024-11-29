import os

AUTHORITY = os.getenv("AUTHORITY")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

REDIRECT_PATH = "/auth/redirect"
SCOPE = ["User.Read", "email"]
SESSION_TYPE = "filesystem"