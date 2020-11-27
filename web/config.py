from pymongo import MongoClient
from flask import Flask
from flask_restful import Api
import bcrypt


app = Flask(__name__)
app.secret_key = b"@\xe4\x82+{\xed)~\x92\x84K\x11:)\x95\xf4"
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.WeatherDB
users = db["Users"]


# some global variables
tokens_start = 10

password_length = 8
username_length = 5
min_username = f"Useranme must be at least {username_length} characters long"
min_password = f"Password must be at least {password_length} characters long"

register_keys_valid = ["username", "password"]

weather_keys_valid = [
    "username", "password", "city", "format_temperature"
]
main_keys_valid = ["temp", "temp_max", "temp_min", "feels_like"]
keys_weather_return = [
    "Temperature", "Minimum temperature", "Maximum temperature",
    "Feels like", "Description", "Wind speed"
]

admin_pwd = "ad002.C2f"
admin_name = "admin"
refill_keys_valid = ["username", "admin_pwd", "amount"]
# crypting admin's password and inserting into database
admin_pwd_crypted = bcrypt.hashpw(
    admin_pwd.encode("utf8"), bcrypt.gensalt()
)
