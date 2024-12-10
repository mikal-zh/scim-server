import os
from dotenv import load_dotenv

load_dotenv()

AUTHORITY = os.getenv("AUTHORITY")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
DB_URL = os.getenv("DB_URL")

REDIRECT_PATH = "/auth/redirect"
SCOPE = ["User.Read", "email"]
SESSION_TYPE = "filesystem"
