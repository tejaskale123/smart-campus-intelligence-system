from pymongo import MongoClient
from mongodb import db
client = MongoClient("mongodb://localhost:27017/")

db = client["smart_campus_db"]