import os

from dotenv import load_dotenv


load_dotenv()


AW_URL = os.getenv("AW_URL")
NOTEBOOKS_DIR = os.getenv("NOTEBOOKS_DIR")

OAUTH_CLIENT_ID = os.getenv("OAUTH_CLIENT_ID")
OAUTH_CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")
