""" Weather API that give some information about current weather. """

from flask import Flask, jsonify
from flask_restful import Api, Resource, request
from pymongo import MongoClient
from werkzeug.wrappers import BaseResponse
from pprint import pprint
from http import HTTPStatus
from operator import add, sub
import requests
import json
import helper
import bcrypt


# TODO: test code
# TODO: docstrings and comments
# TODO: GET RID OF SPAGHETTI CODE

app = Flask(__name__)
api = Api(app)
client = MongoClient("mongodb://db:27017")
db = client.WeatherDB
users = db["Users"]

# some global variables
tokens_start = 10

password_length = 8
username_length = 5
min_username = f"Useranme must be at least {username_length} long"
min_password = f"Password must be at least {password_length} long"

register_keys_valid = ["username", "password"]


class Register(Resource):
    """ User registration. """
    def post(self) -> BaseResponse:
        """ Called when we have a POST request.

        Returns:
            BaseResponse object with message and code
        """
        data = request.get_json()
        # data_keys_list = list(data.keys())
        is_valid, msg, code = helper.user_validation(
            users, data, register_keys_valid, is_register=True
        )
        if not is_valid:
            return jsonify({"Message": msg,"Code": code})
        username = data["username"]
        password = data["password"]

        try:
            username = helper.validate_type(
                username, "username", str,
                ValueError, helper.INVALID_USERNAME,
                min_error=min_username, min_=username_length
            )
        except ValueError as ex:
            return jsonify({"Message": ex.args[0], "Code": ex.args[1]})

        try:
            password = helper.validate_type(
                password, "password", str,
                ValueError, helper.INVALID_PASSWORD,
                min_error=min_password, min_=password_length
            )
        except ValueError as ex:
            return jsonify({"Message": ex.args[0], "Code": code.args[1]})

        # hash password
        hashed_pw = bcrypt.hashpw(password.encode("utf8"), bcrypt.gensalt())
        # add user to database
        users.insert(
            {
                "Username": username,
                "Password": hashed_pw,
                "Tokens": tokens_start
            }
        )
        return jsonify(
            {
                "Messagee": "You signed up successfully.",
                "Code": helper.OK
            }
        )


weather_keys_valid = [
    "username", "password", "city", "format_temperature"
]
main_keys_valid = ["temp", "temp_max", "temp_min", "feels_like"]
keys_weather_return = [
    "Temperature", "Minimum temperature", "Maximum temperature",
    "Feels like", "Description", "Wind speed"
]


class Weather(Resource):
    """ Send user information about weather in their city. """
    def post(self):
        """ Called when we have a POST request.

        Returns:
            BaseResponse object with message and code
        """
        data = request.get_json()

        # if we do, than we can take values that is sent
        is_valid, msg, code = helper.user_validation(
            users, data, weather_keys_valid, is_register=False
        )
        if not is_valid:
            return jsonify({"Message": msg, "Code": code})

        city = data["city"]
        username = data["username"]
        format_temp = str(data["format_temperature"]).upper()
        if helper.count_tokens(users, username) <= 0:
            return jsonify(
                {
                    "Message": "You are out of tokens, please refill.",
                    "Code": helper.OUT_OF_TOKENS
                }
            )

        # get data from openweather web app
        r = requests.get(f"http://api.openweathermap.org/data/2.5/"
                         f"weather?q={city}"
                         f"&appid=5b18652fc700a44670ccb177ade90c69")
        data_return = dict(r.json())
        # validate that city and counrry exist
        try:
            all_values = helper.validate_city_and_country(
                data_return, helper.DATA_NOT_EXIST
            )
        except KeyError as ex:
            return jsonify({"Message": ex.args[0], "Code": ex.args[1]})

        weather_return = dict(zip(keys_weather_return, all_values))
        temp_to_convert = [weather_return[key] for key in weather_return[:4]]

        try:
            temp_to_convert = helper.validate_temp(
                format_temp, temp_to_convert, weather_return
            )
        except ValueError:
            return jsonify(
                {
                    "Message": ("For temperature in Celsius send 'C', "
                                "for temperature in Fahrenheit send 'F'."),
                    "Code": helper.KEYS_NOT_VALID
                }
            )

        # don't forget to take one token from user
        helper.update_tokens(users, username, sub, 1)
        # finaly, return valid respond with OK status
        return jsonify(
            {
                "Message":
                {
                    f"This is weather for {city}": weather_return
                },
                "Code": helper.OK
            }
        )


admin_pwd = "ad002.C2f"
admin_name = "admin"
refill_keys_valid = ["username", "admin_pwd", "amout"]
# crypting admin's password and inserting into database
admin_pwd_crypted = bcrypt.hashpw(
    admin_pwd.encode("utf8"), bcrypt.gensalt()
)


class Refill(Resource):
    """ Refill tokens. """
    def post(self) -> BaseResponse:
        """ Called when we have a POST request.

        Returns:
            BaseResponse object with message and code
        """
        # add admin's password and username to database
        users.insert(
            {
                "Username": admin_name,
                "Password": admin_pwd_crypted
            }
        )
        data = request.get_json()
        is_valid, msg, code = helper.user_validation(
            users, data, refill_keys_valid, is_register=False
        )
        if not is_valid:
            return jsonify({"Message": msg, "Code": code})
        username = data["username"]
        admin_password = data["admin_pwd"]
        amout_tokens = data["amout"]

        # refill tokens
        helper.update_tokens(
            users, username, add, amout_tokens
        )
        return jsonify(
            {
                "Message": "Tokens updated successfully.",
                "Code": helper.OK
            }
        )


api.add_resource(Register, "/register")
api.add_resource(Weather, "/weather")
api.add_resource(Refill, "/refill")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
