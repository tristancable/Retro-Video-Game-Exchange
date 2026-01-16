from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://dev:dev@cluster0.ftmds5c.mongodb.net/?appName=Cluster0"

client = MongoClient(uri, server_api=ServerApi('1'))
db = client["RetroVideoGameExchange"]

games_collection = db["Games"]
users_collection = db["Users"]