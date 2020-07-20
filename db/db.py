from pymongo import MongoClient


client = MongoClient("mongodb://db:27017")
db = client.WeatherDB
users = db["Users"]
