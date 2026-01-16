import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGODB_URI environment variable is not set")

client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
db = client["RetroVideoGameExchange"]

games_collection = db["Games"]
users_collection = db["Users"]
