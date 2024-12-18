import os
from dotenv import load_dotenv

load_dotenv()

# Flask settings
SQLALCHEMY_DATABASE_URI= os.getenv("DB_URL")
SQLALCHEMY_TRACK_MODIFICATIONS= False
PREFERRED_URL_SCHEME= "https"
SESSION_TYPE= "filesystem"
    
# Environment variables
AUTHORITY = os.getenv("AUTHORITY")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
SCIM_SECRET = os.getenv("SCIM_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

# Constants for the application
REDIRECT_PATH = "/auth/redirect"
PORT = os.getenv("PORT") or 5000
